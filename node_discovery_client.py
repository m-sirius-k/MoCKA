import socket

PORT = 9200

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("", PORT))

print("LISTENING FOR MOCKA NODES")

while True:

    data, addr = sock.recvfrom(1024)

    if data == b"MOCKA_NODE":

        print("NODE FOUND", addr[0])

