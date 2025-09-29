Domain collection
=====================

In order to discover SSHFP misconfigurations, we first had to compile a large dataset of domains to analyze. We used multiple public data sources that contain domain names to find as many German domains (belonging to the .de TLD) as possible:

- Censys 
	- https://censys.com/
	- Dataset: `2023-11-01T12:50:08.942841Z`
- CertStream 
	- https://certstream.calidog.io/
	- Dataset: Several weeks passive collection
- crt.sh 
	- https://crt.sh/
	- Dataset: PostgreSQL database
- OpenIntel
	- https://openintel.nl/
	- Datasets: Alexa 1M, Tranco 1M, Radar 1M, Umbrella 1M

After the individual data sources' domain collection, the domain names were merged and compiled into a unique domain set in `MERGED`.

Please note that the data files have been compressed due to their sheer size. You might need to decompress them either with gzip or lzma.

You might need to install the following python packages:

- fastavro - https://pypi.org/project/fastavro/
- tldextract - https://pypi.org/project/tldextract/