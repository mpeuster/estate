#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
from mininet.cli import CLI
from mininet.node import RemoteController
import time

"""
TODO: -
"""

"""
Traffic network: (10.0.0.0/8)

 client1 \_     /  mb1 \_
          _  s1         _-- s2 -- server1
 client2 /      \. mb2 /


Management network (192.0.0.0/8):

mb1 --
       s3 -- redis1
mb2 --
"""


def setup_bridge(node, br="br0", if0="eth0", if1="eth1"):
    """
    Creates a bridge interface and connects the two specified
    network interfaces to it.
    """
    print "Setting up bridge on node: %s" % node.name
    # shutdown both interfaces
    node.cmdPrint("ifconfig %s-%s 0.0.0.0 down" % (node.name, if0))
    node.cmdPrint("ifconfig %s-%s 0.0.0.0 down" % (node.name, if1))
    # create bridge
    node.cmdPrint("brctl addbr %s" % (br))
    # add interfaces to bridge
    node.cmdPrint("brctl addif %s %s-%s" % (br, node.name, if0))
    node.cmdPrint("brctl addif %s %s-%s" % (br, node.name, if1))
    # manage STP
    node.cmdPrint("brctl stp %s off" % br)
    # bring up all interfaces and bridge
    node.cmdPrint("ifconfig %s-%s up" % (node.name, if0))
    node.cmdPrint("ifconfig %s-%s up" % (node.name, if1))
    node.cmdPrint("ifconfig %s up" % (br))


def start_tcp_echo_traffic(server, client_list, base_port=1201):
    """
    Runs an TCP echo server and a client which sends
    random data on each host specified in the client_list.
    Starts one server process for each client.
    Server outputs are written to central log files.
    """
    for client in client_list:
        server.cmd("./echoserver.py %d > /tmp/echo_server_%s.log 2>&1 &" % (base_port, client.name))
        time.sleep(1)
        client.cmd("./rndclient.py %s %d > /tmp/rnd_client_%s.log 2>&1 &" % (server.IP(), base_port, client.name))
        base_port += 1  # increase port number for next server


def setupMiddleboxExperiment():
    net = Mininet()

    # create SDN controller (local)
    # c1 = net.addController("c1")
    # create SDN controller (remote)
    c1 = net.addController("c1", controller=RemoteController, ip='127.0.0.1', port=6633)

    # add two switches
    s1 = net.addSwitch("s1")
    s2 = net.addSwitch("s2")
    s3 = net.addSwitch("s3")

    # create test client and server hosts
    client1 = net.addHost("client1")
    net.addLink(client1, s1)
    client2 = net.addHost("client2")
    net.addLink(client2, s1)
    server1 = net.addHost("server1")
    net.addLink(s2, server1)

    # create REDIS host
    redis1 = net.addHost("redis1")
    net.addLink(redis1, s3)

    # create middleboxes (1)
    mb1 = net.addHost("mb1")
    # - data plane
    net.addLink(s1, mb1)
    net.addLink(mb1, s2)
    # - control plane
    net.addLink(mb1, s3)
    mb1.setIP("192.0.0.2", intf="mb1-eth2")
    # create middleboxes (2)
    mb2 = net.addHost("mb2")
    # - data plane
    net.addLink(s1, mb2)
    net.addLink(mb2, s2)
    # - control plane
    net.addLink(mb2, s3)
    mb2.setIP("192.0.0.3", intf="mb2-eth2")

    # run the network
    net.staticArp()
    net.start()

    # do mb bridge configuration
    setup_bridge(mb1)
    setup_bridge(mb2)

    # FIXME: ugly but setIP does not work on default interfaces
    redis1.cmd("ifconfig redis1-eth0 192.0.0.1 netmask 255.0.0.0")

    # debugging
    print "Dumping host connections"
    dumpNodeConnections(net.hosts)
    print "Testing network connectivity"
    net.ping(hosts=[client1, server1])
    net.ping(hosts=[client2, server1])
    # net.ping(hosts=[redis1, mb1, mb2])

    # start redis backend
    redis1.cmdPrint("../../redis-3.0.1/src/redis-server > /tmp/redis_server.log 2>&1 &")
    # start traffic generation
    start_tcp_echo_traffic(server1, [client1, client2])
    # server1.cmdPrint("tail -f /tmp/echo_server1201.log /tmp/echo_server1202.log")
    # start dummy IDS monitors
    mb1.cmdPrint("./monitor.py 1 > /tmp/monitor1.log 2>&1 &")
    mb2.cmdPrint("./monitor.py 2 > /tmp/monitor2.log 2>&1 &")

    # enter user interface
    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    setupMiddleboxExperiment()

"""
    #mb1.setIP("11.0.0.2", intf="mb1-eth1")
"""
