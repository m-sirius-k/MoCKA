import socket
import time

PORT = 9200

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

msg = b"MOCKA_NODE"

print("NODE DISCOVERY BROADCAST START")

while True:

    sock.sendto(msg, ("255.255.255.255", PORT))

    print("BROADCAST SENT")

    time.sleep(5)

