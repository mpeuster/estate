#!/usr/bin/python

import ctypes
import sys
import time
import signal

local_node = None

class Node(object):

    def __init__(self, NID):
        self.lib = ctypes.cdll.LoadLibrary('../libestatepp/Debug/libestatepp.so')
        self.NID = NID
        print "Node %d: created" % NID
        self.init()
        

    def init(self):
        self.lib.es_init(self.NID)

    def close(self):
        self.lib.es_close()
        print "Node %d: destroyed" % self.NID

    def set(self, k, v):
        self.lib.es_set(k, v)

    def get(self, k):
        rptr = self.lib.es_get(k)
        return ctypes.c_char_p(rptr).value

    def delete(self, k):
        self.lib.es_del(k)

    def fill_with_dummy_data(self, n=100):
        for i in range(0, n):
            self.set("key_n%d_%d" % (self.NID, i), "value_n%d_%d" % (self.NID, i))

    def start_endless_processing(self):
        """
        This emulates endless processing of a node e.g. a firewall or IDS.
        """
        try:
            while(True):
                time.sleep(2)
                print "Node %d: wakeup" % self.NID
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
    # create node
    local_node = Node(int(sys.argv[1]))
    local_node.fill_with_dummy_data()
    local_node.start_endless_processing()



if __name__ == '__main__':
    main()
