#!/bin/bash
set +x
# Replace <iface> with the outgoing (internet connected?) interface name

iptables -A OUTPUT -o <iface> -d 10.0.0.0/8 -j REJECT
iptables -A OUTPUT -o <iface> -d 172.16.0.0/12 -j REJECT
iptables -A OUTPUT -o <iface> -d 192.168.0.0/16 -j REJECT
# Add more CIDR ranges if needed.