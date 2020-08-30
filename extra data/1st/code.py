import hashlib
import hmac
key="pawan"

def hash_str(s):
	return hashlib.md5(s).hexdigest()

#hmac hashing
def hash_str(s):
	return hmac.new(key,s).hexdigest()


def make_secure_value(s):
	return "%s|%s" % (s,hash_str(s))


def check_secure(h):
	val=h.split(',')[0]
	if h==make_secure_value(val)
		return val

print(make_secure_value("cool"))



import random
import string

def make_salt():
    return ''.join(random.choice(string.letters) for x in xrange(5))

# Implement the function valid_pw() that returns True if a user's password 
# matches its hash. You will need to modify make_pw_hash.

#  h[0]= hash(name+pass+salt) and h[1]=salt
def make_pw_hash(name, pw,salt=None):
    if not salt:
    	salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s,%s' % (h, salt)

def valid_pw(name, pw, h):
	salt=h.split(',')[1]
    if h==make_pw_hash(name,pw,salt):




#for parser of xml
from xml.dom import minidom
minidom.parseString
	<function xml.dom.minidom.parseString>
minidom.parseString("<mytag>content!<children><item>1</item><item>2</item></children></mytag>")
	<xml.dom.minidom.Document instance at 0x7fa3c8ab70e0>
x=minidom.parseString("<mytag>content!<children><item>1</item><item>2</item></children></mytag>")
dir(x) #for print attribute of object of class
x.(att).items() #to print key and value of dictionary











when user login or submit the form or password 
it sending to server and attcker can get  it by http
so we can encrypt out http using ssl
https=http+ssl














JSON

we put data in json:
	variable= json.loads('{"key ":"data"}')
for escaping use double salash before the element
	variable= json.loads('{"key ":"data \\"is"}')
for row string to remove escaping
	variable= json.loads(r'{"key ":"data"}')

to convert string or data in json 
	use json.dumps(data)
		json.dumps({"st":"asdf"})