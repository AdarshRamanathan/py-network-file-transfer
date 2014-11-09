import socket
import json
import struct

def sendframe(sock, obj):
    frame = json.dumps(obj)
    sock.send(struct.pack('I', len(frame)))
    sock.send(frame)

def recvframe(sock):
    size = struct.unpack('I', sock.recv(4))[0]
    return json.loads(sock.recv(size).strip())
