Merged dataset
===============

This dataset is contructed from all the `extracted-*.txt` files from the other data sources to get a unique list of domains to scan.

# Merging

First, the script `00-merge-datasets.sh` and `01-make-unique.py` are used to merge all datasets into a combined, unique one.

# Existence

Since some domains might not be active anymore, we perform two iterations of an existence check with `02-query-existence.py`, `03-filter-existence.py` and `04-query-existence-slow.py` and `05-filter-existence.py`. 

# Final dataset

Finally, we create the `06-existing-domains.txt` file by taking the existing domains and matching the unique subdomains from `unique-extracted-domains.txt`.

