"""
 libestate prototype using libestatepp as backend
"""

import ctypes
import os


class state_item_t(ctypes.Structure):
    """
    This custom structure corresponds to the state_item_t structure of
    libestate.
    It wraps the C struct to a normal pyhton class.
    """
    _fields_ = [("timestamp", ctypes.c_int),
                ("node_identifier", ctypes.c_char_p),
                ("data", ctypes.c_char_p)]

    def __str__(self):
        return "StateItem: %s(time=%d,node=%s)" % (
            str(self.data), self.timestamp, str(self.node_identifier))


class estate(object):

    def __init__(self, instance_id):
        self.instance_id = int(instance_id)

    def init_libestate(self, ip, port, peerlist=["127.0.0.1", "9000"]):
        print "Loading lib ..."
        self.lib = ctypes.cdll.LoadLibrary(
            os.path.join(os.path.dirname(__file__),
                         "../libestatepp/Debug/libestatepp.so"))
        self.ip = str(ip)
        self.port = int(port)
        self.lib.es_init_with_peers(
            self.ip, self.port, self.to_peerlist_str(peerlist))
        print "ES: Initialized estate for instance: %d with peers: %s" % (
            self.instance_id, self.to_peerlist_str(peerlist))

    def close(self):
        self.lib.es_close()
        print "closed"

    def set(self, k, v):
        # print "ES: SET k=%s v=%s" % (str(k), str(v))
        self.lib.es_set(str(k), str(v))
        return True

    def get(self, k):
        # print "ES: GET k=%s" % (str(k))
        try:
            self.lib.es_get.restype = ctypes.c_char_p
            rptr = self.lib.es_get(str(k))
            val = ctypes.c_char_p(rptr).value
            return val if val != "ES_NONE" else None
        except Exception:
            return None

    def delete(self, k):
        # print "ES: DEL k=%s" % (str(k))
        self.lib.es_del(str(k))
        return True

    def get_global(self, k, red_func=0):
        """
        red_func: 0 = latest
                  1 = sum
                  2 = avg
        """
        # we handle all kinds of formats to be compatible
        red_func = str(red_func)
        rf_id = 0
        if "latest" in red_func:
            rf_id = 0
        elif "sum" in red_func:
            rf_id = 1
        elif "avg" in red_func:
            rf_id = 2
        else:
            try:
                rf_id = int(red_func)
            except:
                rf_id = 0
                print "WARNING: estate.py unknown red_func value"

        # print "ES: GET_GLOBAL k=%s f=%s" % (str(k), str(rf_id))
        try:
            # attention: setting the restype is important!
            self.lib.es_get_global_predefined_reduce.restype = ctypes.c_char_p
            rptr = self.lib.es_get_global_predefined_reduce(str(k))
            val = ctypes.c_char_p(rptr).value
            return val
        except:
            return "ES_NONE"

    def to_peerlist_str(self, lst):
        res = ""
        for i in range(0, len(lst), 2):
            res += lst[i] + ":" + lst[i + 1] + " "
        return res
