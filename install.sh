#!/bin/bash

# CloudFlare DDNS setup

CFG_FILE=/etc/cf-ddns/cf-ddns.conf

read -p "Please provide your CloudFlare email? " CF_EMAIL;
read -p "Please provide your CloudFlare access key? " CF_KEY;

# Create config file
mkdir -p /etc/cf-ddns
echo "CF_EMAIL=$CF_EMAIL" > $CFG_FILE
echo "CF_KEY=$CF_KEY" >> $CFG_FILE
echo "WAN_IP_FILE=$HOME/.cf-ddns-wanip.log" >> $CFG_FILE

apt-get install curl
# Download script
curl -o /usr/sbin/cf-ddns.sh https://raw.githubusercontent.com/tphuocthai/cf-ddns/master/cf-ddns.sh
chmod +x /usr/sbin/cf-ddns.sh

# Install cronjob
echo "*/5 *    * * *    root    /usr/sbin/cf-ddns.sh >/dev/null 2>&1" > /etc/cron.d/cf-ddns
chmod +x /etc/cron.d/cf-ddns
service cron restart