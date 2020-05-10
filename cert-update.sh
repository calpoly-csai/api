#!/bin/bash

certbot renew
cd /api-certificates
git pull
tar cvf /api-certificates/letsencrypt_backup.tar /etc/letsencrypt
git add .
git commit -m "automated upload from google cloud"
git push