#!/usr/bin/python


from simplenode import Node
import subprocess
import time
import os
import signal
import traceback

process_list = []

def run_additional_node(port):
    global process_list
    p = subprocess.Popen(["./simplenode.py", "127.0.0.1", str(port)], preexec_fn=os.setsid)
    process_list.append(p)

def stop_all_nodes():
    global process_list
    for p in process_list:
        os.killpg(p.pid, signal.SIGTERM)


def run_local_node(port):
    """
    This is where our local test/experiment code goes.
    We have a node which interacts with the additionally created peer nodes.
    """
    n = Node("127.0.0.1", port)
    n.set("k1", "value_of_node_%s:%d" % (n.ip, n.port))

    time.sleep(1) # wait a bit to stabilize all peers

    # do some tires with our get global method
    for i in range(0, 2):
        print n.get_global("k1")
        time.sleep(2)

    # dummy wait
    time.sleep(1)
    n.close()


def main():
    print "Running example.py ..."
    # first start 5 additional nodes to have a network
    for i in range(9000, 9005):
        run_additional_node(i)

    # run local node to exectue some tests
    try:
        run_local_node(9005)
    except:
        traceback.print_exc()
    finally:
        # clean up environment
        stop_all_nodes()

    




if __name__ == '__main__':
    main()
