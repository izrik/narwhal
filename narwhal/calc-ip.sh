#!/bin/bash

/sbin/ifconfig | grep '\<inet\>' | grep -v '127.0.0.1' | awk '{print $2}' | sed 's/[^01-9\.]//g' | head -n 1
