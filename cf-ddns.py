#!/usr/bin/python3
# Update a set of A records in Cloudflare with the network public IP address
#
# @author Trinh Phuoc Thai <tphuocthai@gmail.com>
#
import subprocess, json, time
from http.client import HTTPSConnection

config = json.loads(open('___CONF_FILE___', 'r').read())

headers = {
    'Content-Type': "application/json",
    'Cache-Control': "no-cache"
}

if 'cf_token' in config:
    headers['Authorization'] = f"Bearer {config['cf_token']}"
else:
    headers = headers | {
        'X-Auth-Email': config['cf_email'],
        'X-Auth-Key': config['cf_api_key'],
    }

conn = HTTPSConnection("api.cloudflare.com")

def log(message):
    # print(f"LOG: {message}")
    with open(config['log_file'], "a") as myfile:
        myfile.write("[%s] %s\n" % (time.strftime("%d/%m/%Y - %H:%M:%S"), message))


def get_records(zone_id):
    url = f"/client/v4/zones/{zone_id}/dns_records?type=A"
    conn.request("GET", url, headers=headers)
    res = conn.getresponse()
    data = json.loads(res.read())

    if data['success'] == False:
        log(f"Error getting zone data {zone_id}")
        return {}
    return { record["name"]: record["id"] for record in data["result"] }


def update_dns_record(zone_id, domain, record_id, new_ip):
    "Send the DNS update request to Cloudflare API"

    url = f"/client/v4/zones/{zone_id}/dns_records/{record_id}"
    payloads = json.dumps({
        "content": new_ip,
        "type": "A",
    })

    conn.request('PATCH', url, body=payloads, headers=headers)
    resp = conn.getresponse()
    data = resp.read()

    dns_response = json.loads(data)
    if dns_response['success'] == False:
        log(f"Error Setting IP for {domain}")
        log("%s: %s" % (dns_response['errors'][0]['message'], data))
        raise Exception(f"Error Setting IP for {domain}")
    log(f"%s IP updated to %s" % (domain, new_ip))


# Main script
def main():
    # Find the old IP
    try: old_ip = open(config['ip_file'], 'r').read()
    except: old_ip = ""

    # Find the new IP
    new_ip = subprocess.check_output(["dig", "+short", "myip.opendns.com", "@208.67.222.222"]).strip().decode()

    # If IP changed or no IP File, update IP File and send requests to Cloudflare API
    if new_ip == old_ip:
        log(f"IP not changed: {new_ip}")
        return
    
    # Do update for each zone
    for zone_id, domains in config['zones'].items():
        # Get dns record datas
        records = get_records(zone_id)
        for domain in domains:
            if domain not in records:
                log(f"Domain {domain} not found in zone {zone_id}")
                continue
            update_dns_record(zone_id, domain, records[domain], new_ip)

    # Save current IP
    with open(config['ip_file'], 'w') as f:
        f.write(new_ip)


if __name__ == '__main__':
    main()
