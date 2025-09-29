import json
import dns.resolver
import time
import csv
import threading
from concurrent.futures import ThreadPoolExecutor


INPUT_FILE = "03-notexisting-flds.txt"
QPS = 10
CHECKPOINT_INTERVAL = 5000
DATA = []

# 
WRITE_LOCK = threading.Lock()
global_resolver = dns.resolver.Resolver()
global_resolver.nameservers = ['1.1.1.1','9.9.9.9', '8.8.8.8', '208.67.222.222', '208.67.220.220']

DE_NAMESERVER_LIST = []
DE_NAMESERVER_RESOLVERS = []

tld_ns_query = global_resolver.resolve('de.', 'NS')
tld_nameservers = [ns.to_text() for ns in tld_ns_query]
for nameserver in tld_nameservers:
	de_ns_query = global_resolver.resolve(nameserver, 'A')
	DE_NAMESERVER_LIST += [a.to_text() for a in de_ns_query]

print(DE_NAMESERVER_LIST)
for ns_ip in DE_NAMESERVER_LIST:
	resolver = dns.resolver.Resolver()
	resolver.nameservers = [ns_ip]
	DE_NAMESERVER_RESOLVERS.append(resolver)


def check_domain(domain, jobid):
	try:
		the_resolver = DE_NAMESERVER_RESOLVERS[jobid % len(DE_NAMESERVER_RESOLVERS)]
		qry = the_resolver.resolve(domain, 'NS', raise_on_no_answer=False, lifetime=5)
		if not qry.response.authority:
			return jobid, domain, False, 'No response'
		domain_ns = [ns.to_text() for ns in qry.response.authority[0]]
		return jobid, domain, True, ','.join(domain_ns)
	except Exception as e:
		return jobid, domain, False, str(e)

def check_domain_done(future):
	global DATA
	d = list(future.result())
	print(d)
	with WRITE_LOCK:
		DATA.append(d[1:])
		if d[0] % CHECKPOINT_INTERVAL == 0: #d[0] is jobid:
			save_checkpoint(d[0])

def save_checkpoint(id):
	global DATA
	print(f"Checkpointing: {id}")
	with open(f"checkpoints2/existing_domains-{id}.csv", "w") as f:
		csvw = csv.writer(f)
		csvw.writerow(["Domain", "Status", "Nameservers or Error"])
#		with WRITE_LOCK:
		for l in DATA:
			csvw.writerow(l)
		DATA = []


with ThreadPoolExecutor(max_workers=5) as e:
	with open(INPUT_FILE) as f:
		jobid = 0
		for line in f:
			line = line.strip()
			future = e.submit(check_domain, line, jobid)
			future.add_done_callback(check_domain_done)
			jobid += 1
			time.sleep(1 / QPS)
save_checkpoint("finished")
