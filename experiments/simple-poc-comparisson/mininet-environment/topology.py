#!/usr/bin/python

from mininet.net import Mininet
#from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
from mininet.cli import CLI
#from mininet.node import RemoteController
#import time


class GenericMiddleBoxTopology(object):

    def __init__(self, mbox_instances=3):
        self.mbox_instances = mbox_instances

        # bring up Mininet
        self.net = Mininet()

        # topology elements
        self.controllers = []
        self.switches = []
        self.middlebox_hosts = []

        # do network setup
        self.setup_controllers()
        self.setup_switches()
        self.setup_middlebox_hosts()

        # single pointers to nw components
        self.control_switch = None

    def start_network(self):
        # run the network
        self.net.staticArp()
        self.net.start()
        # additional start tasks
        self.config_middlebox_hosts()
        self.run_middlebox_hosts()

    def test_network(self):
        print "### Testing middlebox replica connectivity"
        if self.net.ping(hosts=self.middlebox_hosts) < 0.1:
            print "### OK"

    def enter_cli(self):
        # enter user interface
        CLI(self.net)
        self.net.stop()

    def setup_controllers(self):
        c1 = self.net.addController("c1")
        self.controllers.append(c1)

    def setup_switches(self):
        s = self.net.addSwitch("s1")
        self.switches.append(s)
        self.control_switch = s

    def setup_middlebox_hosts(self):
        """
        basic host setup of MB hosts
        """
        for i in range(0, self.mbox_instances):
            mb = self.net.addHost("mb%d" % (i + 1))
            self.middlebox_hosts.append(mb)
            self.net.addLink(mb, self.control_switch)


    def config_middlebox_hosts(self):
        """
        additional runtime configurations of MB hosts
        """
        pass

    def run_middlebox_hosts(self):
        """
        run NF functionality inside MB hosts
        """
        pass


class LibestateTopology(GenericMiddleBoxTopology):

    def __init__(self, **kwargs):
        super(LibestateTopology, self).__init__(**kwargs)

    def config_middlebox_hosts(self):
        for mb in self.middlebox_hosts:
            # set all environment variables for each middlebox host
            print mb.cmd("source environment_vars.sh")

    def run_middlebox_hosts(self):
        """
        Executes the libestate node on each host.
        Assumes that the management network is the first interface of a host.
        """
        for mb in self.middlebox_hosts:
            print "Run cppesnode ..."
            # get list of peer instances
            peers = [p for p in self.middlebox_hosts if p is not mb]
            # build argument string
            arg_str = "%s 9000" % mb.IP()
            for p in peers:
                arg_str += " %s 9000" % p.IP()
            print arg_str
            # run libestate node with and tell it which peers to use
            mb.cmd("cppesnode 8800 %s > log/cppesnode_%s.log 2>&1 &" % (arg_str, mb.name))





if __name__ == '__main__':
    setLogLevel('info')
    #mt = GenericMiddleBoxTopology(mbox_instances=3)
    mt = LibestateTopology(mbox_instances=3)
    mt.start_network()
    mt.test_network()
    mt.enter_cli()
