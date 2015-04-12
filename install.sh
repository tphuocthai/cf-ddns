#!/bin/bash

# CloudFlare DDNS setup

FILE=/etc/cf-ddns/cf-ddns.conf

read -p "Please provide your CloudFlare email? " CF_EMAIL;
read -p "Please provide your CloudFlare access key? " CF_KEY;

# Create config file
echo "CF_EMAIL=$CF_EMAIL" > $FILE
echo "CF_KEY=$CF_KEY" >> $FILE

apt-get install curl
# Download script
curl -o /usr/sbin/cf-ddns.sh https://raw.githubusercontent.com/tphuocthai/cf-ddns/master/cf-ddns.sh

# Install cronjob
echo "*/5 *    * * *    root    /usr/sbin/cf-ddns.sh >/dev/null 2>&1" > /etc/cron.d/cf-ddns
chmod +x /etc/cron.d/cf-ddns
service cron restart