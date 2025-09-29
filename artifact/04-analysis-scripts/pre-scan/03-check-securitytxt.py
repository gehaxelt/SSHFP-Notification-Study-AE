import requests
import csv
import json
import base64
import os

INFILE = "notification-data.csv"
# RFC: https://datatracker.ietf.org/doc/html/rfc9116
SECURITYTXT_PATHS = [".well-known/security.txt", "security.txt"]
PROTOCOLS = ["https"]

DOMAINS = set()

with open(INFILE) as f:
	csvw = csv.reader(f)
	next(csvw) # skip header
	for line in csvw:
		_, fld, subdomain, _, _, _ = line
		DOMAINS.add(fld)
		DOMAINS.add(subdomain)

RESULTS = {}

try:
	os.mkdir("./securitytxt/")
except:
	pass

def scan_domain(domain):
	global RESULTS
	try:
		for proto in PROTOCOLS:
			for i, path in enumerate(SECURITYTXT_PATHS):
				try:
					key = f"{domain}_{proto}_{i}"
					r = requests.get(f"{proto}://{domain}/{path}", timeout=3, allow_redirects=True, verify=False)
					if r.status_code in [200] and b'Contact' in r.content:
						print("FOUND: ", key)
						data = base64.b64encode(r.content).decode()
						RESULTS[key] = data
						with open(f"./securitytxt/{key}.txt", "wb") as f:
							f.write(r.content)
				except Exception as e:
					print(domain, e)
				print("[-] FAILED: ", domain)
	except Exception as e:
		print(domain, e)
	print("[-] FAILED: ", domain)

for i, domain in enumerate(DOMAINS):
	print(f"{i}: Scanning {domain}")
	scan_domain(domain)

	with open("05-securitytxt.json", "w") as f:
		f.write(json.dumps(RESULTS, indent=2))