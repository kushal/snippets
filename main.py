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
    
    def render(self, template_name, template_values):
        self.response.headers['Content-Type'] = 'text/html'
        path = os.path.join(os.path.dirname(__file__), 'templates/%s.html' % template_name)
        self.response.out.write(template.render(path, template_values))
        

class UserHandler(BaseHandler):
    """Show a given user's snippets."""

    @authenticated
    def get(self, email):
        user = self.get_user()
        email = urllib.unquote_plus(email)
        desired_user = user_from_email(email)
        snippets = desired_user.snippet_set
        snippets = sorted(snippets, key=lambda s: s.date, reverse=True)
        following = email in user.following 
        tags = [(t, t in user.tags_following) for t in desired_user.tags]
         
        template_values = {
                           'current_user' : user,
                           'user': desired_user,
                           'snippets': snippets,
                           'following': following,
                           'tags': tags
                           }
        self.render('user', template_values)


class FollowHandler(BaseHandler):
    """Follow a user or tag."""
    @authenticated
    def get(self):
        user = self.get_user()
        desired_tag = self.request.get('tag')
        desired_user = self.request.get('user')
        continue_url = self.request.get('continue')
        
        if desired_tag and (desired_tag not in user.tags_following):
            user.tags_following.append(desired_tag)
            user.put()
        if desired_user and (desired_user not in user.following):
            user.following.append(desired_user)
            user.put()
            
        self.redirect(continue_url)


class UnfollowHandler(BaseHandler):
    """Unfollow a user or tag."""
    @authenticated
    def get(self):
        user = self.get_user()
        desired_tag = self.request.get('tag')
        desired_user = self.request.get('user')
        continue_url = self.request.get('continue')
        
        if desired_tag and (desired_tag in user.tags_following):
            user.tags_following.remove(desired_tag)
            user.put()
        if desired_user and (desired_user in user.following):
            user.following.remove(desired_user)
            user.put()
            
        self.redirect(continue_url)
        

class TagHandler(BaseHandler):
    """View this week's snippets in a given tag."""
    @authenticated
    def get(self, tag):
        user = self.get_user()
        d = date_for_retrieval()
        all_snippets = Snippet.all().filter("date =", d).fetch(500)
        if (tag != 'all'):
            all_snippets = [s for s in all_snippets if tag in s.user.tags]
        following = tag in user.tags_following

        template_values = {
                           'current_user' : user,
                           'snippets': all_snippets,
                           'following': following,
                           'tag': tag
                           }
        self.render('tag', template_values)

    
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

        # Update tags if sent
        tags = self.request.get('tags')
        if tags:
            user.tags = [s.strip() for s in tags.split(',')]
            user.put()
            
        # Fetch user list and display
        raw_users = User.all().order('email').fetch(500)
        following = compute_following(user, raw_users)
        all_users = [(u, u.email in following) for u in raw_users]

        template_values = {
                           'current_user' : user,
                           'all_users': all_users                           
                           }
        self.render('index', template_values)


def main():
    application = webapp.WSGIApplication(
                                         [('/', MainHandler),
                                          ('/user/(.*)', UserHandler),
                                          ('/tag/(.*)', TagHandler),
                                          ('/follow', FollowHandler),
                                          ('/unfollow', UnfollowHandler),
                                          ('/reminderemail', ReminderEmail),
                                          ('/digestemail', DigestEmail)],
                                          debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
