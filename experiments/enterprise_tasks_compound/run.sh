#!/bin/bash

set -e

declare -A api_names
api_names["gpt-4o-mini-2024-07-18"]="openai"
api_names["gpt-4o-2024-08-06"]="openai"
api_names["o1-2024-12-17"]="openai"
api_names["claude-3-5-sonnet-20240620"]="anthropic"
api_names["claude-3-5-sonnet-20241022"]="anthropic"
api_names["llama3.1:70b-instruct-fp16"]="ollama"

# First execute the pipeline tasks with all models (apart from o1 due to high costs)

# Pipeline is 1) schema_matching 2) entity_matching 3) data_integration
# vs. end2end

models=(
"gpt-4o-mini-2024-07-18"
"gpt-4o-2024-08-06"
"claude-3-5-sonnet-20241022"
"llama3.1:70b-instruct-fp16"
)

sub_dataset="100_customers_0.6_overlap_0.8_discrepancies_0.2_altering"

subtasks=(
  "schema_matching"
  "entity_matching"
  "data_integration"
  "end2end"
)

for model in "${models[@]}"; do
  echo $model
  echo $sub_dataset
  for subtask in "${subtasks[@]}"; do
    echo $subtask
    python tasks/compound_task/customer_integration/${subtask}_preprocess.py \
      experiment="$subtask" \
      exp_name="${subtask}-${sub_dataset}-${model}" \
      dataset="customer_integration" \
      sub_dataset="$sub_dataset" \
      model="$model"

    python tasks/compound_task/${subtask}_prepare_requests.py \
      experiment="$subtask" \
      exp_name="${subtask}-${sub_dataset}-${model}" \
      dataset="customer_integration" \
      model="$model"

    python tasks/execute_requests.py -cp "../config/compound_task" \
      dataset="customer_integration" \
      experiment="$subtask" \
      exp_name="${subtask}-${sub_dataset}-${model}" \
      api_name="${api_names[${model}]}"

    python tasks/compound_task/${subtask}_evaluate.py \
      experiment="$subtask" \
      exp_name="${subtask}-${sub_dataset}-${model}" \
      dataset="customer_integration" \
      sub_dataset="$sub_dataset" \
      model="$model"
  done
done

# execute end2end scaling experiments with OpenAI o1:
model="o1-2024-12-17"
subtask="end2end"

sub_datasets=(
  "50_customers_0.6_overlap_0.8_discrepancies_0.2_altering"
  "100_customers_0.6_overlap_0.8_discrepancies_0.2_altering"
  "150_customers_0.6_overlap_0.8_discrepancies_0.2_altering"
  "200_customers_0.6_overlap_0.8_discrepancies_0.2_altering"
  "300_customers_0.6_overlap_0.8_discrepancies_0.2_altering"
)

python experiments/enterprise_tasks_compound/plot.py

for sub_dataset in "${sub_datasets[@]}"; do
  echo $sub_dataset
  python tasks/compound_task/customer_integration/${subtask}_preprocess.py \
    experiment="$subtask" \
    exp_name="${subtask}-${sub_dataset}-${model}" \
    dataset="customer_integration" \
    sub_dataset="$sub_dataset" \
    model="$model"

  python tasks/compound_task/${subtask}_prepare_requests.py \
    experiment="$subtask" \
    exp_name="${subtask}-${sub_dataset}-${model}" \
    dataset="customer_integration" \
    model="$model"

  python tasks/execute_requests.py -cp "../config/compound_task" \
    dataset="customer_integration" \
    experiment="$subtask" \
    exp_name="${subtask}-${sub_dataset}-${model}" \
    api_name="${api_names[${model}]}"

  python tasks/compound_task/${subtask}_evaluate.py \
    experiment="$subtask" \
    exp_name="${subtask}-${sub_dataset}-${model}" \
    dataset="customer_integration" \
    sub_dataset="$sub_dataset" \
    model="$model"
done