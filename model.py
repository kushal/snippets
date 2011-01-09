class User(db.Model):
    user = db.UserProperty()
    enabled = db.StringProperty(multiline=True)
    date = db.DateTimeProperty(auto_now_add=True)