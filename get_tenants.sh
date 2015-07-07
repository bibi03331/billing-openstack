#!/bin/bash

CONTROLLER_HOST=192.168.1.10

TOKEN=$(./get_token.sh)

curl -s -H "X-Auth-Token: $TOKEN" http://$CONTROLLER_HOST:5000/v2.0/tenants | python -mjson.tool > tenants.json
