#!/usr/bin/python

"""
 simple executable to create a node process
 running until it receives SIGTERM
"""

import sys
import time
import signal
from pyclient.estate import estate


local_node = None


class Node(object):

    def __init__(self, instance_id):
        self.instance_id = instance_id
        self.es = estate(instance_id)

    def init_libestate(self, ip, port, peerlist):
        self.es.init_libestate(ip, port, peerlist)

    def fill_with_dummy_data(self, n=2):
        for i in range(0, n):
            self.es.set("key_%d" % (i), "value_%d" % (i))
        self.es.set("X", "0")

    def start_endless_processing(self):
        """
        This emulates endless processing of a node e.g. a firewall or IDS.
        """
        try:
            while True:
                time.sleep(2)
                print "Node:%d wakeup" % (self.instance_id)
                r = self.es.get("X")
                print "get X: %s"
                rint = int(r)
                rint += 1
                self.es.set("X", str(rint))
                print "set X: %d" % rint

                time.sleep(1)
                if self.instance_id == 0:
                    rg = self.es.get_global("X")
                    print "get_global X: %s" % rg
                else:
                    time.sleep(5)
        except:
            print "Stopping..."
        finally:
            self.es.close()


def sigterm_handler(_signo, _stack_frame):
    global local_node
    if local_node:
        local_node.es.close()
    sys.exit(0)


def main():
    global local_node
    signal.signal(signal.SIGTERM, sigterm_handler)
    if len(sys.argv) > 1:
        instance_id = int(sys.argv[1])
    else:
        print "Argument missing: instance_id:int"
        sys.exit(1)

    # create node
    local_node = Node(instance_id)
    local_node.init_libestate(
        "127.0.0.1", 9000 + instance_id,
        ["127.0.0.1", "9000", "127.0.0.1", "9001"])
    local_node.fill_with_dummy_data()
    local_node.start_endless_processing()



if __name__ == '__main__':
    main()
