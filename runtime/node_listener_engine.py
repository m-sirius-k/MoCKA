import socket
import json

PORT = 8890

def listen():

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(("", PORT))

    print("MOCKA_NODE_LISTENER_START")

    while True:

        data, addr = s.recvfrom(4096)

        try:
            msg = json.loads(data.decode())
        except:
            continue

        print("NODE_DISCOVERED")
        print("ADDRESS:", addr[0])
        print("DATA:", msg)

if __name__ == "__main__":
    listen()
