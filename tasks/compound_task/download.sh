#!/bin/bash

set -e

datasets=("customer_integration")

for dataset in "${datasets[@]}"; do
  if [ "$dataset" == "customer_integration" ]; then
    if [ ! -d "data/compound_task/customer_integration/download" ]; then
        echo "for exact reproducibility, you must manually obtain \`data/compound_task/customer_integration/download\`"
        exit 1
    fi
  else
    python tasks/compound_task/$dataset/download.py dataset=$dataset
  fi
done