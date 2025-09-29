#!/usr/bin/env python3
import psycopg2
import psycopg2.extras
import time

print("Establishing connection")
conn = psycopg2.connect(dbname="certwatch", user="guest", host="crt.sh", cursor_factory=psycopg2.extras.RealDictCursor)
conn.set_session(readonly=True, autocommit=True)
offset = 165 * 1000 #started at 0 * 1000
limit = 5000
while True:
    try:
        print("Building query: ",offset)
        Q = f"select x509_commonName(certificate) as cn ,x509_altNames(certificate) as an from certificate WHERE x509_commonName(certificate) like '%.de' LIMIT {limit} OFFSET {offset};"
        #Q = f"select x509_commonName(certificate) as cn ,x509_altNames(certificate) as an, x509_notBefore(certificate) as notbefore from certificate WHERE x509_commonName(certificate) like '%.de' LIMIT {limit} OFFSET {offset};"
        cur = conn.cursor()
        print("Executing query ",Q)
        cur.execute(Q)
        with open(f"{offset}.csv", "w") as f:
            for row in cur.fetchall():
                cn = row['cn']
                an = row['an']
                #nb = row['notbefore']
                f.write(f"{cn},{an}\n")
                #f.write(f"{cn},{an},{nb}\n")
        print("Success: ", offset)
    except Exception as e:
        print(offset, e)
        if 'statement timeout' in str(e) or 'conflict with recovery' in str(e):
            continue
        try: 
            print("Establishing connection")
            conn = psycopg2.connect(dbname="certwatch", user="guest", host="crt.sh", cursor_factory=psycopg2.extras.RealDictCursor)
            conn.set_session(readonly=True, autocommit=True)
        except Exception as e:
            continue
        continue
    offset += limit
