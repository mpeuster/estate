import pandas as pd
import os
import io
import sys
import json

RESULT_PATH = "../results/"


class Scenario():
    """
    One emulation run.
    - name
    - mblogs: dict of middlebox logs as pandas df
    - TODO allow to get one combined dataframe with intergrated
    scenario definition: lambda, #mbs etc
    (each key of params dict becomes an additional column).
    """

    def __init__(self, path, name):
        self.path = os.path.join(path, name)
        self.name = name
        self.mblogs = {}  # dict containing pandas frames of middlebox logs
        self.params = {}  # params of scenario from params.json
        print "Creating scenario '%s' location: '%s'" % (self.name, self.path)
        self.load_scenario_parameters()
        self.load_middlebox_logs()

    def load_scenario_parameters(self):
        fpath = os.path.join(self.path, "params.json")
        with open(fpath) as f:
            data = json.load(f)
        self.params = data
        print str(self.params)

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
        try:
            data = self._load_logfile_as_csv(fname)
            df = pd.read_csv(io.StringIO(data), sep=";", dtype=float)
            # for now we will have only positive values
            num = df._get_numeric_data()
            num[num < 0] = 0
            return df
        except:
            print "WARNING: EMPTY monitor.log"
        return None

    def _annotate_df(self, df, mbfile="-1"):
        """
        Add additional data to dataframes to add
        mb number and params to our data.
        """
        # add column with filename (ATTENTION: May break!)
        df["mb"] = int(filter(lambda x: x.isdigit(), mbfile))
        # add params columns
        for k, v in self.params.items():
            try:
                df[str(k)] = float(v)
            except:
                df[str(k)] = v
        return df

    def _calc_global_values(self):
        """
        If we use our local only implementation as a baseline,
        we do not have any results for global values because the
        system operates without global state.
        Thus we calculate these global values for the plot only
        by summing up results from the MB logs.
        """
        for k1, v1 in self.mblogs.iteritems():
            v1["pps_global"] = 0
            v1["pcount_global"] = 0
            v1["matchcount_global"] = 0
            for k2, v2 in self.mblogs.iteritems():
                v1["pps_global"] += v2["pps_local"]
                v1["pcount_global"] += v2["pcount_local"]
                v1["matchcount_global"] += v2["matchcount_local"]

    def load_middlebox_logs(self):
        files = self._get_monitoring_files()
        for f in files:
            df = self._load_middlebox_log_to_pandas(f)
            if df is not None:
                self.mblogs[f] = self._annotate_df(df, f)
                print ("Loaded log from: %s containing %d rows."
                       % (f, len(self.mblogs[f].index)))
                print "Columns: %s" % list(self.mblogs[f].columns.values)
        if self.params["backend"] == "libestatelocal":
            # if we have local only results, we compute the global values
            # to make results comparable
            self._calc_global_values()

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

    def get_combined_dfs(self):
        """
        Generates one dataframe with all log data.
        """
        return pd.concat(
            [d for d in self.mblogs.itervalues()],
            ignore_index=True)


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
            if "DS_Store" not in n:
                # only use folders with monitor data
                spath = os.path.join(self.path, n)
                if len([f for f in os.listdir(spath)
                        if "monitor_" in f]) > 0:
                    self.scenarios[n] = Scenario(self.path, n)

    def load(self):
        self.load_scenarios()

    def normalize_times(self):
        for s in self.scenarios.itervalues():
            s.normalize_times()

    def get_combined_df(self, filter=None):
        """
        Return dataframe data of all scenarios.
        Adds additional index columns based on
        scenario params.
        """
        dfs = [s.get_combined_dfs() for s in self.scenarios.itervalues()]
        return pd.concat(dfs, ignore_index=True)


def main():
    ed = ExperimentData()
    cdf = ed.get_combined_df()
    print cdf
    print "=" * 70
    print "Columns: %s " % str(cdf.columns.values)
    print "Rows: %d " % len(cdf)

if __name__ == '__main__':
    main()
