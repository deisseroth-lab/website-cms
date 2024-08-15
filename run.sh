#!/bin/bash

PORT=8000
AUTH_PORT=5001

# case $OSTYPE in
#     linux*)
#         CLOUD_SQL_PROXY_BIN=./cloud-sql-proxy
#     ;;
#     darwin*)
#         CLOUD_SQL_PROXY_BIN=./cloud-sql-proxy-mac
#     ;;
# esac

if [ "$1" == "--container" ]; then
    podman build -f website-cms.cf -t website-cms --ignorefile .containerignore $(dirname "$0")
    podman run \
        -p $PORT:$PORT \
        website-cms
        # -e GOOGLE_APPLICATION_CREDENTIALS=/tmp/keys/gcloud_creds.json \
        # -v $GOOGLE_APPLICATION_CREDENTIALS:/tmp/keys/gcloud_creds.json:ro \
        # -e PROVISION_DATABASE_URI=$PROVISION_DATABASE_URI \
else
    # export PROVISION_DATABASE_URI="${PROVISION_DATABASE_URI:-sqlite:///provision/database.db}"
    # $CLOUD_SQL_PROXY_BIN soe-licorice:us-central1:provision-test -p $AUTH_PORT &
    litestar --app website_cms.app:app run -d --port $PORT $@
fi
