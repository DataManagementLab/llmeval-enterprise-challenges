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
)

runs=(
"1"
"2"
"3"
)

declare -A api_names
api_names["gpt-4o-mini-2024-07-18"]="openai"
api_names["gpt-4o-2024-08-06"]="openai"
api_names["claude-3-5-sonnet-20241022"]="anthropic"
api_names["claude-3-5-sonnet-20240620"]="anthropic"
api_names["llama3.1:70b-instruct-fp16"]="ollama"

declare -A enterprise_api_names
enterprise_api_names["gpt-4o-mini-2024-07-18"]="aicore"
enterprise_api_names["gpt-4o-2024-08-06"]="aicore"
enterprise_api_names["claude-3-5-sonnet-20240620"]="aicore"
enterprise_api_names["llama3.1:70b-instruct-fp16"]="aicore"

if [[ -d "data/aicore_cache" || -d "data/openai_cache" || -d "data/anthropic_cache" || -d "data/ollama_cache" ]]; then
    echo "please back up (move) the llm cache directories before executing this script"
    exit 1
else
  echo "proceed"
fi

for dataset in "${datasets[@]}"; do
  for model in "${models[@]}"; do
    for run in "${runs[@]}"; do
      if [ "$dataset" = "enterprisetables_cta" ]; then
        api_name="${enterprise_api_names[${model}]}"
        use_inst_all_column_types=true
        num_inst_all_column_types=200
        max_tokens_over_ground_truth=null
      else
        api_name="${api_names[${model}]}"
      fi

      bash tasks/column_type_annotation/run.sh \
        exp_name="enterprise-data-variability-ablations-cta_${model}_with-headers_${run}" \
        dataset="$dataset" \
        limit_instances="$limit_instances" \
        api_name="$api_name" \
        model="$model" \
        use_inst_all_column_types="$use_inst_all_column_types" \
        num_inst_all_column_types="$num_inst_all_column_types" \
        max_tokens_over_ground_truth="$max_tokens_over_ground_truth"

      if [[ -d "data/aicore_cache" ]]; then
        rm -r data/aicore_cache
      else
        echo "no aicore_cache to delete"
      fi

      if [[ -d "data/openai_cache" ]]; then
        rm -r data/openai_cache
      else
        echo "no openai_cache to delete"
      fi

      if [[ -d "data/anthropic_cache" ]]; then
        rm -r data/anthropic_cache
      else
        echo "no anthropic_cache to delete"
      fi

      if [[ -d "data/ollama_cache" ]]; then
        rm -r data/ollama_cache
      else
        echo "no ollama_cache to delete"
      fi

      bash tasks/column_type_annotation/run.sh \
        exp_name="enterprise-data-variability-ablations-cta_${model}_without-headers_${run}" \
        dataset="$dataset" \
        limit_instances="$limit_instances" \
        api_name="$api_name" \
        model="$model" \
        use_inst_all_column_types="$use_inst_all_column_types" \
        num_inst_all_column_types="$num_inst_all_column_types" \
        max_tokens_over_ground_truth="$max_tokens_over_ground_truth" \
        linearize_table.csv_params.header=false \
        'linearize_table.template="{{table}}"'

      if [[ -d "data/aicore_cache" ]]; then
        rm -r data/aicore_cache
      else
        echo "no aicore_cache to delete"
      fi

      if [[ -d "data/openai_cache" ]]; then
        rm -r data/openai_cache
      else
        echo "no openai_cache to delete"
      fi

      if [[ -d "data/anthropic_cache" ]]; then
        rm -r data/anthropic_cache
      else
        echo "no anthropic_cache to delete"
      fi

      if [[ -d "data/ollama_cache" ]]; then
        rm -r data/ollama_cache
      else
        echo "no ollama_cache to delete"
      fi
    done
  done
done

python experiments/enterprise_data_variability_ablations_cta/gather.py
