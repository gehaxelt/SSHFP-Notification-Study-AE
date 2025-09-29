Crt.sh
=============

Crt.sh is another Certificate Transparency Log provider. They offer access to their data through a PostgreSQL connection.

# Database connection

We have implemented a script to query the crt.sh postgreSQL database to obtain domain information in `01-query-crtsh.py`. Since the connection was often unstable, reconnection logic was implemented. At several points, the start offset `offset = 165 * 1000` had to adjusted.

The data was collected around November 28, 2023 - December 1, 2023.

# Extract domains

In the second step, we used `02-extract-domains.py` to extract the first-level domains and subdomains into `extracted-domains.txt` and `extracted-flds.txt`
