import logging

from google.appengine.api import users
from google.appengine.ext import db

class User(db.Model):
    # Just store email address, because GAFYD seems to be buggy (omits domain in stored email or something...)
    email = db.StringProperty()
    following = db.StringListProperty()
    enabled = db.BooleanProperty(default=True)
    tags = db.StringListProperty()
    tags_following = db.StringListProperty()
    
class Snippet(db.Model):
    user = db.ReferenceProperty(User)
    text = db.TextProperty()
    date = db.DateProperty()
    
def compute_following(current_user, users):
    """Return set of email addresses being followed by this user."""
    email_set = set(current_user.following)
    tag_set = set(current_user.tags_following)
    following = set()
    for u in users:
        if ((u.email in email_set) or
            (len(tag_set.intersection(u.tags)) > 0)):
            following.add(u.email)
    return following            
    
def user_from_email(email):
    return User.all().filter("email =", email).fetch(1)[0]
    
def create_or_replace_snippet(user, text, date):
    # Delete existing (yeah, yeah, should be a transaction)
    for existing in Snippet.all().filter("date =", date).filter("user =", user).fetch(10):
        existing.delete()
    
    # Write new
    snippet = Snippet(text=text, user=user, date=date)
    snippet.put()
       