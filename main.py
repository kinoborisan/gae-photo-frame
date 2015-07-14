import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'mysite.settings'
import django.core.handlers.wsgi
app = django.core.handlers.wsgi.WSGIHandler()

import time
import datetime
import base64
import string

import webapp2
from google.appengine.ext import db
from google.appengine.api import images
from google.appengine.api import urlfetch
from google.appengine.ext.webapp import template

class TblCard(db.Model):
  CardNum = db.IntegerProperty()
  CardName = db.StringProperty(multiline=False)
  CardDesc = db.StringProperty(multiline=True)
  CardDate = db.DateTimeProperty()
  CardImage = db.BlobProperty()
  CardIPAddress = db.StringProperty(multiline=False)

class TblFrame(db.Model):
  FrameNum = db.IntegerProperty()
  FrameDate = db.DateTimeProperty()
  FrameImage = db.BlobProperty()
  FrameIPAddress = db.StringProperty(multiline=False)


class MainHandler(webapp2.RequestHandler):
  def get(self):
    tl = db.GqlQuery("SELECT * FROM TblCard ORDER BY CardDate DESC LIMIT 20")

    template_values = {
      'tl': tl
    }
    self.response.out.write(template.render('htdocs/index.html', template_values))

class FormHandler(webapp2.RequestHandler):
  def get(self):
    tlFrame = db.GqlQuery("SELECT * FROM TblFrame ORDER BY FrameDate DESC LIMIT 200")

    template_values = {
      'tlFrame': tlFrame
    }
    self.response.out.write(template.render('htdocs/form.html', template_values))

class SetCardHandler(webapp2.RequestHandler):
  def post(self):
    if ( self.request.get("img1") ):
      PresentTCard = TblCard.all()
      PresentTCard.order('CardNum').fetch(limit=1)
      NextId = 0
      for r in PresentTCard:
        if PresentTCard:
          NextId = r.CardNum + 1
        else:
          NextId = 0
      TCard = TblCard()
      TCard.CardNum = NextId
      if self.request.get("name1"):
        TCard.CardName = self.request.get("name1")
      else:
        TCard.CardName = u"aainc member"
      if self.request.get("desc1"):
        TCard.CardDesc = self.request.get("desc1")
      else:
        TCard.CardDesc = u"thanks"

      Img = images.resize(self.request.get("img1").decode('base64'),600,600)


      framePath = 'http://' + os.environ['HTTP_HOST'] + self.request.get("framePath")

      try:
        ImgFrame = images.resize(urlfetch.Fetch(framePath).content,600,600)
      except:
        time.sleep(3)
        ImgFrame = images.resize(urlfetch.Fetch(framePath).content,600,600)
        try:
          ImgFrame = images.resize(urlfetch.Fetch(framePath).content,600,600)
        except:
          time.sleep(3)
          ImgFrame = images.resize(urlfetch.Fetch(framePath).content,600,600)

      ImgComp = images.composite([(Img,0,0,1.0,0),(ImgFrame,0,0,1.0,0)],600,600)
      TCard.CardImage = db.Blob(ImgComp)

      TCard.CardDate = datetime.datetime.today() + datetime.timedelta(hours=9)
      TCard.CardIPAddress = os.environ['REMOTE_ADDR']

      db.put(TCard)

      cUrl = "/Detail?cid=" + str( TCard.CardNum )
      self.response.out.write( cUrl )

    else:
      self.response.out.write( "/Err" )

# FRAME
class FrameFormHandler(webapp2.RequestHandler):
  def get(self):
    tl = db.GqlQuery("SELECT * FROM TblCard ORDER BY CardDate DESC LIMIT 20")
    tlFrame = db.GqlQuery("SELECT * FROM TblFrame ORDER BY FrameDate DESC LIMIT 200")

    template_values = {
      'tl': tl,
      'tlFrame': tlFrame
    }
    self.response.out.write(template.render('htdocs/frameForm.html', template_values))

class SetFrameHandler(webapp2.RequestHandler):
  def post(self):
    if ( self.request.get("img1") ):
      PresentTFrame = TblFrame.all()
      PresentTFrame.order('FrameNum').fetch(limit=1)
      NextId = 0
      for r in PresentTFrame:
        if PresentTFrame:
          NextId = r.FrameNum + 1
        else:
          NextId = 0
      TFrame = TblFrame()
      TFrame.FrameNum = NextId

      Img = images.resize(self.request.get("img1"), 600, 600)

      TFrame.FrameImage = db.Blob(Img)

      TFrame.FrameDate = datetime.datetime.today() + datetime.timedelta(hours=9)
      TFrame.FrameIPAddress = os.environ['REMOTE_ADDR']

      db.put(TFrame)

      cUrl = "/FrameForm"
      self.redirect( cUrl )

    else:
      self.redirect( '/Err' )

class DeleteFrameHandler(webapp2.RequestHandler):
  def get(self):
    if ( self.request.get("deleteID") ):
      entity = db.get(self.request.get("deleteID"))
      entity.delete()
      cUrl = "/FrameForm"
      self.redirect( cUrl )

    else:
      self.redirect( '/Err' )


# detail
class DetailHandler(webapp2.RequestHandler):
  def get(self):
    if self.request.get("cid")!="":
      CardNum = int(self.request.get("cid"))
      TCard = TblCard.all()
      tl = db.GqlQuery("SELECT * FROM TblCard WHERE CardNum =:CCardNum", CCardNum = int(CardNum) )

      CardName = ""
      CardImage = ""
      CardDesc = ""
      CardDate = ""

      for r in tl:
        CardNum = r.CardNum
        CardName = r.CardName
        CardDate = r.CardDate
        CardDesc = r.CardDesc
        CardImage = r.key()

      template_values = {
        'CardNum' : CardNum ,
        'CardName': CardName,
        'CardDate': CardDate,
        'CardDesc': CardDesc,
        'CardImage': CardImage
        }

      self.response.out.write(template.render('htdocs/detail.html', template_values))


class Image (webapp2.RequestHandler):
  def get(self):
    UQ = db.get(self.request.get("img_id"))
    if UQ.CardImage:
      self.response.headers['Content-Type'] = "image/png"
      self.response.out.write(UQ.CardImage)
    else:
      self.response.out.write("No image")

class FrameImage (webapp2.RequestHandler):
  def get(self):
    UQ = db.get(self.request.get("img_id"))
    if UQ.FrameImage:
      self.response.headers['Content-Type'] = "image/png"
      self.response.out.write(UQ.FrameImage)
    else:
      self.response.out.write("No image")

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/Form', FormHandler),
    ('/SetCard', SetCardHandler),
    ('/FrameForm', FrameFormHandler),
    ('/SetFrame', SetFrameHandler),
    ('/DeleteFrame', DeleteFrameHandler),
    ('/Detail',DetailHandler),
    ('/Image', Image),
    ('/FrameImage', FrameImage)
], debug=True)