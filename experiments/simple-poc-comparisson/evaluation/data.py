import pandas as pd
import os
import io
import sys

RESULT_PATH = "../results/"


class Scenario():
    """
    One emulation run.
    - name
    - mblogs: dict of middlebox logs as pandas df
    """

    def __init__(self, path, name):
        self.path = os.path.join(path, name)
        self.name = name
        self.mblogs = {}  # dict containing pandas frames of middlebox logs
        print "Creating scenario '%s' location: '%s'" % (self.name, self.path)
        self.load_middlebox_logs()

    def _get_monitoring_files(self):
        return [
            f for f in os.listdir(self.path)
            if "monitor_" in f]

    def _load_logfile_as_csv(self, fname):
        fpath = os.path.join(self.path, fname)
        data = u""

        def filter_line(l):
            # filers non-data lines
            if "LOG_NETWORK_MONITOR" not in l:
                return ""
            l = l.replace("LOG_NETWORK_MONITOR:", "").rstrip().rstrip(";") + "\n"
            return l

        # open file and read line by line
        with open(fpath, "r") as f:
            for line in f:
                data += filter_line(line)
        return data

    def _load_middlebox_log_to_pandas(self, fname):
        data = self._load_logfile_as_csv(fname)
        df = pd.read_csv(io.StringIO(data), sep=";", dtype=float)
        # for now we will have only positive values
        num = df._get_numeric_data()
        #num[num < 0] = 0
        return df

    def load_middlebox_logs(self):
        files = self._get_monitoring_files()
        for f in files:
            self.mblogs[f] = self._load_middlebox_log_to_pandas(f)
            print ("Loaded log from: %s containing %d rows."
                   % (f, len(self.mblogs[f].index)))
            print "Columns: %s" % list(self.mblogs[f].columns.values)

    def normalize_times(self, timefield="t"):
        """
        Change times so that min(t) is aligned to 0.
        """
        print "Normalizing timestamps %s" % timefield
        tmin = sys.maxint
        for df in self.mblogs.itervalues():
            tmin = df[timefield].min() if df[timefield].min() < tmin else tmin
        for df in self.mblogs.itervalues():
            df[timefield] = df[timefield] - tmin

    def get_middlerbox_names(self):
        return self.mblogs.keys()

    def get_values(self, mbname, fieldname):
        df = self.mblogs.get(mbname, None)
        if df is None:
            raise Exception("mbname not found")
        return df[fieldname].tolist()


class ExperimentData():
    """
    Represents all data collected within one experiment.
    Typically:
    - scenarios dict: name -> scenario_obj
    """

    def __init__(self, path=RESULT_PATH):
        self.path = path
        self.scenarios = {}
        self.load()

    def _get_scenario_names(self):
        return os.listdir(self.path)

    def load_scenarios(self):
        ns = self._get_scenario_names()
        print "Loading scenarios: %s" % str(ns)
        for n in ns:
            self.scenarios[n] = Scenario(self.path, n)

    def load(self):
        self.load_scenarios()

    def normalize_times(self):
        for s in self.scenarios.itervalues():
            s.normalize_times()


def main():
    ed = ExperimentData()


if __name__ == '__main__':
    main()
