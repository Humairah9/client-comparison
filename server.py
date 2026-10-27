"""Tiny local test server (standard library only). All data is invented."""
import json, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

TOKEN = "demo-token"
BOOKS = [
    {"id": 1, "title": "The Lantern Keepers", "author": "Ines Marlowe"},
    {"id": 2, "title": "Salt and Signal", "author": "Tobias Quill"},
    {"id": 3, "title": "Harbour of Small Hours", "author": "Ines Marlowe"},
]

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):  # keep the demo output clean
        pass

    def _send(self, status, body=None, headers=None):
        payload = json.dumps(body if body is not None else {}).encode()
        try:
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            for key, value in (headers or {}).items():
                self.send_header(key, value)
            self.end_headers()
            self.wfile.write(payload)
        except (BrokenPipeError, ConnectionResetError):
            pass  # the client gave up (e.g. a timeout), which some demos do on purpose

    def _authorised(self):
        return self.headers.get("Authorization") == f"Bearer {TOKEN}"

    def do_GET(self):
        url = urlparse(self.path)
        query = parse_qs(url.query)
        if url.path == "/old":
            return self._send(302, {}, {"Location": "/new"})
        if url.path == "/new":
            return self._send(200, {"moved": True})
        if url.path == "/api/slow":
            time.sleep(float(query.get("seconds", ["1"])[0]))
            return self._send(200, {"slow": True})
        if not self._authorised():
            return self._send(401, {"error": "bad token"})
        if url.path == "/api/books":
            author = query.get("author", [None])[0]
            found = [b for b in BOOKS if author is None or b["author"] == author]
            return self._send(200, found)
        if url.path.startswith("/api/books/"):
            book = next((b for b in BOOKS if str(b["id"]) == url.path.rsplit("/", 1)[1]), None)
            return self._send(200, book) if book else self._send(404, {"error": "not found"})
        self._send(404, {"error": "no such route"})

    def do_POST(self):
        if not self._authorised():
            return self._send(401, {"error": "bad token"})
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length) or b"{}")
        if self.path == "/api/loans" and {"book_id", "member_id"} <= body.keys():
            return self._send(201, {"loan_id": 101, **body})
        self._send(400, {"error": "bad request"})

def run(port=8765):
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()

if __name__ == "__main__":
    run()
