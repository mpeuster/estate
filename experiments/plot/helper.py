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
    return itertools.cycle([u'o', u's', u'^', u'v', u'p', u'8', u'<', u'>', u'*', u'h', u'H', u'D', u'd'])
