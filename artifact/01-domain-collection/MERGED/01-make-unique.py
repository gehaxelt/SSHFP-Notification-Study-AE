import tldextract

unique_flds = set()
with open("extracted-flds.txt") as f:
    for line in f:
        line = line.strip()
        try:
            line = line.replace("*.", "").replace("*","")
            d = tldextract.extract(f"http://{line}/")
            if d.domain == '':
                continue
            fld = f"{d.domain}.{d.suffix}"
            unique_flds.add(fld)
        except Exception as e:
            print(line , e)
with open("unique-extracted-flds.txt", "w") as f:
    for d in unique_flds:
        f.write(f"{d}\n")

unique_domains = set()
with open("extracted-domains.txt") as f:
    for line in f:
        line = line.strip()
        try:
            line = line.replace("*.", "").replace("*","")
            d = tldextract.extract(f"http://{line}/")
            if d.domain == '':
                continue
            if d.subdomain == '':
                domain = f"{d.domain}.{d.suffix}"
            else:
                if d.subdomain.startswith("."):
                    sub = d.subdomain[1:]
                else:
                    sub = d.subdomain
                domain = f"{sub}.{d.domain}.{d.suffix}"
            unique_domains.add(domain)
        except Exception as e:
            print(line , e)
with open("unique-extracted-domains.txt", "w") as f:
    for d in unique_domains:
        f.write(f"{d}\n")
