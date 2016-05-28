#!/usr/bin/python
# Update a set of A records in Cloudflare with the network public IP address
#
# @author Trinh Phuoc Thai <tphuocthai@gmail.com>
#

import requests
import subprocess
import json
import time

config = json.loads(open('___CONF_FILE___', 'r').read())

headers = {
  'content-type': "application/json",
  'x-auth-email': config['cf_email'],
  'x-auth-key': config['cf_token'],
  'cache-control': "no-cache"
}

def log(message):
  with open(config['log_file'], "a") as myfile:
    myfile.write("[%s] %s\n" % (time.strftime("%d/%m/%Y - %H:%M:%S"), message))


def get_records(zone_id):
  url = "https://api.cloudflare.com/client/v4/zones/" + zone_id + "/dns_records"
  querystring = {"type":"A", "name": config['domains'][zone_id]}
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
try: old_ip = open(config['ip_file'], 'r').read()
except IOError: old_ip = ""

# If IP changed or no IP File, update IP File and send requests to Cloudflare API
if new_ip != old_ip:
  with open(config['ip_file'], 'w') as f:
    f.write(new_ip)

  # Do update for each zone
  for key in config['domains']:
    # Get dns record datas
    zone_data = get_records(key)
    if zone_data['success'] == False:
      log("Error getting zone data %s" % key)
      continue

    dns_response = update_dns_records(zone_data['result'], new_ip)
