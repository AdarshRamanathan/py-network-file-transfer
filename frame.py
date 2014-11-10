import socket
import json
import struct
import zlib

def sendframe(sock, obj, compresslevel=9):
    frame = zlib.compress(json.dumps(obj), compresslevel)
    sock.send(struct.pack('I', len(frame)))
    sock.send(frame)
    return len(frame)

def recvframe(sock):
    rcv = ''
    while len(rcv) < 4:
        rcv += sock.recv(4 - len(rcv))
    size = struct.unpack('I', rcv)[0]

    rcv = ''
    while len(rcv) < size:
        rcv += sock.recv(size - len(rcv))
    return json.loads(zlib.decompress(rcv))
