#!/bin/bash

eval `ssh-agent`
ssh-keyscan -H github.com >> ~/.ssh/known_hosts
ssh-add /nimbus/id_rsa

certbot renew
cd /api-certificates
git pull
tar cvf /api-certificates/letsencrypt_backup.tar /etc/letsencrypt
git add .
# `date` will print the date like this: Sun May 10 15:22:23 PDT 2020
git commit -m "automated upload from google cloud on `date`"
git push