#!/usr/bin/env python

import zmq


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
    C = CppEsNodeClient()
    print C.set("k1", "v1")
    print C.get("k1")
    print C.get_global("k1")
    print C.delete("k1")
    print C.get("k1")
    #TODO start interactive shell


if __name__ == '__main__':
    main()
