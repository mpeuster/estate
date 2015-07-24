#!/usr/bin/python

from elasticstate import estate
from scapy.all import *
import sys
import time

es = None


def get_ecounter(k):
    global es
    count = es.get(k)
    if count is None:
        return 0
    return int(count)


def set_ecounter(k, v):
    global es
    es.set(k, v)


def pkt_callback(pkt):
    global es

    # count packets
    packet_count = get_ecounter("packet_count")
    packet_count += 1
    set_ecounter("packet_count", packet_count)

    # 5 tuple of flow
    src_ip = pkt[IP].src
    dst_ip = pkt[IP].dst
    proto = str(pkt[IP].proto)  # tcp = 6
    src_port = pkt[TCP].sport
    dst_port = pkt[TCP].dport
    flow_id = "flow_%s" % str((src_ip, src_port, dst_ip, dst_port, proto)).replace(" ", "")

    # count packets for each flow
    flow_count = get_ecounter("flow_count:%s" % flow_id)
    flow_count += 1
    set_ecounter("flow_count:%s" % flow_id, flow_count)

    # get raw data and do pattern matching
    data = str(pkt[TCP].payload)
    pattern_count_1 = get_ecounter("pattern_count_1:%s" % flow_id)
    if len(data) > 0:
        pattern_count_1 += data.count("a")
        set_ecounter("pattern_count_1:%s" % flow_id, pattern_count_1)

    # get global view on the system
    global_packet_count = es.get_global("packet_count", red_sum)
    global_flow_count = es.get_global("flow_count", red_sum)
    global_pattern_count_1 = es.get_global("pattern_count_1:%s" % flow_id, red_sum)
    avg_packet_count = es.get_global("packet_count", red_avg)
    avg_flow_count = es.get_global("flow_count", red_avg)
    avg_pattern_count_1 = es.get_global("pattern_count_1", red_avg)

    # return "Packet #" + str(packet_count) + ": " + src_ip + ":" + str(src_port) + "  ==>  " + dst_ip + ":" + str(dst_port)
    return "#MON#%s# time:%f flow:%s pcount:%d fpcount:%d m1count:%d gpcount:%d gfpcount:%d gm1count:%d apcount:%d afpcount:%d am1count:%d" % (
        es.instance_id, time.time(), flow_id, packet_count, flow_count, pattern_count_1,
        global_packet_count, global_flow_count, global_pattern_count_1,
        avg_packet_count, avg_flow_count, avg_pattern_count_1)
    # return pkt.summary()
    # debug
    # pkt.show()


def red_sum(l):
    res = sum([float(i) for i in l])
    print "red_sum: %s = %f" % (str(l), res)
    return res


def red_avg(l):
    res = sum([float(i) for i in l]) / float(len(l))
    print "red_avg: %s = %f" % (str(l), res)
    return res


def main():
    global es
    if len(sys.argv) < 1:
        print "Add instance identifier argument."
        exit(1)
    es = estate(int(sys.argv[1]))
    # test()
    sniff(iface="br0", prn=pkt_callback, filter="ip", store=0)


if __name__ == '__main__':
    main()
