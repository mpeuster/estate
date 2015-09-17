import pandas as pd
import os
import io

RESULT_PATH = "../results/"


class Scenario():

    def __init__(self, path, name):
        self.path = "%s%s/" % (path, name)
        self.name = name
        self.mblogs = {}  # dict containing pandas frames of middlebox logs
        print "Creating scenario '%s' location: '%s'" % (self.name, self.path)
        self.load_middlebox_logs()

    def _get_monitoring_files(self):
        return [
            f for f in os.listdir(self.path)
            if "monitor_" in f]

    def _load_logfile_as_csv(self, fname):
        fpath = "%s%s" % (self.path, fname)
        data = u""

        def filter_line(l):
            # filers non-data lines
            if "LOG_NETWORK_MONITOR" not in l:
                return ""
            l = l.replace("LOG_NETWORK_MONITOR:", "")
            return l
        # open file and read line by line
        with open(fpath, "r") as f:
            for line in f:
                data += filter_line(line)
        return data

    def _load_middlebox_log_to_pandas(self, fname):
        # TODO cleanup
        data = self._load_logfile_as_csv(fname)
        df = pd.read_csv(io.StringIO(data), sep=";")
        print df
        return None

    def load_middlebox_logs(self):
        files = self._get_monitoring_files()
        for f in files:
            self.mblogs[f] = self._load_middlebox_log_to_pandas(f)
            print "Loaded log from: %s" % f


class ExperimentData():

    def __init__(self, path=RESULT_PATH):
        self.path = path
        self.scenarios = {}

    def _get_scenario_names(self):
        return os.listdir(self.path)

    def load_scenarios(self):
        ns = self._get_scenario_names()
        print "Loading scenarios: %s" % str(ns)
        for n in ns:
            self.scenarios[n] = Scenario(self.path, n)



def main():
    ed = ExperimentData()
    ed.load_scenarios()


if __name__ == '__main__':
    main()
