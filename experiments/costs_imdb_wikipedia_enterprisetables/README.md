# Costs for Processing Wikipedia vs. IMDb Database vs. EnterpriseTables vs. Random EnterpriseTables

We compute the tokens/costs for four datasets:

1. Wikipedia
2. IMDb
3. EnterpriseTables (with the tables from the column type annotation task)
4. Random EnterpriseTables (randomly sampled tables)

We use Random EnterpriseTables to compute the tokens per cell for a random sample of the tables, compute the number of
cells per table for a larger sample of the tables, and then extrapolate to the total number of cells in the database
based on the total number of tables.