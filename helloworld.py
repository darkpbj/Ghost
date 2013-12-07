import cgi
import datetime
import urllib
import wsgiref.handlers
import re
from google.appengine.ext import db
from google.appengine.api import users
import webapp2
import httplib2
import os
from google.appengine.ext.webapp import template
import pprint
import pickle
import requests
from google.appengine.api import memcache
from google.appengine.api import users
from apiclient.discovery import build
from apiclient.http import MediaFileUpload
from oauth2client.client import OAuth2WebServerFlow
import functools


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
    credentials = pickle.loads(memcache.get("credentials"))
    http = httplib2.Http()
    http = credentials.authorize(http)
    drive_service = build('drive', 'v2', http=http)
    filelist = drive_service.files().list().execute()
    ghostSheet = None
    for item in filelist["items"] :
      if re.match("ghost", item["title"]):
        ghostSheet = item
    resp, text = drive_service._http.request(re.sub('ods$','csv',ghostSheet["exportLinks"]["application/x-vnd.oasis.opendocument.spreadsheet"]))
    rowArray = re.split('\n',text)
    rows = {};
    #no compose/ anon functions:(
    rowArray = map(functools.partial(re.split,','), rowArray)
    for row in rowArray :
      rows[row[0]] = row[1:]
    self.response.content_type = 'text/html'
    self.response.charset = 'utf8'
    self.response.out.write(rows);
    print("yo from main page")

class Setup(webapp2.RequestHandler):
  CLIENT_ID = '510763562071-0j32rsqmra7jfsabt74vhknje9gsir55.apps.googleusercontent.com'
  CLIENT_SECRET = 'Xi-qFx72hFimUWibH7zLvq06'
  # Check https://developers.google.com/drive/scopes for all available scopes
  OAUTH_SCOPE = 'https://www.googleapis.com/auth/drive'
  # Redirect URI for installed apps
  #REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'
  REDIRECT_URI = 'http://localhost:8080/setup'
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
      code = self.request.get('code').strip()
      credentials = flow.step2_exchange(code)
      memcache.set("credentials", pickle.dumps(credentials))
      self.redirect("/");


  def post(self):
    self.redirect('http://example.com')

def custom_dispatcher(router, req, resp):
  rv = router.default_dispatcher(req, resp)
  if req.path == "setup" :
    rv = webapp2.Response(rv)
    return rv
  credentials = pickle.loads(memcache.get("credentials"))
  http = httplib2.Http()
  http = credentials.authorize(http)
  drive_service = build('drive', 'v2', http=http)
  filelist = drive_service.files().list().execute()
  ghostSheet = None
  for item in filelist["items"] :
    if re.match("ghost", item["title"]):
      ghostSheet = item
  status, text = drive_service._http.request(re.sub('ods$','csv',ghostSheet["exportLinks"]["application/x-vnd.oasis.opendocument.spreadsheet"]))
  rows = re.split('\n',text)
  #no compose/ anon functions:(
  rows = map(functools.partial(re.split,','), rows)
  i = 0
  pageIndex = 0;
  respString = '<pre>'
  while i < rows.__len__() :
    if pageIndex != 0:
      respString = respString + rows[i][pageIndex]+ '\n';
    if rows[i][0] == 'pages':
      pageIndex = rows[i].index('/' if req.path.__len__() == 1 else req.path[1:])
      print("page index = ")
      print(pageIndex)
    i += 1

  resp.content_type = 'text/html'
  resp.charset = 'utf8'
  resp.out.write(respString + '</pre>');
  print("yo from main page")
app = webapp2.WSGIApplication([
  ('/setup', Setup)
], debug=True)
app.router.set_dispatcher(custom_dispatcher)


def main():
  app.RUN()


if __name__ == '__main__':
  main()