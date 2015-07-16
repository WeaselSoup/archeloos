import time
import sys

from notify import Notifier
from reader import Torrent, list_torrents, parse_results
import config

class Archeloos:
    def __init__(self):
        self.config = config.Config()
        self.notifier = Notifier(**self.config.get("notify", None))
        self.watch = self.config.get("torrents", "watch_dir")
        self.torrents = []
        self.shows = self.config.get("torrents", "shows").split(",")
        self.quality = self.config.get("torrents", "quality")

    def check_torrents(self, torrents):
        l = []
        for t in torrents:
            st = "%s" % t
            for s in self.shows:
                if s.lower() in st.lower():
                    if self.quality in t.quality and t.download(self.watch):
                        print(t)
                        l.append(t)
                    #print(t.link)
        #print(len(torrents))
        return l

    def run(self):
        l = []
        tracker = self.config.get("tracker", None)
        while True:
            new_torrents = []
            feed = list_torrents(tracker["rss_url"], tracker["user_id"], tracker["user_pass"])
            lt = parse_results(feed)
            new_torrents = [t for t in lt if t not in self.torrents]
            self.torrents = list(set(lt) | set(self.torrents))
            l = self.check_torrents(new_torrents)
            self.torrents = self.torrents + new_torrents
            self.notifier.notify(l)

            time.sleep(1800)


if __name__ == "__main__":
    archeloos = Archeloos()
    try:
        archeloos.run()
    except KeyboardInterrupt:
        sys.exit()

