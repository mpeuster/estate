#!/usr/bin/python

"""
A simple echo client
"""

import socket
import sys
import time
import string
import random


def random_bytes(size):
    return ''.join(random.choice(string.letters + string.digits) for _ in range(size))


def run_client(host, port):
    size = 32
    wait = 1
    print "Running rndclient.py ..."
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    print "-- rndclient.py connected to %s:%d" % (host, port)

    while True:
        s.send(random_bytes(size))
        print "-- Send %d bytes to %s:%d" % (size, host, port)
        data = s.recv(size)
        if data:
            print "-- Received %d bytes." % len(data)
            # print data
        time.sleep(wait)

    rf.close()
    s.close()


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print "Usage: rndclient.py SRV_IP PORT"
        exit(0)
    run_client(sys.argv[1], int(sys.argv[2]))
