#!/bin/bash

set -e

limit_instances=200
limit_instances_lookup=500
limit_instances_chunking=500

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

task_modes=(
"all"
"lookup-index"
"lookup-header"
"chunking"
)

chunk_sizes=(
"1"
"10"
"20"
"50"
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

for dataset in "${datasets[@]}"; do
  for model in "${models[@]}"; do
    for task_mode in "${task_modes[@]}"; do
      if [ "$dataset" = "enterprisetables_cta" ]; then
        api_name="${enterprise_api_names[${model}]}"
        use_inst_all_column_types=true
        num_inst_all_column_types=200
        max_tokens_over_ground_truth=null
      else
        api_name="${api_names[${model}]}"
      fi

      if [[ "$task_mode" = "lookup-index" || "$task_mode" = "lookup-header" ]]; then
        bash tasks/column_type_annotation/run_lookup.sh \
          exp_name="enterprise-data-task-mode-ablations-cta_${model}_with-headers_${task_mode}" \
          dataset="$dataset" \
          limit_instances="$limit_instances_lookup" \
          api_name="$api_name" \
          model="$model" \
          use_inst_all_column_types="$use_inst_all_column_types" \
          num_inst_all_column_types="$num_inst_all_column_types" \
          max_tokens_over_ground_truth="$max_tokens_over_ground_truth" \
          task_mode="$task_mode" \
          'prompt_chat_template.0.content="Predict the column type of the specified column. Provide just the column type without any introduction or explanation.{{newline}}Column types are: {{all_column_types}}"' \
          'prompt_chat_template.2.content="Predict the column type of the column {{lookup}}!{{newline}}{{newline}}{{table}}"' \
          'example_chat_template.0.content="Predict the column type of the column {{lookup}}!{{newline}}{{newline}}{{table}}"' \
          'example_chat_template.1.content="{{column_type}}"'

        bash tasks/column_type_annotation/run_lookup.sh \
          exp_name="enterprise-data-task-mode-ablations-cta_${model}_without-headers_${task_mode}" \
          dataset="$dataset" \
          limit_instances="$limit_instances_lookup" \
          api_name="$api_name" \
          model="$model" \
          use_inst_all_column_types="$use_inst_all_column_types" \
          num_inst_all_column_types="$num_inst_all_column_types" \
          max_tokens_over_ground_truth="$max_tokens_over_ground_truth" \
          task_mode="$task_mode" \
          'prompt_chat_template.0.content="Predict the column type of the specified column. Provide just the column type without any introduction or explanation.{{newline}}Column types are: {{all_column_types}}"' \
          'prompt_chat_template.2.content="Predict the column type of the column {{lookup}}!{{newline}}{{newline}}{{table}}"' \
          'example_chat_template.0.content="Predict the column type of the column {{lookup}}!{{newline}}{{newline}}{{table}}"' \
          'example_chat_template.1.content="{{column_type}}"' \
          linearize_table.csv_params.header=false \
          'linearize_table.template="{{table}}"'
      else
        if [ "$task_mode" = "all" ]; then
          bash tasks/column_type_annotation/run.sh \
            exp_name="enterprise-data-task-mode-ablations-cta_${model}_with-headers_${task_mode}" \
            dataset="$dataset" \
            limit_instances="$limit_instances" \
            api_name="$api_name" \
            model="$model" \
            use_inst_all_column_types="$use_inst_all_column_types" \
            num_inst_all_column_types="$num_inst_all_column_types" \
            max_tokens_over_ground_truth="$max_tokens_over_ground_truth" \
            task_mode="$task_mode"

          bash tasks/column_type_annotation/run.sh \
            exp_name="enterprise-data-task-mode-ablations-cta_${model}_without-headers_${task_mode}" \
            dataset="$dataset" \
            limit_instances="$limit_instances" \
            api_name="$api_name" \
            model="$model" \
            use_inst_all_column_types="$use_inst_all_column_types" \
            num_inst_all_column_types="$num_inst_all_column_types" \
            max_tokens_over_ground_truth="$max_tokens_over_ground_truth" \
            task_mode="$task_mode" \
            linearize_table.csv_params.header=false \
            'linearize_table.template="{{table}}"'
        else
          if [ "$task_mode" = "chunking" ]; then
            for chunk_size in "${chunk_sizes[@]}"; do
              bash tasks/column_type_annotation/run_chunking.sh \
                exp_name="enterprise-data-task-mode-ablations-cta_${model}_with-headers_${task_mode}_${chunk_size}" \
                dataset="$dataset" \
                limit_instances="$limit_instances" \
                api_name="$api_name" \
                model="$model" \
                use_inst_all_column_types="$use_inst_all_column_types" \
                num_inst_all_column_types="$num_inst_all_column_types" \
                max_tokens_over_ground_truth="$max_tokens_over_ground_truth" \
                task_mode="$task_mode" \
                chunk_size="$chunk_size" \
                limit_instances_chunking="$limit_instances_chunking"

              bash tasks/column_type_annotation/run_chunking.sh \
                exp_name="enterprise-data-task-mode-ablations-cta_${model}_without-headers_${task_mode}_${chunk_size}" \
                dataset="$dataset" \
                limit_instances="$limit_instances" \
                api_name="$api_name" \
                model="$model" \
                use_inst_all_column_types="$use_inst_all_column_types" \
                num_inst_all_column_types="$num_inst_all_column_types" \
                max_tokens_over_ground_truth="$max_tokens_over_ground_truth" \
                task_mode="$task_mode" \
                chunk_size="$chunk_size" \
                limit_instances_chunking="$limit_instances_chunking" \
                linearize_table.csv_params.header=false \
                'linearize_table.template="{{table}}"'
            done
          else
            echo "skip unknown task_mode"
          fi
        fi
      fi
    done
  done
done

python experiments/enterprise_data_task_mode_ablations_cta/gather.py
