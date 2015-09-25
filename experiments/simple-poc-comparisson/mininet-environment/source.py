#!/usr/bin/python

"""
A simple echo client
"""

import socket
import sys
import time
import string
import random
import sys


def random_bytes(size):
    return ''.join(
        random.choice(string.letters + string.digits) for _ in range(size))


def run_client(host, port, arr_lambda=1.0):
    size = 32
    print "Running source.py ... connect to %s:%s" % (host, port)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sys.stdout.flush()
    s.connect((host, port))
    print "-- rndclient.py connected to %s:%d" % (host, port)
    print "lambda=%f" % arr_lambda
    sys.stdout.flush()

    while True:
        s.send(random_bytes(size))
        #print "-- Send %d bytes to %s:%d" % (size, host, port)
        #sys.stdout.flush()
        data = s.recv(size)
        #if data:
        #    print "-- Received %d bytes." % len(data)
        #sys.stdout.flush()
            # print data
        time.sleep(arr_lambda)
    s.close()


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print "Usage: source.py SRV_IP PORT LAMBDA"
        exit(0)
    time.sleep(2)  # wait a bit so that the target server can get up
    run_client(sys.argv[1], int(sys.argv[2]), float(sys.argv[3]))
