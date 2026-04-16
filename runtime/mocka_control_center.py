import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

FILES = {
    "incidents": "incident_summary.txt",
    "alerts": "incident_alert.json",
    "repair": "repair_execution_result.json",
    "verify": "repair_verification.json",
    "model": "repair_strategy_model.json",
"civilization": "mocka_civilization_registry.json"
}

def load_file(path):

    if not os.path.exists(path):
        return "NO_DATA"

    try:
        with open(path,"r",encoding="utf-8-sig") as f:
            return f.read()
    except:
        return "READ_ERROR"

class Handler(BaseHTTPRequestHandler):

    def do_GET(self):

        html = "<html><body>"
        html += "<h1>MoCKA Civilization Control Center</h1>"

        for name,path in FILES.items():

            html += f"<h2>{name}</h2><pre>"
            html += load_file(path)
            html += "</pre>"

        html += "</body></html>"

        self.send_response(200)
        self.send_header("Content-type","text/html")
        self.end_headers()
        self.wfile.write(html.encode())

def main():

    server = HTTPServer(("localhost",8080),Handler)

    print("MOCKA_CONTROL_CENTER_RUNNING")
    print("http://localhost:8080")

    server.serve_forever()

if __name__ == "__main__":
    main()

