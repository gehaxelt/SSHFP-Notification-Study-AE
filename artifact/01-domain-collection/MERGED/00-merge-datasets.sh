#!/bin/bash

echo "Merging datasets..."
time cat ../censys/extracted-flds.txt ../certstreamde/extracted-flds.txt ../crt.sh/extracted-flds.txt ../openintel/extracted-flds.txt > extracted-flds.txt
time cat ../censys/extracted-domains.txt ../certstreamde/extracted-domains.txt ../crt.sh/extracted-domains.txt ../openintel/extracted-domains.txt > extracted-domains.txt


