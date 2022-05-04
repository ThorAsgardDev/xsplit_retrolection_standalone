
# To remove authorization go to: https://myaccount.google.com/permissions

import configparser
import http.server
import requests
import urllib
import socketserver
import sys


config = configparser.ConfigParser()
config.read("config.ini")

oauth_client_id = config["SHEET"]["OAUTH_CLIENT_ID"]
oauth_client_secret = config["SHEET"]["OAUTH_CLIENT_SECRET"]

param = {
	"client_id": oauth_client_id,
	"redirect_uri": "http://localhost:8000",
	"response_type": "code",
	"scope": "https://www.googleapis.com/auth/spreadsheets",
}
url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode(param, True)


print("Copy this url to a web browser, log-in and grant permissions: " + url)

code = None
class MyHandler(http.server.BaseHTTPRequestHandler):

	def do_HEAD(self):
		print("HEAD")
		self.send_response(200)

	def do_GET(self):
		parsed_url = urllib.parse.urlparse(self.path)
		query_components = urllib.parse.parse_qs(parsed_url.query)
		global code
		code = query_components["code"][0]
		print("Code is: ", code)
		self.send_response(200)
		self.end_headers()

	def do_POST(self):
		print("POST")
		self.send_response(405)
		self.end_headers()   

print("serving at port", 8000)
httpd = http.server.HTTPServer(("", 8000), MyHandler)
httpd.handle_request()

headers = {
	"Content-Type": "application/x-www-form-urlencoded",
}
param = {
	"code": code,
	"client_id": oauth_client_id,
	"client_secret": oauth_client_secret,
	"redirect_uri": "http://localhost:8000",
	"grant_type": "authorization_code",
}
url = "https://www.googleapis.com/oauth2/v4/token"
data = urllib.parse.urlencode(param, True)

response = requests.post(url, headers = headers, data = data)

if response.status_code != 200:
	print("BAD STATUS: ", response, response.content)
	sys.exit()
	
response = response.json()

permissions_config = configparser.ConfigParser()
permissions_config["TOKENS"] = {
	"ACCESS_TOKEN": response["access_token"],
	"REFRESH_TOKEN": response["refresh_token"],
}
with open("tokens.ini", "w") as f:
	permissions_config.write(f)
	
print("Permissions OK!")
