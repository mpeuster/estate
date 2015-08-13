#!/usr/bin/env python

import zmq
import IPython
import sys

DOC = """
This is a interactive client that interacts with a running
estate node.

Command line arguments:
    interactivenode.py [ip_addr] [port]

Interactive API:
    C.set(k, v)
    C.get(k)
    C.delete(k)
    C.get_global(k, "LAST|AVG|SUM")
"""

class CppEsNodeClient(object):

    def __init__(self):
        self.address = None
        self.port = 0
        self.set_connection_properties()
        self.context = zmq.Context()

    def set_connection_properties(self, address="127.0.0.1", port=8800):
        self.address = address
        self.port = port

    def do_request(self, request_parts):
        socket = self.context.socket(zmq.REQ)
        socket.connect("tcp://%s:%d" % (self.address, self.port))
        # send request
        socket.send_multipart(request_parts)
        # get reply
        reply = socket.recv_multipart()
        socket.close()
        return reply


    def set(self, k, v):
        r = self.do_request(["SET", str(k), str(v)])
        if "OK" in r:
            return True
        print r
        return False

    def get(self, k):
        r = self.do_request(["GET", str(k)])
        if "OK" in r and len(r) > 1:
            return r[1]
        print r
        return "ERROR"

    def delete(self, k):
        r = self.do_request(["DEL", str(k)])
        if "OK" in r:
            return True
        print r
        return False

    def get_global(self, k, red="LATEST"):
        """
        Attention, we can not specify our own reduce functions,
        when useing the cppesnode tool.

        You have to select one of the reduce functions implemented
        in cppesnode:
            - LATEST
            - SUM
            - AVG
        """
        r = self.do_request(["GET_GLOBAL", str(k), str(red)])
        if "OK" in r and len(r) > 1:
            return r[1]
        print r
        return "ERROR"



def main():
    ip = "127.0.0.1"
    port = 8800
    if len(sys.argv) > 1:
        ip = sys.argv[1]
    if len(sys.argv) > 2:
        port = int(sys.argv[2])

    C = CppEsNodeClient()
    C.set_connection_properties(ip, port)
    # start interactive shell
    print DOC
    IPython.embed()


if __name__ == '__main__':
    main()
