#! /bin/bash
eval `ssh-agent`
# clones current info from the private repo using the ssh key setup on deploy
cd /
# this will setup github's fingerprint so we can ssh in, and setup our keys
mkdir ~/.ssh
ssh-keyscan -H github.com >> ~/.ssh/known_hosts
ssh-add /nimbus/id_rsa
git clone git@github.com:calpoly-csai/api-certificates.git
git config --global user.email "cpcsai.nimbus@gmail.com"
git config --global user.name "GCE_GIT_BOT"
cd /api-certificates
tar xvf letsencrypt_backup.tar -C /
crontab /nimbus/scripts/letsencrypt-backup-tar.cron
# updating the certs is free, and shouldn't actually happen if the above has all
# been successful.  This avoids us not updating if deploys interrupt the update
# from happening.
/bin/bash /nimbus/scripts/cert-update.sh
