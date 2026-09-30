"""Local skeleton only: business APIs fail closed until authentication exists."""
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from backend.db import initialize, connect, ROOT

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/health':
            with connect() as conn:
                conn.execute('SELECT 1').fetchone()
            self.reply(200, {'status': 'ok', 'mode': 'local-skeleton'})
        elif self.path == '/':
            body = (ROOT / 'frontend' / 'index.html').read_bytes()
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(body)
        else:
            self.reply(404, {'error': 'not_implemented'})
    def do_POST(self):
        self.reply(501, {'error': 'business_api_not_implemented'})
    def reply(self, status, data):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(body)

if __name__ == '__main__':
    initialize()
    print('Local skeleton: http://127.0.0.1:8000', flush=True)
    HTTPServer(('127.0.0.1', 8000), Handler).serve_forever()
