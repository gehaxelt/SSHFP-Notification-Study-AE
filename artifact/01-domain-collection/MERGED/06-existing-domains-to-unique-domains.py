import tldextract

existing_flds = set()
with open("05-existing-flds.txt") as f:
    for line in f:
        line = line.strip()
        existing_flds.add(line)

print("We have existing flds: ", len(existing_flds))

existing_domains = set()
with open("unique-extracted-domains.txt") as f:
    for line in f:
        try:
            line = line.strip()
            d = tldextract.extract(f"http://{line}")
            fld = f"{d.domain}.{d.suffix}"

            if fld in existing_flds:
                existing_domains.add(line)

        except Exception as e:
            print(e)

print("We have existing domains: ", len(existing_domains))

with open("06-existing-domains.txt", "w") as f:
    for domain in existing_domains:
        f.write(f"{domain}\n")
