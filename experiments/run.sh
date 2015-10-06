#!/bin/bash

cd simple-poc-comparisson; python experiment.py
sleep 30
mn -c
cd ..
sleep 30
cd scaleability-fixed; python experiment.py
sleep 30
mn -c
cd ..
sleep 30
#cd scaleability-dynamic; python experiment.py
sleep 30
mn -c
cd ..

