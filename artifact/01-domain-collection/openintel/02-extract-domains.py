import json
import tldextract
import glob
import concurrent.futures


all_domains_set = set()
all_flds_set = set()

def extract_domains(file):
    domains = set()
    flds = set()

    with open(file) as f:
        for line in f:
            try:
                d = tldextract.extract(line.strip())
                fld = f"{d.domain}.{d.suffix}"
                sub = d.subdomain.replace("*.", "") if d.subdomain else ''
                sub = sub.replace("*","")
                if sub != '':
                    domain = f"{sub}.{fld}"
                else:
                    domain = fld
                flds.update([fld.lower()])
                domains.update([domain.lower()])
            except Exception as e:
                print(e)

    return flds, domains


with concurrent.futures.ProcessPoolExecutor(max_workers=1) as executor:
    future_to_domains = {executor.submit(extract_domains, f): f for f in glob.glob("./top1m-de-domains.txt")}
    for future in concurrent.futures.as_completed(future_to_domains):
        f = future_to_domains[future]
        try:
            flds, domains = future.result()
            all_flds_set |= flds
            all_domains_set |= domains
            print(f, len(all_domains_set), len(all_flds_set))
        except Exception as e:
            print(e)
        del future_to_domains[future]

print("Writing to file...")
with open("extracted-domains.txt", "w") as f:
    for domain in all_domains_set:
        f.write(f"{domain}\n")

with open("extracted-flds.txt", "w") as f:
    for domain in all_flds_set:
        f.write(f"{domain}\n")

