CloudFlare Dynamic DNS
=======================

Script to update dynamic DNS to CloudFlare DNS service

*------------ OUTDATED -------------*

Install
------------------------
* Automatic installation (tested using ubuntu/debian)
Get your cloudflare key and email address before process.

```
wget https://raw.githubusercontent.com/tphuocthai/cf-ddns/master/install.sh
chmod +x install.sh
sudo ./install.sh
```

* Manual Install
See ```install.sh``` for more information

Config your hosts file
-------------------------

Enter host need to be update line by line to ```/etc/cf-ddns/hosts``` as following structure
```
<id>:<name>:<domain>
```

To get record's ```id``` see [```rec_load_all```](https://www.cloudflare.com/docs/client-api.html#s3.3) section from [here](https://www.cloudflare.com/docs/client-api.html)