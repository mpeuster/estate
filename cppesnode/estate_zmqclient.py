"""
 libestate prototype using a zmq connection to a cppesnode instance,
 which then uses libestate as backend

 this seems to work better than the Python-to-C interface
"""

import zmq
import subprocess
import time


class estate(object):

    def __init__(self, instance_id):
        self.instance_id = int(instance_id)
        self.address = None
        self.port = 0
        self.node_proc = None
        self.set_connection_properties()
        self.context = zmq.Context()

        print "ES-ZMQ: Initialized estate for instance: %s" % self.instance_id

    def start_cppesnode_process(
            self, local_api_port=8800, peerlist=["127.0.0.1", "9000"]):
        self.node_proc = subprocess.Popen(
            ["cppesnode",
             str(local_api_port)] + peerlist)

    def stop_cppesnode_process(self):
        if self.node_proc is not None:
            self.node_proc.terminate()

    def set_connection_properties(self, address="127.0.0.1", port=8800):
        self.address = address
        self.port = port

    def do_request(self, request_parts):
        socket = self.context.socket(zmq.REQ)
        # socket.connect("tcp://%s:%d" % (self.address, self.port))
        socket.connect("ipc://estatezmq:%d" % (self.port))
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
        # if someone thorws in a function pointer, try to translate it
        if "function" in str(red):
            if "latest" in str(red):
                red = "LATEST"
            if "sum" in str(red):
                red = "SUM"
            if "avg" in str(red):
                red = "AVG"

        red = "LATEST" if red is None else str(red)
        r = self.do_request(["GET_GLOBAL", str(k), str(red)])
        if "OK" in r and len(r) > 1:
            return r[1]
        print r
        return "ES_NONE"


def main():
    # test code
    e = estate(0)
    print "start:"
    e.start_cppesnode_process()
    for _ in range(0, 5):
        print "wait ..."
        time.sleep(1)
    print "stop."
    e.stop_cppesnode_process()


if __name__ == '__main__':
    main()
