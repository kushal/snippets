import logging

from google.appengine.api import users
from google.appengine.ext import db

class User(db.Model):
    # Just store email address, because GAFYD seems to be buggy (omits domain in stored email or something...)
    email = db.StringProperty()
    following = db.ListProperty(db.Key)
    enabled = db.BooleanProperty(default=True)
    
class Snippet(db.Model):
    user = db.ReferenceProperty(User)
    text = db.TextProperty()
    date = db.DateProperty()
    
def user_from_email(email):
    return User.all().filter("email =", email).fetch(1)[0]
    
def create_or_replace_snippet(user, text, date):
    # Delete existing (yeah, yeah, should be a transaction)
    for existing in Snippet.all().filter("date =", date).filter("user =", user).fetch(10):
        existing.delete()
    
    # Write new
    snippet = Snippet(text=text, user=user, date=date)
    snippet.put()
       