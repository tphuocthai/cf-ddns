#!/usr/bin/python

# Update a set of A records in Cloudflare with the machine current IP address
#
# If you don't know your domain information (like id), you should run:
#
#  curl https://www.cloudflare.com/api_json.html \
#  -d 'a=rec_load_all' \
#  -d 'tkn=CLOUDFLARE_TOKEN' \
#  -d 'email=MY_EMAIL' \
#  -d 'z=DOMAIN' >> response.json;
#
# In the response.json file you can find all DNS records for the domain.
# Make sure this script runs on a cron job or whenever you get a new IP.
#
# Based on Aaron Rice : cloudflare_dynamic_dns.py (https://gist.github.com/riceo/2401865)
#
# @author Bernardo Rittmeyer <bernardo@rittme.com>
# @author Trinh Phuoc Thai <tphuocthai@gmail.com>

import urllib
import json
import time

IP_FILE_NAME = '/var/log/cf-ddns/wanip.log'     # Path to the file that contains the actual/old IP address
LOG_FILE_NAME = '/var/log/cf-ddns/logfile.log'  # Path to the log file
TOKEN = "YOUR_API_KEY" # Your cloudflare token
EMAIL = "YOUR_EMAIL"                  # Your cloudflare account email

# This tuple should have a dictionary for each domain you want to keep up to date
domains = (
  {
    "z"             : "example.com",  # zone_name
    "id"            : "424754044",      # rec_id
    "name"          : "name",            # name
    "service_mode"  : 1                 # Status of CloudFlare Proxy, 1 = orange cloud, 0 = grey cloud.
  }, )

# External IP Address services we use to find our IP Address (if the first fail we use the next one, and so on)
services = ("http://ip.appspot.com/", "http://my-ip.heroku.com/", "http://icanhazip.com", "http://checkip.dyndns.org", "http://curlmyip.com")

def log(message):
  with open(LOG_FILE_NAME, "a") as myfile:
    myfile.write("[%s] %s\n" % (time.strftime("%d/%m/%Y - %H:%M:%S"), message))

def ddns_update(new_ip):
  "Send the DNS update request to Cloudflare API"
  data = {
    "a"             : "rec_edit",
    "tkn"           : TOKEN,
    "email"         : EMAIL,
    "type"          : "A",
    "content"       : new_ip.strip(),
    "ttl"           : 1
  }

  for d in domains:
    d.update(data)
    try:
      dns_response = json.loads(urllib.urlopen("https://www.cloudflare.com/api_json.html", urllib.urlencode(d)).read())

      if dns_response[u'result'] == 'success':
        log("%s IP updated to %s" % (d['name']+"."+d['z'], new_ip))
      else:
        log("Error Setting IP for %s" % d['name']+"."+d['z'])
    except:
      log("Error with cloudflare API")


#Main script

#Find the new IP
new_ip = ""
for s in services:
  try:
    new_ip = urllib.urlopen(s).read()
  except Exception:
    pass
  if new_ip:
    break

#Find the old IP
old_ip = ""
noFile = False
try:
  with open(IP_FILE_NAME, 'r') as f:
    old_ip = f.read()
except IOError:
   noFile = True

# If IP changed or no IP File, update IP File and send requests to Cloudflare API
if new_ip != old_ip or noFile:
  with open(IP_FILE_NAME,'w') as f:
    f.write(new_ip)
  ddns_update(new_ip)
