import csv
import json

# This file is the 'notification-data.csv' manually extended by the fields "email, title, firstname1, lastname1, token" from the contact address collection.
INFILE = "notification-data-monitor.csv"

TOKENS = {}

DOMAINS = {}

with open(INFILE) as f:
	reader = csv.reader(f)
	next(reader) # Skip header
	# ['ID', 'type', 'domain', 'subdomain_1', 'is_contact', 'diffdomains', 'cname_1', 'cname_2', 'cname_3', 'email', 'title', 'firstname1', 'lastname1', 'token', 'group', 'hosts', 'ASN_IDs', 'ASN_names', '']
	# 0			1 		2 			3 			 4				5			6			7			8			9		10		11				12			13		14			15		16			17
	for row in reader:
		domain = row[2]
		subdomain = row[3]
		token = row[13].lower()

		if token:
			if not token in TOKENS:
				TOKENS[token] = {
					'ids': [domain],
					'domains': set(),
					'group': "tool"
				}
			else:
				if not domain in TOKENS[token]['ids']:
					TOKENS[token]['ids'].append(domain)

		if domain not in DOMAINS:
			DOMAINS[domain] = {
				'subs': []
			}
		if subdomain not in DOMAINS[domain]['subs']:
			DOMAINS[domain]['subs'].append(subdomain)


for token in TOKENS.keys():
	for maindomain in TOKENS[token]['ids']:
		TOKENS[token]['domains'].add(maindomain)
		for sub in DOMAINS[maindomain]['subs']:
			TOKENS[token]['domains'].add(sub)
	TOKENS[token]['domains'] = sorted(list(TOKENS[token]['domains']))
with open("tokens.json", "w") as f:
	json.dump(TOKENS,f, indent=2)
print(json.dumps(TOKENS, indent=2))
#print(DOMAINS)