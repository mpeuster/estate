import pylab
import matplotlib
import os
import data
from helper import ensure_dir, get_markers, get_upb_colors, get_preset_colors, label_rename
# ensure correct fonts for ACM/IEEE
matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42
# style template ('bmh', 'ggplot', 'fivethirtyeight')
#matplotlib.pyplot.style.use("ggplot")
matplotlib.pyplot.style.use("grayscale")


def multi_scenario_plot(
        output,
        ed,
        xfield="numbermb",
        yfield=["pps_global", "pps_local"],
        destinction_field="backend",
        rowfilter={"controldelay": 0},
        xname=None,
        yname="pps",
        name_pre="",
        name_post=""
        ):
    # get dataframe
    df = ed.get_combined_df()
    # input processing
    if isinstance(yfield, basestring) or isinstance(yfield, str):
        yfield = [yfield]
    xname = xfield if xname is None else xname
    yname = yfield if yname is None else yname
    # setup
    pname = "plt_multi_%s%s_%s%s" % (name_pre, xfield, "_".join(yfield), name_post)
    print "Plotting: %s" % pname
    # figure
    fig = pylab.figure()
    g1 = fig.add_subplot(111)
    # iterators
    markers = get_markers()
    colors = get_preset_colors()

    # get different values for lines to be plotted
    destinction_values = [""]
    if destinction_field is not None:
        destinction_values = list(set(df[destinction_field].tolist()))

    print df
    print destinction_values

    # filter data for single plot
    for yf in yfield:
        for dv in destinction_values:
            dfiltered = df
            if destinction_field is not None:
                dfiltered = dfiltered[dfiltered[destinction_field] == dv]
            if len(rowfilter) > 0:
                for k, v in rowfilter.items():
                    dfiltered = dfiltered[dfiltered[k] == v]

            # reduce data to have xfield -> yflied 1:1 relationship
            dfiltered = dfiltered.groupby(xfield).mean()
            print dfiltered
            # do plots
            g1.plot(
                dfiltered.index.values,
                dfiltered[yf].tolist(),
                linewidth=1.5,
                alpha=1.0,
                marker=markers.next(),
                color=colors.next(),
                label=label_rename("%s %s" % (dv, yf)))

    # label etc.
    g1.legend(
        bbox_to_anchor=(1.02, 1),
        loc=2,
        borderaxespad=0.,
        fancybox=False,
        shadow=False,
        ncol=1,
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


def plot(experiment, output_dir="evaluation/multi_scenario", input_dir="results/"):
    # setup directories for this plot
    input_dir = os.path.join(experiment, input_dir)
    output_dir = os.path.join(experiment, output_dir)
    ensure_dir(output_dir, rm=True)
    print input_dir
    print output_dir

    # load data
    ed = data.ExperimentData(path=input_dir)
    ed.normalize_times()
    df = ed.get_combined_df()

    cdelays = df["controldelay"].drop_duplicates().tolist()
    print cdelays

    lambdas = df["srclambda"].drop_duplicates().tolist()
    print lambdas

    middleboxes = df["numbermb"].drop_duplicates().tolist()
    print middleboxes

    """
    Plots:
    xaxis = numbermb
    yaxis = pps, request times, global pcount
    layout: one plot line per backend
    """
    for delay in cdelays:
        for lmb in lambdas:
            multi_scenario_plot(
                output_dir,
                ed,
                xfield="numbermb",
                yfield=["pps_global", "pps_local"],
                destinction_field="backend",
                rowfilter={"controldelay": delay, "srclambda": lmb},
                xname="number of NF replicas",
                yname="packets per second",
                name_pre="",
                name_post="_d%03d_l%03d" % (delay, lmb*100)
                )
            multi_scenario_plot(
                output_dir,
                ed,
                xfield="numbermb",
                yfield=["t_request_global", "t_request_local"],
                destinction_field="backend",
                rowfilter={"controldelay": delay, "srclambda": lmb},
                xname="number of NF replicas",
                yname="state request delay [s]",
                name_pre="",
                name_post="_d%03d_l%03d" % (delay, lmb*100)
                )
            multi_scenario_plot(
                output_dir,
                ed,
                xfield="numbermb",
                yfield=["pcount_global"],
                destinction_field="backend",
                rowfilter={"controldelay": delay, "srclambda": lmb},
                xname="number of NF replicas",
                yname="number of processed packets",
                name_pre="",
                name_post="_d%03d_l%03d" % (delay, lmb*100)
                )

    """
    Plots:
    xaxis = controldelay
    yaxis = pps, request times, global pcount
    layout: one plot line per backend
    """
    for nmb in middleboxes:
        for lmb in lambdas:
            multi_scenario_plot(
                output_dir,
                ed,
                xfield="controldelay",
                yfield=["pps_global", "pps_local"],
                destinction_field="backend",
                rowfilter={"numbermb": nmb, "srclambda": lmb},
                xname="control plane latency [ms]",
                yname="packets per second",
                name_pre="",
                name_post="_nmb%03d_l%03d" % (nmb, lmb*100)
                )
            multi_scenario_plot(
                output_dir,
                ed,
                xfield="controldelay",
                yfield=["t_request_global", "t_request_local"],
                destinction_field="backend",
                rowfilter={"numbermb": nmb, "srclambda": lmb},
                xname="control plane latency [ms]",
                yname="state request delay [s]",
                name_pre="",
                name_post="_nmb%03d_l%03d" % (nmb, lmb*100)
                )
            multi_scenario_plot(
                output_dir,
                ed,
                xfield="controldelay",
                yfield=["pcount_global"],
                destinction_field="backend",
                rowfilter={"numbermb": nmb, "srclambda": lmb},
                xname="control plane latency [ms]",
                yname="number of processed packets",
                name_pre="",
                name_post="_nmb%03d_l%03d" % (nmb, lmb*100)
                )
if __name__ == '__main__':
    plot()