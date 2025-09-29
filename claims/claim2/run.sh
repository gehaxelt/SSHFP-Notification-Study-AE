#!/bin/bash
set -e

for cmd in docker gzip; do
    if ! command -v "$cmd" >/dev/null 2>&1; then
        echo "Error: '$cmd' is required but not installed." >&2
        echo 'You might need install the docker engine and the docker compose extension and gzip'
        exit 1
    fi
done

echo "Changing into artifact/02-scanning-tool"
cd ../../artifact/02-scanning-tool/
echo $PWD
echo;

echo "Building docker containers"
echo "!! Ensure you can run 'sudo docker' otherwise things might fail."
sudo docker compose build
echo;

echo "Ensuring no containers run"
sudo docker compose down
echo;

echo "Starting DNS resolver containers in the background"
sudo docker compose up -d recursor dnssecrecursor
echo "Waiting 30s for containers to come up"
sleep 30s
echo;

echo;
echo "### We will use collector/data/domains.txt with only 10k domains to speed things up."
echo "### To use the tranco list, change the DOMAINFILE value in the docker-compose.yml to '/data/tranco_G8KK.csv'"
echo;

echo "Starting the scanning tool now."
echo "Wait for it to finish. You track its performance with: tail -f collector/data/logs/current/*.log or watch -n5 'wc -l collector/data/logs/current/*.log'"
sudo docker compose up collector --force-recreate
echo;

echo "The scan finished. We should have some data in collector/data/logs/current now."
ls -lha collector/data/logs/current
ls -lha collector/data/logs/current/
echo;

echo "Lets compress the files for our analysis tools."
(
set -x;
cd collector/data/logs; 
cat current/certstream.log | gzip > current/certstream.log.new.gz;
cat current/domainfile.log | gzip > current/domainfile.log.new.gz;
cat current/parser.log | gzip > current/parser.log.new.gz;
cat current/query.log  | gzip > current/query.log.new.gz ;
cat current/server.log | gzip > current/server.log.new.gz;
)
echo;
echo "You should see some compressed files now:"
ls -lha collector/data/logs/current/
echo;

echo "Let's run the analysis. Remember: If there are too few detected misconfigured SSHFP setups in the 10k domains.txt, the analysis might not report any findings."
sudo docker compose up analysis --build
echo;

echo "You should see some data in the figures/ and results/ folder:"
ls -lha collector/data/analysis/*_current/
ls -lha collector/data/analysis/*_current/figures/
ls -lha collector/data/analysis/*_current/results