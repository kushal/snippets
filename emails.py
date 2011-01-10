import logging

from google.appengine.api import mail
from google.appengine.api import taskqueue
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

from dateutil import *
from model import *

REMINDER = """
Hey nerd,

The kids want to know what you're up to. Don't leave 'em hanging.
"""

class ReminderEmail(webapp.RequestHandler):
    def __send_mail(self, recipient):
        mail.send_mail(sender="snippets <snippets@fssnippets.appspotmail.com>",
                       to=recipient,
                       subject="Snippet time!",
                       body=REMINDER)

    def get(self):
        all_users = User.all().filter("enabled =", True).fetch(500)
        for user in all_users:
            # TODO: Check if one has already been submitted for this period.
            self.__send_mail(user.email)

class DigestEmail(webapp.RequestHandler):
    def __send_mail(self, recipient, body):
        mail.send_mail(sender="snippets <snippets@fssnippets.appspotmail.com>",
                       to=recipient,
                       subject="Snippet delivery!",
                       body=body)

    def __snippet_to_text(self, snippet):
        divider = '-' * 30
        return '%s\n%s\n%s' % (snippet.user.email, divider, snippet.text)
    
    def get(self):
        all_users = User.all().filter("enabled =", True).fetch(500)
        d = date_for_new_snippet()
        all_snippets = Snippet.all().filter("date =", d).fetch(500)
        for user in all_users:
            following = compute_following(user, all_users)
            body = '\n\n\n'.join([self.__snippet_to_text(s) for s in all_snippets if s.user.email in following])
            if body:
                self.__send_mail(user.email, body)
            else:
                logging.info(user.email + ' not following anybody.')
