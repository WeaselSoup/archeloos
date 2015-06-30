import configparser

class Config(object):
    def __init__(self, options = "r"):
        self.config = configparser.RawConfigParser()
        self.fp = open("archeloos.conf", options)
        self.config.readfp(self.fp)

    def __del__(self):
        self.fp.close()

    def set(self, section, key, value):
        if section not in self.config.sections():
            self.config.add_section(section)
        self.config.set(section, key, value)

    def get(self, section, key):
        if not key:
            return dict(self.config.items(section))
        return self.config.get(section, key)

    def save(self):
        self.config.write(self.fp)

if __name__ == "__main__":
    import settings
    config = Config("w+")
    config.set("tracker", "rss_url", settings.URL)
    config.set("tracker", "user_id", settings.UID)
    config.set("tracker", "user_pass", settings.PASS)

    config.set("torrents", "shows", settings.SHOWS)
    config.set("torrents", "watch_dir", settings.WATCH_DIR)

    config.set("notify", "sender", settings.FROM)
    config.set("notify", "user", settings.USERNAME)
    config.set("notify", "password", settings.PASSWORD)
    config.set("notify", "server", settings.SMTP_SERVER)
    config.set("notify", "receivers", settings.TO)
    config.save()

    d = config.get("tracker", None)
    print(d)
    d = config.get("torrents", None)
    print(d)
    d = config.get("notify", None)
    print(d)
