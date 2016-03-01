from plot import plot_single_scenario
from plot import plot_multi_scenario
import sys


def do_single_scenario_plots(exp_to_plot=["simple-poc-comparisson", "scale-down-hack"]):
    for e in exp_to_plot:
        print "=" * 70
        print "Plotting experiment: %s" % e
        print "=" * 70
        plot_single_scenario.plot(e)


def do_multi_scenario_plots(exp_to_plot=["scaleability-fixed"]):
    for e in exp_to_plot:
        print "=" * 70
        print "Plotting experiment: %s" % e
        print "=" * 70
        plot_multi_scenario.plot(e)


def main(args=None):
    if len(args) < 2:
        do_single_scenario_plots()
        do_multi_scenario_plots()
    else:
        if "-s" in args:
            do_single_scenario_plots()
        elif "-m" in args:
            do_multi_scenario_plots()
    print "I'am done. Be happy."


if __name__ == '__main__':
    main(sys.argv)
