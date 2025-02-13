#!/usr/bin/python3
# CloudFlare DDNS setup

import json, os
from urllib.request import urlopen
from http.client import HTTPSConnection

LOG_DIR = '/var/log/cf-ddns'
CONF_DIR = '/etc/cf-ddns'
CFG_FILE = CONF_DIR + '/config.json'

# Ensure directories exists
if not os.path.exists(CONF_DIR):
    os.makedirs(CONF_DIR)

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

headers = {
  'content-type': "application/json",
  'cache-control': "no-cache"
}

config_data = {
    'ip_file': LOG_DIR + '/wanip.log',
    'log_file': LOG_DIR + '/logfile.log',
}

# User credentials input
cf_token = input("Please provide your CloudFlare access token (Leave empty if you want to use Global API Key): ")
if cf_token != '':
    headers['Authorization'] = f"Bearer {cf_token}"
    config_data['cf_token'] = cf_token
else:
    cf_email = input("Please provide your CloudFlare email: ")
    cf_api_key = input("Please provide your CloudFlare access token: ")
    headers = headers | {
        'x-auth-email': cf_email,
        'x-auth-key': cf_api_key,
    }
    config_data = config_data | {
        'cf_email': cf_email,
        'cf_api_key': cf_api_key,
    }

conn = HTTPSConnection("api.cloudflare.com")

def get_records(zone_id, domain):
    print(f"Fetching records for domain {domain}")

    url = f"/client/v4/zones/{zone_id}/dns_records?type=A"
    conn.request("GET", url, headers=headers)
    res = conn.getresponse()
    resp = json.loads(res.read())

    if resp['success'] == False:
        return ''

    dns_name = []
    for dns in resp['result']:
        choice = input("\tDo you want to update %s (y/N)?: " % dns['name'])
        if choice.upper() == 'Y':
            dns_name.append(dns['name'])
    print("")
    return dns_name


def records_choice():
    domains = input("Enter your domain name (single or comma separated): ")
    url = f'/client/v4/zones?status=active&name={domains}'
    conn.request("GET", url, headers=headers)
    res = conn.getresponse()
    resp = json.loads(res.read())

    if resp['success'] == False:
        return

    domain_records = {}
    for z in resp['result']:
        entries = get_records(z['id'], z['name'])
        if len(entries) > 0:
            domain_records[z['id']] = entries
    return domain_records

config_data['zones'] = records_choice()

# # Create config file
with open(CFG_FILE, 'w') as f:
    f.write(json.dumps(config_data, indent=2, sort_keys=True))

# Download script
script_content = ''
with urlopen("https://raw.githubusercontent.com/tphuocthai/cf-ddns/master/cf-ddns.py") as response:
    data = response.read()
    script_content = data.decode("utf-8")

script_path = '/usr/sbin/cf-ddns.py'
with open(script_path, 'w') as f:
    f.write(script_content.replace('___CONF_FILE___', CFG_FILE))
os.chmod(script_path, 0o755)

# Install cronjob
cron_path = '/etc/cron.d/cf-ddns'
with open(cron_path, 'w') as f:
    f.write("*/5 *    * * *    root    %s >/dev/null 2>&1\n" % (script_path))
os.chmod(cron_path, 0o755)
