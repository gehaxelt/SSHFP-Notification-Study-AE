#!/bin/bash
check_command() {
    local cmd=$1
    if command -v "$cmd" >/dev/null 2>&1; then
        echo "$cmd is installed: $($cmd --version 2>/dev/null | head -n 1)"
    else
        echo "$cmd is NOT installed."
    fi
}

echo "# System"
# Check the /etc/os-release file for distribution information
if [ -f /etc/os-release ]; then
    . /etc/os-release
    case "$ID" in
        debian)
            echo "This system is Debian."
            ;;
        ubuntu)
            echo "This system is Ubuntu."
            ;;
        arch)
            echo "This system is Arch Linux."
            ;;
        *)
            echo "This system is not Debian, Ubuntu, or Arch Linux. Detected: $ID"; exit 1;
            ;;
    esac
else
    echo "/etc/os-release not found. Unable to determine system."
    exit 1
fi
echo;

cat <<EOF 
# Requirements
- Please ensure you have 'docker' and 'docker compose' installed.
EOF

# Check for Docker
check_command docker

# Check for Docker Compose (new plugin syntax: docker compose, old binary: docker-compose)
if docker compose version >/dev/null 2>&1; then
    echo "Docker Compose (plugin) is installed: $(docker compose version | head -n 1)"
elif command -v docker-compose >/dev/null 2>&1; then
    echo "Docker Compose (standalone) is installed: $(docker-compose --version)"
else
    echo "Docker Compose is NOT installed."
fi
echo;

cat <<EOF
- Please ensure your environment has 'xz', 'gzip', 'wc', 'cat' available.
EOF
check_command xz
check_command gzip
check_command wc
check_command cat
echo;

cat <<EOF
# Claims
- There is no automatic execution of all claims.
- Please execute the 'run.sh' after changing into the individual claims{1..4} folders

Thank you!
EOF
