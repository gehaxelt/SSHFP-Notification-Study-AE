#!/usr/bin/python3
import requests
import json
import sys
import os
import hashlib
import time
import random

from fastavro import reader
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

CAPI="https://search.censys.io/api/v1"

headers = {
    'accept': 'application/json',
    'Authorization': 'Basic [YOURCENSYSAPIKEY]'
}

#datasets = requests.get(f"{CAPI}/data/certificates-v2-full", headers=headers)
#print(datasets.json())
# {'id': 'certificates-v2-full', 'name': 'Full Set of X.509 Certificates', 'description': 'Parsed X.509 certificates featuring all certificates known to Censys. Schema version 2.', 'results': {'latest': {'id': '2023-06-01T12:50:07.519583Z', 'timestamp': '20230601T125008', 'details_url': 'https://search.censys.io/api/v1/data/certificates-v2-full/2023-06-01T12:50:07.519583Z'}, 'historical': [{'id': '2023-06-01T12:50:07.519583Z', 'timestamp': '20230601T125008', 'details_url': 'https://search.censys.io/api/v1/data/certificates-v2-full/2023-06-01T12:50:07.519583Z'}]}}
#dataset_id = "2023-06-01T12:50:07.519583Z"
dataset_id = "2023-11-01T12:50:08.942841Z"

#datasets = requests.get(f"{CAPI}/data/certificates-v2-full/{dataset_id}", headers=headers)
#with open("datasets.json", "w") as f:
#    f.write(json.dumps(datasets.json()))

# https://stackoverflow.com/questions/16694907/download-large-file-in-python-with-requests
def download_file(url, local_filename):
    # NOTE the stream=True parameter below
    time.sleep(random.randint(15,60))
    with requests.get(url, stream=True, headers=headers) as r:
        print("Error", r.raise_for_status(), local_filename)
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): 
                # If you have chunk encoded response uncomment if
                # and set chunk_size parameter to None.
                #if chunk: 
                f.write(chunk)
    return local_filename

def dl_and_analyze_avro(file, f_url, f_hash):
    if not os.path.exists(file):
        print("Downloading", file, 'from', f_url)
        download_file(f_url, file)
    elif f_hash != hashlib.md5(open(file, 'rb').read()).hexdigest():
        print("File is corrupt: ", file)
        os.unlink(file)
        print("Downloading", file, 'from', f_url)
        download_file(f_url, file)
    else:
        print("File can be analyzed: ", file)

    if f_hash != hashlib.md5(open(file, 'rb').read()).hexdigest():
        print("Download was incomplete")
        return
    else:
        print("Download was complete: ", file)

    tld_de_domains = set()
    with open(file, 'rb') as f:
        print("Reading avro records of ", file)
        for record in reader(f):
            if not 'parsed' in record:
                continue
            if not record['parsed']:
                continue
            parsed = record['parsed']
            cert_names = set()
            if ('subject' in parsed and parsed['subject']) and ('common_name' in parsed['subject'] and parsed['subject']['common_name']):
                common_names = parsed['subject']['common_name']
                cert_names.update(common_names)

            if ('extensions' in parsed and parsed['extensions']) and ('subject_alt_name' in parsed['extensions'] and parsed['extensions']['subject_alt_name']) and ('dns_names' in parsed['extensions']['subject_alt_name'] and parsed['extensions']['subject_alt_name']['dns_names']):
                dns_names = parsed['extensions']['subject_alt_name']['dns_names']
                cert_names.update(dns_names)

            tld_de_domains.update(filter(lambda x: x.endswith(".de"), cert_names))
    print("Writing resulting .de domains of", file)
    with open(f"{file}.domains.json", "w") as f:
        f.write(json.dumps(list(tld_de_domains)))

    os.unlink(file)



if __name__ == "__main__":
    with open("datasets.json") as f:
        data = json.loads(f.read())

    #executor = ThreadPoolExecutor(max_workers=5)
    executor = ProcessPoolExecutor(max_workers=7)

    for file in data['files']:
        f_url = data['files'][file]['download_path']
        f_hash = data['files'][file]['compressed_md5_fingerprint']

        #fid = file.replace("certificates-","").replace(".avro","")
        #if int(fid) < 0 * 1000 or int(fid) > 16 * 1000:
        #    continue

        if os.path.exists(f"{file}.domains.json"):
            print("Skipping: ", file)
            continue

        time.sleep(random.randint(1,5))
        w = executor.submit(dl_and_analyze_avro, file, f_url, f_hash)

    executor.shutdown(wait=True)




