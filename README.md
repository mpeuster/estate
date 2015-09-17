# estate
State management framework for elastic deployments of stateful VNFs.

Questions: manuel.peuster [a-t] uni-paderborn [d-o-t] . de

Basic documentation: [https://github.com/mpeuster/estate/wiki]

## Experiment Folder Structure

* experiment-name/
** mininet-environment/
*** topology.py (mininet script for a single experiment)
*** logs/ (folder with outputs of one exeriment)
** pox/
*** upb/ (sdn scripts)
** evaluation
*** plot.py
*** figures/
** results/
*** scenario_name1/ (copy of log folder from one run)
*** scenario_name2/
*** ...
** start_mininet.sh (debugging)
** start_pox.sh (defines which sdn cript is used)
** experiment.py (central run script)


## Run an Experiment

In experiment folder:

`sudo python experiment.py`


