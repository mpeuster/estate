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
                self.assertEqual(e.get("key1"), None)
            else:
                self.assertEqual(e.get("key1"), "value1.%s" % str(e.instance_id))

    # TODO get_global_avg
    # TODO get global sum
    # TODO get global latest





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


class LibestateTestCase(GenericEstateTestCase):

    def setUp(self):
        """
        This test case is a bit different.
        We need to start some other nodes as real external processes which
        built our peer network.

        These nodes might need some time to stabalize their entwork so we need some delays.
        Also, the nodes have to be killed after each test to ensure that the network
        ports are free for the next test.
        """
        START_DELAY = 0.1

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
    # libestate version (UPB)
    ts3 = unittest.TestLoader().loadTestsFromTestCase(LibestateTestCase)
    if len(sys.argv) < 2 or sys.argv[1] == "3":
        suite.addTest(ts3)

    #execute
    unittest.TextTestRunner(verbosity=0).run(suite)
