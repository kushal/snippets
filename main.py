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

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp import util

from emails import *
from model import *

import functools
import urllib

def authenticated(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        # TODO: handle post requests separately
        user = users.get_current_user()
        if not user:
            self.redirect(users.create_login_url(self.request.uri))
            return None
        return method(self, *args, **kwargs)
    return wrapper

class BaseHandler(webapp.RequestHandler):
    def get_user(self):
        '''Returns the user object on authenticated requests'''
        user = users.get_current_user()
        assert user

        userObj = User.all().filter("email =", user.email()).fetch(1)
        if not userObj:
            userObj = User(email=user.email())
            userObj.put()
        else:
            userObj = userObj[0]
        return userObj


class UserHandler(BaseHandler):
    """Show a given user's snippets."""

    @authenticated
    def get(self, email):
        user = self.get_user()
        email = urllib.unquote_plus(email)

        desired_user = user_from_email(email)

        snippets = user.snippet_set
        snippets = sorted(snippets, key=lambda s: s.date, reverse=True)

        self.response.headers['Content-Type'] = 'text/html'
        template_values = {
                           'current_user' : user,
                           'user': desired_user,
                           'snippets': snippets
                           }

        path = os.path.join(os.path.dirname(__file__), 'templates/user.html')
        self.response.out.write(template.render(path, template_values))


class MainHandler(BaseHandler):
    """Show list of all users and acting user's settings."""

    @authenticated
    def get(self):
        user = self.get_user()
        # Update enabled state if requested
        set_enabled = self.request.get('setenabled')
        if set_enabled == '1':
            user.enabled = True
            user.put()
        elif set_enabled == '0':
            user.enabled = False
            user.put()

        # Fetch user list and display
        all_users = User.all().fetch(500)
        self.response.headers['Content-Type'] = 'text/html'
        template_values = {
                           'current_user' : user,
                           'all_users': all_users
                           }

        path = os.path.join(os.path.dirname(__file__), 'templates/index.html')
        self.response.out.write(template.render(path, template_values))


def main():
    application = webapp.WSGIApplication(
                                         [('/', MainHandler),
                                          ('/user/(.*)', UserHandler),
                                          ('/reminderemail', ReminderEmail),
                                          ('/digestemail', DigestEmail)],
                                          debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
