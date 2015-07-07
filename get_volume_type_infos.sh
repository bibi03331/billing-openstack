#!/bin/bash

CONTROLLER_HOST=192.168.1.10

ADMIN_TENANT_ID=$1
VOLUME_TYPE_ID=$2

TOKEN=$(./get_token.sh)

curl -s -X GET -H "X-Auth-Token: $TOKEN" http://$CONTROLLER_HOST:8776/v2/$ADMIN_TENANT_ID/types/$VOLUME_TYPE_ID | python -mjson.tool
