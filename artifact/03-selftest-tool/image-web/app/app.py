from flask import Flask, render_template, request, g, redirect, url_for, make_response, session, flash, send_from_directory
from flask_httpauth import HTTPBasicAuth
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
import io
import re
import os
import tldextract
import base64
import subprocess
import uuid
import glob
import time
import json
import datetime
import socket
import sys
import dns.resolver
import dns.exception
import ipaddress
import limits

from threading import Lock
from libsshfp import SSHFP, SSHFPDomain, SSHFPComparison

app = Flask(__name__)
app.config['BOOTSTRAP_SERVE_LOCAL'] = True
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SESSION_TYPE'] = 'filesystem'
app.secret_key = os.urandom(64)
Session(app)

app.lock = Lock()
app.logfile_iteractions = os.environ.get("LOGFILE_INTERACTIONS", 'interactions.log')
app.languages = {}
for f in glob.glob("*.json", root_dir="./languages/"):
    k = f.replace(".json", "")
    app.languages[k] = json.loads(open(os.path.join("./languages",f)).read())

app.token_config = json.loads(open("tokens.json").read())
app.tokens = {k.lower(): v for k, v in app.token_config['tokens'].items()}
app.groups = app.token_config['groups']
app.always_allowed_views = ['index', 'static', 'favicon', 'legal','login', 'language', 'logout', 'faq']

auth = HTTPBasicAuth()
http_basic_auth_username = os.environ.get("HTTP_BASIC_AUTH_USERNAME", 'ssh')
http_basic_auth_password = os.environ.get("HTTP_BASIC_AUTH_PASSWORD", 'ssh')
users = {
    http_basic_auth_username: generate_password_hash(http_basic_auth_password)
}

recursor_ip = socket.gethostbyname('recursor')
dnssec_recursor_ip = socket.gethostbyname('dnssecrecursor')

dns.resolver.default_resolver = dns.resolver.Resolver(configure=False)
dns.resolver.default_resolver.nameservers = [f"{recursor_ip}"]

BLOCKED_NETWORKS = []
if "BLOCKED_NETWORKS" in os.environ:
    for subnet in os.environ.get("BLOCKED_NETWORKS", "").split(","):
        try:
            ipnet = ipaddress.ip_network(subnet)
            print("Blacklisting network", ipnet)
            BLOCKED_NETWORKS.append(ipnet)
        except Exception as e:
            print(subnet, e)

LIMITS_STORAGE = limits.storage.MemoryStorage()
LIMITS_STRATEGY = limits.strategies.MovingWindowRateLimiter(LIMITS_STORAGE)

def is_rate_limited(token):
    if LIMITS_STRATEGY.hit(limits.parse(os.environ.get("RATE_LIMIT","1500/hour")), token):
        return False
    return True

def is_blocked_ip(ip):
    for bnet in BLOCKED_NETWORKS:
        if ipaddress.ip_address(ip) in bnet:
            return True
    return False

@auth.verify_password
def verify_password(username, password):
    if username in users and \
            check_password_hash(users.get(username), password):
        return username

@app.before_request
def before_request_callback():
    request.uuid = str(uuid.uuid4())


    default_lang = os.environ.get("WEBSITE_DEFAULT_LANGUAGE", list(app.languages.keys())[0])
    lang = request.cookies.get('lang', default_lang) or request.accept_languages.best_match(app.languages, default=default_lang)
    g.lang = lang


    token = session.get('token', None)
    if token:
        if not token in app.tokens:
            del session['token']
            return redirect(url_for('index'))

        g.token = token
        if request.endpoint in app.always_allowed_views:
            return

        if not can_view(g.token, request.endpoint):
            flash(t("You cannot view this page."), 'danger')
            return redirect(url_for("login"))
    elif request.endpoint in app.always_allowed_views:
        return
    else:
        flash(t("Please login with a token first."), 'danger')
        return redirect(url_for('login'))


def can_scan_domain(token, domain):
    if not token or token not in app.tokens:
        return False

    if token.lower() == "__SUPER_SECRET_ADMIN__".lower():
        return True

    if domain.lower().strip() not in list(map(lambda x: x.lower().strip(), app.tokens[token]['domains'])):
        return False

    return True


@app.template_filter()
def can_view(token, endpoint):
    if not token:
        if endpoint in app.always_allowed_views:
            return True
        else:
            return False

    group = app.tokens[token]['group']
    allowed_views = app.groups[group]['views'] + app.always_allowed_views
    if endpoint in allowed_views:
        return True
    else:
        return False

@app.template_filter()
def b64encode(m):
    return base64.b64encode(m.encode()).decode()

@app.template_filter()
def t(m):
    if m in app.languages[g.lang]:
        return app.languages[g.lang][m]
    else:
        return m



def log_event(msg, type="default",domain=""):
    now = str(datetime.datetime.now())
    unix = time.time()
    token = session['token'] if 'token' in session else None
    msgobj = {'unix': unix, 'date': now, 'uuid':request.uuid, 'msg': msg, 'type':type, 'domain': domain, 'token': token}
    with app.lock:
        with open(app.logfile_iteractions, "a") as f:
            f.write(json.dumps(msgobj, default=lambda x: x.__dict__) + "\n")



def check_domain(r, prefill=None):
    output = io.StringIO()
    result = {
        'show': True
    }
    raw_domain = r.form.get('domain', None)

    # Check input
    if not raw_domain:
        output.write(t("Error: No domain provided") + ".\n")
        outstr = output.getvalue()
        log_event({'outstr': outstr, 'result':result},type="result", domain="No input")
        return outstr, result

    # Parse domain
    try:
        result['raw_domain'] = raw_domain
        d = tldextract.extract(raw_domain.strip())
        if not d.suffix or d.suffix == '':
            output.write(t("Error: Domain suffix is invalid") + ".\n")
            outstr = output.getvalue()
            log_event({'outstr': outstr, 'result':result, 'input': raw_domain},type="result", domain="Invalid domain")
            return outstr, result
        domain = f"{d.suffix}"
        if not d.domain or d.domain == '':
            output.write(t("Error: Domain is invalid") + ".\n")
            outstr = output.getvalue()
            log_event({'outstr': outstr, 'result':result, 'input': raw_domain},type="result", domain="Invalid domain")
            return outstr, result
        domain = f"{d.domain}.{domain}"
        if d.subdomain and d.subdomain != '':
            domain = f"{d.subdomain}.{domain}"
        output.write(t("Testing domain") + f": {domain}\n")
        result['domain'] = domain
    except Exception as e:
        print(e)
        output.write(t("An unexpected error occurred :-(\nPlease try again later or contact us.\n"))
        outstr = output.getvalue()
        log_event({'outstr': outstr, 'result':result, 'input': raw_domain},type="result", domain="Invalid domain")
        return outstr, result

    if not can_scan_domain(g.token, result['domain']):
        output.write(t("You are not allowed to scan this domain. You can only scan the (sub)domains we included in the notification.\n"))
        log_event(f"Tried to scan unauthorized domain!", type="auth", domain=domain)
        flash(t("You are not allowed to scan this domain. You can only scan the (sub)domains we included in the notification.\n"), 'danger')
        result['show'] = False
        return output.getvalue(), result

    if is_rate_limited(g.token):
        output.write(t("You have reached the maximum number of scans per hour. Please try again later!\n"))
        log_event(f"Rate limit exceeded!", type="limit", domain=domain)
        flash(t("You have reached the maximum number of scans per hour. Please try again later!\n"), 'danger')
        result['show'] = False
        return output.getvalue(), result

    if prefill:
        log_event(f"Scan started with prefill d={prefill}",type="scan",domain=domain)
    else:
        log_event(f"Scan started without prefill",type="scan",domain=domain)


    # Query for SSHFP records
    output.write("\n")
    try:
        output.write(t("Querying for SSHFP records...") + "\n")
        answer = dns.resolver.resolve(domain, 'SSHFP', lifetime=10)
        #req = dns.message.make_query(domain, dns.rdatatype.SSHFP)
        #answer = dns.query.udp(req, where=result['ns_server'], timeout=10)
        records = sorted(set([sshfp.to_text() for sshfp in answer]))
        output.write(t("Success: Got XXX SSHFP records:\n").replace("XXX", str(len(records))))
        for i, record in enumerate(records):
            output.write(f"\t{i+1}. {t('SSHFP record')}: {record}\n")
        result['has_dns_sshfps'] = True
        result['dns_sshfps_raw'] = records
    except dns.resolver.NoAnswer as e:
        print(e, file=sys.stderr)
        output.write(t("Error: The domain XXX does not have any SSHFP records configured.").replace("XXX",domain) + "\n")
        result['has_dns_sshfps'] = False
        outstr = output.getvalue()
        log_event({'outstr': outstr, 'result':result},type="result", domain=domain)
        return outstr, result
    except dns.exception.DNSException as e:
        print(e, file=sys.stderr)
        output.write(t("Error: A DNS resolving error occurred. Please try again later.\n"))
        outstr = output.getvalue()
        log_event({'outstr': outstr, 'result':result},type="result", domain=domain)
        return outstr, result
    except Exception as e:
        print(e, file=sys.stderr)
        output.write(t("Error: An unexpected error occurred :-(\nPlease try again later or contact us.\n"))
        outstr = output.getvalue()
        log_event({'outstr': outstr, 'result':result},type="result", domain=domain)
        return outstr, result

    # Parse SSHFP records
    output.write(t("Parsing and validating the SSHFP records...\n"))
    dns_sshfpd = SSHFPDomain(domain=domain, timestamp=int(time.time()))

    result['dns_sshfps_parsed'] = []
    for i, record in enumerate(result['dns_sshfps_raw']):
        try:
            sshfp = SSHFP.from_string(record)
            sshfp.domain = domain
            sshfp.timestamp = dns_sshfpd.timestamp

            #csv_writer.writerow([sshfp.timestamp, sshfp.domain, sshfp.algo_stringified(), sshfp.type_stringified(), sshfp.fingerprint])
            dns_sshfpd.records.append(sshfp)
            result['dns_sshfps_parsed'].append(sshfp)
            output.write(f"\t{i+1}. {t('SSHFP record')}: ALGO={sshfp.algo_stringified()}\tHASH={sshfp.type_stringified()}\tFINGERPRINT={sshfp.fingerprint}\n")
        except Exception as e:
            print(e)
            output.write(f"\t{i+1}. {t('SSHFP record')}: {t('This record is invalid.')}")

    if not result['dns_sshfps_parsed']:
        output.write(t("Error: No valid SSHFP records were found.\n"))
        outstr = output.getvalue()
        log_event({'outstr': outstr, 'result':result},type="result", domain=domain)
        return outstr, result

    if len(result['dns_sshfps_raw']) == len(result['dns_sshfps_parsed']):
        result['dns_sshfps_valid'] = True
    else:
        result['dns_sshfps_valid'] = False

    # Check DNSSEC validation
    output.write("\n")
    output.write(t("Checking DNSSEC support... "))
    try:
        # From https://stackoverflow.com/a/26137120
        req = dns.message.make_query(domain, dns.rdatatype.SSHFP, want_dnssec=True)
        resp = dns.query.udp(req, where=dnssec_recursor_ip, timeout=10)

        rcode = resp.rcode()
        if rcode != 0:
            raise Exception(f"{dns.rcode.to_text(rcode)}")

        is_authentic = 'AD' in dns.flags.to_text(resp.flags)
    except Exception as e:
        is_authentic = False

    output.write(f"{is_authentic}\n")
    result['has_dnssec'] = is_authentic

    # Find hosts
    output.write("\n")
    output.write(t("Resolving A record to find servers...\n"))
    result['server_ips'] = []
    try:
        answer = dns.resolver.resolve(domain, 'A')
        a_records = sorted(set([a.to_text() for a in answer]))
        result['has_server_ips'] = True
        result['server_ips'] = []
        output.write(t("Success: Found XXX servers:\n").replace("XXX", str(len(a_records))))
        for i, ip in enumerate(a_records):
            if len(BLOCKED_NETWORKS):
                try:
                    output.write(f"\t{i+1}. Server: {ip}\t")
                    if is_blocked_ip(ip):
                        output.write(t("The IP belongs to a blocked network. Skipping it.\n"))
                        continue
                    else:
                        result['server_ips'].append(ip)
                        output.write("\n")
                except Exception as e:
                    print(f"Failed to validate IP address: {ip}")
                    continue
    except dns.resolver.NoAnswer as e:
        print(e)
        output.write(t("Error: No IPv4 addresses were found for XXX.\n").replace("XXX", domain))
        result['has_server_ips'] = False
        outstr = output.getvalue()
        log_event({'outstr': outstr, 'result':result},type="result", domain=domain)
        return outstr, result
    except dns.exception.DNSException as e:
        print(e)
        output.write(t("Error: A DNS resolving error occurred. Please try again later.\n"))
        outstr = output.getvalue()
        log_event({'outstr': outstr, 'result':result},type="result", domain=domain)
        return outstr, result
    except Exception as e:
        print(e)
        output.write(t("Error: An unexpected error occurred. Please try again later.\n"))
        outstr = output.getvalue()
        log_event({'outstr': outstr, 'result':result},type="result", domain=domain)
        return outstr, result

    if not result['server_ips']:
        output.write(t("Error: No servers with an IPv4 address were found."))
        outstr = output.getvalue()
        log_event({'outstr': outstr, 'result':result},type="result", domain=domain)
        return outstr, result

    # Obtain SSH Fingerprints from associated servers
    output.write("\n")
    output.write(t("Obtaining SSH fingerprints from the servers...\n"))
    server_sshfpd = SSHFPDomain(timestamp=int(time.time()), domain=dns_sshfpd.domain)
    sshfp_comp = SSHFPComparison(domain=dns_sshfpd.domain, dns_sshfp=dns_sshfpd, server_sshfp=server_sshfpd)
    errors = []
    result['server_sshfps'] = {}
    for i, ip in enumerate(result['server_ips']):
        try:
            output.write(f"{t('Contacting')} {i+1}. {t('server')} ({ip})...\n")
            # https://linux.die.net/man/1/ssh-keyscan
            proc = subprocess.run(['ssh-keyscan', '-D', '-4','-t', 'dsa,rsa,ecdsa,ed25519','-T','5', ip], capture_output=True)
            if proc.returncode > 0:
                output.write(t("\tFailed to contact server using ssh-keyscan.\n"))
                raise Exception(f"{t('SSH-Keyscan failed for')} domain={dns_sshfpd.domain} and ip={ip}")

            server_records = sorted(set(map(lambda q: re.sub(r'.*?IN SSHFP\s+','', q), filter(lambda x: len(x)>0 and 'IN SSHFP' in x, proc.stdout.decode().split('\n')))))
            if len(server_records) == 0:
                output.write(t("\tFailed to find SSH fingerprints using ssh-keyscan for this host.\n"))
                raise Exception(t("SSH-Keyscan returned no fingerprints"))


            result['server_sshfps'][ip] = {}

            result['server_sshfps'][ip]['raw'] = server_records
            result['server_sshfps'][ip]['parsed'] = []

            for j, record in enumerate(server_records):
                output.write(f"\t{j+1}. {t('raw SSH fingerprint')}: {record}\n")

            output.write(t("Parsing XXX. server's raw SSH fingerprints...\n").replace("XXX", str(i+1)))
            for j, record in enumerate(server_records):
                try:
                    sshfp = SSHFP.from_string(record)
                    sshfp.timestamp = int(time.time())
                    sshfp.domain = ip
                    server_sshfpd.records.append(sshfp)
                    result['server_sshfps'][ip]['parsed'].append(sshfp)
                    output.write(f"\t{j+1}. {t('parsed SSH fingerprint')}: ALGO={sshfp.algo_stringified()}\tHASH={sshfp.type_stringified()}\tFINGERPRINT={sshfp.fingerprint}\n")
                except Exception as e:
                    output.write(f"\t{j+1}. {t('This fingerprint appears to be invalid and could not be parsed.')}\n")
                    errors.append(f"{t('Failed to parse fingerprint')} {record}\n")

            if len(result['server_sshfps'][ip]['raw']) == len(result['server_sshfps'][ip]['parsed']):
                result['server_sshfps'][ip]['records_valid'] = True
            else:
                result['server_sshfps'][ip]['records_valid'] = False

        except Exception as e:
            errors.append(t("Analysis failed for server with ip=XXX with error e=YYY").replace("XXX",ip).replace("YYY",str(e)))
    sshfp_comp.errors=errors
    output.write(''.join(sshfp_comp.errors))

    if not result['server_sshfps']:
        output.write(t("No server-side SSH fingerprints could be found.\n"))
        outstr = output.getvalue()
        log_event({'outstr': outstr, 'result':result},type="result", domain=domain)
        return outstr, result

    for i, ip in enumerate(result['server_sshfps'].keys()):
        result['server_sshfps'][ip]['matching'] = []
        result['server_sshfps'][ip]['mismatching'] = []

        output.write(t("Comparing DNS and XXX. server's SSH fingerprints...\n").replace("XXX", str(i+1)))
        for h_sshfp in result['server_sshfps'][ip]['raw']:
            if h_sshfp in result['dns_sshfps_raw']:
                result['server_sshfps'][ip]['matching'].append(h_sshfp)
                output.write(f"\t{t('Match')}: {h_sshfp}\n")
            else:
                result['server_sshfps'][ip]['mismatching'].append(h_sshfp)
                output.write(f"\t{t('Mismatch')}: {h_sshfp}\n")
        output.write(f"\t=> {t('Matching')}: {len(result['server_sshfps'][ip]['matching'])}, {t('Mismatching')}: {len(result['server_sshfps'][ip]['mismatching'])}")


    outstr = output.getvalue()

    log_event({'outstr': outstr, 'result':result},type="result", domain=domain)
    return outstr, result

@app.route("/", methods=['GET'])
#@auth.login_required
def index():
    token = None
    try:
        token = request.args.get('t', None)
    except Exception as e:
        pass

    if token is None:
        log_event({'message':"Redirecting from index to faq"},type="page")
        return redirect(url_for('faq'))
    else:
        return redirect(url_for('login', t=token.lower()))

@app.route('/login', methods=['GET'])
def login():
    token = None
    try:
        token = request.args.get('t', None)
        if token == '':
            flash(t("The token was not found."),'danger')
    except Exception as e:
        pass

    if not token:
        return render_template("login.html")

    token = token.lower()

    if not token in app.tokens:
        flash(t("The token was not found."),'danger')
        return render_template("login.html")

    session['token'] = token
    g.token = token
    flash(t("You can use the website now."), 'success')
    log_event({'message':"Login successful"},type="login")

    # Since we only have the tool group, we can redirect there directly
    return redirect(url_for('tool'))
#    return render_template("login.html")

@app.route("/tool", methods=['GET', 'POST'])
#@auth.login_required
def tool():
    prefill = None
    try:
        prefill = base64.b64decode(request.args.get('d', None)).decode().strip()
    except Exception as e:
        pass

    if request.method == "GET":
        if prefill:
            log_event(f"Website loaded with prefill d={prefill}",type="prefill", domain=prefill)
        else:
            log_event(f"Website loaded without prefill",type="pageload")
        return render_template("tool.html",prefill=prefill)

    elif request.method == 'POST':
        log_event({'message':"Starting tool"},type="tool")
        output, result = check_domain(request, prefill=prefill)
        return render_template("tool.html",output=output, result=result, prefill=prefill)


@app.route("/faq", methods=['GET'])
#@auth.login_required
def faq():
    log_event({'message':"Viewing page: faq"},type="page")
    return render_template("faq.html")

@app.route("/legal", methods=['GET'])
#@auth.login_required
def legal():
    log_event({'message':"Viewing page: legal"},type="page")
    if 'IMPRESSUM_LINK' in os.environ:
        return redirect(os.environ['IMPRESSUM_LINK'])
    else:
        raise Exception("No Impressum link")


@app.route("/language", methods=['GET'])
#@auth.login_required
def language():
    app.jinja_env.cache = {}
    resp = make_response(redirect(url_for("index")))

    default_lang = os.environ.get("WEBSITE_DEFAULT_LANGUAGE", list(app.languages.keys())[0])
    language = request.args.get("lang",default_lang)
    if not language in app.languages:
        language = default_lang

    resp.set_cookie("lang", language)
    log_event({'message': f"Changing language {language}"},type="language")

    return resp

@app.route("/logout", methods=['GET'])
#@auth.login_required
def logout():
    if 'token' in session:
        del session['token']
        g.token = None
    flash(t("You have been successfully logged out."), 'success')
    log_event({'message':"Viewing page: logout"},type="page")
    return redirect(url_for('index'))

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == "__main__":
    app.run(debug=False if os.environ.get('DEBUG', False) in ["0",0,False,"False", "false"] else True,host='0.0.0.0',port='8000')
