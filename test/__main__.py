"""
 simple test script to check different libestate implementations
"""

import unittest
import subprocess
import time
import sys

from libestateredis.estate_redis import estate as estater
from libestatecassandra.estate_cassandra import estate as estatec
from pyclient.estate import estate as estatep
from cppesnode.estate_zmqclient import estate as estatez


class GenericEstateTestCase(unittest.TestCase):
    """
    This is the generic use case in which our tests are defined.
    All library speciffic use cases inherit from this class and apply
    the tests to their own library instances.
    """

    def __init__(self, args):
        super(GenericEstateTestCase, self).__init__(args)
        self.es = []
        self.enode = []

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_single_set(self):
        self.assertTrue(self.es[0].set("key1", "value1"))

    def test_single_get(self):
        self.assertTrue(self.es[0].set("key1", "value1"))
        self.assertEqual(self.es[0].get("key1"), "value1")

    def test_multi_instance_set_get(self):
        for e in self.es:
            self.assertTrue(e.set("key1", "value1.%s" % str(e.instance_id)))

        for e in self.es:
            self.assertEqual(e.get("key1"), "value1.%s" % str(e.instance_id))

    def test_multi_instance_single_delete(self):
        for e in self.es:
            self.assertTrue(e.set("key1", "value1.%s" % str(e.instance_id)))

        self.assertTrue(self.es[0].delete("key1"))

        for e in self.es:
            if str(e.instance_id) == "0":
                self.assertEqual(e.get("key1"), "ES_NONE")
            else:
                self.assertEqual(e.get("key1"), "value1.%s" % str(e.instance_id))

    #@unittest.skip("skip globals")
    def test_get_globel_latest(self):
        # set values to all nodes
        for e in self.es:
            self.assertTrue(e.set("key_1", "value1.%s" % str(e.instance_id)))

        # wait here to not run into effects
        # caused by realtime clock resolution (this is part of evaluation)
        time.sleep(0.01)

        # overwrite one value
        self.es[0].set("key_1", "value1.1.updated")

        # get latest value on each node!
        for e in self.es:
            self.assertEqual(e.get_global("key_1", None), "value1.1.updated")

    #@unittest.skip("skip globals")
    def test_get_globel_sum(self):
        # set values to all nodes
        for e in self.es:
            self.assertTrue(e.set("key_1", 0.8))

        # overwrite one value
        self.es[0].set("key_1", 0.7)

        # get global value (expected: 4 * 0.8 + 1 * 0.7 = 3.9)
        for e in self.es:
            if str(self.__class__.__name__) == "CppesnodeEstateTestCase":
                # Cppesnode cases have to be handled different, since reduce functions
                # are implemented remotely
                self.assertAlmostEqual(
                    float(e.get_global("key_1", "SUM")), (len(self.es) - 1) * 0.8 + 0.7)
            else:
                # normal case, with local defined reduce functions
                self.assertAlmostEqual(
                    float(e.get_global("key_1", red_sum)), (len(self.es) - 1) * 0.8 + 0.7)

    #@unittest.skip("skip globals")
    def test_get_globel_avg(self):
        # set values to all nodes
        for e in self.es:
            self.assertTrue(e.set("key_1", 0.8))

        # overwrite one value
        self.es[0].set("key_1", 0.7)

        # get global value (expected: (4 * 0.8 + 1 * 0.7) / 5 = 0.78)
        for e in self.es:
            if str(self.__class__.__name__) == "CppesnodeEstateTestCase":
                # Cppesnode cases have to be handled different, since reduce functions
                # are implemented remotely
                self.assertAlmostEqual(
                    float(e.get_global("key_1", "AVG")),
                    ((len(self.es) - 1) * 0.8 + 0.7) / len(self.es))
            else:
                # normal case, with local defined reduce functions
                self.assertAlmostEqual(
                    float(e.get_global("key_1", red_avg)),
                    ((len(self.es) - 1) * 0.8 + 0.7) / len(self.es))





class ReditEstateTestCase(GenericEstateTestCase):

    def setUp(self):
        # create a number of es instances (all running in test process)
        self.es = []
        for i in range(0, 5):
            self.es.append(estater(i))


class CassandraEstateTestCase(GenericEstateTestCase):

    def setUp(self):
        # create a number of es instances (all running in test process)
        self.es = []
        for i in range(0, 5):
            self.es.append(estatec(i))


class CppesnodeEstateTestCase(GenericEstateTestCase):
    """
        libestate (UPB) using direct Python-to-C wrapper
    """

    def setUp(self):
        # create a number of es instances (all running in separated process)
        N_NODES = 5
        peers = []
        for i in range(0, N_NODES):
            peers.append("127.0.0.1")
            peers.append("%d" % (9000 + i))

        self.es = []
        for i in range(0, N_NODES):
            e = estatez(i)
            e.set_connection_properties(port=8800+i)
            e.start_cppesnode_process(local_api_port=8800+i, peerlist=rotate_list(peers, i * 2))
            self.es.append(e)

    def tearDown(self):
        for e in self.es:
            e.stop_cppesnode_process()
        # just to be sure ;-)
        subprocess.call(["pkill", "cppesnode"])


class LibestateTestCase(GenericEstateTestCase):
    """
        libestate (UPB) using direct Python-to-C wrapper

        This test case is a bit different.
        We need to start some other nodes as real external processes which
        built our peer network.

        These nodes might need some time to stabalize their entwork so we need some delays.
        Also, the nodes have to be killed after each test to ensure that the network
        ports are free for the next test.
    """

    def setUp(self):
        START_DELAY = 0.5

        # run 4 environment instaces (node.py)
        self.enodes = []
        for i in range(1, 6):
            self.enodes.append(subprocess.Popen(["./pyclient/node.py", str(i)]))
            print "Started node.py %d" % i
            time.sleep(START_DELAY)

        # create local test instance
        self.es = []
        self.es.append(estatep(0))
        time.sleep(START_DELAY)

    def tearDown(self):
        STOP_DELAY = 0.1

        for e in self.enodes:
            e.terminate()
            time.sleep(STOP_DELAY)

        # not nice, but helps if e.terminate does not work
        subprocess.call(["pkill", "node.py"])
        time.sleep(STOP_DELAY)

        for e in self.es:
            e.close()
            time.sleep(STOP_DELAY)



def red_sum(l):
    print str(l)
    res = sum([float(i) for i in l])
    print "red_sum: %s = %f" % (str(l), res)
    return res


def red_avg(l):
    print str(l)
    res = sum([float(i) for i in l]) / float(len(l))
    print "red_avg: %s = %f" % (str(l), res)
    return res

def rotate_list(lst, offset):
    return lst[offset:] + lst[:offset]

if __name__ == '__main__':
    suite = unittest.TestSuite()
    # redis version
    ts1 = unittest.TestLoader().loadTestsFromTestCase(ReditEstateTestCase)
    if len(sys.argv) < 2 or sys.argv[1] == "1":
        suite.addTest(ts1)
    # cassandra version
    ts2 = unittest.TestLoader().loadTestsFromTestCase(CassandraEstateTestCase)
    if len(sys.argv) < 2 or sys.argv[1] == "2":
        suite.addTest(ts2)
    # libestate version (UPB) using cppesnode as bridge
    ts3 = unittest.TestLoader().loadTestsFromTestCase(CppesnodeEstateTestCase)
    if len(sys.argv) < 2 or sys.argv[1] == "3":
        suite.addTest(ts3)
    # libestate version (UPB) direct Python-to-C wrapper
    #ts4 = unittest.TestLoader().loadTestsFromTestCase(LibestateTestCase)
    #if len(sys.argv) < 2 or sys.argv[1] == "4":
    #    suite.addTest(ts4)

    #execute
    unittest.TextTestRunner(verbosity=0).run(suite)
