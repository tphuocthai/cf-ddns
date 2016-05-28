#!/usr/bin/python

# Update a set of A records in Cloudflare with the network public IP address
#
# If you don't know your domain id, you should run:
#
#  curl -X GET "https://api.cloudflare.com/client/v4/zones?name=domain.com" \
#       -H "Content-Type: application/json" 
#       -H "X-Auth-Email: EMAIL" 
#       -H "X-Auth-Key: TOKEN" >> response.json;
#
# In the response.json file you will find the zone_id of given domain.
# Make sure this script runs on a cron job or whenever you get a new IP.
#
# @author Trinh Phuoc Thai <tphuocthai@gmail.com>

import requests
import subprocess
import json
import time

IP_FILE_NAME = '/var/log/cf-ddns/wanip.log'     # Path to the file that contains the actual/old IP address
LOG_FILE_NAME = '/var/log/cf-ddns/logfile.log'  # Path to the log file

TOKEN = "YOUR_API_KEY"                # Your cloudflare token
EMAIL = "YOUR_EMAIL"                  # Your cloudflare account email

# List of record names by zone_id
domains = {
  'zone_id_hashed': 'comma separated names without space'
}

headers = {
  'content-type': "application/json",
  'x-auth-email': EMAIL,
  'x-auth-key': TOKEN,
  'cache-control': "no-cache"
}

def log(message):
  with open(LOG_FILE_NAME, "a") as myfile:
    myfile.write("[%s] %s\n" % (time.strftime("%d/%m/%Y - %H:%M:%S"), message))


def get_records(zone_id):
  url = "https://api.cloudflare.com/client/v4/zones/" + zone_id + "/dns_records"
  querystring = {"type":"A", "name": domains[zone_id]}
  resp = requests.get(url, headers=headers, params=querystring)
  return json.loads(resp.text)


def update_dns_records(records, new_ip):
  "Send the DNS update request to Cloudflare API"

  for rec in records:
    url = "https://api.cloudflare.com/client/v4/zones/" + rec['zone_id'] + "/dns_records/" + rec['id']
    payloads = {
      "content": new_ip,
      "type":"A",
      "name": rec['name']
    }
    dns_response = json.loads(requests.put(url, data=json.dumps(payloads), headers=headers).text)

    if dns_response['success'] == True:
      log("%s IP updated to %s" % (rec['name'], new_ip))
    else:
      log("Error Setting IP for %s" % rec['name'])
      log('%s: %s' % (dns_response['errors'][0]['message'], json.dumps(dns_response)))



# Main script
# Find the new IP
new_ip = subprocess.check_output(["dig", "+short", "myip.opendns.com", "@resolver1.opendns.com"]).strip()

# Find the old IP
try: old_ip = open(IP_FILE_NAME, 'r').read()
except IOError: old_ip = ""

# If IP changed or no IP File, update IP File and send requests to Cloudflare API
if new_ip != old_ip:
  with open(IP_FILE_NAME, 'w') as f:
    f.write(new_ip)

  # Do update for each zone
  for key in domains:
    # Get dns record datas
    zone_data = get_records(key)
    if zone_data['success'] == False:
      log("Error getting zone data %s" % key)
      continue

    dns_response = update_dns_records(zone_data['result'], new_ip)
