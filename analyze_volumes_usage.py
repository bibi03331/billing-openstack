import json
import sys
import os.path
from pylab import *
from datetime import datetime

PROJECT_ID=sys.argv[1]
DATE_DEBUT=sys.argv[2]
DATE_FIN=sys.argv[3]

TENANT_FILE='tenants.json'
VOLUMES_FILE='volumes_type.json'
PROJECT_DIR = 'projet-' + PROJECT_ID
COMPTE_RENDU = PROJECT_DIR + '/compte_rendu.json'

CMPT_UPTIME = 0

# Recuperation de l ID du tenant admin
os.system('./get_tenants.sh')

tenants = open(TENANT_FILE,'r')
tenants_json = json.load(tenants)
tenants.close()

for i in range(0,size(tenants_json['tenants'])):
    if tenants_json['tenants'][i]['name'] == 'admin':
        ADMIN_TENANT_ID = tenants_json['tenants'][i]['id']

# Recuperation de la liste des types de volume
cmd = './get_volume_types.sh ' + ADMIN_TENANT_ID
os.system(cmd)

volumes = open(VOLUMES_FILE,'r')
volumes_json = json.load(volumes)
volumes.close()

type_volume_id = [ ]
type_volume_name = [ ]
for i in range(0,size(volumes_json['volume_types'])):
    type_volume_id.append(volumes_json['volume_types'][i]['id'])
    type_volume_name.append(volumes_json['volume_types'][i]['name'])

nb_type_volumes=size(type_volume_id)

PROJECT_DIR = 'projet-' + PROJECT_ID

if not os.path.exists(PROJECT_DIR):
  os.makedirs(PROJECT_DIR)

for i in range(0,nb_type_volumes):
    cmd = './get_volume_usage.sh ' + PROJECT_ID + ' ' + type_volume_id[i] + ' "' + type_volume_name[i] + '"'
    VOLUME_TYPE = PROJECT_DIR + '/type-' + type_volume_name[i]

    volume = os.popen(cmd)
    volume_json = json.load(volume)
    for y in range(0,size(volume_json)):
        if (volume_json[y]['metadata']['status'] == 'in-use') or (volume_json[y]['metadata']['status'] == 'available'):

            if not os.path.exists(VOLUME_TYPE):
                os.makedirs(VOLUME_TYPE)

            creation_date = datetime.strptime(volume_json[y]['metadata']['created_at'], '%Y-%m-%d %H:%M:%S')
            date_fin = datetime.strptime(DATE_FIN, '%Y-%m-%dT%H:%M:%S')
            date_debut = datetime.strptime(DATE_DEBUT, '%Y-%m-%dT%H:%M:%S')

            if creation_date < date_fin:

                if creation_date < date_debut:
                    UPTIME = date_fin - date_debut
                    UPTIME_INT = float(UPTIME.total_seconds() - 7200) / 86400
                else:
                    UPTIME = date_fin - creation_date
                    UPTIME_INT = float(UPTIME.total_seconds()) / 86400

                UPTIME_INT = UPTIME_INT * int(volume_json[y]['metadata']['size'])
                CMPT_UPTIME = CMPT_UPTIME + UPTIME_INT

                volume_infos_json = {
                    "display_name": volume_json[y]['metadata']['display_name'],
                    "volume_id": volume_json[y]['metadata']['volume_id'],
                    "date_creation": volume_json[y]['metadata']['created_at'],
                    "snapshot_id": volume_json[y]['metadata']['snapshot_id'],
                    "up_time": UPTIME_INT
                }

                VOLUME_FILE = VOLUME_TYPE + '/volume-' + volume_json[y]['metadata']['volume_id'] + '.json'

                volume = open(VOLUME_FILE, 'w')
                json.dump(volume_infos_json, volume, indent=2)
                volume.close()

                if os.path.exists(COMPTE_RENDU):
                    compte_rendu = open(COMPTE_RENDU,'r')
                    compte_rendu_json = json.load(compte_rendu)
                    compte_rendu.close()

                    compte_rendu_json['volumes'][type_volume_name[i]] = CMPT_UPTIME

                    compte_rendu = open(COMPTE_RENDU,'w')
                    json.dump(compte_rendu_json, compte_rendu, indent=2)
                    compte_rendu.close()

if os.path.exists(VOLUMES_FILE):
    os.remove(VOLUMES_FILE)
