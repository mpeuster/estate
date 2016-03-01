#!/usr/bin/python

"""
A simple echo server
"""

import socket
import sys


def run_server(port):
    host = ''
    backlog = 1
    size = 1024
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen(backlog)
    while 1:
        print "*** Waiting for connection on port: %d ***" % port
        sys.stdout.flush()
        client, address = s.accept()
        while 1:
            try:
                data = client.recv(size)
                if len(data) == 0:
                    print "*** Hangup ***"
                    client.close()
                    break
                if data:
                    # print data
                    #print "Received %d bytes from %s" % (len(data), str(address))
                    #sys.stdout.flush()
                    client.send(data)
            except Exception as e:
                print str(e)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "Usage: target.py PORT"
        exit(0)
    run_server(int(sys.argv[1]))
