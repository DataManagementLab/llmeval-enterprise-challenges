#!/bin/bash

set -e

python experiments/costs_imdb_wikipedia_enterprisetables/run.py
python experiments/costs_imdb_wikipedia_enterprisetables/count_cells.py
