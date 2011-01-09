import datetime
import email
import logging

from google.appengine.ext import webapp 
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler 
from google.appengine.ext.webapp import util

from model import user_from_email, create_or_replace_snippet


class Eastern_tzinfo(datetime.tzinfo):
    """Implementation of the Eastern timezone.
    
    Adapted from http://code.google.com/appengine/docs/python/datastore/typesandpropertyclasses.html
    """
    def utcoffset(self, dt):
        return datetime.timedelta(hours=-5) + self.dst(dt)

    def _FirstSunday(self, dt):
        """First Sunday on or after dt."""
        return dt + datetime.timedelta(days=(6-dt.weekday()))

    def dst(self, dt):
        # 2 am on the second Sunday in March
        dst_start = self._FirstSunday(datetime.datetime(dt.year, 3, 8, 2))
        # 1 am on the first Sunday in November
        dst_end = self._FirstSunday(datetime.datetime(dt.year, 11, 1, 1))

        if dst_start <= dt.replace(tzinfo=None) < dst_end:
            return datetime.timedelta(hours=1)
        else:
            return datetime.timedelta(hours=0)
        
    def tzname(self, dt):
        if self.dst(dt) == datetime.timedelta(hours=0):
            return "EST"
        else:
            return "EDT"
        
        
class ReceiveEmail(InboundMailHandler):
    """Receive a snippet email and create or replace snippet for this week."""

    def receive(self, message):
        user = user_from_email(message.sender)               
        for content_type, body in message.bodies('text/plain'):        
            today = datetime.datetime.now(Eastern_tzinfo()).date()
            
            # For now, just align to next Monday, unless it is Monday (0), Tuesday (1)
            if (today.weekday() < 2):
                aligned = today - datetime.timedelta(days=today.weekday())
            else:
                aligned = today + datetime.timedelta(days=(7 - today.weekday()))
    
            create_or_replace_snippet(user, body.decode(), aligned)


def main():
    application = webapp.WSGIApplication([ReceiveEmail.mapping()], debug=True)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()
        

