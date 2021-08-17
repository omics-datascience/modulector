#!/bin/bash
echo "Moving desired configuration to /var/lib/postgresql/data/postgresql.conf"
cat /etc/postgresql/postgresql.conf > /var/lib/postgresql/data/postgresql.conf
