import webapp2
import cgi
'''form="""
<form method="post" action="/testform">
	<input name="q">
	<input type="submit">
</form>
"""'''
form="""
<form method="post">
	<label>
	Month
	<input type="text/plain" name="month" value=%(month)s>
	</label>
	<label>
	Day
	<input type="text/plain" name="day" value=%(day)s>
	</label>
	<label>
	Year
	<input type="text/plain" name="year" value=%(year)s>
	</label>
	
	<br>
	<div style="color: green">%(error)s</div>
	<br>

	<input type="submit">
</form>
"""
def valid_month(s):
	months=['January','Febuary','March','April','May','June','July','Auguest','September','October','November','December']
	ss=s.capitalize()
	#print ss
	if ss in months:
		return ss
def valid_day(s):
	if s and s.isdigit():
		ss=int(s)
		if ss>=1 and ss<=31:
			return ss
def valid_year(s):
	if s and s.isdigit():
		ss=int(s)
		if ss>=1900 and ss<=2020:
			return ss
#print(valid_month("january"))
def eascape_html(s):
	return cgi.escape(s,quote=True)
class mainpage(webapp2.RequestHandler):
	def write_form(self,error="",month="",day="",year=""):
		self.response.out.write(form%{"error":error, "month":eascape_html(month),"day":eascape_html(day),"year":eascape_html(year)})
	def get(self):
		#self.response.headers['Content-Type'] = 'text/plain'
		self.write_form()
	def post(self):
		month=self.request.get("month")
		day=self.request.get("day")
		year=self.request.get("year")
		user_month=valid_month(month)
		user_day=valid_day(day)
		user_year=valid_year(year)
		if not(user_month and user_day and user_year):
			self.write_form("wrong input",month,day,year)
		else:
			self.redirect("/thanks")
class thankshandler(webapp2.RequestHandler):
	def get(self):
		self.response.out.write("thanks for the registratation")
'''class testhandler(webapp2.RequestHandler):
	def post(self):
		q=self.request.get("q")
		self.response.out.write(q)
		#self.response.headers['Content-Type'] = 'text/plain'
		#self.response.out.write(self.request)
'''
app=webapp2.WSGIApplication([('/', mainpage),('/thanks',thankshandler)], debug=True)