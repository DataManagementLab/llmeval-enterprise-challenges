#!/bin/bash

set -e

limit_instances=200
models=(
"gpt-4o-mini-2024-07-18"
"gpt-4o-2024-08-06"
"claude-3-5-sonnet-20241022"
"llama3.1:70b-instruct-fp16"
)
modes=(
"zero_shot"
"one_shot"
"few_shot"
"RAG"
"few_and_docu"
)

for model in "${models[@]}"; do
  for mode in "${modes[@]}"; do
      bash tasks/text2signal/run.sh \
        exp_name="enterprise-knowledge-text2signal_${model}_${mode}" \
        dataset="signavio" \
        api_name="aicore" \
        model="$model" \
        mode="$mode" \
        limit_instances="$limit_instances"
  done
done

python experiments/enterprise_knowledge_text2signal/gather.py
python experiments/enterprise_knowledge_text2signal/plot.py
