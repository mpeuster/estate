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
        return "StateItem: %s(time=%d,node=%s)" % (str(self.data), self.timestamp, str(self.node_identifier))

class estate(object):

    def __init__(self, instance_id, ip="127.0.0.1", base_port=9000):
    	self.instance_id = int(instance_id)
        self.lib = ctypes.cdll.LoadLibrary("libestatepp/Debug/libestatepp.so")
        self.ip = str(ip)
        self.port = int(self.instance_id + base_port)
        self.lib.es_init(self.ip, self.port)
        print "ES: Initialized estate for instance: %d" % self.instance_id

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


    def _get_all_replicas(self, k):
        # return all map items, except of the latest field
        return []

    def _get_newest_replica(self, k):
        return None

    def get_global(self, k, red_func):

        if red_func is None:
            red_func = reduce_test

        print "ES: GET_GLOBAL k=%s f=%s" % (str(k), str(red_func))
        # define signature of reduce function (first argument is the return type)
        CMPFUNC = ctypes.CFUNCTYPE(ctypes.c_char_p, ctypes.POINTER(state_item_t), ctypes.c_int)
        # create a callback pointer for the given reduce function
        reduce_func = CMPFUNC(red_func)
        # call the C library with the callback pointer
        rptr = self.lib.es_get_global(k, reduce_func)
        return ctypes.c_char_p(rptr).value


def reduce_test(data_ptr, length):
    """
    Example reduce function.
    Most important: Convertion from C char** to a python list 
    of strings: data_lst = [data_ptr[i] for i in range(0, length)]
    """
    # TODO hide this when in a nice python module so that the outside does not
    # notice that we are useing a C library
    print "Python reduce: " + str(data_ptr)
    print "Python length: " + str(length)
    # convert to pyhton list of strings
    data_lst = [str(data_ptr[i]) for i in range(0, length)]
    print str(data_lst)
    return "ES_NONE"
