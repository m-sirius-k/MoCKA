import os
import json
from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = 9100
SNAP_DIR = "runtime/snapshots"

class NodeHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        if self.path == "/snapshots":

            files = os.listdir(SNAP_DIR)

            data = json.dumps(files).encode()

            self.send_response(200)
            self.send_header("Content-Type","application/json")
            self.end_headers()
            self.wfile.write(data)

        elif self.path.startswith("/snapshot/"):

            name = self.path.split("/")[-1]
            path = os.path.join(SNAP_DIR,name)

            if os.path.exists(path):

                with open(path,"rb") as f:
                    data = f.read()

                self.send_response(200)
                self.end_headers()
                self.wfile.write(data)

            else:

                self.send_response(404)
                self.end_headers()

        else:

            self.send_response(404)
            self.end_headers()

print("NODE SYNC SERVER START",PORT)

server = HTTPServer(("0.0.0.0",PORT),NodeHandler)
server.serve_forever()

