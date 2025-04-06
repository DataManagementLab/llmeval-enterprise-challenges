#!/bin/bash

set -e

limit_instances=2000
models=("gpt-4o-mini-2024-07-18")

for model in "${models[@]}"; do
      bash tasks/schema_prediction/run.sh \
        exp_name="enterprise-knowledge-schema-prediction_${model}" \
        dataset="enterprisetables" \
        api_name="aicore" \
        model="$model" \
        limit_instances="$limit_instances"
done

python experiments/enterprise_knowledge_schema_prediction/gather.py
python experiments/enterprise_knowledge_schema_prediction/plot.py
