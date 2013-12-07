import cgi
import datetime
import urllib
import wsgiref.handlers
from google.appengine.ext import db
from google.appengine.api import users
import webapp2
import os
from google.appengine.ext.webapp import template
import pprint
import pickle
from google.appengine.api import memcache
from google.appengine.api import users
from apiclient.discovery import build
from apiclient.http import MediaFileUpload
from oauth2client.client import OAuth2WebServerFlow


class Greeting(db.Model):
  """Models an individual Guestbook entry with an author, content, and date."""
  author = db.UserProperty()
  content = db.StringProperty(multiline=True)
  date = db.DateTimeProperty(auto_now_add=True)


def guestbook_key(guestbook_name=None):
  """Constructs a datastore key for a Guestbook entity with guestbook_name."""
  return db.Key.from_path('Guestbook', guestbook_name or 'default_guestbook')

class MainPage(webapp2.RequestHandler):
  def get(self):
    credentials = memcache.get("credentials")

    """guestbook_name=self.request.get('guestbook_name')
    greetings_query = Greeting.all().ancestor(
        guestbook_key(guestbook_name)).order('-date')
    greetings = greetings_query.fetch(10)

    if users.get_current_user():
        url = users.create_logout_url(self.request.uri)
        url_linktext = 'Logout'
    else:
        url = users.create_login_url(self.request.uri)
        url_linktext = 'Login'
        
    template_values = {
        'greetings': "fuck off",
        'url': "example.com",
        'url_linktext': "clicky",
    }

    path = os.path.join(os.path.dirname(__file__), 'index.html')
    self.response.out.write(template.render(path, template_values"""

class Setup(webapp2.RequestHandler):
  CLIENT_ID = '510763562071-0j32rsqmra7jfsabt74vhknje9gsir55.apps.googleusercontent.com'
  CLIENT_SECRET = 'Xi-qFx72hFimUWibH7zLvq06'
  # Check https://developers.google.com/drive/scopes for all available scopes
  OAUTH_SCOPE = 'https://www.googleapis.com/auth/drive'
  # Redirect URI for installed apps
  REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'
  # Path to the file to upload
  FILENAME = 'localTest.txt'

  def get(self):
    if memcache.get("flow") == None :
      flow = OAuth2WebServerFlow(self.CLIENT_ID, self.CLIENT_SECRET, self.OAUTH_SCOPE, self.REDIRECT_URI)
      authorize_url = flow.step1_get_authorize_url()
      memcache.set("flow", pickle.dumps(flow))
      self.redirect(authorize_url)
    else:
      flow = pickle.loads(memcache.get("flow"))
      code = self.request.get('verification_code').strip()
      credentials = flow.step2_exchange(code)
      memcache.set("credentials", pickle.dumps(credentials))
      self.response.out.write("yo from else")

  def post(self):
    self.redirect('http://example.com')

app = webapp2.WSGIApplication([
  ('/', MainPage),
  ('/setup', Setup)
], debug=True)


def main():
  app.RUN()


if __name__ == '__main__':
  main()