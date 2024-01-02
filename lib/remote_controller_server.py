
import http.server
import threading
import urllib

class MyHttpHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        parsed_url = urllib.parse.urlparse(self.path)
        self.server.context(parsed_url.path)
        self.send_response(200)
        self.end_headers()

class MyHttpServer(http.server.HTTPServer):
    def __init__(self, server_address, RequestHandlerClass, context):
        http.server.HTTPServer.__init__(self, server_address, RequestHandlerClass)
        self.context = context

class RemoteControllerServerThread(threading.Thread):
    def __init__(self, config, cb):
        threading.Thread.__init__(self)
        self.daemon = True
        self.cb = cb

    def run(self):
        print("Remote controller server listening on port", 8000)
        httpd = MyHttpServer(("", 8000), MyHttpHandler, self.cb)
        httpd.serve_forever()
