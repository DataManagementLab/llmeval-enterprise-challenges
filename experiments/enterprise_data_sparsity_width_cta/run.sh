#!/bin/bash

set -e

limit_instances=null

use_inst_all_column_types=true
num_inst_all_column_types=200
max_tokens_over_ground_truth=null

dataset="enterprisetables_cta"

models=(
"gpt-4o-mini-2024-07-18"
"gpt-4o-2024-08-06"
"claude-3-5-sonnet-20240620"
"llama3.1:70b-instruct-fp16"
)

declare -A enterprise_api_names
enterprise_api_names["gpt-4o-mini-2024-07-18"]="aicore"
enterprise_api_names["gpt-4o-2024-08-06"]="aicore"
enterprise_api_names["claude-3-5-sonnet-20240620"]="aicore"
enterprise_api_names["llama3.1:70b-instruct-fp16"]="aicore"

########################################################################################################################
# run ablation for sparsity
########################################################################################################################

for model in "${models[@]}"; do
  api_name="${enterprise_api_names[${model}]}"

  bash tasks/column_type_annotation/run.sh \
    exp_name="enterprise-data-sparsity-width-cta_${model}_with-headers_sparsity" \
    dataset="$dataset" \
    limit_instances="$limit_instances" \
    api_name="$api_name" \
    model="$model" \
    use_inst_all_column_types="$use_inst_all_column_types" \
    num_inst_all_column_types="$num_inst_all_column_types" \
    max_tokens_over_ground_truth="$max_tokens_over_ground_truth" \
    dataset.sparsify=true

  bash tasks/column_type_annotation/run.sh \
    exp_name="enterprise-data-sparsity-width-cta_${model}_without-headers_sparsity" \
    dataset="$dataset" \
    limit_instances="$limit_instances" \
    api_name="$api_name" \
    model="$model" \
    use_inst_all_column_types="$use_inst_all_column_types" \
    num_inst_all_column_types="$num_inst_all_column_types" \
    max_tokens_over_ground_truth="$max_tokens_over_ground_truth" \
    linearize_table.csv_params.header=false \
    'linearize_table.template="{{table}}"' \
    dataset.sparsify=true
done

########################################################################################################################
# run ablation for table width
########################################################################################################################

for model in "${models[@]}"; do
  api_name="${enterprise_api_names[${model}]}"

  bash tasks/column_type_annotation/run.sh \
    exp_name="enterprise-data-sparsity-width-cta_${model}_with-headers_num_columns" \
    dataset="$dataset" \
    limit_instances="$limit_instances" \
    api_name="$api_name" \
    model="$model" \
    use_inst_all_column_types="$use_inst_all_column_types" \
    num_inst_all_column_types="$num_inst_all_column_types" \
    max_tokens_over_ground_truth="$max_tokens_over_ground_truth" \
    dataset.sample_columns=true

  bash tasks/column_type_annotation/run.sh \
    exp_name="enterprise-data-sparsity-width-cta_${model}_without-headers_num_columns" \
    dataset="$dataset" \
    limit_instances="$limit_instances" \
    api_name="$api_name" \
    model="$model" \
    use_inst_all_column_types="$use_inst_all_column_types" \
    num_inst_all_column_types="$num_inst_all_column_types" \
    max_tokens_over_ground_truth="$max_tokens_over_ground_truth" \
    linearize_table.csv_params.header=false \
    'linearize_table.template="{{table}}"' \
    dataset.sample_columns=true
done

python experiments/enterprise_data_sparsity_width_cta/gather.py
python experiments/enterprise_data_sparsity_width_cta/plot.py
