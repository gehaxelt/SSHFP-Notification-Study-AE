#!/bin/bash
set -e

for cmd in docker; do
    if ! command -v "$cmd" >/dev/null 2>&1; then
        echo "Error: '$cmd' is required but not installed." >&2
        echo 'You might need install the docker engine and the docker compose extension'
        exit 1
    fi
done

echo "Changing into artifact/03-... folder/pre-scan/"
cd ../../artifact/03-analysis-scripts/pre-scan/
echo $PWD
echo;

echo "Building docker containers"
echo "!! Ensure you can run 'sudo docker' otherwise things might fail."
sudo docker compose build
echo;

echo "Ensuring no containers run"
sudo docker compose down
echo;

echo "Lets run 01-analyze-serverlog-analysis-notifications.py"
sudo docker compose up analyze-logs
echo; echo "There should be a notification-data.csv in 03-analysis-scripts/pre-scan/ now."
ls -lha notification-data.csv
echo;

echo "Lets run 02-find-cnames.py. Attention: The two example.{org/com} domains do not use cnames. Thus, you might want to replace any of the subdomains in notification-data.csv with one that uses a CNAME record."
sudo docker compose up find-cnames
echo; echo "There should be a domains-with-cnames.csv in 03-analysis-scripts/pre-scan/ now."
ls -lha domains-with-cnames.csv
echo;

echo "Lets run 03-check-securitytxt.py. Attention: The two example.{org/com} domains do not use security.txt files. Thus, you might want to replace any of the subdomains in notification-data.csv with one that uses a security.txt."
sudo docker compose up check-securitytxt
echo; echo "There should be a 05-securitytxt.json and a folder securitytxt/ in 03-analysis-scripts/pre-scan/ now."
ls -lha securitytxt
ls -lha 05-securitytxt.json
echo;

echo "Lets run 04-gen-tokens.py."
sudo docker compose up gen-tokens
echo; echo "There should be a 'tokens.json' file and the output should look like expected/token-config.output"
ls -lha tokens.json
echo;