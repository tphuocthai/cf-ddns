#!/usr/bin/python
# CloudFlare DDNS setup

import requests, json, os

LOG_DIR = '/var/log/cf-ddns'
CONF_DIR = '/etc/cf-ddns'
CFG_FILE = CONF_DIR + '/config.json'

# Ensure directories exists
if not os.path.exists(CONF_DIR):
  os.makedirs(CONF_DIR)

if not os.path.exists(LOG_DIR):
  os.makedirs(LOG_DIR)

# User credentials input
cf_email = raw_input("Please provide your CloudFlare email? ")
cf_token = raw_input("Please provide your CloudFlare access token? ")

headers = {
  'content-type': "application/json",
  'x-auth-email': cf_email,
  'x-auth-key': cf_token,
  'cache-control': "no-cache"
}

def get_records(zone_id, domain):
  print "Fetching records for domain %s" % (domain)
  url = "https://api.cloudflare.com/client/v4/zones/" + zone_id + "/dns_records"
  querystring = {"type":"A"}
  resp = json.loads(requests.get(url, headers=headers, params=querystring).text)
  if resp['success'] == False:
    return ''

  dns_name = []
  for dns in resp['result']:
    choice = raw_input("\tDo you want to update %s (y/N)?: " % dns['name'])
    if choice == 'Y' or choice == 'y':
      dns_name.append(dns['name'])
  print ""
  return ','.join(dns_name)


def records_choice():
  domains = raw_input("Enter your domain name (single or comma separated): ")
  url = 'https://api.cloudflare.com/client/v4/zones'
  querystring = {"status": "active", "name": domains}
  resp = json.loads(requests.get(url, headers=headers, params=querystring).text)
  if resp['success'] == False:
    return

  domain_records = {}
  for z in resp['result']:
    entries = get_records(z['id'], z['name'])
    if len(entries) > 0:
      domain_records[z['id']] = entries
  return domain_records

config_data = {
  'cf_email': cf_email,
  'cf_token': cf_token,
  'ip_file': LOG_DIR + '/wanip.log',
  'log_file': LOG_DIR + '/logfile.log',
  'domains': records_choice()
}

# Create config file
with open(CFG_FILE, 'w') as f:
  f.write(json.dumps(config_data, indent=2, sort_keys=True))

# Download script
script_content = requests.get('https://raw.githubusercontent.com/tphuocthai/cf-ddns/master/cf-ddns.py').text
script_path = '/usr/sbin/cf-ddns.py'
with open(script_path, 'w') as f:
  f.write(script_content.replace('___CONF_FILE___', CFG_FILE))
os.chmod(script_path, 0755)

# Install cronjob
cron_path = '/etc/cron.d/cf-ddns'
with open(cron_path, 'w') as f:
  f.write("*/5 *    * * *    root    %s >/dev/null 2>&1\n" % (script_path))
os.chmod(cron_path, 0755)
