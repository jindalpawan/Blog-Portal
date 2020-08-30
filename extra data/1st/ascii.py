import os
import webapp2
import logging
import jinja2
import urllib2
from xml.dom import minidom
from google.appengine.api import memcache
from google.appengine.ext import db
from collections import namedtuple
template_dir=os.path.join(os.path.dirname(__file__),'template')
jinja_env=jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),autoescape=True)

#Point = namedtuple('Point', ["lat", "lon"])
#points=[Point(1,2),Point(3,4),Point(5,6)]

GMAPS_URL ="http://maps.googleapis.com/maps/api/staticmap?size=380x263&sensor=false&"
def gmaps_img(points):
	markers='&'.join('markers=%s,%s'%(p.lat,p.lon) for p in points)
	#print(GMAPS_URL)
	return GMAPS_URL+markers


Format_URL="http://api.hostip.info/?ip="
def get_coordinate(ip):
	ip="23.24.209.141"
	url=Format_URL+ip
	content=None
	try:
		req = urllib2.Request(url, headers={'User-Agent' : "Magic Browser"}) 
		content=urllib2.urlopen(req).read()
	except URLError:
		return
	if content:
		#print(content)
		d=minidom.parseString(content)
		coords=d.getElementsByTagName("gml:coordinates")[0]
		if coords and coords.childNodes[0].nodeValue:
			x,y=coords.childNodes[0].nodeValue.split(',')
			#print(x , y)
			return db.GeoPt(y,x)


class handler(webapp2.RequestHandler):
	def write(self,*a,**kw):
		self.response.out.write(*a,**kw)

	def render_str(self,template,**params):
		t=jinja_env.get_template(template)
		return t.render(params)

	def render(self,template,**kw):
		self.write	(self.render_str(template,**kw))

def top_art(update=False):
	key='top'
	arts=memcache.get(key)
	if arts is None or update:
		logging.error("DB QUERY")
		arts=db.GqlQuery("select * from Art order by create desc")
		arts=list(arts)
		memcache.set(key,arts)
	return arts


class Art(db.Model):
	title=db.StringProperty(required=True)
	art = db.TextProperty(required=True)
	create=db.DateTimeProperty(auto_now_add=True)
	coords=db.GeoPtProperty()
	#lat=db.StringProperty()
	#lng=db.StringProperty()

class mainpage(handler):
	def front_render(self,title="",art="",error=""):
		arts=top_art()
		points=filter(None,(a.coords for a in arts)) #filter...
		img_url=None
		#print(points)
		if points:
			img_url=gmaps_img(points)
		#print(img_url)	
		self.render("ascii.html",title=title,art=art,error=error,arts=arts, img_url=img_url,points=points)
	def get(self):
		#self.write(repr(get_coordinate(self.request.remote_addr)))
		self.front_render()

	def post(self):
		title=self.request.get("title")
		art=self.request.get("art")

		if title and art:
			a=Art(title=title,art=art)
			coors=get_coordinate(self.request.remote_addr)
			if coors:
				a.coords=coors
			a.put()
			top_art(True)
			self.redirect("/")
		else:
			error="we need title and some art work"
			self.front_render(title,art,error)

app=webapp2.WSGIApplication([('/',mainpage),],debug=True)