#!/bin/bash

set -e

limit_instances=200

use_inst_all_column_types=false
num_inst_all_column_types=0
max_tokens_over_ground_truth=100

datasets=(
"enterprisetables_cta"
"gittablesCTA"
"sportstables"
)
models=(
"gpt-4o-mini-2024-07-18"
"gpt-4o-2024-08-06"
"claude-3-5-sonnet-20241022"
"llama3.1:70b-instruct-fp16"
)

declare -A api_names
api_names["gpt-4o-mini-2024-07-18"]="openai"
api_names["gpt-4o-2024-08-06"]="openai"
api_names["claude-3-5-haiku-20241022"]="anthropic"
api_names["claude-3-5-sonnet-20241022"]="anthropic"
api_names["claude-3-5-sonnet-20240620"]="anthropic"
api_names["llama3.1:8b-instruct-fp16"]="ollama"
api_names["llama3.1:70b-instruct-fp16"]="ollama"

declare -A enterprise_api_names
enterprise_api_names["gpt-4o-mini-2024-07-18"]="aicore"
enterprise_api_names["gpt-4o-2024-08-06"]="aicore"
enterprise_api_names["claude-3-5-haiku-20241022"]="aicore"
enterprise_api_names["claude-3-5-sonnet-20241022"]="aicore"
enterprise_api_names["claude-3-5-sonnet-20240620"]="aicore"
enterprise_api_names["llama3.1:8b-instruct-fp16"]="aicore"
enterprise_api_names["llama3.1:70b-instruct-fp16"]="aicore"

for dataset in "${datasets[@]}"; do
  for model in "${models[@]}"; do
    if [ "$dataset" = "enterprisetables_cta" ]; then
      api_name="${enterprise_api_names[${model}]}"
      use_inst_all_column_types=true
      num_inst_all_column_types=200
      max_tokens_over_ground_truth=null
      python tasks/column_type_annotation/enterprisetables_cta/analyze.py dataset="$dataset"
    else
      api_name="${api_names[${model}]}"
    fi

    bash tasks/column_type_annotation/run.sh \
      exp_name="enterprise-data-headers-types-cta_${model}_with-headers" \
      dataset="$dataset" \
      limit_instances="$limit_instances" \
      api_name="$api_name" \
      model="$model" \
      use_inst_all_column_types="$use_inst_all_column_types" \
      num_inst_all_column_types="$num_inst_all_column_types" \
      max_tokens_over_ground_truth="$max_tokens_over_ground_truth"

    bash tasks/column_type_annotation/run.sh \
      exp_name="enterprise-data-headers-types-cta_${model}_without-headers" \
      dataset="$dataset" \
      limit_instances="$limit_instances" \
      api_name="$api_name" \
      model="$model" \
      use_inst_all_column_types="$use_inst_all_column_types" \
      num_inst_all_column_types="$num_inst_all_column_types" \
      max_tokens_over_ground_truth="$max_tokens_over_ground_truth" \
      linearize_table.csv_params.header=false \
      'linearize_table.template="{{table}}"'
  done
done

python experiments/enterprise_data_headers_types_cta/gather.py
python experiments/enterprise_data_headers_types_cta/plot.py
