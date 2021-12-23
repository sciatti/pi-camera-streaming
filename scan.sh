#!/usr/bin/env bash

IP_END=$1

for i in {0..255}; do
	#echo "$IP_END$i"
	out=$(ping $IP_END$i -c 1 -W 1 | grep 100%\ packet\ loss | wc -l)
	if [[ $out == "0" ]]; then
		echo "I need to scan $IP_END$i with some other command to find the hostname"
	fi
done	
