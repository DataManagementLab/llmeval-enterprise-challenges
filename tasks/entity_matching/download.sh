#!/bin/bash

set -e

datasets=("pay_to_inv")

for dataset in "${datasets[@]}"; do
  python tasks/entity_matching/$dataset/download.py dataset=$dataset
done