"""
This component is for use with the OpenFlow tutorial.

It acts as a simple hub, but can be modified to act like an L2
learning switch.

It's roughly similar to the one Brandon Heller did for NOX.
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
        log.debug("Wakeup controller s%d. Flow move in %d seconds!" % (sc.switch, i))
        time.sleep(10)
    sc.flow_move_1()
    # second step move client1 also to mb2
    for i in range(FLOW_MOVE_DELAY, 0, -10):
        log.debug("Wakeup controller s%d. Flow move in %d seconds!" % (sc.switch, i))
        time.sleep(10)
    sc.flow_move_2()


class SwitchController(object):
    """
    A Tutorial object is created for each switch that connects.
    A Connection object for that switch is passed to the __init__ function.
    """
    def __init__(self, connection):
        # Keep track of the connection to the switch so that we can
        # send it messages!
        self.connection = connection

        # This binds our PacketIn event listener
        connection.addListeners(self)

        # witch switch of our topology are we controlling?
        self.switch = int(connection.dpid)
        if self.switch not in [1, 2, 3]:
            log.error("Unidentified switch! Something seems to be wrong with the experiment setup.")

        log.debug("Controlling s%d" % self.switch)
        log.info("Port information {}".format(connection.ports))

        # setup static forwarding rules for experiment
        self.setup_static_rules()

        # start countdown thread for flow change
        if self.switch in [1, 2]:
            start_new_thread(countdown_thread, (self,))

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

    def act_like_hub(self, packet, packet_in):
        """
        Implement hub-like behavior -- send all packets to all ports besides
        the input port.
        """

        # We want to output to all ports -- we do that using the special
        # OFPP_ALL port as the output port.  (We could have also used
        # OFPP_FLOOD.)
        log.debug("called act_like_hub")
        self.resend_packet(packet_in, of.OFPP_ALL)

        # Note that if we didn't get a valid buffer_id, a slightly better
        # implementation would check that we got the full data before
        # sending it (len(packet_in.data) should be == packet_in.total_len)).

    def act_like_switch(self, packet, packet_in):
        """
        Implement switch-like behavior.
        """
        """ # DELETE THIS LINE TO START WORKING ON THIS (AND THE ONE BELOW!) #

        # Here's some psuedocode to start you off implementing a learning
        # switch.  You'll need to rewrite it as real Python code.

        # Learn the port for the source MAC
        self.mac_to_port ... <add or update entry>

        if the port associated with the destination MAC of the packet is known:
          # Send packet out the associated port
          self.resend_packet(packet_in, ...)

          # Once you have the above working, try pushing a flow entry
          # instead of resending the packet (comment out the above and
          # uncomment and complete the below.)

          log.debug("Installing flow...")
          # Maybe the log statement should have source/destination/port?

          #msg = of.ofp_flow_mod()
          #
          ## Set fields to match received packet
          #msg.match = of.ofp_match.from_packet(packet)
          #
          #< Set other fields of flow_mod (timeouts? buffer_id?) >
          #
          #< Add an output action, and send -- similar to resend_packet() >

        else:
          # Flood the packet out everything but the input port
          # This part looks familiar, right?
          self.resend_packet(packet_in, of.OFPP_ALL)

        """  # DELETE THIS LINE TO START WORKING ON THIS #
        pass

    def setup_static_rules(self):
        if self.switch == 1:
            log.info("Setup rules for %d" % self.switch)
            # always use first link as default
            self.set_static_rule(1, 3, 0)
            self.set_static_rule(2, 3, 0)
            self.set_static_rule(3, [1, 2], 0)
            self.set_static_rule(4, [1, 2], 0)
        elif self.switch == 2:
            log.info("Setup rules for %d" % self.switch)
            # always use first link as default
            self.set_static_rule(1, 2, 0)
            self.set_static_rule(2, 1, 0)
            self.set_static_rule(3, 1, 0)
        elif self.switch == 3:
            # set static hub behavior
            self.set_static_rule(None, of.OFPP_ALL, 0)

    def flow_move_1(self):
        log.info("Flow move on s%d" % self.switch)
        if self.switch == 1:
            # move flow from client2 to second link
            self.set_static_rule(2, 4, 10,  dl_type=0x800, nw_src="10.0.0.2", nw_dst="10.0.0.3")
        elif self.switch == 2:
            # move flow from client2 to second link
            self.set_static_rule(1, 3, 10,  dl_type=0x800, nw_src="10.0.0.3", nw_dst="10.0.0.2")

    def flow_move_2(self):
        log.info("Flow move on s%d" % self.switch)
        if self.switch == 1:
            # move flow from client1 to second link
            self.set_static_rule(1, 4, 10,  dl_type=0x800, nw_src="10.0.0.1", nw_dst="10.0.0.3")
        elif self.switch == 2:
            # move flow from client1 to second link
            self.set_static_rule(1, 3, 10,  dl_type=0x800, nw_src="10.0.0.3", nw_dst="10.0.0.1")

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

    def act_static_experiment(self, packet, packet_in):
        # if self.switch == 1:
        #    log.debug(str(packet))
        # self.resend_packet(packet_in, of.OFPP_ALL)
        pass

    def _handle_PacketIn(self, event):
        """
        Handles packet in messages from the switch.
        """

        packet = event.parsed  # This is the parsed packet data.
        if not packet.parsed:
            log.warning("Ignoring incomplete packet")
            return

        packet_in = event.ofp  # The actual ofp_packet_in message.

        # Comment out the following line and uncomment the one after
        # when starting the exercise.
        if self.switch == 1 or self.switch == 2:
            self.act_static_experiment(packet, packet_in)
        else:
            # use HUB behavior as default (e.g. control network)
            self.act_like_hub(packet, packet_in)


def launch():
    """
    Starts the component
    """
    def start_switch(event):
        SwitchController(event.connection)
    core.openflow.addListenerByName("ConnectionUp", start_switch)
