import socket
import json
import os
import time

PORT = 9200
REG = "runtime/node_registry.json"

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("", PORT))

def load():

    if not os.path.exists(REG):
        return {}

    with open(REG,"r",encoding="utf-8-sig") as f:
        return json.load(f)

def save(data):

    with open(REG,"w",encoding="utf-8") as f:
        json.dump(data,f,indent=2)

print("NODE REGISTRY START")

while True:

    data, addr = sock.recvfrom(1024)

    if data == b"MOCKA_NODE":

        ip = addr[0]

        reg = load()

        if ip not in reg:

            reg[ip] = {
                "first_seen": int(time.time()),
                "last_seen": int(time.time())
            }

            print("NEW NODE",ip)

        else:

            reg[ip]["last_seen"] = int(time.time())

        save(reg)

