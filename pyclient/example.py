import ctypes
lib = ctypes.cdll.LoadLibrary('../libestatepp/Debug/libestatepp.so')


def main():
    print "Running libestatepp test..."
    lib.es_init()

    lib.es_set("k1", "value1")
    rptr = lib.es_get("k1")
    print ctypes.c_char_p(rptr).value
    lib.es_del("k1")

    lib.es_close()



if __name__ == '__main__':
    main()
