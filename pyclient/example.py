#!/usr/bin/python


from simplenode import Node
import subprocess
import time
import os
import signal
import traceback

process_list = []

def run_additional_node(NID):
    global process_list
    p = subprocess.Popen(["./simplenode.py", str(NID)], preexec_fn=os.setsid)
    process_list.append(p)

def stop_all_nodes():
    global process_list
    for p in process_list:
        os.killpg(p.pid, signal.SIGTERM)


def run_local_node(NID):
    """
    This is where our local test/experiment code goes.
    We have a node which interacts with the additionally created peer nodes.
    """
    n = Node(NID)
    n.set("k1", "value1")
    print n.get("k1")
    n.delete("k1")
    print n.get("k1")
    # dummy wait
    time.sleep(10)
    n.close()


def main():
    print "Running example.py ..."
    # first start 5 additional nodes to have a network
    for i in range(0, 5):
        run_additional_node(i)

    # run local node to exectue some tests
    try:
        run_local_node(5)
    except:
        traceback.print_exc()
    finally:
        # clean up environment
        stop_all_nodes()

    




if __name__ == '__main__':
    main()
