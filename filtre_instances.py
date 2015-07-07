import json
import sys
import os.path
from pylab import *
from datetime import datetime

PROJECT_ID = sys.argv[1]
NOM_TYPE_INSTANCE = sys.argv[2]
DATE_FIN = sys.argv[3]

PROJECT_DIR = 'projet-' + PROJECT_ID
COMPTE_RENDU = PROJECT_DIR + '/compte_rendu.json'
JSON_FILE = 'instances-list-' + NOM_TYPE_INSTANCE + '.json'
INSTANCE_TYPE = PROJECT_DIR + '/type-' + NOM_TYPE_INSTANCE
FLAVORS_FILE='flavors.json'
TENANT_FILE='tenants.json'

# Recuperation de l ID du tenant admin
tenants = open(TENANT_FILE,'r')
tenants_json = json.load(tenants)
tenants.close()

for i in range(0,size(tenants_json['tenants'])):
    if tenants_json['tenants'][i]['name'] == 'admin':
        ADMIN_TENANT_ID = tenants_json['tenants'][i]['id']

CMPT_INSTANCES_TYPE = 0
CMPT_HEURES_INSTANCES = 0

if not os.path.exists(INSTANCE_TYPE):
    os.makedirs(INSTANCE_TYPE)

with open(JSON_FILE) as data_file:
    data = json.load(data_file)

for i in range(0,size(data)):

    INSTANCE_FILE= INSTANCE_TYPE + '/instance-' + data[i]['resource_id']

    if not os.path.exists(INSTANCE_FILE):
        CMPT_INSTANCES_TYPE = CMPT_INSTANCES_TYPE + 1
        UPTIME_INT = '0'

        status = os.popen('./get_instance_status.sh ' + ADMIN_TENANT_ID + ' ' + data[i]['resource_id'])
        status_json = json.load(status)
        if (status_json.get('itemNotFound') == None): # Instance toujours active
            # Recuperation de la date de creation
            CREATED_AT = status_json['server']['created']
            DELETED_AT = None
            first_time = datetime.strptime(status_json['server']['created'], '%Y-%m-%dT%H:%M:%SZ')
            last_time = datetime.strptime(DATE_FIN, '%Y-%m-%dT%H:%M:%S')
            UPTIME = last_time - first_time
            UPTIME_INT = float(UPTIME.total_seconds() - 7200) / 86400

        else: # Instance supprimee
            infos = os.popen('./get_resource_infos.sh ' + data[i]['resource_id'])
            infos_json = json.load(infos)
            CREATED_AT = infos_json['metadata']['created_at']
            DELETED_AT = infos_json['metadata']['deleted_at']

            try:
                first_time = datetime.strptime(infos_json['metadata']['created_at'], '%Y-%m-%dT%H:%M:%S.%f')
            except ValueError:
                first_time = datetime.strptime(infos_json['metadata']['created_at'], '%Y-%m-%d %H:%M:%S+00:00')

            try:
                last_time = datetime.strptime(infos_json['metadata']['deleted_at'], '%Y-%m-%dT%H:%M:%S.%f')
            except ValueError:
                last_time = datetime.strptime(infos_json['metadata']['deleted_at'], '%Y-%m-%d %H:%M:%S+00:00')

            UPTIME = last_time - first_time
            UPTIME_INT = float(UPTIME.total_seconds()) / 86400

        CMPT_HEURES_INSTANCES = CMPT_HEURES_INSTANCES + UPTIME_INT

        instance_infos_json = {
          "gabarit": data[i]['resource_metadata'].get('flavor.name'),
          "nom_instance": data[i]['resource_metadata'].get('display_name'),
          "ram": data[i]['resource_metadata'].get('flavor.ram'),
          "vcpus": data[i]['resource_metadata'].get('flavor.vcpus'),
          "image": data[i]['resource_metadata'].get('image.name'),
          "created_at": CREATED_AT,
          "deleted_at": DELETED_AT,
          "up_time": UPTIME_INT
        }

        instance = open(INSTANCE_FILE, 'w')
        json.dump(instance_infos_json, instance, indent=2)
        instance.close()

if CMPT_INSTANCES_TYPE == 0:
    os.system('rm -R ' + INSTANCE_TYPE)
else:
    if os.path.exists(COMPTE_RENDU):
        compte_rendu = open(COMPTE_RENDU,'r')
        compte_rendu_json = json.load(compte_rendu)
        compte_rendu.close()

        compte_rendu_json['instances'][NOM_TYPE_INSTANCE] = CMPT_HEURES_INSTANCES

        compte_rendu = open(COMPTE_RENDU,'w')
        json.dump(compte_rendu_json, compte_rendu, indent=2)
        compte_rendu.close()

if os.path.exists(JSON_FILE):
    os.remove(JSON_FILE)
