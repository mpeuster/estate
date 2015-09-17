#!/usr/bin/python

import subprocess
import time
import os


def wait(sec):
    for i in range(sec, 0, -1):
        print "Waiting %ds ..." % i
        time.sleep(1)


def shell(cmd):
    print cmd
    subprocess.call(cmd, shell=True)


def helper_ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def helper_call_topology(args):
    cmd = ["cd", "mininet-environment;", "./topology.py"]
    cmd = " ".join(cmd + args)
    #print "calling: %s" % str(cmd)
    print "Statring scenario"
    shell(cmd)


def helper_cleanup_folder(folder):
    cmd = "rm -r %s/*" % folder
    shell(cmd)


def helper_archive_results(name):
    # store time
    cmd = "date > mininet-environment/log/time.log"
    shell(cmd)
    # copy log files
    helper_ensure_dir("results/%s/" % name)
    cmd = "cp mininet-environment/log/* results/%s/" % name
    shell(cmd)


def run_scenario(name, args):
    print "*" * 40
    print "Starting scenario: %s" % name
    print "*" * 40
    print "ARGS=%s" % str(args)
    print "*" * 40
    # 1. clear output folder
    helper_cleanup_folder("mininet-environment/log")
    wait(3)
    # 2. run scenario
    helper_call_topology(args)
    wait(3)
    # 3. archive results
    helper_archive_results(name)
    wait(3)
    # 4. cleanup again
    helper_cleanup_folder("mininet-environment/log")
    wait(3)


def main():
    """
    Define different experiment runs here.
    """
    # cleanup old results
    helper_cleanup_folder("results")

    # scenarios
    run_scenario("scenario_000", ["--controldelay", "0"])
    run_scenario("scenario_010", ["--controldelay", "10"])
    run_scenario("scenario_020", ["--controldelay", "20"])
    run_scenario("scenario_030", ["--controldelay", "30"])
    run_scenario("scenario_040", ["--controldelay", "40"])
    run_scenario("scenario_050", ["--controldelay", "50"])

    print "*" * 40
    print "Finish!"
    print "*" * 40


if __name__ == '__main__':
    main()
