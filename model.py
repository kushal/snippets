import logging

from google.appengine.api import users
from google.appengine.ext import db

class User(db.Model):
    user = db.UserProperty()
    following = db.ListProperty(db.Key)
    enabled = db.BooleanProperty()
    
class Snippet(db.Model):
    user = db.ReferenceProperty(User)
    text = db.TextProperty()
    date = db.DateProperty()
    
def user_from_email(email):
    logging.info(email)
    return User.all().filter("user =", users.User(email)).fetch(1)[0]
    
def create_or_replace_snippet(user, text, date):
    # Delete existing (yeah, yeah, should be a transaction)
    for existing in Snippet.all().filter("date =", date).filter("user =", user).fetch(10):
        existing.delete()
    
    # Write new
    snippet = Snippet(text=text, user=user, date=date)
    snippet.put()
       