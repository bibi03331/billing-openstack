#!/bin/bash

CONTROLLER_HOST=192.168.1.10

TENANT_ID=$1
RESOURCE_ID=$2

TOKEN=$(./get_token.sh)

curl -s -X GET -H "X-Auth-Token: $TOKEN" -H 'Content-Type: application/json' http://$CONTROLLER_HOST:8774/v2/$TENANT_ID/servers/$RESOURCE_ID | python -mjson.tool
