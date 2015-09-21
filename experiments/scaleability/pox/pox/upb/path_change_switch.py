"""
SDN controller for eState experiments.

Scenario:
 * t = 0: flows of c1, c2 pass through mb1
 * t = 60: flow of c2 is moved to mb2
"""


from pox.core import core
import pox.openflow.libopenflow_01 as of
import pox.lib.packet as pkt
import time
from thread import start_new_thread

log = core.getLogger()


FLOW_MOVE_DELAY = 20


def countdown_thread(sc):
    """
    Add everey FLOW_MOVE_DELAY one more MB to the system.
    """
    ACTIVE_MB = 1
    while ACTIVE_MB < len(sc.mb_ports):
        for i in range(FLOW_MOVE_DELAY, 0, -10):
            log.debug(
                "Wakup %d. Re-balance in %d s! MB active: %d" % (sc.switch, i, ACTIVE_MB))
            time.sleep(10)
        ACTIVE_MB += 1
        sc.clear_all_rules()
        sc.install_default_rules()
        sc.install_load_balancing_rules(
            32, n_middleboxes=ACTIVE_MB)
        log.info("Load re-balanced on %d active middleboxes.", ACTIVE_MB)




class SwitchController(object):
    """
    Controller for one switch.
    """
    def __init__(self, connection):
        # store connection to swtich (we have one SwtichController object per switch)
        self.connection = connection

        # This binds our PacketIn event listener
        connection.addListeners(self)

        # witch switch of our topology are we controlling?
        self.switch = int(connection.dpid)
        log.info("Controlling s%d" % self.switch)
        log.info("Port information {}".format(connection.ports))

        # terrible dirty quick hack, but we can not rely
        # on OF portnumber they are not always the same
        pstr = str(connection.ports)
        pstr = pstr.replace("<Ports:", "").replace(">", "")
        parts = pstr.split(",")
        parts = [p.strip() for p in parts]
        mapping = {}
        for p in parts:
            k, v = p.split(":")
            if "-" in k:  # only use "real ports"
                mapping[k] = int(v)

        log.info("Parsed port mappings: %s" % str(mapping))
        self.mapping = mapping

        # extract connections to src/target servers from mapping
        if self.switch == 2:  # source client
            self.st_port = self.mapping["s2-eth1"]
            del self.mapping["s2-eth1"]
        else:  # target server
            self.st_port = self.mapping["s3-eth1"]
            del mapping["s3-eth1"]
        # now mapping our mapping contains only valid middlebox connections

        # get ordered list of middlebox ports available for load balancing
        # TODO alphabetical sorting on things like eth11 vs. eth2 is not perfect!
        self.mb_ports = [v for k, v in sorted(self.mapping.items())]

        # install rules in swtiches
        # install a default rule, always present, all traffic through 1st MB
        self.install_default_rules()

        # start countdown thread for flow change
        start_new_thread(countdown_thread, (self,))

    def _handle_PacketIn(self, event):
        """
        Handles packet in messages from the switch.
        """
        return
        # get and validate packet
        packet = event.parsed  # This is the parsed packet data.
        if not packet.parsed:
            log.warning("Ignoring incomplete packet")
            return
        packet_in = event.ofp  # The actual data packet arrived at the switch
        # process packet
        # show incoming packets
        #log.debug("PACKET_IN: " + str(packet))
        # forward them to all ports (act like a HUB)
        #self.resend_packet(packet_in, of.OFPP_ALL)

    def resend_packet(self, packet_in, out_port):
        """
        Instructs the switch to resend a packet that it had sent to us.
        "packet_in" is the ofp_packet_in object the switch had sent to the
        controller due to a table-miss.
        """
        msg = of.ofp_packet_out()
        msg.data = packet_in

        # Add an action to send to the specified port
        action = of.ofp_action_output(port=out_port)
        msg.actions.append(action)

        # Send message to switch
        self.connection.send(msg)

    def install_default_rules(self):
        """
        Installs default roules to route all traffic
        through the first middlebox in the system.
        These rules are "overloaded" by the load balancing rules
        due to its low priorization.
        """
        # port mappings
        m = self.mapping
        # set default static routes on both switches
        if self.switch == 2:
            self.set_static_rule(self.st_port, m["s2-eth2"], 0)
            self.set_static_rule(m["s2-eth2"], self.st_port, 0)
        elif self.switch == 3:
            self.set_static_rule(m["s3-eth2"], self.st_port, 0)
            self.set_static_rule(self.st_port, m["s3-eth2"], 0)

    def install_load_balancing_rules(
            self,
            n_flows,
            n_middleboxes=9999,
            BASE_PORT=1200):
        """
        Assumes n_flows TCP flows between source and target.
        Each flow on its own TCP port starting with BASE_PORT.
        Distributes this load over the n_middleboxes first middlebox
        replicas available in the port mapping.
        """
        # port mappings
        m = self.mapping
        # calc modulo value
        mod = min(len(self.mb_ports), n_middleboxes)

        # set load balancing rules
        if self.switch == 2:
            for i in range(0, n_flows):
                # s -> t
                self.set_static_rule(
                    self.st_port, self.mb_ports[i % mod], 10,
                    dl_type=pkt.ethernet.IP_TYPE,
                    nw_proto=pkt.ipv4.TCP_PROTOCOL,
                    tp_dst=BASE_PORT + i)
                # t <- s
                self.set_static_rule(
                    self.mb_ports[i % mod], self.st_port, 10,
                    dl_type=pkt.ethernet.IP_TYPE,
                    nw_proto=pkt.ipv4.TCP_PROTOCOL,
                    tp_src=BASE_PORT + i)
        elif self.switch == 3:
            for i in range(0, n_flows):
                # s -> t
                self.set_static_rule(
                    self.mb_ports[i % mod], self.st_port, 10,
                    dl_type=pkt.ethernet.IP_TYPE,
                    nw_proto=pkt.ipv4.TCP_PROTOCOL,
                    tp_dst=BASE_PORT + i)
                # t -> s
                self.set_static_rule(
                    self.st_port, self.mb_ports[i % mod], 10,
                    dl_type=pkt.ethernet.IP_TYPE,
                    nw_proto=pkt.ipv4.TCP_PROTOCOL,
                    tp_src=BASE_PORT + i)

    def clear_all_rules(self):
        """
        Removes all flows from a switch.
        """
        msg = of.ofp_flow_mod(command=of.OFPFC_DELETE)
        self.connection.send(msg)

    def set_static_rule(self, in_port, out_port, prio, **match_args):
        msg = of.ofp_flow_mod()
        msg.priority = prio
        of_match = of.ofp_match(**match_args)
        # matching
        if in_port is not None:
            of_match.in_port = (in_port)
        msg.match = of_match
        # output action
        if out_port is not None:
            of_action = of.ofp_action_output(port=(out_port))
            msg.actions.append(of_action)
        # install rule
        self.connection.send(msg)
        #log.info("SET STATIC PORT RULE: %s" % str(msg))


def launch():
    """
    Starts the component
    """
    def start_switch(event):
        SwitchController(event.connection)
    core.openflow.addListenerByName("ConnectionUp", start_switch)
