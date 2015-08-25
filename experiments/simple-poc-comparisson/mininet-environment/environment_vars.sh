#!/bin/baash

# This file contains environment variables which are set on each 
# Mininet host.

# PATH
export PATH="$PATH:$HOME/estate/cppesnode/Debug/"
export PATH="$PATH:$HOME/cassandra/bin/"
export PATH="$PATH:$HOME/redis-3.0.0/src/"

# PYTHON
export PYTHONPATH="$HOME/estate:$PYTHONPATH"

# LIBS
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$HOME/estate/libestate/Debug/:$HOME/estate/libestatepp/Debug/:/usr/local/lib
