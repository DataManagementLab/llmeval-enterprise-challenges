# Unveiling Challenges for LLMs in Enterprise Data Engineering

**Large Language Models (LLMs) have demonstrated significant potential for automating data engineering tasks on tabular
data, giving enterprises a valuable opportunity to reduce the high costs associated with manual data handling. However,
the enterprise domain introduces unique challenges that existing LLM-based approaches for data engineering often
overlook, such as large table sizes, more complex tasks, and the need for internal knowledge. To bridge these gaps, we
identify key enterprise-specific challenges related to data, tasks, and background knowledge and conduct a comprehensive
study of their impact on recent LLMs for data engineering. Our analysis reveals that LLMs face substantial limitations
in real-world enterprise scenarios, resulting in significant accuracy drops. Our findings contribute to a systematic
understanding of LLMs for enterprise data engineering to support their adoption in industry.**

## Data Availability & Reproducibility

### Column Type Annotation

We publish an adapted version of the [SportsTables](https://github.com/DHBWMosbachWI/SportsTables) dataset where we
introduce all enterprise data challenges (C1-C4) from the paper. The dataset consists of 100 tables annotated with
semantic column types. We publish five versions of it: one for each of the challenges C1-C4 and one that
incorporates all challenges.

Download: `datasets/adapted-sportstables-cta.zip`

### Enterprise Entity Matching (+errors, +multi-matches, +multiple tables)

We publish our payment-to-invoice matching dataset in multiple versions, each consisting of the payment and invoice
tables and a table with the ground-truth matching information. There are versions with up to one or multiple errors per
match, and versions with descriptive, non-descriptive, and multi-table schemas.

Download: `datasets/payment-to-invoice-matching.zip`

### Enterprise Data Integration (Compound Task)

We publish our enterprise data integration dataset, consisting of the input tables from Company A and Company B, the
ground truth output table of the data integration, and the ground truths of the intermediate steps (schema matching
and entity matching). The dataset has different sizes with versions between 50 and 300 customers.

Download: `datasets/enterprise-data-integration.zip`

### Text-to-SIGNAL

We publish our Text-to-SIGNAL dataset of NL-SIGNAL pairs, each including the natural language user request and the
corresponding ground truth SIGNAL query. We also publish all SIGNAL queries generated in our experiments, as well as
our annotated error types for each query. Also included are the documentation and few-shot examples used in our prompts.

Download: `datasets/text-to-signal.zip`

## Experiments

Please find our prompt templates and example prompts in `PROMPTS.md`!

### Headline Experiment

Experiment implemented in `experiments/enterprise_challenges_cta`, task implemented in `tasks/column_type_annotation`.

### The Data Challenge

#### Exp. 1 - 2: Enterprise vs. public tables & Textual vs. numerical data

Experiments implemented in `experiments/enterprise_data_headers_types_cta`, task implemented in
`tasks/column_type_annotation`.

#### Exp. 3: Table width and sparsity

Experiment implemented in `experiments/enterprise_data_sparsity_width_cta`, task implemented in
`tasks/column_type_annotation`.

#### Exp. 4: Improvement strategies

Experiment implemented in `experiments/enterprise_data_task_mode_ablations_cta`, task implemented in
`tasks/column_type_annotation`.

### The Task Challenge

#### Exp. 5 - 6: Increasing task complexity & Data errors amplify task complexity

Experiments implemented in `experiments/enterprise_tasks_pay_to_inv`, task implemented in `tasks/entity_matching`.

#### Exp. 7 - 9: Error propagation in compound tasks & End-to-end task formulation & End-to-end scaling

Experiments implemented in `experiments/enterprise_tasks_compound`, task implemented in `tasks/compound_task`.

### The Knowledge Challenge

#### Exp. 10: Text-to-SIGNAL

Experiment implemented in `experiments/enterprise_knowledge_text2signal`, task implemented in `tasks/text2signal`.

#### Exp. 11: Schema customizations

Experiment implemented in `experiments/enterprise_knowledge_schema_prediction`, task implemented in
`tasks/schema_prediction`.

### Costs

Experiment implemented in `experiments/costs_imdb_wikipedia_enterprisetables`.

### Other Experiments

The other experiments (e.g., ablations) are also implemented in `experiments/`.

## Setup

Make sure you have **[Python 3.13](https://www.python.org)** installed.

Create a virtual environment, activate it, install the dependencies, and add the project to the Python path:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export PYTHONPATH=${PYTHONPATH}:./
```

Run `bash test.sh` to run the test suite and `bash reproduce.sh` to run the experiments.

### OpenAI, Anthropic, Ollama, Hugging Face, and SAP AI Core

To execute API requests, you must also prepare OpenAI, Anthropic, Ollama, Hugging Face, and SAP AI Core.

To reproduce our exact results using the same model responses, you must paste the cached requests and responses into
`data/openai_cache`, `data/anthropic_cache`, `data/ollama_cache`, and `data/aicore_cache`.

#### OpenAI, Anthropic, and Hugging Face

You must store your API keys in an environment variables:

```bash
export OPENAI_API_KEY="<your-key>"
export ANTHROPIC_API_KEY="<your-key>"
export HF_TOKEN="<your-key>"
```

#### Ollama

Use the Ollama [Docker Container](https://hub.docker.com/r/ollama/ollama):

```bash
docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
docker exec -it ollama ollama pull llama3.1:70b-instruct-fp16
```

Cleanup:

```bash
docker ps
docker stop <container-id>
docker container rm <container-id>
docker volume rm ollama
```

#### SAP AI Core

Redacted SAP internal code.

## Repository Structure

The repository is structured into **tasks**, **config**, **data**, **experiments**, and **library code**.

### Tasks

Tasks like *column type annotation* and *entity matching* are implemented in `tasks/<task-name>`. Each task can have
multiple datasets, like `tasks/column_type_annotation/sportstables`.

Each task is implemented as a pipeline of Python scripts:

1. **Download the original dataset** *specific to each task and dataset*
2. **Preprocess to generate evaluation instances** *specific to each task and dataset*
3. **Prepare API requests** *specific to each task*
4. **Execute API requests** *same for all tasks*
5. **Parse API responses** *specific to each task*
6. **Evaluates the predictions** *specific to each task*

### Configuration

Configuration for tasks and datasets uses [Hydra](https://hydra.cc) and is stored in `config`.

**The prompt templates for each task are stored in `config/<task-name>/config.yaml`.**

### Data

Data is stored in `data/<task-name>/<dataset-name>`.

For each dataset, the original download is placed in `data/<task-name>/<dataset-name>/download`.

The experiment runs are stored in `data/<task-name>/<dataset-name>/<experiments>/<experiment-name>`. Each experiment
consists of:

* `instances` as sequentially numbered directories (one for each instance)
* `requests` as sequentially numbered JSON files
* `responses` as sequentially numbered JSON files
* `predictions` as sequentially numbered directories (one for each prediction)
* `results`

### Experiments

Experiment implementations and their results are stored in `experiments/<experiment-name>`. Each experiment typically
conducts a sweep of experiment runs for a task (implemented in `run.sh`) before gathering their results (implemented in
`gather.py`) and plotting them (implemented in `plot.py`).

### Library Code

Library code is implemented in `llms4de`, is mostly functional, and has pytest tests.
