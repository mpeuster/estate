import pylab
import matplotlib
import itertools
import os
import data
from helper import ensure_dir, get_markers, get_upb_colors, get_preset_colors, label_rename, label_rename_matchexample, label_rename_generic_performance
# ensure correct fonts for ACM/IEEE
matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42
# style template ('bmh', 'ggplot', 'fivethirtyeight')
# matplotlib.pyplot.style.use("ggplot")
matplotlib.pyplot.style.use("grayscale")


def single_scenario_plot(sc, output,
                         xfield="t", yfield=["pps_local", "pps_global"],
                         xname="time [s]", yname="pps", xlim=-1, label_rename_func=None):
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
    colors = get_preset_colors()

    def do_label_rename(l):
        label = label_rename(l)
        if label_rename_func is not None:
            label = label_rename_func(label)
        return label

    # do plots
    for yf in sorted(yfield):
        # throw away second pps global
        if yf == "pps_global":
            nfis = ["monitor_mb1.log"]
        else:
            nfis = sc.get_middlerbox_names()
        for n in sorted(nfis):
            g1.plot(
                sc.get_values(n, xfield),
                sc.get_values(n, yf),
                linewidth=1.0,
                alpha=1.0,
                marker=markers.next(),
                color=colors.next(),
                label=do_label_rename("%s %s" % (n, yf)))

    # handover line
    g1.axvline(55, color='gray', linestyle='--')

    # label etc.
    g1.legend(
        #bbox_to_anchor=(1.02, 1),
        loc=2,
        #borderaxespad=0.,
        fancybox=False,
        shadow=False,
        ncol=1,
        prop={'size': 10})
    g1.set_xlabel(xname)
    g1.set_ylabel(yname)
    if xlim > 0:
        g1.set_xlim(0, xlim)
    # fig.suptitle(sc.name)
    # store to disc
    fig.set_size_inches(4, 3)
    pylab.savefig(
        os.path.join(output, pname + ".pdf"),
        bbox_inches='tight')
    # interactive show
    # pylab.show()
    pylab.close()


def plot(experiment, output_dir="evaluation/single_scenario", input_dir="results/"):
    # setup directories for this plot
    input_dir = os.path.join(experiment, input_dir)
    output_dir = os.path.join(experiment, output_dir)
    ensure_dir(output_dir, rm=True)
    print input_dir
    print output_dir

    # load data
    ed = data.ExperimentData(path=input_dir)
    ed.normalize_times()

    # go over all scenarios and call plot methods
    for s in ed.scenarios.itervalues():
        single_scenario_plot(
            s, output_dir, yfield=["pps_local", "pps_global"],
            yname="packets per second", xlim=120, label_rename_func=label_rename_generic_performance)
        single_scenario_plot(
            s, output_dir, yfield=["pcount_local", "pcount_global"],
            yname="# matches", xlim=120, label_rename_func=label_rename_matchexample)
        single_scenario_plot(
            s, output_dir, yfield=["matchcount_local", "matchcount_global"],
            yname="# matches", xlim=120, label_rename_func=label_rename_matchexample)
        single_scenario_plot(
            s, output_dir, yfield=["t_request_local", "t_request_global"],
            yname="state request delay [s]", xlim=120)

if __name__ == '__main__':
    plot("../simple-poc-comparisson")
