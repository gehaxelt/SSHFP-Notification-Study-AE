import json
import tldextract


with open("certstream_counted_unique_domains.json") as f:
    data = json.loads(f.read())

unique_domains = set()
unique_flds = set()
for domain in data['counted_unique_domains'].keys():
    try:
        d = tldextract.extract(domain)
        if not d.suffix == 'de':
            continue
        fld = f"{d.domain}.{d.suffix}"
        sub = d.subdomain.replace("*.","") if d.subdomain else ''
        sub = sub.replace("*","")
        if sub != '':
            domain = f"{sub}.{fld}"
        else:
            domain = fld
        unique_flds.update([fld.lower()])
        unique_domains.update([domain.lower()])
    except Exception as e:
        print(e)

print("Writing to file...")
with open("extracted-domains.txt", "w") as f:
    for domain in unique_domains:
        f.write(f"{domain}\n")

with open("extracted-flds.txt", "w") as f:
    for domain in unique_flds:
        f.write(f"{domain}\n")
