import ctypes
lib = ctypes.cdll.LoadLibrary('../libestatepp/Debug/libestatepp.so')


def main():
    print "Running libestatepp test..."
    # lib.es_set("k2", "value2")
    lib.testpp.restype = ctypes.c_int
    lib.testpp()


if __name__ == '__main__':
    main()
