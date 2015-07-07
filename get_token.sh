#!/bin/bash

TENANT_NAME=a393857513954f25a53d58436acfa5b0
ADMIN_USERNAME=admin
ADMIN_PASSWORD=05046Tomy/
CONTROLLER_HOST=192.168.1.10

REQUEST="{\"auth\": {\"tenantId\":\"$TENANT_NAME\", \"passwordCredentials\": {\"username\": \"$ADMIN_USERNAME\", \"password\": \"$ADMIN_PASSWORD\"}}}"
#echo $REQUEST
RAW_TOKEN=`curl -s -d "$REQUEST" -H "Content-type: application/json" "http://192.168.1.10:5000/v2.0/tokens"`
#echo $RAW_TOKEN
TOKEN=`echo $RAW_TOKEN | python -c "import sys; import json; tok = json.loads(sys.stdin.read()); print tok['access']['token']['id'];"`

echo $TOKEN
