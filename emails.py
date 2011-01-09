from google.appengine.api import mail
from google.appengine.api import taskqueue
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

class ReminderEmail(webapp.RequestHandler):
    def get(self):
        pass
        taskqueue.add(url='/onereminder', params={'user': key})

class DigestEmail(webapp.RequestHandler):
    def get(self):
        # Find all users and add to queue
        taskqueue.add(url='/onedigest', params={'user': key})

class OneReminder(webapp.RequestHandler):
    def post(self):
        key = self.request.get('user')
        mail.send_mail(sender="Example.com Support <support@example.com>",
              to="Albert Johnson <Albert.Johnson@example.com>",
              subject="Your account has been approved",
              body="""
Dear Albert:

Your example.com account has been approved.  You can now visit
http://www.example.com/ and sign in using your Google Account to
access new features.

Please let us know if you have any questions.

The example.com Team
""")

class OneDigest(webapp.RequestHandler):
    def post(self):
        key = self.request.get('user')

