import os
import itertools


def ensure_dir(directory):
    """
    Creates directory if it does not exist.
    """
    if not os.path.exists(directory):
        os.makedirs(directory)

# fg-cn colors
# self.colors = itertools.cycle(['#40458c', '#660066', '#dfa321', '#657bd4', '#ff5cff', '#7f7f7f', 'c', 'y', 'm', 'k'])
# self.colors = itertools.cycle(['r', 'g', 'b', 'c', 'y', 'm', 'k'])
# self.markers = itertools.cycle([u'o', u'v', u'^', u'<', u'>', u'8', u's', u'p', u'*', u'h', u'H', u'D', u'd'])
