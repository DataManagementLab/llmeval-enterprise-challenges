#!/bin/bash

set -e

# extract dataset name from command line input
for arg in "$@"; do
  if [[ $arg =~ dataset=([^[:space:]]+) ]]; then
    dataset="${BASH_REMATCH[1]}"
    break
  fi
done

python tasks/schema_prediction/"$dataset"/preprocess.py "$@"
python tasks/schema_prediction/prepare_requests.py "$@"
python tasks/execute_requests.py -cp "../config/schema_prediction" "$@"
python tasks/schema_prediction/parse_responses.py "$@"
python tasks/schema_prediction/evaluate.py "$@"
