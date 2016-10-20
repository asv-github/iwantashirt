import http.server, cgi
import time
from subprocess import call
import table

class IWantAShirtRequestHandler(http.server.BaseHTTPRequestHandler):
	def reply(self,string):
		self.wfile.write(string.encode('utf-8'))

	def serve_static_page(self, page, status=200):
		self.send_response_only(status)
		self.send_header("Content-Type","text/html; charset=utf-8")
		self.end_headers()
		self.reply(page)
	def serve_fuckup_page(self, errormessage, status=400):
		page = "<!doctype html><html><head><title>You're a fuckup</title></head><body>%s</body></html>\n" % errormessage
		self.send_response_only(status)
		self.send_header("Content-Type","text/html; charset=utf-8")
		self.end_headers()
		self.reply(page)

	def do_GET(self):
		self.serve_static_page("<!doctype html><html><head><title>That was a GET request</title></head><body>Congrats, you sent a GET request! But you probably wanted to send a POST request.</body></html>\n", status=405)

	def do_POST(self):
		form = cgi.FieldStorage(fp=self.rfile,headers=self.headers,environ={'REQUEST_METHOD': 'POST'})
		email = form.getvalue('email')
		numshirts = form.getvalue('numshirts')
		# Like I said, the text area isn't even recorded
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
		elif (" " in email) or ("," in email) or ("\"" in email) or ("\n" in email):
			self.serve_fuckup_page("Your \"email address\" has some funky characters in it. Try again.")
			return
		else:
			# OK, things are probably fine now.
			table.append("{email},{numshirts},{timestamp}\n".format(email=email, numshirts=numshirts, timestamp=int(time.time())))
			self.serve_static_page("<!doctype html><html><head><title>Success!</title></head><body>Awesome! You'll get an email with more details once the exact price of shirts is known.</body></html>\n")
			

if __name__ == "__main__":
	httpd = http.server.HTTPServer(('',8080), IWantAShirtRequestHandler)
	httpd.serve_forever()
