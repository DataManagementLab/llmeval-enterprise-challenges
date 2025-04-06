#!/bin/bash

set -e

# extract dataset name from command line input
for arg in "$@"; do
  if [[ $arg =~ dataset=([^[:space:]]+) ]]; then
    dataset="${BASH_REMATCH[1]}"
    break
  fi
done

python tasks/text2signal/"$dataset"/preprocess.py "$@"
python tasks/text2signal/prepare_requests.py "$@"
python tasks/execute_requests.py -cp "../config/text2signal" "$@"
python tasks/text2signal/parse_responses.py "$@"
python tasks/text2signal/evaluate.py "$@"
