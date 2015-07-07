#!/bin/bash

CONTROLLER_HOST=192.168.1.10

ADMIN_TENANT_ID=$1
FLAVOR_ID=$2

TOKEN=$(./get_token.sh)

curl -s -H "X-Auth-Token: $TOKEN" http://$CONTROLLER_HOST:8774/v2/$ADMIN_TENANT_ID/flavors/$FLAVOR_ID/os-extra_specs | python -mjson.tool
