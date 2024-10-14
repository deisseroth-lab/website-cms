#!/bin/bash

IMAGE=us-west1-docker.pkg.dev/som-deissero/website-cms/website-cms

# build and tag project
# docker build -t $IMAGE $(dirname "$0") -f website-cms.cf
docker build -t $IMAGE $(dirname "$0") -f website-cms.cf

# podman build -f website-cms.cf -t website-cms --ignorefile .containerignore $(dirname "$0")

# upload to registry
docker push $IMAGE

# podman push $IMAGE
gcloud run deploy website-cms --image "${IMAGE}:latest" --project som-deissero --region us-west1
