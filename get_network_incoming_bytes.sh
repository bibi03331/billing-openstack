#!/bin/bash

CONTROLLER_HOST=192.168.1.10

PROJECT_ID=$1
DATE_DEBUT=$2
DATE_FIN=$3

TOKEN=$(./get_token.sh)

curl -s -X GET -H "X-Auth-Token: $TOKEN" -H 'Content-Type: application/json' -d '{"q": [{"field": "timestamp","op": "ge","value": "'$DATE_DEBUT'"},{"field": "timestamp","op": "lt","value": "'$DATE_FIN'"},{"field": "project_id", "op": "eq", "value": "'$PROJECT_ID'"}]}' http://$CONTROLLER_HOST:8777/v2/meters/network.incoming.bytes | python -mjson.tool
