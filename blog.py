import os
import re
import webapp2
import jinja2
import urllib2
import random
import hashlib
import hmac
import logging
import json
from string import letters
from datetime import datetime,timedelta
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

secret = 'fart'

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

def make_secure_val(val):
    return '%s|%s' % (val, hmac.new(secret, val).hexdigest())

def check_secure_val(secure_val):
    val = secure_val.split('|')[0]
    if secure_val == make_secure_val(val):
        return val

class BlogHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        params['user'] = self.user
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def render_json(self, d):
        json_txt = json.dumps(d)
        self.response.headers['Content-Type'] = 'application/json; charset=UTF-8'
        self.write(json_txt)

    def set_secure_cookie(self, name, val):
        cookie_val = make_secure_val(val)
        self.response.headers.add_header(
            'Set-Cookie',
            '%s=%s; Path=/' % (name, cookie_val))

    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val and check_secure_val(cookie_val)

    def login(self, user):
        self.set_secure_cookie('user_id', str(user.key().id()))

    def logout(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        self.user = uid and User.by_id(int(uid))

        if self.request.url.endswith('.json'):
            self.format = 'json'
        else:
            self.format = 'html'


##### user stuff
def make_salt(length = 5):
    return ''.join(random.choice(letters) for x in xrange(length))

def make_pw_hash(name, pw, salt = None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s,%s' % (salt, h)

def valid_pw(name, password, h):
    salt = h.split(',')[0]
    return h == make_pw_hash(name, password, salt)

def users_key(group = 'default'):
    return db.Key.from_path('users', group)

class User(db.Model):
    name = db.StringProperty(required = True)
    dname = db.StringProperty(required = True)
    contact = db.StringProperty()
    email = db.StringProperty()
    pw_hash = db.StringProperty(required = True)


    @classmethod
    def by_id(cls, uid):
        return User.get_by_id(uid, parent = users_key())

    @classmethod
    def by_email(cls, email):
        u = User.all().filter('email =', email).get()
        return u        

    @classmethod
    def by_name(cls, name):
        u = User.all().filter('name =', name).get()
        return u

    @classmethod
    def register(cls, name,dname, pw, email = None,contact=None):
        pw_hash = make_pw_hash(name, pw)
        return User(parent = users_key(),
                    name = name,
                    pw_hash = pw_hash,
                    email = email,
                    dname=dname,
                    contact=contact)

    @classmethod
    def login(cls, name, pw):
        u = cls.by_name(name)
        if u and valid_pw(name, pw, u.pw_hash):
            return u

##### blog stuff

def blog_key(name = 'default'):
    return db.Key.from_path('blogs', name)


class Post(db.Model):
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)

    def render(self):
        content=self.content[:150]
        if len(content)==150:
            content+="........."
        self._render_text = content.replace('\n', '<br>')
        return render_str("post.html", p = self)

    def rr(self):
        self._render_text = self.content.replace('\n', '<br>')
        return render_str("long.html", p = self)

    def as_dict(self):
        time_fmt = '%c'
        d = {'subject': self.subject,
             'content': self.content,
             'created': self.created.strftime(time_fmt),
             'last_modified': self.last_modified.strftime(time_fmt)}
        return d

class BlogFront(BlogHandler):
    def get(self):
        posts=None
        posts = Post.all().order('-created')
        if self.format == 'html':
            self.render('front.html', posts = posts)
        else:
            return self.render_json([p.as_dict() for p in posts])

class PostPage(BlogHandler):
    def get(self, post_id):
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)
        if not post:
            self.error(404)
            return
        if self.format == 'html':
            self.render("perma.html", post = post)
        else:
            self.render_json(post.as_dict())

class NewPost(BlogHandler):
    def get(self):
        if self.user:
            self.render("newpost.html")
        else:
            self.redirect("/login")

    def post(self):
        if not self.user:
            self.redirect('/')

        subject = self.request.get('subject')
        content = self.request.get('content')

        if subject and content:
            p = Post(parent = blog_key(), subject = subject, content = content)
            p.put()
            self.redirect('/%s' % (p.key().id()))
        else:
            error = "subject and content, please!"
            self.render("newpost.html", subject=subject, content=content, error=error)



USER_RE = re.compile(r"^[a-zA-Z0-9 _-]{3,20}$")
def valid_name(name):
    return name and USER_RE.match(name)

PASS_RE = re.compile(r"^.{3,20}$")
def valid_password(password):
    return password and PASS_RE.match(password)

EMAIL_RE  = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
def valid_email(email):
    if len(email)==0:
        return 0
    return not email or EMAIL_RE.match(email)

CONTACT_RE = re.compile(r"^[0-9_-]{10}$")
def valid_contact(contact):
    if len(contact) == 0:
        return True
    if len(contact) != 10:
        return not contact
    return not contact or CONTACT_RE.match(contact) 


class Profile(BlogHandler):
    def get(self):
        if self.user:
            self.render("/profile.html")
        else:
            self.redirect("/login.html")


# id
id=""

class Signup(BlogHandler):
    def get(self):
        self.render("signup.html",id=id)

    def post(self):
        have_error = False
        self.name = self.request.get('name')
        self.dname = self.request.get('dname')
        self.contact = self.request.get('contact')
        self.email = self.request.get('email')
        self.password = self.request.get('password')
        self.verify = self.request.get('verify')

        params = dict(name = self.name,
                      dname = self.dname,
                      id=id,
                      contact=self.contact,
                      email=self.email)

        if not valid_name(self.name):
            params['error_name'] = "That's not a valid username."
            have_error = True

        if not valid_name(self.dname):
            params['error_dname'] = "That's not a valid name."
            have_error = True

        if self.contact:
            if not valid_contact(self.contact):
                params['error_contact'] = "That's not a valid contact."
                have_error = True

        if not valid_password(self.password):
            params['error_password'] = "That wasn't a valid password."
            have_error = True

        elif self.password != self.verify:
            params['error_verify'] = "Your passwords didn't match."
            have_error = True

        if self.email:
            if not valid_email(self.email):
                params['error_email'] = "That's not a valid email."
                have_error = True

        if have_error:
            self.render('signup.html', **params)
        else:
            self.done()

    def done(self, *a, **kw):
        raise NotImplementedError

class Register(Signup):
    def done(self):
        #make sure the user doesn't already exist
        u = User.by_name(self.name)
        u2=User.by_email(self.email)
        if u or u2:
            msg = 'That user already exists.'
            self.render('signup.html', error_name = msg,id=id)
        else:
            u = User.register(self.name,self.dname, self.password, self.email,self.contact)
            ke=u.put()
            self.login(u)
            self.redirect('/')


class Login(BlogHandler):
    def get(self):
        self.render('login.html',id=id)

    def post(self):
        name = self.request.get('name')
        password = self.request.get('password')
        u = User.login(name, password)
        if u:
            self.login(u)
            self.redirect('/')
        else:
            msg = 'Invalid login'
            print(msg)
            self.render('login.html',id=id, error = msg,name=name)


class Logout(BlogHandler):
    def get(self):
        self.logout()
        self.redirect('/signup')



URL= 'https://graph.facebook.com/v6.0/oauth/access_token?client_id=657925015003816&redirect_uri=http://localhost:8888/dataa&client_secret=7ded865c46b21425850884d1c6994c46&code='
URL2="https://graph.facebook.com/me?access_token="
class Facebookdata(BlogHandler):
    def get(self):
        code=self.request.get('code')
        code=URL+str(code)
        r=urllib2.urlopen(code).read()
        data=json.loads(r)
        acc=data["access_token"]
        code2=URL2+str(acc)+"&fields=email,id,name"
        r2=urllib2.urlopen(code2).read()
        data2=json.loads(r2)
        self.name=data2["id"]
        self.dname=data2["name"]
        self.email=data2["email"]
        self.password=data2["id"]
        u = User.by_name(self.name)
        u2=User.by_email(self.email)
        if u or u2:
            if u:
                self.login(u)
            else:
                self.login(u2)

            self.redirect('/')
        else:
            u = User.register(self.name,self.dname, self.password, self.email)
            ke=u.put()
            self.login(u)
            self.redirect('/')


app = webapp2.WSGIApplication([('/?(?:.json)?', BlogFront),
                               ('/([0-9]+)(?:.json)?', PostPage),
                               ('/newpost', NewPost),
                               ('/dataa', Facebookdata),
                               ('/signup', Register),
                               ('/login', Login),
                               ('/logout', Logout),
                               ('/profile', Profile)
                               ],
                              debug=True)
