#!/bin/bash

set -e

python experiments/enterprise_costs/run.py
python experiments/enterprise_costs/count_cells.py
