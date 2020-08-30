import os
import webapp2
import jinja2

form_html="""
	<form>
		<h2>Add a food</h2>
		<input type="text" name="food">
		%s
		<button>Add</button>
	</form>
"""

hidden_html="""
<input type="hidden" name="food" value="%s">
"""

item_list="<li>%s</li>"

shopping_list_html="""
<br>
<br>
<h2>Shopping list</h2>
<ul>
%s
</ul>
"""
class handler(webapp2.RequestHandler):
	def write(self,*a,**kw):
		self.response.out.write(*a,**kw)


class mainpage(handler):
	def get(self):
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

app=webapp2.WSGIApplication([('/',mainpage),],debug=True)




