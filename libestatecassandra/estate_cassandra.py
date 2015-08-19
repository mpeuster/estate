"""
 libestate prototype using cassandra as backend

 idea: test different consistency models
"""

from cassandra import ConsistencyLevel
from cassandra.cqlengine import columns
from cassandra.cqlengine import connection
from cassandra.cqlengine import management
from cassandra.cqlengine import models
from cassandra.cqlengine import CQLEngineException


# define the model
class KeyValueItem(models.Model):
    """
    We use cassandras map column type to store the values of one key
    for all instances as well as the latest one.

    latest field has index = -1
    """
    key = columns.Text(primary_key=True)
    #instance = columns.Integer(primary_key=True)
    #value = columns.Text()
    data = columns.Map(columns.Integer, columns.Text)
    
    def __repr__(self):
        return 'KeyValueItem.%s' % (self.key)

    def __str__(self):
        return self.__repr__()


class estate(object):

    def __init__(self, instance_id):
    	self.instance_id = int(instance_id)

        # setup cassadnra connection
        connection.setup(['127.0.0.1'], "estate1", consistency=ConsistencyLevel.ALL)

        #  TODO move this to an indipened reset DB script
        if self.instance_id == 0:
            print "FLUSH DB"
            # flush database by first node (for development)
            management.drop_keyspace("estate1")
            # create needed tables
            management.create_keyspace_simple("estate1", replication_factor=1, durable_writes=True)
            management.sync_table(KeyValueItem)

        print "ES: Initialized estate for instance: %s" % self.instance_id


    def set(self, k, s):
        print "ES: SET k=%s s=%s" % (str(k), str(s))
        # always update map field "latest" (-1) to contain the latest value for this key
        KeyValueItem.objects(key=k).update(data__update={-1: str(s), self.instance_id: str(s)})
        return True

    def get(self, k):
        print "ES: GET k=%s" % (str(k))
        try:
            kvi = KeyValueItem.get(key=k)
            val = str(kvi.data.get(self.instance_id))
            return val if val != "None" else "ES_NONE"
        except CQLEngineException:
            return "ES_NONE"

    def delete(self, k):
        """
        Deletes item of this instance for the given key.
        Since cassadnra maps do only support add and updata, we set the value to None.
        Attention: This will also set the "latest" map field to None.
        """
        print "ES: DEL k=%s" % (str(k))
        try:
            #kvi = KeyValueItem.get(key=k)
            #kvi.delete()
            KeyValueItem.objects(key=k).update(data__update={-1: None, self.instance_id: None})
            return True
        except CQLEngineException:
            return False

    def _get_all_replicas(self, k):
        try:
            # return all map items, except of the latest field
            return [v for i, v in KeyValueItem.get(key=k).data.iteritems() if i >= 0]
        except CQLEngineException:
            return []

    def _get_newest_replica(self, k):
        try:
            # return all map items, except of the latest field
            return KeyValueItem.get(key=k).data.get(-1)
        except CQLEngineException:
            return "ES_NONE"

    def get_global(self, k, red_func):
        print "ES: GET_GLOBAL k=%s f=%s" % (str(k), str(red_func))
        if red_func is not None:  # custom red function
            return red_func(self._get_all_replicas(k))
        return self._get_newest_replica(k)  # return newest replica
