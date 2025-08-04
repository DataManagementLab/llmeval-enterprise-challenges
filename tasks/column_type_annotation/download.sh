#!/bin/bash

set -e

datasets=("enterprisetables_cta" "sportstables" "wikitables-turl" "gittablesCTA" "sotab")

for dataset in "${datasets[@]}"; do
  if [ "$dataset" == "enterprisetables_cta" ]; then
      if [ ! -d "data/column_type_annotation/enterprisetables_cta/download" ]; then
          echo "for exact reproducibility, you must manually obtain \`data/column_type_annotation/enterprisetables_cta/download\`"
          exit 1
      fi
  elif [ "$dataset" == "sportstables" ]; then
    if [ ! -d "data/column_type_annotation/sportstables/download" ]; then
        echo "for exact reproducibility, you must manually obtain \`data/column_type_annotation/sportstables/download\`"
        exit 1
    fi
  elif [ "$dataset" == "enterprisetables_cta_pub" ]; then
    if [ ! -d "data/column_type_annotation/enterprisetables_cta_pub/download" ]; then
        echo "for exact reproducibility, you must manually obtain \`data/column_type_annotation/enterprisetables_cta_pub/download\`"
        exit 1
    fi
  elif [ "$dataset" == "wikitables-turl" ]; then
    if [ ! -d "data/column_type_annotation/wikitables-turl/download" ]; then
        echo "for exact reproducibility, you must manually obtain \`data/column_type_annotation/wikitables-turl/download\`"
        exit 1
    fi
  else
    python tasks/column_type_annotation/$dataset/download.py dataset=$dataset
  fi
done