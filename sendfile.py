#!/usr/bin/env python2

import sys
import getopt

def usage():
    print 'usage: %s [options]... destination_address filename...' % sys.argv[0]

def help():
    usage()
    print
    print 'Mandatory arguments to long options are mandatory for short options too.'
    print '  -p --port=<port>\tsend data to <port> on the remote machine'
    print '  -s --silent\t\tsuppress the progress bar(s)'
    print '  -v --verbose\t\tsay what is being done'
    print '     --help\t\tprint this help text and exit'

def pathleaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)
    
try:
    opts, args = getopt.getopt(sys.argv[1:], 'p:sv', ['port=', 'silent', 'verbose', 'help'])
except getopt.GetoptError as err:
    print err
    usage()
    print "Try '%s --help' for more information." % sys.argv[0]
    sys.exit(2)

port = 45629
verbose = False
silent = False

for o, a in opts:
    if o in ('-p', '--port'):
        try:
            port = int(a)
        except ValueError:
            raise Exception("bad port '%s'" % a)

    elif o == '--help':
        help()
        sys.exit(0)
            
    elif o in ('-s', '--silent'):
        silent = True

    elif o in ('-v', '--verbose'):
        verbose = True

    else:
        raise Exception("unhandled option '%s'" % o)

import socket
import frame
import zlib
import os
import base64
import ntpath

if not silent:
    import progressbar


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

if verbose:
    print 'attempting to connect...'
sock.connect((args[0], port))

if verbose:
    print 'negotiating transfer...'
frame.sendframe(sock, {'type':'handshake', 'filecount':len(args[1:])})

data = frame.recvframe(sock)

if data['type'] == 'handshake':
    if data['response'] == 'ok':
        pass
    elif data['response'] == 'no':
        raise Exception('connection declined by remote machine.')
    else:
        raise Exception('protocol violation.')
else:
    raise Exception('protocol violation.')

for i in range(1, len(args)):
    try:
        filehandle = open(args[i], 'rb')
    except Exception:
        frame.sendframe(sock, {'type':'metadata', 'subtype':'end', 'index':i, 'name':pathleaf(args[i]), 'size':-1})
        print "failed to open file '%s'" % args[i]
        continue

    size = os.stat(args[i]).st_size
    bytes_sent = 0
    frame.sendframe(sock, {'type':'metadata', 'subtype':'init', 'index':i, 'name':pathleaf(args[i]), 'size':size})
    print
    
    checksum = 0
    buf = filehandle.read(4096)

    if not silent and verbose:
        print "sending file '%s'..." % args[i]
    
    while buf:
        checksum ^= zlib.crc32(buf)
        bytes_sent += len(buf)
        buf = base64.b64encode(buf)
        frame.sendframe(sock, {'type':'data', 'index':i, 'buffer':buf})
        if not silent:
            progressbar.printbar(args[i], bytes_sent, size)
        buf = filehandle.read(4096)

    filehandle.close()
    frame.sendframe(sock, {'type':'metadata', 'subtype':'end', 'file':i, 'checksum':checksum})
