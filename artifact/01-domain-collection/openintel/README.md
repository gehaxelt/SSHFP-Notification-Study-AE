OpenIntel
==========

Openintel.nl is a project that queries DNS entries of different domain datasets. Their scans are partially open source and available.

# Download and extract datasets

We downloaded the latest versions of Alexa 1M, Radar 1M, Tranco 1M and Umbrella 1M public datasets from https://data.openintel.nl/data/ into separate folders (`alexa1m`, `radar1m`, `tranco1m` and `umbrella1m`) and extracted the tar archives.

- `openintel-alexa1m-20230515.tar`
- `openintel-radar1m-20231102.tar`
- `openintel-tranco1m-20231103.tar`
- `openintel-umbrella1m-20231103.tar`

Then, we used avro-tools and `01-extract-data.sh` to extract the domains from the AVRO datasets.

# Extract domains

In the second step, we used `02-extract-domains.py` to extract the first-level domains and subdomains into `extracted-domains.txt` and `extracted-flds.txt`
