#!/bin/bash

IMAGE=us-west1-docker.pkg.dev/som-deissero/website-cms/website-cmsw

# build and tag project
docker build -t $IMAGE $(dirname "$0") -f website-cms.cf

# upload to registry
docker push $IMAGE

gcloud run deploy website-cms --image "${IMAGE}:latest" --project som-deissero --region us-west1
