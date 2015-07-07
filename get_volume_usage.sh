#!/bin/bash

CONTROLLER_HOST=192.168.1.10

PROJECT_ID=$1
VOLUME_TYPE_ID=$2
VOLUME_TYPE_NAME=$3

TOKEN=$(./get_token.sh)

curl -s -X GET -H "X-Auth-Token: $TOKEN" -H 'Content-Type: application/json' -d '{"q": [{"field": "project_id", "op": "eq", "value": "'$PROJECT_ID'"},{"field": "metadata.volume_type", "op": "eq", "value": "'$VOLUME_TYPE_ID'"}]}' http://$CONTROLLER_HOST:8777/v2/resources | python -mjson.tool
