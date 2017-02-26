import time
import sys

from notify import Notifier
from reader import Torrent, Downloader, parse_results
import config

class Archeloos:
    def __init__(self):
        self.config = config.Config()
        self.notifier = Notifier(**self.config.get("notify", None))
        self.watch = self.config.get("torrents", "watch_dir")
        self.torrents = []
        self.shows = self.config.get("torrents", "shows").split(",")
        self.fast_list = self.config.get("torrents", "fast_list").split(",")
        self.resolution = self.config.get("torrents", "resolution")
        self.quality = self.config.get("torrents", "quality")
        self.extra = self.config.get("torrents", "extra")

        tracker = self.config.get("tracker", None)
        self.downloader = Downloader(tracker["rss_url"], tracker["user_id"], tracker["user_pass"])

        print("watch: '%s'" % self.watch)
        print("shows: '%s'" % self.shows)
        print("fast_list: '%s'" % self.fast_list)
        print("resolution: '%s'" % self.resolution)
        print("quality: '%s'" % self.quality)
        print("extra: '%s'" % self.extra)

    def pick_show(self, torrent):
        s = ("%s" % torrent.name).lower()
        shows = [name.lower() for name in self.shows]
        fast_list = [name.lower() for name in self.fast_list]
        print("new pick ", torrent)
        if not any(ss in s for ss in shows):
            return False
        if self.resolution.lower() not in torrent.quality.lower():
            print("  - %s WRONG QUALITY" % torrent)
            return False
        if s in fast_list:
            print("  - %s FAST LIST" % torrent)
            return True
        if self.quality.lower() in torrent.quality.lower():
            print("  - %s OK" % torrent)
            return True
        print("  - %s NOT SELECTED  ('%s' and '%s') != '%s'" % (torrent, self.resolution, self.quality, torrent.quality))
        return False

    def check_torrents(self, torrents):
        l = []
        for t in torrents:
            if self.pick_show(t) and self.downloader.download(t, self.watch):
                l.append(t)
        #print(len(torrents))
        return l

    def run(self):
        l = []
        while True:
            new_torrents = []
            feed = self.downloader.list_torrents()
            lt = parse_results(feed)
            new_torrents = [t for t in lt if t not in self.torrents]
            self.torrents = list(set(lt) | set(self.torrents))
            l = self.check_torrents(new_torrents)
            self.torrents = self.torrents + new_torrents
            self.notifier.notify(l)

            time.sleep(900)


if __name__ == "__main__":
    archeloos = Archeloos()
    try:
        archeloos.run()
    except KeyboardInterrupt:
        sys.exit()

