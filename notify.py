import socket
import smtplib

from email.mime.text import MIMEText

class Notifier(object):
    def __init__(self, user, password, server, sender, receivers):
        self.user = user
        self.password = password
        self.server = server
        self.sender = sender
        self.receivers = receivers

    def send_mail(self, text = ""):
        msg = MIMEText(text, 'plain', 'UTF-8')
        msg["Subject"] = "%s: archeloos" % socket.gethostname()
        msg["From"] = "%s" % self.sender
        msg["To"] = "%s" % self.receivers
        server = smtplib.SMTP(self.server)
        #server.set_debuglevel(True)
        server.starttls()
        server.login(self.user, self.password)
        server.sendmail(self.sender, self.receivers, msg.as_string())
        server.quit()

    def notify(self, torrents = []):
        if not torrents:
            return
        text = ""
        for t in torrents:
            text = text + "%s\n" % t
        self.send_mail(text)
