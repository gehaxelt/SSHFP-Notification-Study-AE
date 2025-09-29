#!/usr/bin/env python3
import gzip
import tldextract
import json
import glob
import concurrent.futures


all_unique_domains = set()
all_unique_flds = set()


def url2domain(url):
    try:
        t = tldextract.extract(url)
        if not t.suffix == 'de':
            return None, None

        fld = f"{t.domain}.{t.suffix}"
        sub = t.subdomain.replace("*.","") if t.subdomain else ''
        sub = sub.replace("*","")
        if sub != '':
            domain = f"{sub}.{fld}"
        else:
            domain = fld

        return domain.lower(), fld.lower()
    except Exception as e:
        print("2 Error: ", e, "Line:", line)
        return None, None
 

def analyze_file(file):
    print("Analyzing: ", file)
    unique_domains = set()
    unique_flds = set()
    with open(file) as f:
        for line in f:
            try:
                line = line.strip()
                cn, an = line.split(",")
                domain, fld = url2domain(f"http://{cn}/")
                if domain is not None:
                    unique_domains.update([domain])
                if fld is not None:
                    unique_flds.update([fld])
                domain, fld = url2domain(f"http://{an}/")
                if domain is not None:
                    unique_domains.update([domain])
                if fld is not None:
                    unique_flds.update([fld])
            except Exception as e:
                print("1 Error: ", e, "Line:", line)
    with open(f"{file}.domains","w") as f:
        for domain in unique_domains:
            f.write(f"{domain}\n")
    with open(f"{file}.flds","w") as f:
        for fld in unique_flds:
            f.write(f"{fld}\n")
    return unique_domains, unique_flds



with concurrent.futures.ProcessPoolExecutor(max_workers=5) as executor:
    future_to_domains = {executor.submit(analyze_file, f): f for f in glob.glob("./*.csv")}
    for future in concurrent.futures.as_completed(future_to_domains):
        f = future_to_domains[future]
        try:
            domains, flds = future.result()
            all_unique_domains |= domains
            all_unique_flds  |= flds
            print(f, len(all_unique_domains), len(all_unique_flds))
        except Exception as e:
            print(e)
        del future_to_domains[future]

print("All domains: ", len(all_unique_domains))
with open("extracted-domains.txt","w") as f:
    for domain in all_unique_domains:
        f.write(f"{domain}\n")

print("All flds: ", len(all_unique_flds))
with open("extracted-flds.txt","w") as f:
    for fld in all_unique_flds:
        f.write(f"{fld}\n")

            

