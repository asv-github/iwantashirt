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
		if not (email and numshirts):
			self.serve_fuckup_page("I need both a number of shirts (for obvious reasons) and an email address (to contact you when the exact price of the shirts is known).")
			return
		try:
			numshirts = int(numshirts)
		except ValueError:
			self.serve_fuckup_page("\"Number of Shirts\" is supposed to be a positive integer, in case that wasn't obvious.")
			return
		if numshirts <= 0:
			self.serve_fuckup_page("\"Number of Shirts\" is supposed to be a positive integer, in case that wasn't obvious.")
			return
		elif numshirts > 20:
			self.serve_fuckup_page("If you're <i>actually</i> interested in that many shirts, send me an email. Otherwise, fuck you, enter a reasonable number.")
			return
		elif len(email) > 128:
			self.serve_fuckup_page("Your email address is too long. If you just want to practice typing that's what the text area is for.")
			return
		elif not re.match("^[a-zA-Z0-9._+@\-]+$", email):
			self.serve_fuckup_page("Your \"email address\" has some funky characters in it. Try again.")
			return
		else:
			# OK, things are probably fine now.
			table.append("{email},{numshirts},{timestamp}\n".format(email=email, numshirts=numshirts, timestamp=int(time.time())))
			self.serve_static_page("<!doctype html><html><head><title>Success!</title></head><body>Awesome! You'll get an email with more details once the exact price of shirts is known.<br>While you're waiting, why not <a href=\"https://bp4u.ru/\">do us a click!</a></body></html>\n")
			

if __name__ == "__main__":
	httpd = http.server.HTTPServer(('',8080), IWantAShirtRequestHandler)
	httpd.serve_forever()
