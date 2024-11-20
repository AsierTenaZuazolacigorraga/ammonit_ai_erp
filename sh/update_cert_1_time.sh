#!/bin/bash

source .env

ssh -i "$KEY_PATH" -t "$USER@$HOST" << EOF
    sudo certbot delete --noninteractive --cert-name ${DOMAIN}
    sudo certbot delete --noninteractive --cert-name www.${DOMAIN}
    sudo certbot certonly --standalone --agree-tos --domains ${DOMAIN} --domains www.${DOMAIN} --email ${EMAIL}
    sudo cp /etc/letsencrypt/live/${DOMAIN}/fullchain.pem /home/ubuntu/projects/${REPO}/certs
    sudo cp /etc/letsencrypt/live/${DOMAIN}/privkey.pem /home/ubuntu/projects/${REPO}/certs
EOF