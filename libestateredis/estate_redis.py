"""
 libestate prototype using a central redis instance
 (used for basic experiment in first paper)
"""
import redis
import time


class estate(object):

    def __init__(self, instance_id):
        # used to distinguish between NF instances
        self.instance_id = str(instance_id)
        # setup redis connection
        self.r = redis.StrictRedis(host="127.0.0.1", port=6379, db=0)
        self.r.flushdb()
        print "ES: Initialized estate for instance: %s" % self.instance_id

    def _acquire_lock(self, lockname):
        while not self.r.setnx(lockname, 1):
            print "ES: Wait for lock..."
            time.sleep(0.1)
        print "ES: Acquired: %s" % lockname

    def _release_lock(self, lockname):
        self.r.delete(lockname)
        print "ES: Released: %s" % lockname

    def _update_time(self, k):
        """
        Attention: Needs global value key!
        Simplification: Redis INCR should already be atomic so that no
        lock mechanism is needed. However, we keep for easy debugging of
        locking times.
        """
        self._acquire_lock("lock.%s" % k)
        val = self.r.incr("globaltime.%s" % k)
        print "ES: Update time: %s is %d" % (k, val)
        self._release_lock("lock.%s" % k)
        return int(val)

    def to_instance_key(self, k):
        return "%s.%s" % (str(k), str(self.instance_id))

    def set(self, k, s):
        # fetch new timestamp for this update
        ts = self._update_time(k)
        kl = self.to_instance_key(k)
        print "ES: SET k=%s s=%s" % (str(kl), str(s))
        # use pipelined command execution for consistency
        pipe = self.r.pipeline()
        pipe.set("timestamp.%s" % kl, ts)
        pipe.set(kl, s)
        return pipe.execute()[1]

    def get(self, k):
        kl = self.to_instance_key(k)
        print "ES: GET k=%s" % (str(kl))
        return self.r.get(kl)

    def delete(self, k):
        kl = self.to_instance_key(k)
        print "ES: DEL k=%s" % (str(kl))
        # use pipelined command execution for consistency
        pipe = self.r.pipeline()
        pipe.delete("timestamp.%s" % kl)
        pipe.delete(kl)
        return pipe.execute()[1]

    def _get_all_replicas(self, k):
        """
        Returns lists tuple:
            1. state list
            2. timestamp list
        """
        keys = self.r.keys("%s*" % k)
        states = []
        timestamps = []
        for kl in keys:
            pipe = self.r.pipeline()
            pipe.get("timestamp.%s" % kl)
            pipe.get(kl)
            res = pipe.execute()
            timestamps.append(res[0])
            states.append(res[1])
        return (states, timestamps)

    def _get_newest_replica(self, k):
        states, timestamps = self._get_all_replicas(k)
        return states[timestamps.index(max(timestamps))]

    def get_global(self, k, red_func):
        print "ES: GET_GLOBAL k=%s f=%s" % (str(k), str(red_func))
        if red_func is not None:  # custom red function
            return red_func(self._get_all_replicas(k)[0])
        return self._get_newest_replica(k)  # return newest replica