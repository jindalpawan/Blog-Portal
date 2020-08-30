import os
import webapp2
import jinja2

template_dir=os.path.join(os.path.dirname(__file__),'template')
jinja_env=jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),autoescape=True)

class handler(webapp2.RequestHandler):
	def write(self,*a,**kw):
		self.response.out.write(*a,**kw)

	def render_str(self,template,**params):
		t=jinja_env.get_template(template)
		return t.render(params)

	def render(self,template,**kw):
		self.write(self.render_str(template,**kw) )


class mainpage(handler):
	def get(self):
		items=self.request.get_all("food")
		self.render("shoping.html",items=items)
		
		n=self.request.get("n")
		if n:
			n=int(n)
		#self.render("shoping.html",animal1=self.request.get("animal1"))
		self.render("shoping.html",n=n)		
		output=form_html
		output_hidden=""
		output_shopping=""
		items=self.request.get_all("food")
		if items:
			output_items=""
			for item in items:
				output_hidden+=hidden_html%item
				output_items+=item_list%item

			output_shopping=shopping_list_html%output_items
			output+=output_shopping
			#print(output_shopping)
		#print(output)
		output=output%output_hidden
		self.write(output)
'''
app=webapp2.WSGIApplication([('/',mainpage),],debug=True)




