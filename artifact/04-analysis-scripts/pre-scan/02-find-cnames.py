#!/usr/bin/env python3

import csv
import dns.resolver
import tldextract

dns.resolver.default_resolver = dns.resolver.Resolver(configure=False)
dns.resolver.default_resolver.nameservers = ["8.8.8.8"]

def domain2cname(domain):
	try:
		answer = dns.resolver.resolve(domain, 'SSHFP', lifetime=10)
		cnames = []
		if answer.chaining_result.cnames:
			for rrset in list(answer.chaining_result.cnames):
				cnames += list([cname.to_text() for cname in rrset])
		return cnames
	except Exception as e:
		print(e)
		return []

def domain2fld(domain):
	try:
		t = tldextract.extract(f"http://{domain}")
		fld = f"{t.domain}.{t.suffix}"
		return fld.strip(".")
	except Exception as e:
		print(e)
		return None

csvr = csv.reader(open("notification-data.csv"), delimiter=",")
next(csvr) # skip header
csvw = csv.writer(open("domains-with-cnames.csv","w"), delimiter=",")
csvw.writerow(["domain","subdomain","diffdomains","cname1", "cname2", "cname3"])
for line in csvr:
	subdomain = line[2]
	fld = domain2fld(subdomain)
	cnames = domain2cname(subdomain)
	if cnames:
		last_cname = cnames[-1]
		last_cname_fld = domain2fld(last_cname)
		if fld == last_cname_fld:
			diff_domain = "0"
		else:
			diff_domain = "1"
		csvw.writerow([fld, subdomain, diff_domain] + cnames)
		print(subdomain, diff_domain, cnames)