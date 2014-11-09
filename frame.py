import socket
import json
import struct

def sendframe(sock, obj):
    frame = json.dumps(obj)
    sock.send(struct.pack('I', len(frame)))
    sock.send(frame)

def recvframe(sock):
    rcv = ''
    while len(rcv) < 4:
        rcv += sock.recv(4 - len(rcv))
    size = struct.unpack('I', rcv)[0]

    rcv = ''
    while len(rcv) < size:
        rcv += sock.recv(size - len(rcv))
    
    return json.loads(rcv)
