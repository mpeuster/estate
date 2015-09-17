import pylab
import matplotlib
matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42


mdata1 = None
mdata2 = None


def normalize_time():
    global mdata1
    global mdata2
    base = min(mdata1["time"] + mdata2["time"])
    mdata1["time"] = [ts - base for ts in mdata1["time"]]
    mdata2["time"] = [ts - base for ts in mdata2["time"]]
    print "Max time: %f" % max(mdata1["time"] + mdata2["time"])


def parse_line(l):
    ldata = {}
    parts = l.split(" ")
    for p in parts:
        if "#MON#" in p:
            continue
        k, v = p.split(":")
        if k == "flow":
            print v
        try:
            ldata[k] = float(v)
        except:
            ldata[k] = str(v)
    return ldata


def read_monitor_data(fname):
    """
    Structure: dict[fieldname] -> list(data)
    """
    data = {}
    for l in open(fname):
        l = l.strip()
        if "#MON#" not in l:
            continue  # skip debug lines
        # TODO remove
        if "flow_('10.0.0.2'" not in l:
            continue  # filter for single flow
        ldata = parse_line(l)
        for k, v in ldata.iteritems():
            if k not in data:
                data[k] = []
            data[k].append(v)
    return data


######################

def plot():
    global mdata1
    global mdata2

     # define to which figure we want to plot
    fig = pylab.figure()
    g1 = fig.add_subplot(211)
    g2 = fig.add_subplot(212)

    #line_colors = helper.get_line_color(True)
    #line_markers = helper.get_line_markers()
    #line_styles = helper.get_line_styles()

    # plot graphs
    # g1.plot(timestamps, aggr_wifi, color=next(line_colors), linewidth=1.0, alpha=1.0, label="Wi-Fi")
    # g1.plot(timestamps, aggr_mobile, color=next(line_colors), ls=next(line_styles), linewidth=1.0, alpha=1.0, label="Cellular")
    g1.plot(mdata1["time"], mdata1["m1count"], color="red", linewidth=0.0, alpha=1.0, marker="+", label="legacy")
    g2.plot(mdata2["time"], mdata2["m1count"], color="red", linewidth=0.0, alpha=1.0, marker="+", label="legacy")
    g1.plot(mdata1["time"], mdata1["gm1count"], color="blue", linewidth=0.0, alpha=1.0, marker="x", label="elastic state")
    g2.plot(mdata2["time"], mdata2["gm1count"], color="blue", linewidth=0.0, alpha=1.0, marker="x", label="elastic state")

    g1.plot([0, 120], [50,50], color="black", linewidth=1.0, alpha=1.0, ls="--", label="alarm threshold")
    g2.plot([0, 120], [50,50], color="black", linewidth=1.0, alpha=1.0, ls="--")

    g1.set_xlim([0, 120])
    g2.set_xlim([0, 120])

    g1.set_ylim([0, 70])
    g2.set_ylim([0, 70])
    
   # g1.set_xlabel("Time [s]")
    g1.set_ylabel("# matches on NF1")
    g1.legend(loc='upper right', fancybox=True, shadow=False, ncol=1)
    

    g2.set_xlabel("Time [s]")
    g2.set_ylabel("# matches on NF2")
    #g2.legend(loc='best', fancybox=True, shadow=False, ncol=1)
    #g2.legend(fancybox=True, shadow=False,bbox_to_anchor=(0., -0.12, 1., .102), loc=3,ncol=2, mode="expand", borderaxespad=0.)

    #pylab.title("...")
    fig.suptitle("Pattern matches on both NF instances", fontsize=14)

    #g = matplotlib.pyplot.gcf()
    fig.set_size_inches(7, 4)
    pylab.savefig(
        'graphs/plot_detectionlevel.pdf', bbox_inches='tight')

    # show on screen
    pylab.show()
    pylab.close()
    print "Plot done."

def main():
    global mdata1
    global mdata2
    mdata1 = read_monitor_data("data/monitor1.log")
    mdata2 = read_monitor_data("data/monitor2.log")

    normalize_time()
    #print mdata2
    plot()

if __name__ == '__main__':
    main()
