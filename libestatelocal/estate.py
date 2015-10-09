"""
Dummy libestate that holds all state local.
Used to have some baseline results.
get_global results are simply the local ones.
"""
import logging
logging.basicConfig(level=logging.INFO)


class estate(object):

    def __init__(self, instance_id):
        # used to distinguish between NF instances
        self.instance_id = str(instance_id)
        self.state = {}  # local state hashmap
        logging.info(
            "ES-LOCAL: Initialized estate for instance: %s"
            % self.instance_id)

    def set(self, k, s):
        # fetch new timestamp for this update
        logging.debug("ES: SET k=%s s=%s" % (str(k), str(s)))
        self.state[str(k)] = str(s)
        return True

    def get(self, k):
        logging.debug("ES: GET k=%s" % (str(k)))
        return self.state.get(str(k), "ES_NONE")

    def delete(self, k):
        logging.debug("ES: DEL k=%s" % (str(k)))
        del self.state[str(k)]
        return True

    def get_global(self, k, red_func=None):
        logging.debug("ES: GET_GLOBAL k=%s f=%s" % (str(k), str(red_func)))
        return self.get(k)


if __name__ == '__main__':
    # some tests
    e = estate(0)
    print e.set("k1", "v1")
    print e.get("k1")
    print e.set("k1", "v1.updated")
    print e.get_global("k1")
    print e.delete("k1")
    print e.get("k1")
    print e.get_global("k1")
