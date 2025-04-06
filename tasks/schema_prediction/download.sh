#!/bin/bash

set -e

datasets=("enterprisetables")

for dataset in "${datasets[@]}"; do
  if [ "$dataset" == "enterprisetables" ]; then
        if [ ! -d "data/schema_prediction/enterprisetables/download" ]; then
            echo "for exact reproducibility, you must manually obtain \`data/schema_prediction/enterprisetables/download\`"
            exit 1
        fi
    else
      python tasks/schema_prediction/$dataset/download.py dataset=$dataset
    fi
done