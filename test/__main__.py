"""
 simple test script to check different libestate implementations
"""

import unittest

from libestateredis.estate_redis import estate as estater
from libestatecassandra.estate_cassandra import estate as estatec





class GenericEstateTestCase(unittest.TestCase):

    def __init__(self, args):
        super(GenericEstateTestCase, self).__init__(args)
        self.es = []

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
        # create a number of es instances
        self.es = []
        for i in range(0, 5):
            self.es.append(estater(i))


class CassandraEstateTestCase(GenericEstateTestCase):

    def setUp(self):
        # create a number of es instances
        self.es = []
        for i in range(0, 5):
            self.es.append(estatec(i))



def old_test():
    es = estatec(0)
    es2 = estatec(1)

    print "-" * 42
    print "TEST"
    print "-" * 42
    # local tests
    print es.set("key1", "value1")
    print es.get("key1")
    print es.delete("key1")
    print es.delete("key1")
    print es.get("key1")
    # global tests
    print es.set("key1", "4")
    print es.set("key2", "3")
    print es2.set("key1", "2")
    print es.set("key1", "8")
    print es.get("key1")
    print es2.get("key1")
    print es.get_global("key1", red_sum)
    print es.get_global("key1", red_avg)
    print es.get_global("key1", None)


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
    suite.addTest(ts1)
    # cassandra version
    ts2 = unittest.TestLoader().loadTestsFromTestCase(CassandraEstateTestCase)
    suite.addTest(ts2)

    #execute
    unittest.TextTestRunner(verbosity=2).run(suite)
