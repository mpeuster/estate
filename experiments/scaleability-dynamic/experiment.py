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
    # always cleanup mininet, just to be on the safe side
    shell("mn -c")
    # call mininet experiment
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
    helper_ensure_dir("mininet-environment/log")
    # cleanup old results
    helper_cleanup_folder("results")

    # global parameters
    DURATION = 60 * 34  # duration of one scenario

    # different backends
    for be in ["redis", "libestatelocal", "libestatepython"]:
        # different delays
        for i in [0, 20, 40, 60, 80, 100, 120, 140, 160, 180, 200]:
            # different lambdas 1.0, 0.1, 0.01
            for l in [0.01]:
                # different dummy state sizes
                for dss in [0, 128, 1024, 10*1024]:
                    run_scenario(
                        "sc_%s_lambda%03d_delay%03d_dss%04d" % (be, l*100, i, dss),
                        ["--backend", "%s" % be,
                         "--duration", "%d" % DURATION,
                         "--controldelay", "%d" % i,
                         "--numbermb", "%d" % 16,
                         "--srclambda", "%f" % l,
                         "--dummystatesize", "%d" % dss])

    print "*" * 40
    print "Finish!"
    print "*" * 40


if __name__ == '__main__':
    main()
