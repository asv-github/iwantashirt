import http.server, cgi
import re
import time
from subprocess import call
import table

class IWantAShirtRequestHandler(http.server.BaseHTTPRequestHandler):

	# ====================== Convenience methods ======================
	def _reply(self,string):
		"""Convenience method for sending a string to the client (encoded in UTF-8)"""
		self.wfile.write(string.encode('utf-8'))
	def serve_static_page(self, page, status=200):
		"""Serve a static HTML page passed in as a string."""
		self.send_response_only(status)
		self.send_header("Content-Type","text/html; charset=utf-8")
		self.end_headers()
		self._reply(page)

	def serve_fuckup_page(self, errormessage, status=400):
		"""Convenience method for serving a page telling the user they fucked up somehow"""
		page = "<!doctype html><html><head><title>You're a fuckup</title></head><body>%s</body></html>\n" % errormessage
		self.serve_static_page(page, status=status)

	def validate_shirt_count(self, numshirts, size):
		"""
		Take in a string numshirts (a form value) and make sure its a reasonable number of shirts. "size" is the shirt size, used in the error message.
		Returns True if a reasonable number of shirts was ordered; otherwise serve an error message and return False.
		"""
		if not numshirts:
			self.serve_fuckup_page("You didn't tell me how many %s shirts you want to buy." % size)
			return False
		try:
			numshirts = int(numshirts)
			if numshirts < 0: raise ValueError()
		except ValueError:
			self.serve_fuckup_page("You must order a nonnegative integer number of %s shirts. (Hint: 0 means you don't want any.)" % size)
			return False
		if numshirts > 5:
			self.serve_fuckup_page("If you're <i>actually</i> interested in that many %s shirts, send me an email. Otherwise, fuck you, enter a reasonable number." % size)
			return False
		return True

	# ======================= Request handlers ======================

	def do_GET(self):
		self.serve_fuckup_page("Congrats, you sent a GET request. But you should have sent a POST request.", status=405)

	def do_POST(self):
		"""
		This method gets called whenever a client makes a POST request.
		We only have one form, so we'll just assume that's what's beging submitted.
		"""
		# The site only has one form, so we'll just assume that's what the user is submitting.
		form = cgi.FieldStorage(fp=self.rfile,headers=self.headers,environ={'REQUEST_METHOD': 'POST'})
		email = form.getvalue('email')
		numshirts = form.getvalue('numshirts')
		# Like it says in form.html, the text area isn't even recorded

		if not email:
			self.serve_fuckup_page("I need your email address so I can track you down when your shirt arrives.")
			return
		elif len(email) > 128:
			self.serve_fuckup_page("Your email address is too long. If you just want to practice typing that's what the text area is for.")
			return
		elif not re.match("^[a-zA-Z0-9._+@\-]+$", email):
			self.serve_fuckup_page("Your \"email address\" has some funky characters in it. Try again.")
			return
		if not all(self.validate_shirt_count(form.getvalue(size),size) for size in ["S","M","L","XL","XXL"]): # Tricky thing here: this is a generator and not a list, so all() shortcuts out after the first error. (This way you only send one error message instead of all of them.)
			# validate_shirt_count serves the appropriate fuckup page
			return
		# OK, things are probably fine now.
		shirts = {size: int(form.getvalue(size)) for size in ["S","M","L","XL","XXL"]}
		# One last check: Did you order any shirts?
		if not any(shirts.values()):
			self.serve_fuckup_page("You want to buy 0 shirts total? Done.")
			return
		else:
			table.append("{email},{shirts[S]},{shirts[M]},{shirts[L]},{shirts[XL]},{shirts[XXL]},{timestamp}\n".format(email=email,shirts=shirts,timestamp=int(time.time())))
			self.serve_static_page("<!doctype html><html><head><title>Success!</title></head><body>Awesome! You'll get an email once shirts arrive.<br>While you're waiting, why not <a href=\"https://bp4u.ru/\">do us a click!</a></body></html>\n")
			

if __name__ == "__main__":
	httpd = http.server.HTTPServer(('',8080), IWantAShirtRequestHandler)
	httpd.serve_forever()
