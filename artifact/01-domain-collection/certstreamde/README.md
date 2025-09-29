Certstream (de)
============

We used the scanning tool to query the certification transparency log stream for certificates that contain German domains. 

# Initial collection

We modified the scanning tool to log `.de` domains. This can be achieved by uncommenting the following lines in the `certstream_callback` function and setting the tool's domain source to `DOMAINSOURCE: certstream` in the `docker-compose.yml` file.

```
#try:
#    d = tldextract.extract(domain)
#    if d.suffix != "de":
#        continue
#except Exception as e:
#    continue
```
Check the scanning tool's README on how to run it.

Since the CT log stream is a continuous source of data, the data collection was performed for a limited time frame while also working on other data sources around November 2023

# Data extraction
As a result, the scanning tool logs all obtained domains and the tool's analysis step, the `certstream_counted_unique_domains.json` file is created which contains the processed domains.

After copying the file from the scanning tool to this directory, `01-extract-domains.py` is used to extract the first-level domains and subdomains into `extracted-domains.txt` and `extracted-flds.txt` 