import os
import json
from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = 9201

STATE_FILE = "runtime/state.json"
HEALTH_FILE = "runtime/node_health.json"

class StateHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        if self.path == "/state":

            data = {}

            if os.path.exists(STATE_FILE):
                with open(STATE_FILE,"r",encoding="utf-8-sig") as f:
                    data["state"] = json.load(f)

            if os.path.exists(HEALTH_FILE):
                with open(HEALTH_FILE,"r",encoding="utf-8-sig") as f:
                    data["health"] = json.load(f)

            body = json.dumps(data).encode()

            self.send_response(200)
            self.send_header("Content-Type","application/json")
            self.end_headers()

            self.wfile.write(body)

        else:

            self.send_response(404)
            self.end_headers()

print("NODE STATE SERVER START",PORT)

server = HTTPServer(("0.0.0.0",PORT),StateHandler)
server.serve_forever()

