CloudFlare Dynamic DNS
=======================

Script to update dynamic DNS to CloudFlare DNS service

Install
------------------------
Prepare your cloudflare key and email address before process. This is tested using ubuntu/debian.

```
wget http://raw.githubusercontent.com/tphuocthai/cf-ddns/master/install.sh
chmod +x install.sh
sudo ./install.sh
```

Config your hosts file
-------------------------

Enter host need to be update line by line to /etc/cf-ddns/hosts as following structure
```
<id>:<name>:<domain>
```
