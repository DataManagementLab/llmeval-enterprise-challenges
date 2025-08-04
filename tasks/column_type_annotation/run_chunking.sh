#!/bin/bash

set -e

# extract dataset name from command line input
for arg in "$@"; do
  if [[ $arg =~ dataset=([^[:space:]]+) ]]; then
    dataset="${BASH_REMATCH[1]}"
    break
  fi
done

python tasks/column_type_annotation/"$dataset"/preprocess.py "$@"
python tasks/column_type_annotation/create_chunking_instances.py "$@"
python tasks/column_type_annotation/prepare_requests.py "$@"
python tasks/execute_requests.py -cp "../config/column_type_annotation" "$@"
python tasks/column_type_annotation/parse_responses.py "$@"
python tasks/column_type_annotation/evaluate.py "$@"
