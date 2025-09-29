#!/bin/bash

set -x
# cd /home/sshfp/scanning-tool # You might need to change that for the cron job
# Run these commands to initialize the containers and before running the cronjob for periodic scans
# - docker compose build
# - docker compose up -d recursor dnssecrecursor
# Cronjob entry (crontab -e): 0 */6 * * * (cd /home/<user>/scanning-tool; ./run.sh)
docker compose up collector --force-recreate

(
cd collector/data/logs; 
cat current/certstream.log | gzip > current/certstream.log.new.gz;
cat current/domainfile.log | gzip > current/domainfile.log.new.gz;
cat current/parser.log | gzip > current/parser.log.new.gz;
cat current/query.log  | gzip > current/query.log.new.gz ;
cat current/server.log | gzip > current/server.log.new.gz;
)

(
cd collector/data/analysis; 
python3 analysis.py;
)
