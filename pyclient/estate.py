"""
 libestate prototype using libestatepp as backend
"""

import ctypes


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
        self.lib = ctypes.cdll.LoadLibrary(
            "../libestatepp/Debug/libestatepp.so")
        self.ip = str(ip)
        self.port = int(port)
        self.lib.es_init_with_peers(
            self.ip, self.port, self.to_peerlist_str(peerlist))
        print "ES: Initialized estate for instance: %d with peers: %s" % (
            self.instance_id, self.to_peerlist_str(peerlist))

    def close(self):
        self.lib.es_close()

    def set(self, k, s):
        print "ES: SET k=%s s=%s" % (str(k), str(s))
        self.lib.es_set(k, s)
        return True

    def get(self, k):
        print "ES: GET k=%s" % (str(k))
        try:
            rptr = self.lib.es_get(k)
            val = ctypes.c_char_p(rptr).value
            return val if val != "ES_NONE" else None
        except Exception:
            return None

    def delete(self, k):
        print "ES: DEL k=%s" % (str(k))
        self.lib.es_del(k)
        return True

    def get_global(self, k, red_func=0):
        """
        red_func: 0 = latest
                  1 = sum
                  2 = avg
        """
        print "ES: GET_GLOBAL k=%s f=%s" % (str(k), str(red_func))
        rptr = self.lib.es_get_global_predefined_reduce(k, int(red_func))
        return ctypes.c_char_p(rptr).value

    def to_peerlist_str(self, lst):
        res = ""
        for i in range(0, len(lst), 2):
            res += lst[i] + ":" + lst[i + 1] + " "
        return res
