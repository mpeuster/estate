import os
import shutil
import brewer2mpl
import itertools


def ensure_dir(directory, rm=False):
    """
    Creates directory if it does not exist.
    """
    if os.path.exists(directory) and rm:
        shutil.rmtree(directory)
    if not os.path.exists(directory):
        os.makedirs(directory)


def get_upb_colors():
    """
    FG-CN colors
    """
    return itertools.cycle(['#40458c', '#660066', '#dfa321', '#657bd4', '#ff5cff', '#7f7f7f', 'c', 'y', 'm', 'k'])


def get_preset_colors():
    # http://www.cookbook-r.com/Graphs/Colors_(ggplot2)/
    return itertools.cycle(brewer2mpl.get_map('Set1', 'qualitative', 8).mpl_colors)


def get_markers():
    return itertools.cycle([u's', u'o', u'^', u'v', u'p', u'8', u'<', u'>', u'*', u'h', u'H', u'D', u'd'])


def label_rename(lbl):
    lbl = lbl.replace("monitor_mb2.log", "NF.2")
    lbl = lbl.replace("monitor_mb1.log", "NF.1")
    lbl = lbl.replace("pcount_local", "local")
    lbl = lbl.replace("pcount_global", "global")
    lbl = lbl.replace("matchcount_local", "local")
    lbl = lbl.replace("matchcount_global", "global")
    lbl = lbl.replace("pps_local", "local")
    lbl = lbl.replace("pps_global", "global")
    lbl = lbl.replace("t_request_local", "local")
    lbl = lbl.replace("t_request_global", "global")

    lbl = lbl.replace("libestatepython", "libestate")
    lbl = lbl.replace("libestatelocal", "baseline")
    lbl = lbl.replace("redis", "centraldb")
    return lbl


def label_rename_matchexample(lbl):
    lbl = lbl.replace("global", "libestate")
    lbl = lbl.replace("local", "legacy")
    return lbl


def label_rename_generic_performance(lbl):
    lbl = lbl.replace("NF.1 global", "total")
    lbl = lbl.replace("local", "")
    return lbl
