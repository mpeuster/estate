import pylab
import matplotlib
from scipy import stats as st
import scipy
import scikits.bootstrap as bootstrap
import numpy as np
import os
import data
from helper import ensure_dir, get_markers, get_upb_colors, get_preset_colors, label_rename
# ensure correct fonts for ACM/IEEE
matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42
# style template ('bmh', 'ggplot', 'fivethirtyeight')
#matplotlib.pyplot.style.use("ggplot")
matplotlib.pyplot.style.use("grayscale")

ENABLE_CONFIDENCE_INTERVAL = False


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
        name_post="",
        xlogscale=False
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

    # print df
    # print destinction_values

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
            dfmean = dfiltered.groupby(xfield).mean()
            # print dfmean["pps_global"]
            # calc confidence intervals:
            # http://stackoverflow.com/questions/18039923/standard-error-ignoring-nan-in-pandas-groupby-groups
            # http://www.randalolson.com/2012/08/06/statistical-analysis-made-easy-in-python/
            # http://stackoverflow.com/questions/15033511/compute-a-confidence-interval-from-sample-data
            dfci = dfiltered.groupby(xfield).aggregate(lambda x: scipy.stats.sem(x) * scipy.stats.t.ppf((1+0.95)/2., len(x)-1))
            # print dfci["pps_global"]

            # create labels
            if len(yfield) < 2:
                labelstr = label_rename("%s" % (dv))
            else:
                labelstr = label_rename("%s %s" % (dv, yf))

            # do plots
            if ENABLE_CONFIDENCE_INTERVAL:
                g1.errorbar(
                    dfmean.index.values,
                    dfmean[yf].tolist(),
                    linewidth=1.5,
                    alpha=1.0,
                    marker=markers.next(),
                    color=colors.next(),
                    label=labelstr,
                    yerr=dfci[yf].tolist())
            else:
                g1.plot(
                    dfmean.index.values,
                    dfmean[yf].tolist(),
                    linewidth=1.5,
                    alpha=1.0,
                    marker=markers.next(),
                    color=colors.next(),
                    label=labelstr)

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

    if xlogscale:
        g1.set_xscale('log', basex=2)

    # fig.suptitle(sc.name)
    # store to disc
    fig.set_size_inches(7, 5)
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

    cdelays = sorted(df["controldelay"].drop_duplicates().tolist())
    print cdelays

    lambdas = sorted(df["srclambda"].drop_duplicates().tolist())
    print lambdas

    middleboxes = sorted(df["numbermb"].drop_duplicates().tolist())
    # middleboxes.remove(16)
    print middleboxes

    dummystatesizes = sorted(df["dummystatesize"].drop_duplicates().tolist())
    print dummystatesizes

    """
    Plots:
    xaxis = numbermb
    yaxis = pps, request times, global pcount
    layout: one plot line per backend
    """
    for delay in cdelays[:2]:
        for lmb in lambdas:
            for dss in dummystatesizes:
                multi_scenario_plot(
                    output_dir,
                    ed,
                    xfield="numbermb",
                    yfield=["pps_global", "pps_local"],
                    destinction_field="backend",
                    rowfilter={
                        "controldelay": delay,
                        "srclambda": lmb,
                        "dummystatesize": dss},
                    xname="number of NF instances",
                    yname="avg. packets/second",
                    name_pre="",
                    name_post="_d%03d_l%03d_dss%08d" % (delay, lmb*100, dss)
                    )
                multi_scenario_plot(
                    output_dir,
                    ed,
                    xfield="numbermb",
                    yfield=["pps_global"],
                    destinction_field="backend",
                    rowfilter={
                        "controldelay": delay,
                        "srclambda": lmb,
                        "dummystatesize": dss},
                    xname="number of NF instances",
                    yname="avg. packets/second",
                    name_pre="",
                    name_post="_d%03d_l%03d_dss%08d" % (delay, lmb*100, dss)
                    )
                multi_scenario_plot(
                    output_dir,
                    ed,
                    xfield="numbermb",
                    yfield=["t_request_global", "t_request_local"],
                    destinction_field="backend",
                    rowfilter={
                        "controldelay": delay,
                        "srclambda": lmb,
                        "dummystatesize": dss},
                    xname="number of NF instances",
                    yname="avg. request delay [s]",
                    name_pre="",
                    name_post="_d%03d_l%03d_dss%08d" % (delay, lmb*100, dss)
                    )
                multi_scenario_plot(
                    output_dir,
                    ed,
                    xfield="numbermb",
                    yfield=["t_request_global"],
                    destinction_field="backend",
                    rowfilter={
                        "controldelay": delay,
                        "srclambda": lmb,
                        "dummystatesize": dss},
                    xname="number of NF instances",
                    yname="avg. request delay [s]",
                    name_pre="",
                    name_post="_d%03d_l%03d_dss%08d" % (delay, lmb*100, dss)
                    )
                multi_scenario_plot(
                    output_dir,
                    ed,
                    xfield="numbermb",
                    yfield=["pcount_global", "pcount_local"],
                    destinction_field="backend",
                    rowfilter={
                        "controldelay": delay,
                        "srclambda": lmb,
                        "dummystatesize": dss},
                    xname="number of NF instances",
                    yname="number of processed packets",
                    name_pre="",
                    name_post="_d%03d_l%03d_dss%08d" % (delay, lmb*100, dss)
                    )

    """
    Plots:
    xaxis = controldelay
    yaxis = pps, request times, global pcount
    layout: one plot line per backend
    """
    for nmb in middleboxes:
        for lmb in lambdas:
            for dss in dummystatesizes[:2]:
                multi_scenario_plot(
                    output_dir,
                    ed,
                    xfield="controldelay",
                    yfield=["pps_global", "pps_local"],
                    destinction_field="backend",
                    rowfilter={
                        "numbermb": nmb,
                        "srclambda": lmb,
                        "dummystatesize": dss},
                    xname="control plane latency [ms]",
                    yname="avg. packets/second",
                    name_pre="",
                    name_post="_nmb%03d_l%03d_dss%08d" % (nmb, lmb*100, dss)
                    )
                multi_scenario_plot(
                    output_dir,
                    ed,
                    xfield="controldelay",
                    yfield=["pps_global"],
                    destinction_field="backend",
                    rowfilter={
                        "numbermb": nmb,
                        "srclambda": lmb,
                        "dummystatesize": dss},
                    xname="control plane latency [ms]",
                    yname="avg. packets/second",
                    name_pre="",
                    name_post="_nmb%03d_l%03d_dss%08d" % (nmb, lmb*100, dss)
                    )
                multi_scenario_plot(
                    output_dir,
                    ed,
                    xfield="controldelay",
                    yfield=["t_request_global", "t_request_local"],
                    destinction_field="backend",
                    rowfilter={
                        "numbermb": nmb,
                        "srclambda": lmb,
                        "dummystatesize": dss},
                    xname="control plane latency [ms]",
                    yname="state request delay [s]",
                    name_pre="",
                    name_post="_nmb%03d_l%03d_dss%08d" % (nmb, lmb*100, dss)
                    )
                multi_scenario_plot(
                    output_dir,
                    ed,
                    xfield="controldelay",
                    yfield=["t_request_global"],
                    destinction_field="backend",
                    rowfilter={
                        "numbermb": nmb,
                        "srclambda": lmb,
                        "dummystatesize": dss},
                    xname="control plane latency [ms]",
                    yname="avg. request delay [s]",
                    name_pre="",
                    name_post="_nmb%03d_l%03d_dss%08d" % (nmb, lmb*100, dss)
                    )
                multi_scenario_plot(
                    output_dir,
                    ed,
                    xfield="controldelay",
                    yfield=["pcount_global"],
                    destinction_field="backend",
                    rowfilter={
                        "numbermb": nmb,
                        "srclambda": lmb,
                        "dummystatesize": dss},
                    xname="control plane latency [ms]",
                    yname="number of processed packets",
                    name_pre="",
                    name_post="_nmb%03d_l%03d_dss%08d" % (nmb, lmb*100, dss)
                    )

    """
    Plots:
    xaxis = dummystatesize
    yaxis = pps, request times, global pcount
    layout: one plot line per backend
    """
    for nmb in middleboxes:
        for lmb in lambdas:
            for delay in cdelays[:2]:
                multi_scenario_plot(
                    output_dir,
                    ed,
                    xfield="dummystatesize",
                    yfield=["pps_global"],
                    destinction_field="backend",
                    rowfilter={
                        "numbermb": nmb,
                        "srclambda": lmb,
                        "controldelay": delay},
                    xname="state size [byte]",
                    yname="avg. packets/second",
                    name_pre="",
                    name_post="_nmb%03d_l%03d_d%03d" % (nmb, lmb*100, delay),
                    xlogscale=True
                    )
                multi_scenario_plot(
                    output_dir,
                    ed,
                    xfield="dummystatesize",
                    yfield=["t_request_global", "t_request_local"],
                    destinction_field="backend",
                    rowfilter={
                        "numbermb": nmb,
                        "srclambda": lmb,
                        "controldelay": delay},
                    xname="state size [byte]",
                    yname="avg. request delay [s]",
                    name_pre="",
                    name_post="_nmb%03d_l%03d_d%03d" % (nmb, lmb*100, delay),
                    xlogscale=True
                    )

if __name__ == '__main__':
    plot("../scaleability-fixed")
