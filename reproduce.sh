#!/bin/bash

set -e

if [ ! -d "data/openai_cache" ]; then
    echo "for exact reproducibility, you must manually obtain \`data/openai_cache\`!"
    exit 1
fi
if [ ! -d "data/anthropic_cache" ]; then
    echo "for exact reproducibility, you must manually obtain \`data/anthropic_cache\`!"
    exit 1
fi
if [ ! -d "data/ollama_cache" ]; then
    echo "for exact reproducibility, you must manually obtain \`data/ollama_cache\`!"
    exit 1
fi
if [ ! -d "data/aicore_cache" ]; then
    echo "for exact reproducibility, you must manually obtain \`data/aicore_cache\`!"
    exit 1
fi

# download datasets
bash tasks/column_type_annotation/download.sh
bash tasks/compound_task/download.sh
bash tasks/entity_matching/download.sh
bash tasks/other_datasets/download.sh
bash tasks/schema_prediction/download.sh
bash tasks/text2signal/download.sh

# run experiments
bash experiments/enterprise_data_headers_types_cta/run.sh
bash experiments/enterprise_data_sparsity_width_cta/run.sh
bash experiments/enterprise_tasks_pay_to_inv/run.sh
bash experiments/enterprise_tasks_compound/run.sh
bash experiments/enterprise_knowledge_text2signal/run.sh
bash experiments/enterprise_knowledge_schema_prediction/run.sh
bash experiments/costs_imdb_wikipedia_enterprisetables/run.sh  # must run after the CTA experiments
bash experiments/enterprise_challenges_cta/run.sh  # must run after the CTA experiments
