#!/usr/bin/python

import ctypes
lib = ctypes.cdll.LoadLibrary('../libestatepp/Debug/libestatepp.so')


def main():
    print "Py: Running libestatepp test..."
    
    # init estate lib
    lib.es_init()

    # populate the store a bit 
    for i in range(0, 10000):
    	lib.es_set("key%d" % i, "the value of key%d" % i)

    # first set / get
    lib.es_set("k1", "value1")
    rptr = lib.es_get("k1")
    print "Py: Result: %s" % ctypes.c_char_p(rptr).value

    # second (update) set/get
    lib.es_set("k1", "value1-updated")
    rptr = lib.es_get("k1")
    print "Py: Result: %s" % ctypes.c_char_p(rptr).value

    # del test
    lib.es_del("k1")
    rptr = lib.es_get("k1")
    print "Py: Result: %s" % ctypes.c_char_p(rptr).value

    # close estate lib
    lib.es_close()



if __name__ == '__main__':
    main()
