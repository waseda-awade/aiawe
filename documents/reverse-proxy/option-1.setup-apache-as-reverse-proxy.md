# Commands used to setup the server

> This is our current setup.

## Install Docker

``` sh
# Update package lists
sudo apt update

# Install curl
sudo apt install curl

# Install Docker
# https://github.com/docker/docker-install
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Manage Docker as a non-root user
# https://docs.docker.com/engine/install/linux-postinstall/#manage-docker-as-a-non-root-user
sudo groupadd docker
sudo usermod -aG docker $USER
```

## Change Apache configuration

Add new configuration for AiAWE reverse proxy

Create `awe-proxy.conf` in `/etc/apache2/sites-available/`

``` conf
<VirtualHost *:80>
    ServerName app.awade.gec.waseda.ac.jp
    ServerAdmin admin@awade

    ProxyPreserveHost On
    ProxyPass / http://localhost:8001/
    ProxyPassReverse / http://localhost:8001/

    ErrorLog ${APACHE_LOG_DIR}/app-error.log
    CustomLog ${APACHE_LOG_DIR}/app-access.log combined

    RewriteEngine on
    RewriteCond %{SERVER_NAME} =app.awade.gec.waseda.ac.jp
    RewriteRule ^ https://%{SERVER_NAME}%{REQUEST_URI} [END,NE,R=permanent]
</VirtualHost>
```

Create `awe-le-ssl-proxy.conf` in `/etc/apache2/sites-available/`

``` conf
<IfModule mod_ssl.c>
<VirtualHost *:443>
    ServerName app.awade.gec.waseda.ac.jp
    ServerAdmin admin@awade

    ProxyPreserveHost On

    # Add these header forwarding directives
    RequestHeader set X-Forwarded-Proto "https"
    RequestHeader set X-Forwarded-Port "443"
    RequestHeader set X-Forwarded-Host %{HTTP_HOST}s

    ProxyPass / http://localhost:8001/
    ProxyPassReverse / http://localhost:8001/

    ErrorLog ${APACHE_LOG_DIR}/app-error.log
    CustomLog ${APACHE_LOG_DIR}/app-access.log combined

    SSLCertificateFile /etc/letsencrypt/live/app.awade.gec.waseda.ac.jp/fullchain.pem
    SSLCertificateKeyFile /etc/letsencrypt/live/app.awade.gec.waseda.ac.jp/privkey.pem
    Include /etc/letsencrypt/options-ssl-apache.conf
</VirtualHost>
</IfModule>
```

Obtain SSL certificates

``` sh
sudo certbot --apache -d app.awade.gec.waseda.ac.jp
```

Enable Apache modules

``` sh
sudo a2enmod proxy
sudo a2enmod proxy_http
sudo a2enmod rewrite
```

Enable the new configuration

``` sh
sudo a2ensite awe-proxy.conf
sudo a2ensite awe-le-ssl-proxy.conf
sudo systemctl restart apache2
```

# FAQ

## Certificate not renewed properly

> TL;DR: the certbot was miss-configed to use nginx, however we are using apache. Solution: change the config to apache.

### How to fix

Edit the following config file:

``` sh
sudo nano /etc/letsencrypt/renewal/app.awade.gec.waseda.ac.jp.conf
```

``` sh
# renew_before_expiry = 30 days
version = 2.9.0
archive_dir = /etc/letsencrypt/archive/app.awade.gec.waseda.ac.jp
cert = /etc/letsencrypt/live/app.awade.gec.waseda.ac.jp/cert.pem
privkey = /etc/letsencrypt/live/app.awade.gec.waseda.ac.jp/privkey.pem
chain = /etc/letsencrypt/live/app.awade.gec.waseda.ac.jp/chain.pem
fullchain = /etc/letsencrypt/live/app.awade.gec.waseda.ac.jp/fullchain.pem

# Options used in the renewal process
[renewalparams]
account = a21d2dcb1fcf80c92f2050e182ffce89
authenticator = nginx # <------------------- Error here
installer = nginx     # <------------------- Error here
server = https://acme-v02.api.letsencrypt.org/directory
key_type = ecdsa
```

Change these two lines to:

``` sh
authenticator = apache # <------------------- change to this
installer = apache     # <------------------- change to this
```

Test renew with dry-run:
``` sh
oem@wasedaP8:~$ sudo certbot renew --dry-run
Saving debug log to /var/log/letsencrypt/letsencrypt.log

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
Processing /etc/letsencrypt/renewal/app.awade.gec.waseda.ac.jp.conf
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
Simulating renewal of an existing certificate for app.awade.gec.waseda.ac.jp

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
Processing /etc/letsencrypt/renewal/awade.gec.waseda.ac.jp.conf
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
Simulating renewal of an existing certificate for awade.gec.waseda.ac.jp

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
Congratulations, all simulated renewals succeeded:
  /etc/letsencrypt/live/app.awade.gec.waseda.ac.jp/fullchain.pem (success)
  /etc/letsencrypt/live/awade.gec.waseda.ac.jp/fullchain.pem (success)
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
```

### Error message:

``` sh
oem@wasedaP8:~$ sudo certbot renew --dry-run

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
Processing /etc/letsencrypt/renewal/app.awade.gec.waseda.ac.jp.conf
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
Account registered.
Simulating renewal of an existing certificate for app.awade.gec.waseda.ac.jp
Encountered exception during recovery: certbot.errors.MisconfigurationError: nginx restart failed:
nginx: [emerg] bind() to 0.0.0.0:80 failed (98: Address already in use)
nginx: [emerg] bind() to [::]:80 failed (98: Address already in use)
nginx: [emerg] bind() to 0.0.0.0:443 failed (98: Address already in use)
nginx: [emerg] bind() to 0.0.0.0:80 failed (98: Address already in use)
nginx: [emerg] bind() to [::]:80 failed (98: Address already in use)
nginx: [emerg] bind() to 0.0.0.0:443 failed (98: Address already in use)
nginx: [emerg] bind() to 0.0.0.0:80 failed (98: Address already in use)
nginx: [emerg] bind() to [::]:80 failed (98: Address already in use)
nginx: [emerg] bind() to 0.0.0.0:443 failed (98: Address already in use)
nginx: [emerg] bind() to 0.0.0.0:80 failed (98: Address already in use)
nginx: [emerg] bind() to [::]:80 failed (98: Address already in use)
nginx: [emerg] bind() to 0.0.0.0:443 failed (98: Address already in use)
nginx: [emerg] bind() to 0.0.0.0:80 failed (98: Address already in use)
nginx: [emerg] bind() to [::]:80 failed (98: Address already in use)
nginx: [emerg] bind() to 0.0.0.0:443 failed (98: Address already in use)
nginx: [emerg] still could not bind()
Failed to renew certificate app.awade.gec.waseda.ac.jp with error: nginx restart failed:
nginx: [emerg] bind() to 0.0.0.0:80 failed (98: Address already in use)
nginx: [emerg] bind() to [::]:80 failed (98: Address already in use)
nginx: [emerg] bind() to 0.0.0.0:443 failed (98: Address already in use)
nginx: [emerg] bind() to 0.0.0.0:80 failed (98: Address already in use)
nginx: [emerg] bind() to [::]:80 failed (98: Address already in use)
nginx: [emerg] bind() to 0.0.0.0:443 failed (98: Address already in use)
nginx: [emerg] bind() to 0.0.0.0:80 failed (98: Address already in use)
nginx: [emerg] bind() to [::]:80 failed (98: Address already in use)
nginx: [emerg] bind() to 0.0.0.0:443 failed (98: Address already in use)
nginx: [emerg] bind() to 0.0.0.0:80 failed (98: Address already in use)
nginx: [emerg] bind() to [::]:80 failed (98: Address already in use)
nginx: [emerg] bind() to 0.0.0.0:443 failed (98: Address already in use)
nginx: [emerg] bind() to 0.0.0.0:80 failed (98: Address already in use)
nginx: [emerg] bind() to [::]:80 failed (98: Address already in use)
nginx: [emerg] bind() to 0.0.0.0:443 failed (98: Address already in use)
nginx: [emerg] still could not bind()
```
