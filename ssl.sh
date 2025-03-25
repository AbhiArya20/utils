#!/bin/bash

set -e
# Define your domain and email variables here
DOMAIN="your_domain"
EMAIL="your_email"

# Check if domain and email are set
if [ -z "$DOMAIN" ] || [ -z "$EMAIL" ]; then
    echo "Please set the DOMAIN and EMAIL variables in the script."
    exit 1
fi
# Obtain SSL certificate
echo "Obtaining SSL certificate for $DOMAIN..."
if [ ! -f /etc/letsencrypt/live/admin.mithilastack.com/fullchain.pem ]; then
    echo "Generating SSL certificates..."
    # Add your SSL certificate generation command here
    certbot --nginx -d "$DOMAIN" --email "$EMAIL" --agree-tos --non-interactive
else
    echo "SSL certificates already exist."
fi

echo "SSL certificate obtained for $DOMAIN."

# Set up automatic renewal
# echo "Setting up automatic renewal..."
# echo "0 12 * * * /usr/bin/certbot renew --quiet --nginx" | crontab -

# nginx -s reload

nginx -g 'daemon off;'

# # Start cron
# cron
