import webapp2
form="""
<form method="post">
	<label>
		Input Data
		<input type="text/plain" name="data" value="%s">
	</label>
	<br>
	<br>

	<input type="submit">
</form>
"""


def rot13(s):
    ss=""
    l=len(s)
    for i in range(l):
        x=ord(s[i])
        if x>=65 and x<=90:
            x=(x-65+13)%26+65
        else:
            x=(x-97+13)%26+97
        ss+=chr(x)
    return ss


class mainpage(webapp2.RequestHandler):
	def write_form(self, data=""):
		#print(form%data)
		#print(data)
		self.response.out.write(form%data)
	def get(self):
		#self.response.headers['Content-Type'] = 'text/plain'
		self.write_form()

	def post(self):
		data = self.request.get("data")
		x=rot13(data)
		#print(data,x)
		self.write_form(x)
app=webapp2.WSGIApplication([('/', mainpage)], debug=True)