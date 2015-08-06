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

    def fill_with_dummy_data(self, n=1):
        for i in range(0, n):
            self.es.set("key_%d" % (i), "value_%d" % (i))

    def start_endless_processing(self):
        """
        This emulates endless processing of a node e.g. a firewall or IDS.
        """
        try:
            while True:
                time.sleep(2)
                print "Node:%d wakeup" % (self.instance_id)
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
    local_node.fill_with_dummy_data()
    local_node.start_endless_processing()



if __name__ == '__main__':
    main()
