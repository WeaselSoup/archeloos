import os
import requests
import re
import feedparser
from guessit import guessit

from urllib.parse import urlparse

import pprint
pp = pprint.PrettyPrinter(indent=4)

PROVIDERS = "HULU|HBO|AMZN"
RIPS = "DSRip|DVBRip|DVDR|DVDRip|DVDScr|BluRay|SatRip|TVRip|WebRip|WEBRip|WEB-DL|WEB|HDTV|HR|PDTV|SVCD"
PACKS = "RERiP|PROPER|REAL|REPACK|EXTENDED|INTERNAL"
RESOLUTION ="720p|1080i|1080p"
QUALITY = "%s|%s|%s|%s|\." % (PROVIDERS, RIPS, PACKS, RESOLUTION)

TITLE = "(!?(%s))[a-zA-Z\.']+" % (QUALITY)

EPISODE = "(?P<name>.*)\.S(?P<season>[0-9]+)\.?E(?P<episode>[0-9]+)(?P<title>%s)?\.(?P<quality>(%s)+)\.(?P<extra>.*)" % (TITLE, QUALITY)
EPISODE_RE = r"^%s$" % EPISODE

SEASON = "(?P<name>.*)\.(S|Season\.)(?P<season>[0-9]+)\.(?P<quality>(%s)+)\.(?P<extra>.*)" % (QUALITY)
SEASON_RE = r"^%s$" % SEASON

COMPLETE = "(?P<name>.*)\.(Complete|COMPLETE)\.(?P<quality>(%s)+)\.(?P<extra>.*)" % (QUALITY)
COMPLETE_RE = r"^%s$" % COMPLETE

STATUS = "Status: (?P<seeders>([0-9]+|no)) seeder(s)? \| (?P<leechers>([0-9]+|no)) leecher(s)?"
#SUMMARY_RE = r"^(%s|%s|%s)\. %s$" % (EPISODE, SEASON, COMPLETE, STATUS)
SUMMARY_RE = r"^%s. %s$" % (EPISODE, STATUS)

class Torrent(object):
    def __init__(self, name, resolution, quality, extra, link, season = None, episode = None, date = None):
        self.name = name
        self.season = season
        self.episode = episode
        self.date = date
        self.resolution = resolution
        self.quality = quality
        self.extra = extra
        self.link = link

    def __str__(self):
        if self.episode:
            s = "%s.S%02d.E%02d.%s.%s.%s" % (self.name, self.season, self.episode, self.resolution, self.quality, self.extra)
        elif self.season:
            s = "%s.S%02d.%s.%s.%s" % (self.name, self.season, self.resolution, self.quality, self.extra)
        elif self.date:
            s = "%s.%s.%s.%s.%s" % (self.name, self.date, self.resolution, self.quality, self.extra)
        else:
            s = "%s.COMPLETE.%s.%s.%s" % (self.name, self.resolution, self.quality, self.extra)
        return s

    def __eq__(self, other):
        if type(other) is type(self):
            return self.__dict__ == other.__dict__
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash("Torrent%s" % self)


class Downloader(object):
    def __init__(self, url, user, password):
        self.url = url
        self.cookies = { "uid" : user, "pass" : password }

    def list_torrents(self):
        try:
            req = requests.get(self.url, cookies=self.cookies)
        except Exception as e:
            print(e)
            return []
        feed = feedparser.parse(req.content)
        #for e in feed["entries"]:
        #    txt = "Title = '%s',  Link = '%s'" % (e["title"], e["link"])
        #    #print(txt)
        return feed["entries"]

    def download(self, torrent, location):
        name = "%s.torrent" % torrent
        #print("download '%s' to '%s'" % (name, location))
        path = location + "/" + name
        #print(name)
        #print(path)
        id_torrent = self.extract_id(torrent.link)
        link = "https://freshon.tv/download.php?" + id_torrent + "&amp;type=torrent"
        #print(link)
        if (os.path.isfile(path + ".added")):
            print("file: '%s' already exist" % path)
            return False
        req = requests.get(link, stream=True, cookies=self.cookies)
        with open(path, "wb") as f:
            for chunk in req.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    f.flush()
        return True

    def extract_id(self, url):
        o = urlparse(url)
        return o.query

def list_lookup(name, season, episode, quality, extra):
    for l in LIST:
        if name == l["name"]:
            print("MATCH: name='%s', season=%d, episode=%d, quality='%s', extra='%s'" % (name, season, episode, quality, extra))

def parse_results(feed):
    status_pattern = re.compile(SUMMARY_RE)
    l = []
    for e in feed:
        t = None
        link = e["link"]
        guess = guessit(e["title"])

        name = None
        season = None
        episode = None
        title = None
        resolution = ""
        quality = ""
        extra = ""
        date = ""
        if "title" in guess:
            name = guess["title"].replace(" ", ".")
        if "season" in guess:
            season = guess["season"]
        if "episode" in guess:
            episode = guess["episode"]
        if "episode_title" in guess:
            title = guess["episode_title"].replace(" ", ".")
        if "date" in guess:
            date = guess["date"]
        if "screen_size" in guess:
            resolution = guess["screen_size"]
        if "format" in guess:
            quality = guess["format"]
        if "video_codec" in guess:
            extra = guess["video_codec"]
        #print("title = '%s'" % e["title"])
        #print(guess)
        if name and (season or date):
            #print("name = '%s',  season = '%s',  episode = '%s',  date= '%s',  resolution = '%s',  quality = '%s',  extra = '%s',  link = '%s'" % (name, season, episode, date, resolution, quality, extra, link))
            t = Torrent(name = name, season = season, episode = episode, date = date, resolution = resolution, quality = quality, extra = extra, link = link)
        else:
            print("no match '%s'" % e["title"])
            print("name = '%s',  season = '%s',  episode = '%s',  date= '%s',  resolution = '%s',  quality = '%s',  extra = '%s',  link = '%s'" % (name, season, episode, date, resolution, quality, extra, link))

        # seeders / leechers
        def _cast_int(s):
            if s == "no":
                return 0
            else:
                return s
        match = status_pattern.match(e["summary"])
        if match:
            seeders = int(_cast_int(match.group("seeders")))
            leechers = int(_cast_int(match.group("leechers")))

        if t:
            l.append(t)

    return l
