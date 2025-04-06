# Column Type Annotation

task mode: "all" or "lookup-index" or "lookup-header"

## Instances

Each instance consists of

*if task mode "all"*

* `table_name.txt` contains the table name
* `table.csv` contains the table
* `column_types.json` contains the list of column types, which contains `None` for any column with unspecified type
* `data_types.json` contains the list of data types (`numerical` or `non-numerical`)

`instances/all_column_types.json` contains the list of all possible column types

*if task mode "lookup-index" or "lookup-header"*

* `table_name.txt` contains the table name
* `table.csv` contains the table
* `index.json` contains the index (integer) of the column to look up
* `column_type.json` contains the column type of the column to look up
* `data_type.json` contains the data type of the column to look up

`instances/all_column_types.json` contains the list of all possible column types

## Predictions

Each prediction consists of

*if task mode "all"*

* `error.json` contains `None` if the API request and parsing succeeded, or the error code if it failed
* `column_types.json` contains the predicted list of column types, or `None` if the API request or parsing failed

*if task mode "lookup-index" or "lookup-header"*

* `error.json` contains `None` if the API request and parsing succeeded, or the error code if it failed
* `column_type.json` contains the predicted column type, or `None` if the API request or parsing failed