Censys dataset
================

Censys provides a dataset of observed certificates on the internet. As certificates can be issued for one or more domains, we tried to obtain as many domains as possible from issued certificates.

To process this dataset, two scripts were implemented.

# 01-get-domains.py

First, register an account with censys and obtain an API token with access to the certificates dataset. Replace `[YOURCENSYSAPIKEY]` with your own API key in `01-get-domains.py`.

Next, identify the ID of currently available (latest) certificate dataset:

```
CAPI="https://search.censys.io/api/v1"
headers = {
    'accept': 'application/json',
    'Authorization': 'Basic [YOURCENSYSAPIKEY]'
}
datasets = requests.get(f"{CAPI}/data/certificates-v2-full", headers=headers)
print(datasets.json())
# {'id': 'certificates-v2-full', 'name': 'Full Set of X.509 Certificates', 'description': 'Parsed X.509 certificates featuring all certificates known to Censys. Schema version 2.', 'results': {'latest': {'id': '2023-06-01T12:50:07.519583Z', 'timestamp': '20230601T125008', 'details_url': 'https://search.censys.io/api/v1/data/certificates-v2-full/2023-06-01T12:50:07.519583Z'}, 'historical': [{'id': '2023-06-01T12:50:07.519583Z', 'timestamp': '20230601T125008', 'details_url': 'https://search.censys.io/api/v1/data/certificates-v2-full/2023-06-01T12:50:07.519583Z'}]}}
```
In this case, it is `2023-06-01T12:50:07.519583Z`. Thus, change `dataset_id` variable accordingly.

Uncomment the lines 26-29 to create the datasets.json file:

```
datasets = requests.get(f"{CAPI}/data/certificates-v2-full/{dataset_id}", headers=headers)
with open("datasets.json", "w") as f:
    f.write(json.dumps(datasets.json()))
```

After obtaining the meta data and the `datasets.json` file, comment the above lines out. The script is now ready to download the dataset pieces and extract domains from the certificates. 

You can change the script's parallelism by changing `max_workers` in `executor = ProcessPoolExecutor(max_workers=7)`. Usually, the network is the limiting factor, so setting a too high amount does not change much in practice.

The script can also be stopped and restartet - it will skip already downloaded and parsed files and redownload incomplete or missing parts.

# 02-extract-domains.py

Once the previous script terminated and all data was successfully downloaded, this script is used to parse all domains and compile a **unique** set of first-level domains and subdomains. 

The output will be `extracted-domains.txt` and `extracted-flds.txt`.

Use `cat extracted-domains.txt.lzma-part-* > extracted-domains.txt.lzma` to reconstruct the split file.