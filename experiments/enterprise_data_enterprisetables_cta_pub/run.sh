#!/bin/bash

set -e

limit_instances=200

use_inst_all_column_types=false
num_inst_all_column_types=0
max_tokens_over_ground_truth=100

dataset="enterprisetables_cta_pub"

models=(
"gpt-4o-mini-2024-07-18"
"gpt-4o-2024-08-06"
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

for model in "${models[@]}"; do
  if [ "$dataset" = "enterprisetables_cta" ]; then
    api_name="${enterprise_api_names[${model}]}"
    use_inst_all_column_types=true
    num_inst_all_column_types=200
    max_tokens_over_ground_truth=null
  else
    if [ "$dataset" = "enterprisetables_cta_pub" ]; then
      api_name="${api_names[${model}]}"
      max_tokens_over_ground_truth=null
      limit_instances=100
    else
      api_name="${api_names[${model}]}"
    fi
  fi

  ######################################################################################################################
  # Large table widths
  ######################################################################################################################

  bash tasks/column_type_annotation/run.sh \
    exp_name="enterprise-data-enterprisetables-cta-pub_${model}_c1-large-table-widths_with-headers" \
    dataset="$dataset" \
    dataset.adapt_width=true \
    limit_instances="$limit_instances" \
    api_name="$api_name" \
    model="$model" \
    use_inst_all_column_types="$use_inst_all_column_types" \
    num_inst_all_column_types="$num_inst_all_column_types" \
    max_tokens_over_ground_truth="$max_tokens_over_ground_truth"

  bash tasks/column_type_annotation/run.sh \
    exp_name="enterprise-data-enterprisetables-cta-pub_${model}_c1-large-table-widths_without-headers" \
    dataset="$dataset" \
    dataset.adapt_width=true \
    limit_instances="$limit_instances" \
    api_name="$api_name" \
    model="$model" \
    use_inst_all_column_types="$use_inst_all_column_types" \
    num_inst_all_column_types="$num_inst_all_column_types" \
    max_tokens_over_ground_truth="$max_tokens_over_ground_truth" \
    linearize_table.csv_params.header=false \
    'linearize_table.template="{{table}}"'

  ######################################################################################################################
  # High sparsity
  ######################################################################################################################

  bash tasks/column_type_annotation/run.sh \
    exp_name="enterprise-data-enterprisetables-cta-pub_${model}_c2-high-sparsity_with-headers" \
    dataset="$dataset" \
    dataset.adapt_sparsity=true \
    limit_instances="$limit_instances" \
    api_name="$api_name" \
    model="$model" \
    use_inst_all_column_types="$use_inst_all_column_types" \
    num_inst_all_column_types="$num_inst_all_column_types" \
    max_tokens_over_ground_truth="$max_tokens_over_ground_truth"

  bash tasks/column_type_annotation/run.sh \
    exp_name="enterprise-data-enterprisetables-cta-pub_${model}_c2-high-sparsity_without-headers" \
    dataset="$dataset" \
    dataset.adapt_sparsity=true \
    limit_instances="$limit_instances" \
    api_name="$api_name" \
    model="$model" \
    use_inst_all_column_types="$use_inst_all_column_types" \
    num_inst_all_column_types="$num_inst_all_column_types" \
    max_tokens_over_ground_truth="$max_tokens_over_ground_truth" \
    linearize_table.csv_params.header=false \
    'linearize_table.template="{{table}}"'

  ######################################################################################################################
  # Low descriptiveness
  ######################################################################################################################

  bash tasks/column_type_annotation/run.sh \
    exp_name="enterprise-data-enterprisetables-cta-pub_${model}_c3-low-descriptiveness_with-headers" \
    dataset="$dataset" \
    dataset.adapt_descriptiveness=true \
    limit_instances="$limit_instances" \
    api_name="$api_name" \
    model="$model" \
    use_inst_all_column_types="$use_inst_all_column_types" \
    num_inst_all_column_types="$num_inst_all_column_types" \
    max_tokens_over_ground_truth="$max_tokens_over_ground_truth"

  bash tasks/column_type_annotation/run.sh \
    exp_name="enterprise-data-enterprisetables-cta-pub_${model}_c3-low-descriptiveness_without-headers" \
    dataset="$dataset" \
    dataset.adapt_descriptiveness=true \
    limit_instances="$limit_instances" \
    api_name="$api_name" \
    model="$model" \
    use_inst_all_column_types="$use_inst_all_column_types" \
    num_inst_all_column_types="$num_inst_all_column_types" \
    max_tokens_over_ground_truth="$max_tokens_over_ground_truth" \
    linearize_table.csv_params.header=false \
    'linearize_table.template="{{table}}"'

  ######################################################################################################################
  # Complex data types
  ######################################################################################################################

  bash tasks/column_type_annotation/run.sh \
    exp_name="enterprise-data-enterprisetables-cta-pub_${model}_c4-complex-data-types_with-headers" \
    dataset="$dataset" \
    dataset.adapt_data_types=true \
    limit_instances="$limit_instances" \
    api_name="$api_name" \
    model="$model" \
    use_inst_all_column_types="$use_inst_all_column_types" \
    num_inst_all_column_types="$num_inst_all_column_types" \
    max_tokens_over_ground_truth="$max_tokens_over_ground_truth"

  bash tasks/column_type_annotation/run.sh \
    exp_name="enterprise-data-enterprisetables-cta-pub_${model}_c4-complex-data-types_without-headers" \
    dataset="$dataset" \
    dataset.adapt_data_types=true \
    limit_instances="$limit_instances" \
    api_name="$api_name" \
    model="$model" \
    use_inst_all_column_types="$use_inst_all_column_types" \
    num_inst_all_column_types="$num_inst_all_column_types" \
    max_tokens_over_ground_truth="$max_tokens_over_ground_truth" \
    linearize_table.csv_params.header=false \
    'linearize_table.template="{{table}}"'

  ######################################################################################################################
  # All challenges
  ######################################################################################################################

  bash tasks/column_type_annotation/run.sh \
    exp_name="enterprise-data-enterprisetables-cta-pub_${model}_all-challenges_with-headers" \
    dataset="$dataset" \
    dataset.adapt_width=true \
    dataset.adapt_sparsity=true \
    dataset.adapt_descriptiveness=true \
    dataset.adapt_data_types=true \
    limit_instances="$limit_instances" \
    api_name="$api_name" \
    model="$model" \
    use_inst_all_column_types="$use_inst_all_column_types" \
    num_inst_all_column_types="$num_inst_all_column_types" \
    max_tokens_over_ground_truth="$max_tokens_over_ground_truth"

  bash tasks/column_type_annotation/run.sh \
    exp_name="enterprise-data-enterprisetables-cta-pub_${model}_all-challenges_without-headers" \
    dataset="$dataset" \
    dataset.adapt_width=true \
    dataset.adapt_sparsity=true \
    dataset.adapt_descriptiveness=true \
    dataset.adapt_data_types=true \
    limit_instances="$limit_instances" \
    api_name="$api_name" \
    model="$model" \
    use_inst_all_column_types="$use_inst_all_column_types" \
    num_inst_all_column_types="$num_inst_all_column_types" \
    max_tokens_over_ground_truth="$max_tokens_over_ground_truth" \
    linearize_table.csv_params.header=false \
    'linearize_table.template="{{table}}"'
done

python experiments/enterprise_data_enterprisetables_cta_pub/gather.py
