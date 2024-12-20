#!/bin/bash

source .env

ssh -i "$KEY_PATH" -t "$USER@$HOST" << EOF
    sudo certbot delete --noninteractive --cert-name ${WEB_DOMAIN}
    sudo certbot delete --noninteractive --cert-name www.${WEB_DOMAIN}
    sudo certbot certonly --standalone --agree-tos --domains ${WEB_DOMAIN} --domains www.${WEB_DOMAIN} --email ${EMAIL}
    sudo cp /etc/letsencrypt/live/${WEB_DOMAIN}/fullchain.pem /home/ubuntu/projects/${GIT_REPO}/certs
    sudo cp /etc/letsencrypt/live/${WEB_DOMAIN}/privkey.pem /home/ubuntu/projects/${GIT_REPO}/certs
EOF