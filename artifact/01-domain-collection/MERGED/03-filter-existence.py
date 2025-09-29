import glob
import csv

existing_flds = set()
notexisting_flds = set()

def process_file(path):
    with open(path) as f:
        r = csv.reader(f)
        next(f) # skip header
        for record in r:
            domain = record[0]
            exists = record[1]
            _ = record[2]

            if exists == "True":
                existing_flds.add(domain)
            else:
                notexisting_flds.add(domain)
    

for f in glob.glob("./checkpoints/*.csv"):
    process_file(f)

print("Existing: ", len(existing_flds))
with open("03-existing-flds.txt", "w") as f:
    for domain in existing_flds:
        f.write(f"{domain}\n")

print("Not existing: ", len(notexisting_flds))
with open("03-notexisting-flds.txt", "w") as f:
    for domain in notexisting_flds:
        f.write(f"{domain}\n")
