#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp import util

from emails import *
from model import *

class UserHandler(webapp.RequestHandler):
    def get(self):
        pass

class FollowHandler(webapp.RequestHandler):
    def post(self):
        pass

class ReceiveEmail(webapp.RequestHandler):
    def post(self):
        pass

class MainHandler(webapp.RequestHandler):
  def get(self):
        user = users.get_current_user()

        if user:
            self.response.headers['Content-Type'] = 'text/plain'
            self.response.out.write('Hello, ' + user.nickname())
            template_values = {
            'greetings': greetings,
            'url': url,
            'url_linktext': url_linktext,
            }

            path = os.path.join(os.path.dirname(__file__), 'index.html')
            self.response.out.write(template.render(path, template_values))
        else:
            self.redirect(users.create_login_url(self.request.uri))

def main():
    application = webapp.WSGIApplication(
                                         [('/', MainHandler),
                                          ('/user', UserHandler),
                                          ('/follow', FollowHandler),
                                          ('/reminderemail', ReminderEmail),
                                          ('/digestemail', DigestEmail),
                                          ('/onereminder', OneReminder),
                                          ('/onedigest', OneDigest),
                                          ('/_ah/mail/snippet@fssnippets.appspotmail.com', ReceiveEmail)],
                                          debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
