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
    wait = 10
    print "Running source.py ... connect to %s:%s" % (host, port)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sys.stdout.flush()
    s.connect((host, port))
    print "-- rndclient.py connected to %s:%d" % (host, port)

    while True:
        s.send(random_bytes(size))
        print "-- Send %d bytes to %s:%d" % (size, host, port)
        sys.stdout.flush()
        data = s.recv(size)
        if data:
            print "-- Received %d bytes." % len(data)
        sys.stdout.flush()
            # print data
        time.sleep(wait)
    s.close()


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print "Usage: source.py SRV_IP PORT"
        exit(0)
    time.sleep(2)  # wait a bit so that the target server can get up
    run_client(sys.argv[1], int(sys.argv[2]))
