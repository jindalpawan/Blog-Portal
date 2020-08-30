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


def user(s):
    for x in s:
        if x=='(' or x==')' or x=='-' or x=='*' or x=='/' or x=='[' :
            return 0
        if x==' ' or x==',' or x=='%' or x=='@' or x=='#' or x==']' :
            return 0
        if len(s)==0:
        	return 0
    return 1
x=""
class mainpage(webapp2.RequestHandler):
	def write_page(self,username="",password="",vpassword="",a="",b="",c=""):
		self.response.out.write(form% {"username":username,"password":password,"vpassword":vpassword,"a":a,"b":b,"c":c})
	def get(self):
		self.write_page()

	def post(self):
		email=self.request.get("email")	
		username=self.request.get("username")
		password=self.request.get("password")
		vpassword=self.request.get("vpassword")
		if user(username) and password and password==vpassword:
			x=username
			self.redirect("/welcome")
		else:
			if not(user(username)):
				self.write_page(username,password,vpassword,"Invalid User_name")
			elif len(password)==0:
				self.write_page(username,password,vpassword,"","Invalid Password")
			elif password!=vpassword:
				self.write_page(username,password,vpassword,"","","Password not match")

class welcomepage(webapp2.RequestHandler):
	def get(self):
		self.response.out.write("Welcome")
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

app=webapp2.WSGIApplication([('/', mainpage),('/welcome',welcomepage)], debug=True)