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


FLOW_MOVE_DELAY = 60


def countdown_thread(sc):
    # first step move client2 to mb2
    for i in range(FLOW_MOVE_DELAY, 0, -10):
        log.debug(
            "Wakeup controller s%d. Flow move in %d seconds!" % (sc.switch, i))
        time.sleep(10)
    sc.flow_move_1()
    # second step move client1 also to mb2
    #for i in range(FLOW_MOVE_DELAY, 0, -10):
    #    log.debug(
    #        "Wakeup controller s%d. Flow move in %d seconds!" % (sc.switch, i))
    #    time.sleep(10)
    #sc.flow_move_2()


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
            mapping[k] = int(v)

        log.info(mapping)
        self.mapping = mapping


        # setup static forwarding rules for experiment
        self.setup_static_rules()

        # start countdown thread for flow change
        start_new_thread(countdown_thread, (self,))

    def _handle_PacketIn(self, event):
        """
        Handles packet in messages from the switch.
        """
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

    def setup_static_rules(self):
        m = self.mapping
        if self.switch == 2:
            log.info("Setup rules for s%d" % self.switch)
            # TODO add constants for port numbers
            # SRC1_S2 = 3
            # MB1_S2 = 1
            # ...
            
            # always use first link as default
            self.set_static_rule(m["s2-eth3"], m["s2-eth1"], 0)
            self.set_static_rule(m["s2-eth4"], m["s2-eth1"], 0)
            self.set_static_rule(m["s2-eth1"], [m["s2-eth3"], m["s2-eth4"]], 0)
            self.set_static_rule(m["s2-eth2"], [m["s2-eth3"], m["s2-eth4"]], 0)
        elif self.switch == 3:
            log.info("Setup rules for s%d" % self.switch)
            # always use first link as default
            self.set_static_rule(m["s3-eth1"], m["s3-eth3"], 0)
            self.set_static_rule(m["s3-eth2"], m["s3-eth3"], 0)
            self.set_static_rule(m["s3-eth3"], m["s3-eth1"], 0)
        #else:
            # set static hub behavior
            #self.set_static_rule(None, of.OFPP_ALL, 0)

    def set_static_rule(self, in_port, out_port, prio, **match_args):
        msg = of.ofp_flow_mod()
        msg.priority = prio
        of_match = of.ofp_match(**match_args)
        if in_port is not None:
            of_match.in_port = (in_port)
        msg.match = of_match
        if isinstance(out_port, list):
            for oport in out_port:
                of_action = of.ofp_action_output(port=(oport))
                msg.actions.append(of_action)
        else:
            of_action = of.ofp_action_output(port=(out_port))
            msg.actions.append(of_action)
        self.connection.send(msg)
        # log.debug("SET RULE: %s" % str(msg))

    def flow_move_1(self):
        log.info("Flow move c2 on s%d" % self.switch)
        m = self.mapping
        if self.switch == 2:
            # move flow from client2 to second link
            self.set_static_rule(
                m["s2-eth4"], m["s2-eth2"], 10, dl_type=0x800, nw_src="20.0.0.2", nw_dst="20.0.1.1")
        elif self.switch == 3:
            # move flow from client2 to second link
            self.set_static_rule(
                m["s3-eth3"], m["s3-eth2"], 10, dl_type=0x800, nw_src="20.0.1.1", nw_dst="20.0.0.2")

    def flow_move_2(self):
        log.info("Flow move c1 on s%d" % self.switch)
        if self.switch == 2:
            # move flow from client1 to second link
            self.set_static_rule(
                m["s2-eth3"], m["s2-eth2"], 10, dl_type=0x800, nw_src="20.0.0.1", nw_dst="20.0.1.1")
        elif self.switch == 3:
            # move flow from client1 to second link
            self.set_static_rule(
                m["s3-eth3"], m["s3-eth2"], 10, dl_type=0x800, nw_src="20.0.1.1", nw_dst="20.0.0.1")


def launch():
    """
    Starts the component
    """
    def start_switch(event):
        SwitchController(event.connection)
    core.openflow.addListenerByName("ConnectionUp", start_switch)
