#!/bin/sh
# 
# CloudFlare Dynamic DNS Update
#

# Import config
. /etc/cf-ddns/cf-ddns.conf

if [ -f $WAN_IP_FILE ]; then
    OLD_WAN_IP=`cat $WAN_IP_FILE`
else
    echo "No file, need IP"
    OLD_WAN_IP=""
fi

WAN_IP=`dig +short myip.opendns.com @resolver1.opendns.com`
if [ "$WAN_IP" = "$OLD_WAN_IP" ]; then
    echo "IP Unchanged"
    exit 1
fi

echo $WAN_IP > $WAN_IP_FILE
echo "Updating DNS to $WAN_IP"

IFS=:
while read id name zone
do
    echo "Updating: $name.$zone"
    curl https://www.cloudflare.com/api_json.html \
      -d "tkn=$CF_KEY" \
      -d "email=$CF_EMAIL" \
      -d "content=$WAN_IP" \
      -d "z=$zone" \
      -d "id=$id" \
      -d "name=$name" \
      -d 'a=rec_edit' \
      -d 'type=A' \
      -d 'ttl=1'
    echo ""
done < /etc/cf-ddns/hosts
