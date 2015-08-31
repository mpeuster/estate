#!/usr/bin/python

from libestateredis.estate_redis import estate as estater
from cppesnode.estate_zmqclient import estate as estatez
from scapy.all import sniff
from scapy.layers.inet import TCP, IP
import sys
import time

es = None


def get_ecounter(k):
    global es
    count = es.get(k)
    if count is None:
        return 0
    if count == "ES_NONE":
        return 0

    try:
        res = int(count)
    except ValueError:
        res = 0
        print "ERROR monitor.py: cannot convert get_ecounter value to int."
    return res


def set_ecounter(k, v):
    global es
    es.set(k, v)

def pkt_callback_debug(pkt):
    sys.stdout.flush()
    return pkt.summary()

def pkt_callback(pkt):
    global es
    sys.stdout.flush()
    # we focus on TCP packets
    if IP not in pkt:
        return
    if TCP not in pkt:
        return
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
    # FIXME do not do this for each packet, it will overload everthing
    global_packet_count = es.get_global("packet_count", red_sum)
    global_flow_count = es.get_global("flow_count", red_sum)
    global_pattern_count_1 = es.get_global("pattern_count_1:%s" % flow_id, red_sum)
    avg_packet_count = es.get_global("packet_count", red_avg)
    avg_flow_count = es.get_global("flow_count", red_avg)
    avg_pattern_count_1 = es.get_global("pattern_count_1", red_avg)

    # artifical delay for debugging
    time.sleep(5)

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
    if len(l) < 1:
        return 0
    res = sum([float(i) for i in l]) / float(len(l))
    print "red_avg: %s = %f" % (str(l), res)
    return res


def main():
    global es
    if len(sys.argv) < 3:
        print "Arguments missing:"
        print "monitor.py BACKEND INST_ID [BACKEND_OPTIONS1...N]"
        print "e.g.: monitor.py redis 1 10.0.0.1"
        exit(1)

    backend = str(sys.argv[1])
    instance_id = int(sys.argv[2])
    options = sys.argv[3:]

    if backend == "redis":
        es = estater(instance_id, redis_host=options[0])
    elif backend == "estatepp":
        es = estatez(instance_id)
        es.set_connection_properties()
        es.start_cppesnode_process(local_api_port=8800, peerlist=options)
    else:
        print "specified backend not known"

    if es is None:
        print "backend not initialized. abort."
        exit(1)

    # start monitoring
    sniff(iface="br0", prn=pkt_callback, filter="ip and tcp", store=0)


if __name__ == '__main__':
    main()
