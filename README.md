CloudFlare Dynamic DNS
=======================

Script to update dynamic DNS to CloudFlare DNS service

Install
------------------------
* Automatic installation (Recomnended)
Get your cloudflare key and email address before process.

```
wget https://raw.githubusercontent.com/tphuocthai/cf-ddns/master/install.py
chmod +x install.py
sudo ./install.py
```

* Manual Install
- Download `https://raw.githubusercontent.com/tphuocthai/cf-ddns/master/cf-ddns.py` and save to `/usr/sbin` folder make it executable
- Edit that file to replace `___CONF_FILE___` with `/etc/cf-ddns/config.json`
- Create `/etc/conf.d/cf-ddns` with following content and make it executable
	```
	*/5 *    * * *    root    /usr/sbin/cf-ddns.py >/dev/null 2>&1
	```
- Create configuation file in `etc/cf-ddns/config.json`. Here is example content
	```
	{
	  "cf_email": "your_cloundflair_email", 
	  "cf_token": "your_cf_token_key", 
	  "domains": {
	    "zone_id": "list,of,dns,name,separated,by,comma"
	  }, 
	  "ip_file": "/var/log/cf-ddns/wanip.log", 
	  "log_file": "/var/log/cf-ddns/logfile.log"
	}
	```

To obtain `zone_id` and dns record name see [`CloudFlare API V4 Documentation`](https://api.cloudflare.com/)