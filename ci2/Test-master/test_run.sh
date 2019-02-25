#!/bin/bash
/etc/init.d/ssh start
cd service
./run_output.sh
cd ../tools
python3 init_selfchecker.py
cd ../src/test
./run.sh $1