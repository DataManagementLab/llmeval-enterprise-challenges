#!/bin/bash

set -e

datasets=("imdb" "wikipedia" "narayan")

for dataset in "${datasets[@]}"; do
  python tasks/other_datasets/$dataset/download.py dataset=$dataset
done