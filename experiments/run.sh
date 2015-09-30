#!/bin/bash

cd simple-poc-comparisson; python experiment.py
cd ..;
cd scaleability-fixed; python experiment.py
cd ..;
#cd scaleability-dynamic; python experiment.py
#cd ..;

