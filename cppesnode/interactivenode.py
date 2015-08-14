#!/usr/bin/env python

import IPython
import sys
from estate_zmqclient import estate

DOC = """
This is a interactive client that interacts with a running
estate node.

Command line arguments:
    interactivenode.py [ip_addr] [port]

Interactive API:
    ES.set(k, v)
    ES.get(k)
    ES.delete(k)
    ES.get_global(k, "LAST|AVG|SUM")
"""

def main():
    ip = "127.0.0.1"
    port = 8800
    if len(sys.argv) > 1:
        ip = sys.argv[1]
    if len(sys.argv) > 2:
        port = int(sys.argv[2])

    ES = estate(0)
    ES.set_connection_properties(ip, port)
    # start interactive shell
    print DOC
    IPython.embed()


if __name__ == '__main__':
    main()
