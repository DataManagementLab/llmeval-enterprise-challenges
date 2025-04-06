#!/bin/bash

set -e

datasets=("signavio")

for dataset in "${datasets[@]}"; do
  if [ "$dataset" == "signavio" ]; then
        if [ ! -d "data/text2signal/signavio/download" ]; then
            echo "for exact reproducibility, you must manually obtain \`data/text2signal/signavio/download\`"
            exit 1
        fi
    else
      python tasks/text2signal/$dataset/download.py dataset=$dataset
    fi
done