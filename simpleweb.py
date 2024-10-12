from http.server import BaseHTTPRequestHandler, HTTPServer
import webbrowser
import urllib

class RedirectHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        query = urllib.parse.urlparse(self.path).query
        query_components = dict(qc.split("=") for qc in query.split("&"))
        code = query_components.get('code')
        self.wfile.write(f"<html><head><title>Authorization Response</title></head><body><h1>You may now close this window.</h1><p>Code: {code}</p></body></html>".encode())

if __name__ == "__main__":
    port = 8889
    webbrowser.open(f'https://accounts.spotify.com/authorize?client_id=YOUR_CLIENT_ID&response_type=code&redirect_uri=http://localhost:{port}/callback&scope=playlist-modify-private')
    server = HTTPServer(('localhost', port), RedirectHandler)
    server.serve_forever()

