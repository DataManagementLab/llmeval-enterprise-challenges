#!/bin/bash

set -e

# extract dataset name from command line input
for arg in "$@"; do
  if [[ $arg =~ dataset=([^[:space:]]+) ]]; then
    dataset="${BASH_REMATCH[1]}"
    break
  fi
done

python tasks/entity_matching/"$dataset"/preprocess.py "$@"
python tasks/entity_matching/prepare_requests.py "$@"
python tasks/execute_requests.py -cp "../config/entity_matching" "$@"
python tasks/entity_matching/parse_responses.py "$@"
python tasks/entity_matching/evaluate.py "$@"
