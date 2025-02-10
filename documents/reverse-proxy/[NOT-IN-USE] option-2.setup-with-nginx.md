# Commands used to setup the server

> [!WARNING] This is an alternative setup.
> We are currently using the Apache setup.

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

``` sh
# Check Apache configuration
# less /etc/apache2/sites-available/wordpress.conf
# less /etc/apache2/sites-available/wordpress-le-ssl.conf

# Change the port to 8000
sudo nano /etc/apache2/sites-available/wordpress.conf
```

Old configuration:

``` conf
<VirtualHost *:80>
        ServerAdmin admin@awade
        DocumentRoot /var/www/html/wordpress
        ServerName awade.gec.waseda.ac.jp
        ServerAlias awade.gec.waseda.ac.jp

        <Directory /var/www/html>
                AllowOverride All
                Require all granted
        </Directory>

        ErrorLog ${APACHE_LOG_DIR}/error.log
        CustomLog ${APACHE_LOG_DIR}/access.log combined
RewriteEngine on
RewriteCond %{SERVER_NAME} =awade.gec.waseda.ac.jp
RewriteRule ^ https://%{SERVER_NAME}%{REQUEST_URI} [END,NE,R=permanent]
</VirtualHost>
```

New configuration:

``` conf
<VirtualHost *:8000>
        ServerAdmin admin@awade
        DocumentRoot /var/www/html/wordpress
        ServerName awade.gec.waseda.ac.jp
        ServerAlias awade.gec.waseda.ac.jp
        <Directory /var/www/html>
                AllowOverride All
                Require all granted
        </Directory>
        ErrorLog ${APACHE_LOG_DIR}/error.log
        CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>
```

Edit the ports file to listen to 8000 with the following command:
 `sudo nano /etc/apache2/ports.conf`

``` conf
# Listen 80
Listen 8000

#<IfModule ssl_module>
#        Listen 443
#</IfModule>
#<IfModule mod_gnutls.c>
#        Listen 443
#</IfModule>
```

``` sh
# disable the SSL module
sudo a2dismod ssl

# disable the SSL site
sudo a2dissite wordpress-le-ssl.conf

# restart apache
sudo systemctl restart apache2

# check status
sudo systemctl status apache2
```

Check ports.

``` sh
# Install net-tools
sudo apt install net-tools

# Check that whether apache is listening to 8000
sudo netstat -tlpn | grep apache2
```


## Setup Nginx

``` sh
# Install Nginx
sudo apt install nginx -y

# Install Certbot for Nginx
sudo apt install certbot python3-certbot-nginx
```

``` sh
# Create a reverse proxy configuration file
sudo nano /etc/nginx/sites-available/reverse-proxy
```

Write the following configuration.

v1:

``` conf
server {
    listen 80;
    listen 443 ssl;
    server_name awade.gec.waseda.ac.jp;

    ssl_certificate /etc/letsencrypt/live/awade.gec.waseda.ac.jp/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/awade.gec.waseda.ac.jp/privkey.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

v2:

``` conf
server {
    listen 80;
    server_name awade.gec.waseda.ac.jp;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name awade.gec.waseda.ac.jp;

    ssl_certificate /etc/letsencrypt/live/awade.gec.waseda.ac.jp/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/awade.gec.waseda.ac.jp/privkey.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        sub_filter 'http://' 'https://';
        sub_filter_once off;
    }
}

server {
    listen 80;
    server_name app.awade.gec.waseda.ac.jp;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name app.awade.gec.waseda.ac.jp;

    # These will be created by Certbot
    # ssl_certificate /etc/letsencrypt/live/app.awade.gec.waseda.ac.jp/fullchain.pem;
    # ssl_certificate_key /etc/letsencrypt/live/app.awade.gec.waseda.ac.jp/privkey.pem;

    location / {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        sub_filter 'http://' 'https://';
        sub_filter_once off;
    }
}
```

Restart Nginx.

``` sh
# Create a symbolic link
sudo ln -s /etc/nginx/sites-available/reverse-proxy /etc/nginx/sites-enabled/

# Test the configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

### Create SSL certificates

``` sh
sudo certbot --nginx -d app.awade.gec.waseda.ac.jp
```

## Other issues

### Fix the mixed content error

Issue:

Contents of the page are loaded over HTTPS, but some resources (css stylesheets, images, etc.) are still pointing to HTTP.

``` error
Mixed Content: The page at 'https://awade.gec.waseda.ac.jp/' was loaded over HTTPS, but requested an insecure stylesheet 'http://awade.gec.waseda.ac.jp/wp-includes/blocks/navigation/style.min.css?ver=6.7.1'. This request has been blocked; the content must be served over HTTPS.
```

Check out this post: [How to fix the mixed content error in WordPress step by step](https://www.wpbeginner.com/plugins/how-to-fix-the-mixed-content-error-in-wordpress-step-by-step/)
