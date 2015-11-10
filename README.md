# estate
State management framework for elastic deployments of stateful VNFs.

Questions: manuel.peuster [a-t] uni-paderborn [d-o-t] . de

Basic documentation: [https://github.com/mpeuster/estate/wiki]

## Requirements

### Environment
* running Mininet installation
* gcc / g++ > 4.8.1 installed

### Packages
* `sudo apt-get install libzmq3`
* `sudo apt-get install libzmq3-dev`
* `sudo apt-get install bridge-utils`
* `sudo apt-get install iperf`

### Python:
* `sudo pip install zmq`
* `sudo pip install redis`
* `sudo pip install redis-py-cluster`
* `sudo pip install cassandra-driver`

### C++:
* `git clone https://github.com/zeromq/zmqpp`
 * `make & make install`

### Redis:
* http://redis.io/download

### Cassandra:
* TODO


#### Setup `.bashrc`
* export PATH="$PATH:$HOME/estate/cppesnode/Debug/:$HOME/redis-3.0.4/src/"
* export PYTHONPATH="$HOME/estate:$PYTHONPATH"
* export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$HOME/estate/libestatepp/Debug:/usr/local/lib
* export CPLUS_INCLUDE_PATH=$CPLUS_INCLUDE_PATH:$HOME/estate/libestatepp/src/

If ld error occurs: Hardlink the lib: `sudo ln libestatepp.so /lib/libestatepp.so`

## Built
* `estate/libestatepp/Debug$ make all`
* `estate/cppesnode/Debug$ make all`

## Experiments
### Folder Structure

* experiment-name/
	* mininet-environment/
		- topology.py (mininet script for a single experiment)
		- logs/ (folder with outputs of one exeriment)
	* pox/
		- upb/ (sdn scripts)
	* evaluation
		- plot.py
		- figures/
	* results/
		- scenario_name1/ (copy of log folder from one run)
		- scenario_name2/
		- ...
	* start_mininet.sh (debugging)
	* start_pox.sh (defines which sdn cript is used)
	* experiment.py (central run script)


### Run an Experiment

In experiment folder:

`sudo python experiment.py`

### Run Tests:
* `python test` (in root directory)
 * use `python test 1-3` to select which kind of implementation to test
 * Attention: You have to run local Cassandra / Redis instances in order to run the corresponding test cases.

