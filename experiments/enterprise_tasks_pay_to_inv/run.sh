#!/bin/bash

set -e

limit_instances=2000

models=(
"gpt-4o-mini-2024-07-18"
"gpt-4o-2024-08-06"
"claude-3-5-sonnet-20241022"
"llama3.1:70b-instruct-fp16"
)

declare -A api_names
api_names["gpt-4o-mini-2024-07-18"]="openai"
api_names["gpt-4o-2024-08-06"]="openai"
api_names["claude-3-5-sonnet-20240620"]="anthropic"
api_names["claude-3-5-sonnet-20241022"]="anthropic"
api_names["llama3.1:70b-instruct-fp16"]="ollama"

schema_modes=(
# "descriptive" (not in the paper)
"opaque"
"multi-table"
)
perturbation_modes=(
"single"
"multi"
)

for model in "${models[@]}"; do
  for schema_mode in "${schema_modes[@]}"; do
    for perturbation_mode in "${perturbation_modes[@]}"; do
      if [[ "$perturbation_mode" = "single" && "$schema_mode" = "multi-table" ]]; then
        continue
      fi
      bash tasks/entity_matching/run.sh \
        exp_name="enterprise-tasks-pay-to-inv_${model}_${schema_mode}_${perturbation_mode}" \
        dataset="pay_to_inv" \
        api_name="${api_names[${model}]}" \
        model="$model" \
        limit_instances="$limit_instances" \
        dataset.schema_mode="$schema_mode" \
        dataset.perturbation_mode="$perturbation_mode"
    done
  done
done

python experiments/enterprise_tasks_pay_to_inv/gather.py
python experiments/enterprise_tasks_pay_to_inv/plot.py
python experiments/enterprise_tasks_pay_to_inv/determine_cost.py
