import os
import requests
import feedparser
import re

import pprint
pp = pprint.PrettyPrinter(indent=4)


QUALITY = "DSRip|DVBRip|DVDR|DVDRip|DVDScr|HDTV|HR.HDTV|HR.PDTV|PDTV|SatRip|SVCD|TVRip|WebRip|720p|720p.HDTV|1080i|1080p|\."

EPISODE = "(?P<name>.*)\.S(?P<season>[0-9]+)E(?P<episode>[0-9]+)\.(?P<quality>(%s)+)\.(?P<extra>.*)" % QUALITY
EPISODE_RE = r"^%s$" % EPISODE

SEASON = "(?P<name>.*)\.(S|Season\.)(?P<season>[0-9]+)\.(?P<quality>(%s)+)\.(?P<extra>.*)" % QUALITY
SEASON_RE = r"^%s$" % SEASON

COMPLETE = "(?P<name>.*)\.Complete\.(?P<quality>(%s)+)\.(?P<extra>.*)" % QUALITY
COMPLETE_RE = r"^%s$" % COMPLETE

STATUS = "Status: (?P<seeders>([0-9]+|no)) seeder(s)? \| (?P<leechers>([0-9]+|no)) leecher(s)?"
#SUMMARY_RE = r"^(%s|%s|%s)\. %s$" % (EPISODE, SEASON, COMPLETE, STATUS)
SUMMARY_RE = r"^%s. %s$" % (EPISODE, STATUS)

class Torrent(object):
    def __init__(self, name, quality, extra, link, season = None, episode = None):
        self.name = name
        self.season = season
        self.episode = episode
        self.quality = quality
        self.extra = extra
        self.link = link

    def __str__(self):
        if self.episode:
            s = "%s.S%02d.E%02d.%s.%s" % (self.name, self.season, self.episode, self.quality, self.extra)
        elif self.season:
            s = "%s.S%02d.%s.%s" % (self.name, self.season, self.quality, self.extra)
        else:
            s = "%s.COMPLETE.%s.%s" % (self.name, self.quality, self.extra)
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

    def download(self, location):
        name = "%s.torrent" % self
        #print("download '%s' to '%s'" % (name, location))
        path = location + "/" + name
        #print(name)
        #print(path)
        #print(self.link)
        if (os.path.isfile(path + ".added")):
            print("file: '%s' already exist" % path)
            return False
        req = requests.get(self.link, stream=True)
        with open(path, "wb") as f:
            for chunk in req.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    f.flush()
        return True

def list_torrents(url, user, password):
    cookies = { "uid" : user, "pass" : password }
    try:
        req = requests.get(url, cookies=cookies)
    except Exception as e:
        print(e)
        return []
    feed = feedparser.parse(req.content)
    #for e in feed["entries"]:
    #    txt = "Title = '%s',  Link = '%s'" % (e["title"], e["link"])
    #    #print(txt)
    return feed["entries"]

def list_lookup(name, season, episode, quality, extra):
    for l in LIST:
        if name == l["name"]:
            print("MATCH: name='%s', season=%d, episode=%d, quality='%s', extra='%s'" % (name, season, episode, quality, extra))

def parse_results(feed):
    episode_pattern = re.compile(EPISODE_RE)
    season_pattern = re.compile(SEASON_RE)
    complete_pattern = re.compile(COMPLETE_RE)
    status_pattern = re.compile(SUMMARY_RE)
    l = []
    for e in feed:
        t = None
        #pp.pprint(e)
        #print("---")
        link = e["link"]

        # episode
        match = episode_pattern.match(e["title"])
        if match:
            name = match.group("name")
            season = int(match.group("season"))
            episode = int(match.group("episode"))
            quality = match.group("quality")
            extra = match.group("extra")
            t = Torrent(name = name, season = season, episode = episode, quality = quality, extra = extra, link = link)
        else:
            # season
            match = season_pattern.match(e["title"])
            if match:
                name = match.group("name")
                season = int(match.group("season"))
                quality = match.group("quality")
                extra = match.group("extra")
                t = Torrent(name = name, season = season, quality = quality, extra = extra, link = link)
            else:
                # complete
                match = complete_pattern.match(e["title"])
                if match:
                    name = match.group("name")
                    quality = match.group("quality")
                    extra = match.group("extra")
                    t = Torrent(name = name, quality = quality, extra = extra, link = link)

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
