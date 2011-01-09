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


class BaseHandler(webapp.RequestHandler):
    """Obtain user object and pass it into handling logic in subclass."""
    
    def get_user(self):
        user = users.get_current_user()
        if not user:
            self.redirect(users.create_login_url(self.request.uri))
            return None
    
        userObj = User.all().filter("user =", user).fetch(1)
        if not userObj:
            userObj = User(user=user)
            userObj.put()
        else:
            userObj = userObj[0]
        return userObj

    def get(self):
        user = self.get_user()
        if user:
            self.authed_get(user)
            
    def post(self):
        user = self.get_user()
        if user:
            self.authed_post(user)


class UserHandler(BaseHandler):
    """Show a given user's snippets."""
    
    def authed_get(self, user):
        desired_user = user_from_email(self.request.get('email'))
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


class FollowHandler(BaseHandler):
    """Change acting user's follow relationship with another user."""
    
    def authed_post(self, user):
        pass


class MainHandler(BaseHandler):
    """Show list of all users and acting user's settings."""
    
    def authed_get(self, user):
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
                                          ('/user', UserHandler),
                                          ('/follow', FollowHandler),
                                          ('/reminderemail', ReminderEmail),
                                          ('/digestemail', DigestEmail)],
                                          debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
