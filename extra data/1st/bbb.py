import os
import webapp2
import jinja2
from google.appengine.ext import db
template_dir=os.path.join(os.path.dirname(__file__),'template')
jinja_env=jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),autoescape=True)

class handler(webapp2.RequestHandler):
	def write(self,*a,**kw):
		self.response.out.write(*a,**kw)

	def render_str(self,template,**params):
		t=jinja_env.get_template(template)
		print(t.__dict__)
		return t.render(params)

	def render(self,template,**kw):
		self.write	(self.render_str(template,**kw))


class blogs(db.Model):
	title=db.StringProperty(required=True)
	bg=db.TextProperty(required=True)
	time=db.DateTimeProperty(auto_now_add=True)


class mainpage(handler):
	def get(self):
		blogs=db.GqlQuery("select * from blogs order by time desc")
		self.render("bbb.html",blogs=blogs)


class newblog(mainpage):
	def newblog_render(self,title="",bg="", error=""):
		self.render("newblog.html",title=title,bg=bg,error=error)

	def get(self):
		self.newblog_render()	
	
	def post(self):
		title=self.request.get("title")
		bg=self.request.get("bg")
		if title and bg:
			blog=blogs(title=title,bg=bg)
			blog.put()
			self.redirect("/")
		else:
			error="Both entry mandatory"
			self.newblog_render(title,bg,error)


app=webapp2.WSGIApplication([('/',mainpage),('/newblog', newblog),],debug=True)