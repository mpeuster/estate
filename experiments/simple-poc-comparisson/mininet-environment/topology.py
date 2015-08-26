#!/usr/bin/python

from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
from mininet.cli import CLI
from mininet.node import OVSSwitch
from mininet.node import Controller, RemoteController
#import time


def config_bridge(node, br="br0", if0="eth1", if1="eth2"):
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


class MultiSwitch(OVSSwitch):
    """
    Custom switch that connects to specified controller.
    """

    #def __init__(self, **kwargs):
    #    super(MultiSwitch, self).__init__(**kwargs)
    #    self.custom_ctrl = None

    def set_custom_controller(self, c):
        self.custom_ctrl = c

    def start(self, controllers):
        if self.custom_ctrl is not None:
            return OVSSwitch.start(self, [self.custom_ctrl])
        else:
            return OVSSwitch.start(self, controllers)


class GenericMiddleBoxTopology(object):
    """
    This class creates a basic experminet topology containing
    traffic sources and targets as well as intermediate middlebox
    machines. The number of hosts per type can be defined in the
    constructor.

    Management network: 10.0.0.0/8
    User data network:  20.0.0.0/8

     client1  --         -- mb1 --          -- target1
                |       |    |    |        |
                -- s1 --    s3     -- s2 --
                |       |    |    |        |
     client2  --         -- mb2 --          -- target2

    """

    def __init__(self, source_instances=2, target_instances=1, mbox_instances=2):
        self.source_instances = source_instances
        self.target_instances = target_instances
        self.mbox_instances = mbox_instances

        # bring up Mininet
        self.net = Mininet()

        # topology elements
        self.controllers = []
        self.switches = []
        self.middlebox_hosts = []
        self.source_hosts = []
        self.target_hosts = []
        # single pointers to nw components
        self.control_switch = None
        self.source_switch = None
        self.target_switch = None
        self.default_controller = None
        self.data_controller = None

        # do network setup
        self.setup_controllers()
        self.setup_switches()
        self.setup_hosts()


    def start_network(self):
        # run the network
        self.net.staticArp()
        #self.net.start()
        # build network
        self.net.build()
        # start controllers
        self.data_controller.start()
        self.default_controller.start()
        # start switches and assign controller
        self.control_switch.start([self.default_controller])
        self.source_switch.start([self.data_controller])
        self.target_switch.start([self.data_controller])
        # additional start tasks
        self.config_middlebox_hosts()
        self.run_middlebox_hosts()

    def test_network(self):
        # debugging
        print "### Dumping host connections"
        dumpNodeConnections(self.net.hosts)
        print "### Testing middlebox replica connectivity"
        if self.net.ping(hosts=self.middlebox_hosts) < 0.1:
            print "### OK"

    def enter_cli(self):
        # enter user interface
        CLI(self.net)
        self.net.stop()

    def setup_controllers(self):
        # default controller for managemen switch
        c1 = self.net.addController("c1", port=6634)
        self.default_controller = c1
        self.controllers.append(c1)
        # custom controller for user traffic management
        c2 = self.net.addController(
            "c2", controller=RemoteController, ip='127.0.0.1', port=6633)
        self.data_controller = c2
        self.controllers.append(c2)

    def setup_switches(self):
        # management switch
        s = self.net.addSwitch("s1")
        self.switches.append(s)
        self.control_switch = s
        # source switch
        s = self.net.addSwitch("s2")
        self.switches.append(s)
        self.source_switch = s
        # target switch
        s = self.net.addSwitch("s3")
        self.switches.append(s)
        self.target_switch = s

    def setup_hosts(self):
        """
        basic host setup
        """
        # middlebox hosts
        for i in range(0, self.mbox_instances):
            mb = self.net.addHost("mb%d" % (i + 1))
            self.middlebox_hosts.append(mb)
            # management plane links
            self.net.addLink(mb, self.control_switch)
            # data plane links
            self.net.addLink(mb, self.source_switch)
            self.net.addLink(mb, self.target_switch)
        # source hosts
        for i in range(0, self.source_instances):
            sh = self.net.addHost(
                "source%d" % (i + 1),
                ip="20.0.0.%d" % (i + 1))
            self.source_hosts.append(sh)
            self.net.addLink(sh, self.source_switch)
        # target hosts
        for i in range(0, self.target_instances):
            th = self.net.addHost(
                "target%d" % (i + 1),
                ip="20.0.1.%d" % (i + 1))
            self.target_hosts.append(th)
            self.net.addLink(th, self.target_switch)


    def config_middlebox_hosts(self):
        """
        additional runtime configurations of MB hosts
        """
        for mb in self.middlebox_hosts:
            config_bridge(mb)

    def run_middlebox_hosts(self):
        """
        run NF functionality inside MB hosts
        """
        pass


class LibestateTopology(GenericMiddleBoxTopology):

    def __init__(self, **kwargs):
        super(LibestateTopology, self).__init__(**kwargs)

    def config_middlebox_hosts(self):
        super(LibestateTopology, self).config_middlebox_hosts()
        for mb in self.middlebox_hosts:
            # set all environment variables for each middlebox host
            print mb.cmd("source environment_vars.sh")

    def run_middlebox_hosts(self):
        """
        Executes the libestate node on each host.
        Assumes that the management network is the first interface of a host.
        """
        super(LibestateTopology, self).run_middlebox_hosts()
        for mb in self.middlebox_hosts:
            # get list of peer instances
            peers = [p for p in self.middlebox_hosts if p is not mb]
            # build argument string
            arg_str = "%s 9000" % mb.IP()
            for p in peers:
                arg_str += " %s 9000" % p.IP()
            print "%s run cppesnode with args: %s " % (mb.name, arg_str)
            # run libestate node with and tell it which peers to use
            mb.cmd("cppesnode 8800 %s > log/cppesnode_%s.log 2>&1 &"
                   % (arg_str, mb.name))


class CassandraTopology(GenericMiddleBoxTopology):

    def __init__(self, **kwargs):
        super(CassandraTopology, self).__init__(**kwargs)

    def config_middlebox_hosts(self):
        super(CassandraTopology, self).config_middlebox_hosts()
        for mb in self.middlebox_hosts:
            # set all environment variables for each middlebox host
            print mb.cmd("source environment_vars.sh")

    def run_middlebox_hosts(self):
        super(CassandraTopology, self).run_middlebox_hosts()
        for mb in self.middlebox_hosts:
            # run cassandra instance
            # BUG: This won't work for multiple instances. Cassandra clustering need work!
            mb.cmd("cassandra > log/cassandra_%s.log 2>&1 &"
                   % (mb.name))


class RedisTopology(GenericMiddleBoxTopology):

    def __init__(self, **kwargs):
        # pointer to additional redis host
        self.redis_host = None
        super(RedisTopology, self).__init__(**kwargs)

    def setup_hosts(self):
        """
        overwrite and extend host setup: we need an additional redis host
        """
        super(RedisTopology, self).setup_hosts()
        # add additional host running central redis instance
        self.redis_host = self.net.addHost("redis")
        self.net.addLink(self.redis_host, self.control_switch)

    def config_middlebox_hosts(self):
        super(RedisTopology, self).config_middlebox_hosts()
        for mb in self.middlebox_hosts + [self.redis_host]:
            # set all environment variables for each middlebox host
            print mb.cmd("source environment_vars.sh")

    def run_middlebox_hosts(self):
        super(RedisTopology, self).run_middlebox_hosts()
        self.redis_host.cmd("redis-server > log/redis.log 2>&1 &")



if __name__ == '__main__':
    setLogLevel('info')
    #mt = GenericMiddleBoxTopology()
    #mt = LibestateTopology()s
    #mt = CassandraTopology()
    mt = RedisTopology()
    mt.start_network()
    mt.test_network()
    mt.enter_cli()
