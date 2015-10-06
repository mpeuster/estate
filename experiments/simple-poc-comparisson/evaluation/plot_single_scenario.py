import pylab
import matplotlib
import brewer2mpl
import itertools
import os
import data
from helper import ensure_dir, get_markers, get_upb_colors
# ensure correct fonts for ACM/IEEE
matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42
# style template ('bmh', 'ggplot', 'fivethirtyeight')
# matplotlib.pyplot.style.use("ggplot")
matplotlib.pyplot.style.use("grayscale")


def single_scenario_plot(sc, output,
                         xfield="t", yfield=["pps_local", "pps_global"],
                         xname="Time [s]", yname="pps"):
    # input processing
    if isinstance(yfield, basestring) or isinstance(yfield, str):
        yfield = [yfield]
    # setup
    pname = "plt_%s_%s_%s" % (xfield, "_".join(yfield), sc.name)
    print "Plotting: %s" % pname
    # figure
    fig = pylab.figure()
    g1 = fig.add_subplot(111)
    # iterators
    markers = get_markers()
    #colors = get_upb_colors()
    # http://www.cookbook-r.com/Graphs/Colors_(ggplot2)/
    colors = itertools.cycle(brewer2mpl.get_map('Set1', 'qualitative', 8).mpl_colors)
    # do plots
    for n in sc.get_middlerbox_names():
        for yf in yfield:
            g1.plot(
                sc.get_values(n, xfield),
                sc.get_values(n, yf),
                linewidth=1.25,
                alpha=1.0,
                marker=markers.next(),
                color=colors.next(),
                label="%s %s" % (n, yf))
    # label etc.
    g1.legend(
        bbox_to_anchor=(0., 1.02, 1., .102),
        loc=3,
        fancybox=True,
        shadow=False,
        ncol=2,
        mode="expand",
        prop={'size': 10})
    g1.set_xlabel(xname)
    g1.set_ylabel(yname)
    # fig.suptitle(sc.name)
    # store to disc
    fig.set_size_inches(7, 4)
    pylab.savefig(
        os.path.join(output, pname + ".pdf"),
        bbox_inches='tight')
    # interactive show
    # pylab.show()
    pylab.close()


def plot(output="figures/"):
    # prepare output
    ensure_dir(output)
    # load data
    ed = data.ExperimentData()
    ed.normalize_times()

    # go over all scenarios and call plot methods
    for s in ed.scenarios.itervalues():
        single_scenario_plot(
            s, output, yfield=["pps_local", "pps_global"], yname="pps")
        single_scenario_plot(
            s, output, yfield=["pcount_local", "pcount_global"], yname="pcount")
        single_scenario_plot(
            s, output, yfield=["matchcount_local", "matchcount_global"], yname="mcount")
        single_scenario_plot(
            s, output, yfield=["t_request_local", "t_request_global"], yname="t request")

if __name__ == '__main__':
    plot()
