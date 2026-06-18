import sys
import io
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf_8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
﻿import socket
import json

PORT = 8890

def broadcast_state():

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    state = {
        "node": "mocka-node-1",
        "service": "mocka_runtime"
    }

    data = json.dumps(state).encode()

    s.sendto(data, ("<broadcast>", PORT))

    print("NODE_BROADCAST_SENT")

if __name__ == "__main__":
    broadcast_state()
