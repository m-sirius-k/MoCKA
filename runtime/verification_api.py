from http.server import BaseHTTPRequestHandler, HTTPServer
import json, subprocess

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/verify":
            r1 = subprocess.call("python verify_token.py",shell=True)
            r2 = subprocess.call("python verify_ledger.py",shell=True)

            res = {
                "token": r1 == 0,
                "ledger": r2 == 0
            }

            self.send_response(200)
            self.send_header("Content-Type","application/json")
            self.end_headers()
            self.wfile.write(json.dumps(res).encode())

def run():
    server = HTTPServer(("0.0.0.0",8000),Handler)
    print("API START 8000")
    server.serve_forever()

if __name__ == "__main__":
    run()
