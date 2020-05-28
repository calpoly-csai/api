#!/bin/bash
#
# This script manually deploys to Google Compute Engine
#
#

export GITHUB_SHA=`git rev-parse HEAD`

docker build -t gcr.io/$GCE_PROJECT/$GCE_INSTANCE-image:$GITHUB_SHA \
          --build-arg GITHUB_SHA="$GITHUB_SHA" \
          --build-arg GITHUB_REF="$GITHUB_REF" \
          --build-arg DATABASE_HOSTNAME \
          --build-arg DATABASE_PASSWORD \
          --build-arg DATABASE_USERNAME \
          --build-arg DATABASE_NAME \
          --build-arg PYDRIVE_CLIENT_ID \
          --build-arg PYDRIVE_CLIENT_SECRET \
          --build-arg GOOGLE_DRIVE_CREDENTIALS \
          --build-arg GOOGLE_DRIVE_FOLDER_ID \
          --build-arg GOOGLE_CLOUD_NLP_CREDENTIALS \
          --build-arg GOOGLE_CLOUD_NLP_MODEL_NAME \
          --build-arg GIT_SSH_CERT \
          --build-arg PORT="$SSL_PORT" .

docker push gcr.io/$GCE_PROJECT/$GCE_INSTANCE-image:$GITHUB_SHA

# sleep for 60 seconds to allow gce to restart after deploy
gcloud compute instances update-container $GCE_INSTANCE \
    --zone $GCE_INSTANCE_ZONE \
    --container-image=gcr.io/$GCE_PROJECT/$GCE_INSTANCE-image:$GITHUB_SHA \
    --project=$GCE_PROJECT && sleep 60 && gcloud compute ssh $GCE_INSTANCE --zone=$GCE_INSTANCE_ZONE --project=$GCE_PROJECT --command='docker image prune -a -f'
