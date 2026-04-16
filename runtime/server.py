from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os

INPUT_PATH = "input.json"

def ensure_input():
    if not os.path.exists(INPUT_PATH):
        with open(INPUT_PATH, "w", encoding="utf-8") as f:
            json.dump([], f)

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        data = self.rfile.read(length)

        try:
            payload = json.loads(data.decode("utf-8"))

            ensure_input()

            with open(INPUT_PATH, "r", encoding="utf-8") as f:
                current = json.load(f)

            if isinstance(payload, list):
                current.extend(payload)
            else:
                current.append(payload)

            with open(INPUT_PATH, "w", encoding="utf-8") as f:
                json.dump(current, f, indent=2)

            print("RECEIVED:", payload)

            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")

        except Exception as e:
            print("ERROR:", e)
            self.send_response(500)
            self.end_headers()

def run():
    server = HTTPServer(("0.0.0.0", 5000), Handler)
    print("SERVER START http://0.0.0.0:5000")
    server.serve_forever()

if __name__ == "__main__":
    run()
