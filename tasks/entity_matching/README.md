# Entity Matching

## Instances

Each instance consists of

* `ground_truth.json` contains `{"rows_match": <boolean whether they match>}`
* `source_row.csv` contains the source row (from the first table)
* `target_row.csv` contains the target row (from the second table)

`instances/examples_pos_neg.json` contains `{"positive": [<idx of matches>], "negative": [<idx of no-matches>]}`

## Predictions

Each prediction consists of

* `error.json` contains `None` if the API request and parsing succeeded, or the error code if it failed
* `prediction.json` contains `{"rows_match": <boolean whether predicted match>}` or `None` in case of errors