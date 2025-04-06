#!/bin/bash

set -e

limit_instances=null

dataset="enterprisetables_cta"

models=(
"gpt-4o-mini-2024-07-18"
"gpt-4o-2024-08-06"
"claude-3-5-sonnet-20241022"
"llama3.1:70b-instruct-fp16"
)

declare -A enterprise_api_names
enterprise_api_names["gpt-4o-mini-2024-07-18"]="aicore"
enterprise_api_names["gpt-4o-2024-08-06"]="aicore"
enterprise_api_names["claude-3-5-haiku-20241022"]="aicore"
enterprise_api_names["claude-3-5-sonnet-20241022"]="aicore"
enterprise_api_names["llama3.1:8b-instruct-fp16"]="aicore"
enterprise_api_names["llama3.1:70b-instruct-fp16"]="aicore"

for model in "${models[@]}"; do
  api_name="${enterprise_api_names[${model}]}"
  max_tokens_over_ground_truth=null
  num_inst_all_column_types=200
  use_inst_all_column_types=true
  filter_zzz_columns=false

  bash tasks/column_type_annotation/run.sh \
    exp_name="enterprise-challenges-cta_${model}_data" \
    dataset="$dataset" \
    limit_instances="$limit_instances" \
    api_name="$api_name" \
    model="$model" \
    use_inst_all_column_types="$use_inst_all_column_types" \
    num_inst_all_column_types="$num_inst_all_column_types" \
    max_tokens_over_ground_truth="$max_tokens_over_ground_truth" \
    filter_zzz_columns="$filter_zzz_columns"

  use_inst_all_column_types=false
  bash tasks/column_type_annotation/run.sh \
    exp_name="enterprise-challenges-cta_${model}_tasks" \
    dataset="$dataset" \
    limit_instances="$limit_instances" \
    api_name="$api_name" \
    model="$model" \
    use_inst_all_column_types="$use_inst_all_column_types" \
    num_inst_all_column_types="$num_inst_all_column_types" \
    max_tokens_over_ground_truth="$max_tokens_over_ground_truth" \
    filter_zzz_columns="$filter_zzz_columns"

  filter_zzz_columns=true
  bash tasks/column_type_annotation/run.sh \
    exp_name="enterprise-challenges-cta_${model}_knowledge" \
    dataset="$dataset" \
    limit_instances="$limit_instances" \
    api_name="$api_name" \
    model="$model" \
    use_inst_all_column_types="$use_inst_all_column_types" \
    num_inst_all_column_types="$num_inst_all_column_types" \
    max_tokens_over_ground_truth="$max_tokens_over_ground_truth" \
    filter_zzz_columns="$filter_zzz_columns"
done

python experiments/enterprise_challenges_cta/gather.py
read -rp "manually copy the CTA results from SportsTables into \`f1_scores.csv\` as column \`sportstables/public\`, then press enter"
python experiments/enterprise_challenges_cta/plot.py
