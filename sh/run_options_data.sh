#!/bin/bash
ROOT=/home/larry-13.04/workspace/finopt
export PYTHONPATH=$ROOT/src
python $ROOT/src/finopt/options_data.py $ROOT/src/config/app.cfg
