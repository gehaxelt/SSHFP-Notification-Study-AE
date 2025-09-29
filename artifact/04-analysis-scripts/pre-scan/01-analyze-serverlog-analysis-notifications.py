import json
import csv
import tldextract
import pyasn
import gzip

# pyasn_util_download.py --latest
# pyasn_util_convert.py --single rib.20230713.1400.bz2 rib.20230713.1400.bz2.ipasn
# asn names = wget https://ftp.ripe.net/ripe/asnames/asn.txt -O asn_names.txt

# TODO: Convert asn_names.csv to asn_names.json with {asnid:name}
csvr = csv.reader(open("asn_names.txt"), delimiter=" ")
asn_mapping = {}
for row in csvr:
	try:
		asnid, asnname = row[0], row[1]
		asn_mapping[int(asnid)] = asnname
	except Exception as e:
		pass

def lookup_as_name(as_id):
	global asn_mapping
	if not as_id in asn_mapping:
		return "unknown"
	else:
		return asn_mapping[as_id]

# TODO: echo '{}' > asn_names.json
asndb = pyasn.pyasn("rib.20231211.0800.bz2.ipasn",as_names_file="asn_names.json")

data = json.load(open("serverlog_analysis_notifications.json"))

csvw = csv.writer(open("notification-data.csv", "w"), delimiter=",")
csvw.writerow(['type','domain','subdomain', 'hosts','ASN_IDs', 'ASN_names'])

type_map={
	'match_insecure': "Fingerprints miss DNSSEC",
	'match_no': 'Fingerprints do not match'
}

lines = []
for t in ['match_insecure', 'match_no']:
	for k in data[t]:
		record = data[t][k]
		try:
			subdomain = record['domain']
			d = tldextract.extract(subdomain)
			domain = f"{d.domain}.{d.suffix}"
			hosts = '|'.join(record['hosts'])
			asn_list = []
			asn_names = []
			for host in record['hosts']:
				asn,network = asndb.lookup(host)
				asn_list.append(str(asn))
				asn_name = lookup_as_name(asn)
				asn_names.append(asn_name)
			asns = '|'.join(asn_list)
			asn_names = '|'.join(asn_names)
			lines.append([type_map[t], domain,subdomain, hosts, asns, asn_names])
		except Exception as e:
			print(e)
for line in sorted(lines):
	csvw.writerow(line)