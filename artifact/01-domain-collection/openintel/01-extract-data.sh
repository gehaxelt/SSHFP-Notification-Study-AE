#!/bin/bash

for f in $(find . -type f -name '*.avro'); do
	echo "$f"
	avrocat "$f" | jq ".query_name" | sed 's/"//g' | grep '\.de\.$' | sort -u > "$f.domains"
	wc -l "$f.domains"
done
echo "Merging domain files..."
for f in $(find . -type f -name '*.domains'); do
	cat "$f"
done | sort -u | sed 's/\.$//g' > "top1m-de-domains.txt"
