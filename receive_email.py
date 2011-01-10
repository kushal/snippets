import datetime
import email
import logging

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
            create_or_replace_snippet(user, body.decode(), date_for_new_snippet())


def main():
    application = webapp.WSGIApplication([ReceiveEmail.mapping()], debug=True)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()
        

