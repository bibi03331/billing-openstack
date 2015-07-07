#!/bin/bash

CONTROLLER_HOST=192.168.1.10

RESOURCE_ID=$1

TOKEN=$(./get_token.sh)

curl -s -X GET -H "X-Auth-Token: $TOKEN" -H 'Content-Type: application/json' http://$CONTROLLER_HOST:8777/v2/resources/$RESOURCE_ID | python -mjson.tool
