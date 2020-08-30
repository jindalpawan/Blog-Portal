import os
import webapp2
import jinja2
import re
import hashlib
import hmac
from string import letters
from google.appengine.ext import db
template_dir=os.path.join(os.path.dirname(__file__),'template')
jinja_env=jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),autoescape=True)

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

key="sosecret"

def hash_str(s):
	#hashlib.md5(s).hexdigest()
	return hmac.new(key,s).hexdigest()

def make_secure_value(s):
	return "%s|%s" % (s,hash_str(s))


def check_secure(h):
	val=h.split('|')[0]
	if h==make_secure_value(val):
		return val


class BlogHandler(webapp2.RequestHandler):
	def write(self,*a,**kw):
		self.response.out.write(*a,**kw)

	def render_str(self,template,**params):
		t=jinja_env.get_template(template)
		return t.render(params)

	def render(self,template,**kw):
		self.write(self.render_str(template,**kw))

class Mainpage(BlogHandler):
	def get(self):
		# self.write('hello,Udacity')
		self.response.headers['Content-Type']="text/plain"
		visits=0
		visits_cookie_str=self.request.cookies.get('visits')
		#print(visits_cookie_str)
		'''
		print(visits_cookie_str)
		if visits_cookie_str=="None":
			visits=0
		'''
		if not visits_cookie_str:
			visits=0
		elif visits_cookie_str:
			cookie_val=check_secure(visits_cookie_str)
			#print(cookie_val)
			if cookie_val:
				visits=int(cookie_val)
				print(visits)
		#print(visits)
		visits=visits+1
		new_cookie=make_secure_value(str(visits))
		#print(new_cookie)
		self.response.headers.add_header('Set-Cookie','visits=%s' %new_cookie)

		if visits>10:
			self.write("you are  best")
		else:
			self.write("you have been %s times" % visits)


def blog_key(name='default'):
	return db.Key.from_path('blogs', name)


class Post(db.Model):
	subject=db.StringProperty(required=True)
	content=db.TextProperty(required=True)
	created=db.DateTimeProperty(auto_now_add=True)
	last_Modified=db.DateTimeProperty(auto_now=True)

	def render(self):
		self._render_text=self.content.replace('\n','<br>')
		return render_str("post.html",p = self)

class BlogFront(BlogHandler):
    def get(self):
        posts = db.GqlQuery("select * from Post order by created desc limit 10")
        self.render('front.html', posts = posts)

class PostPage(BlogHandler):
	def get(self,post_id):
		key=db.Key.from_path('Post',int(post_id),parent=blog_key())
		post=db.get(key)

		if not post:
			self.error(404)
			return
		self.render("permalink.html",post=post)

class Newpost(BlogHandler):
	def get(self):
		self.render("newpost.html")
	def post(self):
		subject=self.request.get('subject')
		content=self.request.get('content')
		if subject and content:
			p=Post(parent=blog_key(),subject=subject,content=content)
			p.put()
			self.redirect('/blog/%s '% str(p.key().id()))
		else:
			error="subject and content plz!!"
			self.render("newpost.html",subject=subject,content=content,error=error)


app = webapp2.WSGIApplication([('/',Mainpage),
								('/blog/?',BlogFront),
								('/blog/([0-9]+)',PostPage),
								('/blog/newpost',Newpost),
								],debug=True)

