CloudFlare Dynamic DNS
=======================

Script to update dynamic DNS to CloudFlare DNS service

### Automatic installation (Recomnended)
Get your cloudflare key and email address before process.

```
sudo apt-get install -y dnsutils
wget https://raw.githubusercontent.com/tphuocthai/cf-ddns/master/install.py
chmod +x install.py
sudo ./install.py
```

### Manual Install
1. Download `https://raw.githubusercontent.com/tphuocthai/cf-ddns/master/cf-ddns.py` and save to `/usr/sbin` folder make it executable
2. Edit that file to replace `___CONF_FILE___` with `/etc/cf-ddns/config.json`
3. Create `/etc/conf.d/cf-ddns` with following content and make it executable

	```
	*/5 *    * * *    root    /usr/sbin/cf-ddns.py >/dev/null 2>&1
	```
4. Create configuation file in `/etc/cf-ddns/config.json`. Here is example content:
	You can provide either just `cf_token` or both (`cf_email` and `cf_api_key`)

	```
	{
	  "cf_token": "your_cloudflare_access_token",
	  "cf_email": "your_cloudflare_email", 
	  "cf_api_key": "your_cf_token_key", 
	  "zones": {
	    "zone_id": ["list","of","dns","names","as","array"]
	  },
	  "ip_file": "/var/log/cf-ddns/wanip.log", 
	  "log_file": "/var/log/cf-ddns/logfile.log"
	}
	```

To obtain `zone_id` and dns record name see [`CloudFlare API V4 Documentation`](https://api.cloudflare.com/)