#!/bin/bash

cd pox; ./pox.py log.level --DEBUG upb.path_change_switch #> ../mininet-environment/log/pox.log 2>&1 &