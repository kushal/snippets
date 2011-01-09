import logging, email
from google.appengine.ext import webapp 
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler 
from google.appengine.ext.webapp.util import run_wsgi_app

class ReceiveEmail(InboundMailHandler):
    def receive(self, message):
        logging.info("Received a message from: " + message.sender)
        plaintext_bodies = message.bodies('text/plain')

def main():
    application = webapp.WSGIApplication([ReceiveEmail.mapping()], debug=True)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()
        

