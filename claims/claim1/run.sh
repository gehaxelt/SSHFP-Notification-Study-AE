#!/bin/bash
set -e

for cmd in xz wc cat; do
    if ! command -v "$cmd" >/dev/null 2>&1; then
        echo "Error: '$cmd' is required but not installed." >&2
        echo 'You might need install "xz-utils" and "coreutils" or similar packages'
        exit 1
    fi
done

echo "# Openintel"
echo "## Number of subdomains:"
xz -dc ../../artifact/01-domain-collection/openintel/extracted-domains.txt.lzma | wc -l

echo "## Number of domains:"
xz -dc ../../artifact/01-domain-collection/openintel/extracted-flds.txt.lzma | wc -l

echo; echo;

echo "# CRT.sh"
echo "## Number of subdomains"
xz -dc ../../artifact/01-domain-collection/crt.sh/extracted-domains.txt.lzma | wc -l 
echo "## Number of domains"
xz -dc ../../artifact/01-domain-collection/crt.sh/extracted-flds.txt.lzma | wc -l 

echo; echo; 

echo "# CertStream"
echo "## Number of subdomains"
xz -dc ../../artifact/01-domain-collection/certstreamde/extracted-domains.txt.lzma | wc -l 
echo "## Number of domains"
xz -dc ../../artifact/01-domain-collection/certstreamde/extracted-flds.txt.lzma | wc -l 

echo; echo; 

echo "# Censys"
echo "## Number of subdomains"
cat ../../artifact/01-domain-collection/censys/extracted-domains.txt.lzma-part-* | xz --format=lzma -dc | wc -l
echo "## Number of domains"
xz -dc ../../artifact/01-domain-collection/censys/extracted-flds.txt.lzma | wc -l 
 
echo; echo; 

echo "# Merged (Total)"
echo "## Number of subdomains"
cat ../../artifact/01-domain-collection/MERGED/extracted-domains.txt.lzma-part-* | xz --format=lzma -dc | wc -l
echo "## Number of domains"
cat ../../artifact/01-domain-collection/MERGED/extracted-flds.txt.lzma | xz --format=lzma -dc | wc -l

echo; echo; 

echo "# Merged (Unique)"
echo "## Number of subdomains"
cat ../../artifact/01-domain-collection/MERGED/unique-extracted-domains.txt.lzma-part-* | xz --format=lzma -dc | wc -l
echo "## Number of domains"
cat ../../artifact/01-domain-collection/MERGED/unique-extracted-flds.txt.lzma | xz --format=lzma -dc | wc -l

echo; echo; 

echo "# Existing"
echo "## Number of subdomains"
cat ../../artifact/01-domain-collection/MERGED/06-existing-domains.txt.lzma-part-* | xz --format=lzma -dc | wc -l
echo "## Number of domains"
cat ../../artifact/01-domain-collection/MERGED/05-existing-flds.txt.lzma | xz --format=lzma -dc | wc -l
