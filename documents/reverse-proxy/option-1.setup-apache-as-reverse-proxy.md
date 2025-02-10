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
