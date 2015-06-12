#!/usr/bin/python

import ctypes
import sys
import time
import signal

local_node = None

class Node(object):

    def __init__(self, ip, port):
        self.lib = ctypes.cdll.LoadLibrary('../libestatepp/Debug/libestatepp.so')
        self.ip = str(ip)
        self.port = int(port)
        print "Node %s:%d created" % (self.ip, self.port)
        self.init()
        

    def init(self):
        self.lib.es_init(self.ip, self.port)

    def close(self):
        self.lib.es_close()
        print "Node %s:%d destroyed" % (self.ip, self.port)

    def set(self, k, v):
        self.lib.es_set(k, v)

    def get(self, k):
        rptr = self.lib.es_get(k)
        return ctypes.c_char_p(rptr).value

    def get_global(self, k):
        rptr = self.lib.es_get_global(k)
        return ctypes.c_char_p(rptr).value

    def delete(self, k):
        self.lib.es_del(k)

    def fill_with_dummy_data(self, n=100):
        for i in range(0, n):
            self.set("key_n%d_%d" % (self.port, i), "value_n%d_%d" % (self.port, i))

    def start_endless_processing(self):
        """
        This emulates endless processing of a node e.g. a firewall or IDS.
        """
        try:
            while(True):
                time.sleep(2)
                print "Node %s:%d wakeup" % (self.ip, self.port)
        except:
            pass
        finally:
            self.close()


def sigterm_handler(_signo, _stack_frame):
    global local_node
    local_node.close()
    sys.exit(0)


def main():
    global local_node
    signal.signal(signal.SIGTERM, sigterm_handler)
    ip = "127.0.0.1"
    port = 9000
    if len(sys.argv) > 2:
        ip = str(sys.argv[1])
        port = int(sys.argv[2])
    # create node
    local_node = Node(ip, port)
    local_node.fill_with_dummy_data()
    local_node.start_endless_processing()



if __name__ == '__main__':
    main()
