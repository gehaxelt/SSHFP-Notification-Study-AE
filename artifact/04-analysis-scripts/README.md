Analysis Tools
=========================

We used a variety of scripts to analyze and enrich our collected data. The analysis step happens after the domain collection, scanning tool usage, so we assume that the data resulting from these previous steps is available.

# Pre-Scan

These scripts were used to prepare the data for the notification experiment. 

## Server-log analysis & ASN assignment

In order to output a CSV for further processing and assigning ASN numbers to the domains' IP addresses, we use pyasn and the script `analyze-serverlog-analysis-notifications.py`. 

For that to work, install `pyasn` with `pip3 install pyasn` and download the RIB file to convert it to IPASN:
```
pyasn_util_download.py --latest
pyasn_util_convert.py --single rib.20230713.1400.bz2 rib.20230713.1400.bz2.ipasn
curl https://ftp.ripe.net/ripe/asnames/asn.txt -o asn_names.txt
```

Place the `serverlog_analysis_notifications.json` from the scanning tool in this directory and run `python3 analyze-serverlog-analysis-notifications.py`. The output will be `notification-data.csv`

## Security.txt retrieval

Security relevant contact information might be available in the so called security.txt file. With `check-securitytxt.py` we try to obtain this file from the domains' `/security.txt` or `.well-known/security.txt` paths, for the `https://` protocol.

The responses to these HTTP requests are written to separate files (`[domain]_[protocol]_[filepathindex]`) to a newly created directory `./securitytxt/` for manual review and retrieval of contact details. The only filter applied in the a check for the `Contact` keyword as defined in  [RFC 9116](https://www.rfc-editor.org/rfc/rfc9116#name-contact).

The script also generates a `05-securitytxt.json` file with the information about the retrieved files.

## Find CNAMEs

To detect which domains have CNAMEs set, we use the script `find-cnames.py` to query the domains from `notification-data.csv` for CNAME entries and mark whether the CNAME's domain is different from the requested domain. The results are saved into `domains-with-cnames.csv`

## Gen Tokens Script

At a later stage of our notification study, before sending out the notification emails, we assinged randomly generated tokens (in MS Excell or LibreOffice Spreadsheet). The script `gen-tokens.py` reads our notification-data CSV file and generates `token` dictionary suitable for copy/pasting into the `tokens.json` configuration file of the selftest-tool.

# Post-Scan

These scripts were used to post-process the data collected during or after the notification study, for example, analyzing the data with SPSS. 