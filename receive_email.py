import datetime
import email
import logging
import re

from google.appengine.ext import webapp
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler
from google.appengine.ext.webapp import util

from dateutil import date_for_new_snippet
from model import user_from_email, create_or_replace_snippet

class ReceiveEmail(InboundMailHandler):
    """Receive a snippet email and create or replace snippet for this week."""

    def receive(self, message):
        user = user_from_email(email.utils.parseaddr(message.sender)[1])
        for content_type, body in message.bodies('text/plain'):
            content = body.decode()

            sig_pattern = re.compile(r'^\-\-\s*$', re.MULTILINE)
            split_email = re.split(sig_pattern, content)
            content = split_email[0]

            reply_pattern = re.compile(r'^On.*foursquare.com.*wrote:$', re.MULTILINE)
            split_email = re.split(reply_pattern, content)
            content = split_email[0]

            create_or_replace_snippet(user, content, date_for_new_snippet())


def main():
    application = webapp.WSGIApplication([ReceiveEmail.mapping()], debug=True)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()


