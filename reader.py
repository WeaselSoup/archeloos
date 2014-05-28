import requests
import feedparser
import re

#import pprint
#pp = pprint.PrettyPrinter(indent=4)

from settings import UID, PASS, URL, LIST

QUALITY = "DSRip|DVBRip|DVDR|DVDRip|DVDScr|HDTV|HR.HDTV|HR.PDTV|PDTV|SatRip|SVCD|TVRip|WebRip|720p|720p.HDTV|1080i|1080p|\."

NAME = "(?P<name>.*)\.S(?P<season>[0-9]+)E(?P<episode>[0-9]+)\.(?P<quality>(%s)+)\.(?P<extra>.*)" % QUALITY
TITLE_RE = r"^%s$" % NAME

STATUS = "Status: (?P<seeders>([0-9]+|no)) seeder(s)? \| (?P<leechers>([0-9]+|no)) leecher(s)?"
SUMMARY_RE = r"^%s\. %s$" % (NAME, STATUS)

def download_torrent(url):
    name = url.split("/")[-1]
    req = requests.get(URL, stream=True)
    with open(TORRENTS_FOLDER + "/" + name, "wb") as f:
        for chunk in req.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
                f.flush()
    return name

def list_torrents(url, user, password):
    cookies = { "uid" : user, "pass" : password }
    req = requests.get(url, cookies=cookies)
    feed = feedparser.parse(req.content)
    for e in feed["entries"]:
        txt = "Title = '%s',  Link = '%s'" % (e["title"], e["link"])
        #print(txt)
    return feed["entries"]

def list_lookup(name, season, episode, quality, extra):
    for l in LIST:
        if name == l["name"]:
            print("MATCH: name='%s', season=%d, episode=%d, quality='%s', extra='%s'" % (name, season, episode, quality, extra))

def parse_results(feed):
    title_pattern = re.compile(TITLE_RE)
    status_pattern = re.compile(SUMMARY_RE)
    for e in feed:
        #print(e)
        txt = ""

        # title
        match = title_pattern.match(e["title"])
        if match:
            name = match.group("name")
            season = int(match.group("season"))
            episode = int(match.group("episode"))
            quality = match.group("quality")
            extra = match.group("extra")

            txt = "name='%s', season=%d, episode=%d, quality='%s', extra='%s'" % (name, season, episode, quality, extra)
            list_lookup(name, season, episode, quality, extra)

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
            txt = txt + ", seeders=%d, leechers=%d" % (seeders, leechers)

        if txt:
            print(txt)


if __name__ == "__main__":
    feed = list_torrents(URL, UID, PASS)
    parse_results(feed)
