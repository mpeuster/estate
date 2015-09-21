#!/usr/bin/python

from libestateredis.estate_redis import estate as estater
from cppesnode.estate_zmqclient import estate as estatez
from scapy.all import sniff
from scapy.layers.inet import TCP, IP
import sys
import time
import thread

es = None

# global values for pps calculation
last_log_timestamp = 0
last_local_pcount = 0
last_global_pcount = 0


def get_ecounter(k):
    count = es.get(k)
    if count is None:
        return 0
    if count == "ES_NONE":
        return 0
    # TODO try get_global latest if we have a miss
    try:
        res = int(count)
    except ValueError:
        res = 0
        print ("ERROR monitor.py:"
               " Cannot convert get_ecounter value to int: %s" % str(count))
    return res


def set_ecounter(k, v):
    es.set(k, v)


def incr_ecounter(k, incr=1):
    c = get_ecounter(k)
    set_ecounter(k, c + incr)


def get_ecounter_global_sum(k):
    c = es.get_global(k, red_sum)
    try:
        return int(c)
    except ValueError:
        print ("ERROR monitor.py: cannot convert get_ecounter_global_sum"
               " value to int.")
    return 0


def pkt_callback_debug(pkt):
    sys.stdout.flush()
    return pkt.summary()


def pkt_callback(pkt):
    """
    Called for each packet seen on br0.
    Updates NF state, e.g., packet counters.
    """
    # filter for IPv4/TCP packets
    if IP not in pkt:
        return
    if TCP not in pkt:
        return

    # create 5 tuple flow identifier
    flow_id = "flow_%s" % str(
        (pkt[IP].src,
         pkt[TCP].sport,
         pkt[IP].dst,
         pkt[TCP].dport,
         str(pkt[IP].proto))
        ).replace(" ", "")

    # do pattern matching on raw data
    PATTERN = "a"
    pattern_count = 0
    data = str(pkt[TCP].payload)
    if len(data) > 0:
        pattern_count = data.count(PATTERN)

    # update state values:
    # general packet count
    incr_ecounter("pcount")
    # flow specific packet count
    incr_ecounter("pcount:%s" % flow_id)
    # general match count
    incr_ecounter("matchcount", pattern_count)
    # flow specific match count
    incr_ecounter("matchcount:%s" % flow_id, pattern_count)

    # TODO: add state: flows seen, flows active on instance (local dict)

    # debugging:
    #return "PKT: " + str(pkt.summary())


def init_state():
    """
    Initializes estate values, and lcoal values.
    """
    global last_log_timestamp
    last_log_timestamp = time.time()


def log_global_state():
    """
    Executed periodically.
    Requets local and global state and logs (outputs it).
    """
    global last_log_timestamp
    global last_local_pcount
    global last_global_pcount

    # receive local values
    t_get_local_start = time.time()
    pcount_local = get_ecounter("pcount")
    matchcount_local = get_ecounter("matchcount")
    time_local_request = time.time() - t_get_local_start

    # receive global values
    t_get_global_start = time.time()
    pcount_global = get_ecounter_global_sum("pcount")
    matchcount_global = get_ecounter_global_sum("matchcount")
    time_global_request = time.time() - t_get_global_start

    # calculate pps
    timespan = abs(time.time() - last_log_timestamp)
    last_log_timestamp = time.time()
    if timespan == 0:
        raise Exception("We have a zero timespan for PPS calculation")
    pps_local = (pcount_local - last_local_pcount) / timespan
    last_local_pcount = pcount_local
    pps_global = (pcount_global - last_global_pcount) / timespan
    last_global_pcount = pcount_global

    # generate log output
    print("LOG_NETWORK_MONITOR:"
          "%f;%f;%f;%f;%f;%f;%f;%f;%f;"
          % (time.time(),
             pps_local,
             pps_global,
             pcount_local,
             pcount_global,
             matchcount_local,
             matchcount_global,
             time_local_request,
             time_global_request))


def print_log_header():
    # generate log output
    print("LOG_NETWORK_MONITOR:"
          "t;"
          "pps_local;"
          "pps_global;"
          "pcount_local;"
          "pcount_global;"
          "matchcount_local;"
          "matchcount_global;"
          "t_request_local;"
          "t_request_global;")


def log_thread_func():
    while True:
        time.sleep(5)
        log_global_state()
        sys.stdout.flush()


def red_sum(l):
    res = sum([float(i) for i in l])
    #print "red_sum: %s = %f" % (str(l), res)
    return res


def red_avg(l):
    if len(l) < 1:
        return 0
    res = sum([float(i) for i in l]) / float(len(l))
    #print "red_avg: %s = %f" % (str(l), res)
    return res

#TODO add red_latest implementation


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
        es.set_connection_properties(port=(8800 + instance_id))
        es.start_cppesnode_process(
            local_api_port=(8800 + instance_id), peerlist=options)
    else:
        print "specified backend not known"

    if es is None:
        print "backend not initialized. abort."
        exit(1)

    # initialize state
    init_state()

    #start logger
    thread.start_new_thread(log_thread_func, ())

    print_log_header()
    # start monitoring (and block!)
    sniff(iface="br0", prn=pkt_callback, filter="ip and tcp", store=0)


if __name__ == '__main__':
    main()
