import os
import itertools


def ensure_dir(directory):
    """
    Creates directory if it does not exist.
    """
    if not os.path.exists(directory):
        os.makedirs(directory)


# self.colors = itertools.cycle(['r', 'g', 'b', 'c', 'y', 'm', 'k'])

def get_upb_colors():
    """
    FG-CN colors
    """
    return itertools.cycle(['#40458c', '#660066', '#dfa321', '#657bd4', '#ff5cff', '#7f7f7f', 'c', 'y', 'm', 'k'])


def get_markers():
    return itertools.cycle([u'o', u's', u'^', u'v', u'p', u'8', u'<', u'>', u'*', u'h', u'H', u'D', u'd'])
