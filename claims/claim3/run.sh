#!/bin/bash
set -e

for cmd in docker; do
    if ! command -v "$cmd" >/dev/null 2>&1; then
        echo "Error: '$cmd' is required but not installed." >&2
        echo 'You might need install the docker engine and the docker compose extension'
        exit 1
    fi
done

echo "Changing into artifact/04-... folder"
cd ../../artifact/04-selftest-tool/
echo $PWD
echo;

echo "Copying tokens.json.sample to tokens.json"
cp image-web/app/tokens.json.sample image-web/app/tokens.json

echo "Replacing 'YOURDOMAIN.TLD' with 'example.com' and 'DOMAIN1.TLD' with 'example.org'"
sed -i image-web/app/tokens.json -e 's/YOURDOMAIN.TLD/example.com/g'
sed -i image-web/app/tokens.json -e 's/DOMAIN1.TLD/example.org/g'
cat image-web/app/tokens.json
echo;

echo "Copying environment-web.env.sample to environment-web.env"
cp environment-web.env.sample environment-web.env

echo "Building docker containers"
echo "!! Ensure you can run 'sudo docker' otherwise things might fail."
sudo docker compose build
echo;

echo "Ensuring no containers run"
sudo docker compose down
echo;

echo "Starting the self-test-tool containers in the background"
sudo docker compose up -d
echo "Wait for 30s"
sleep 30s
echo;

echo "You should be able to visit http://localhost:8000/ now and use the Selftest-tool with the tokens 'secrettoken1' for example.com and 'secrettoken2' for example.org"
echo "If asked for basic authentication, use the credentials configured in the 'environment-web.env': ssh/[YOURSTRONGPASSWORD] "
echo "Then you can click on Self-test tool and login with the secrettokens. Scan the domains SUB1.example.com or example.org"