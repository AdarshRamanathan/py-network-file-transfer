#!/usr/bin/env python2

import sys
import getopt

def usage():
    print 'usage: %s [options]...' % sys.argv[0]

def help():
    usage()
    print
    print '  -p --port=<port>\tlisten for connections and receive data on <port>'
    print '  -s --silent\t\tsuppress the progress bar(s)'
    print '  -v --verbose\t\tsay what is being done'
    print '     --help\t\tprint this help text and exit'

def inittransfer(obj):
    if obj['type'] != 'metadata':
        raise Exception("cannot handle packets of type '%s'" % data['type'])

    if obj['subtype'] != 'init':
        raise Exception("cannot handle packets of subtype '%s'" % data['subtype'])

    if int(obj['index']) <= index:
        raise Exception('sequencing failure')
    
    if done < size:
        if not silent:
            progressbar.printbar(name, -1, size)
        else:
            print "failed to receive file '%s'" % name,

    print

    try:
        handle = open(obj['name'], 'r')
        handle.close()
        print 'file already exists - choose a new name, or hit return to overwrite (%s)' % obj['name'],
        name = raw_input()
        if len(name) <= 0:
            name = obj['name']
        
    except IOError as err:
        if err.errno != 2:
            raise err
        name = obj['name']

    return name
    
try:
    opts, args = getopt.getopt(sys.argv[1:], 'p:vs', ['port=', 'verbose', 'silent' 'help'])
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
import base64

if not silent:
    import progressbar

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('0.0.0.0', port))

if verbose:
    print 'waiting for connection from remote machine...'

sock.listen(5)

class BreakLoop(Exception):
    pass

filecount = 0

try:
    while True:
        connection, address = sock.accept()

        data = frame.recvframe(connection)

        try:
            if data['type'] != 'handshake':
                continue

            filecount = int(data['filecount'])

            if filecount <= 0:
                raise Exception('nonpositive filecount (%d)' % filecount)
        
        except (KeyError, ValueError):
            continue
        
        print 'receiving %d files from %s proceed? (yes/no)' % (filecount, address[0]),

        while True:
            resp = raw_input()
            if resp == 'yes':
                frame.sendframe(connection, {'type':'handshake', 'response':'ok'})
                raise BreakLoop()
            
            elif resp == 'no':
                frame.sendframe(connection, {'type':'handshake', 'response':'no'})
                connection.close()
                break
            
            else:
                print "type 'yes' or 'no'",
except BreakLoop:
    pass

index = 0
size = 0
done = 0
name = None
handle = None
checksum = 0

if verbose:
    print 'receiving data...'

while True:
    data = frame.recvframe(connection)
    
    if data['type'] == 'metadata':
        
        if data['subtype'] == 'init':
            
            name = inittransfer(data)
            index = data['index']
            size = data['size']
            done = 0
            checksum = 0
            handle = open(name, 'wb')
        
        elif data['subtype'] == 'end':

            try:
                if data['size'] < 0:
                    print "failed to receive file '%s' from remote machine" % data['name']
                    if int(data['index']) >= filecount:
                        break
            except KeyError:
            
                handle.close()

                if checksum != data['checksum']:
                    if not silent:
                        progressbar.printbar(name, -1, size)
                    else:
                        print "checksum for file '%s' failed" % name,
            
            if index >= filecount:
                break
        
        else:
            raise Exception('protocol violation')
    
    elif data['type'] == 'data':

        if data['index'] == index:
            buf = base64.b64decode(data['buffer'])
            checksum ^= zlib.crc32(buf)
            done += len(buf)
            if not silent:
                progressbar.printbar(name, done, size)
            handle.write(buf)
        
        else:
            raise Exception('sequencing failure')
    
    else:
        raise Exception('protocol violation')
