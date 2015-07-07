import json
import sys
import os.path
from pylab import *
from datetime import datetime

DATE_DEBUT=sys.argv[1]
DATE_FIN=sys.argv[2]

TENANT_FILE='tenants.json'

date_debut_usage = datetime.strptime(DATE_DEBUT, '%Y-%m-%dT%H:%M:%S')
date_fin_usage = datetime.strptime(DATE_FIN, '%Y-%m-%dT%H:%M:%S')

USAGE_FILE = 'usage_from_' + date_debut_usage.strftime("%Y-%m-%d_%H-%M") + '_to_' + date_fin_usage.strftime("%Y-%m-%d_%H-%M") + '.json'
FLAVORS_FILE = 'flavors.json'
VOLUMES_FILE = 'volumes_type.json'

# Recuperation de l ID du tenant admin
os.system('./get_tenants.sh')

tenants = open(TENANT_FILE,'r')
tenants_json = json.load(tenants)
tenants.close()

tenants = open(TENANT_FILE,'r')
tenants_json = json.load(tenants)
tenants.close()

for y in range(0,size(tenants_json['tenants'])):
    if tenants_json['tenants'][y]['name'] == 'admin':
        ADMIN_TENANT_ID = tenants_json['tenants'][y]['id']

# Recuperation de la liste des gabarits
os.system('./get_flavors.sh ' + ADMIN_TENANT_ID)

gabarits = open(FLAVORS_FILE,'r')
gabarits_json = json.load(gabarits)
gabarits.close()

# Suppression du rapport precedent
if os.path.exists(USAGE_FILE):
    os.remove(USAGE_FILE)

# Creation du fichier contenant les usages
if not os.path.exists(USAGE_FILE):
    usage_json = [ ]
    usage = open(USAGE_FILE,'w')
    json.dump(usage_json, usage, indent=2)
    usage.close()

for i in range(0,size(tenants_json['tenants'])):
    if not (tenants_json['tenants'][i]['name'] == 'admin') and not (tenants_json['tenants'][i]['name'] == 'service'):

        print 'Traitement du projet : ' + tenants_json['tenants'][i]['name'] + '...'

        PROJECT_DIR = 'projet-' + tenants_json['tenants'][i]['id']
        COMPTE_RENDU = PROJECT_DIR + '/compte_rendu.json'

        # Creation du repertoire du projet
        if not os.path.exists(PROJECT_DIR):
          os.makedirs(PROJECT_DIR)

        # Creation du repertoire pour le type d instance en cours de traitement
        type_gabarit = [ ]
        for y in range(0,size(gabarits_json['flavors'])):
            INSTANCE_TYPE = PROJECT_DIR + '/type-' + gabarits_json['flavors'][y]['name']
            if not os.path.exists(INSTANCE_TYPE):
                os.makedirs(INSTANCE_TYPE)

        # Creation du rapport
        os.system('./get_flavors.sh ' + ADMIN_TENANT_ID)
        gabarits = open(FLAVORS_FILE,'r')
        gabarits_json = json.load(gabarits)
        gabarits.close()

        os.system('./get_volume_types.sh ' + ADMIN_TENANT_ID)
        volumes = open(VOLUMES_FILE,'r')
        volumes_json = json.load(volumes)
        volumes.close()

        compte_rendu_INSTANCES_json = { }
        for z in range(0,size(gabarits_json['flavors'])):
            compte_rendu_INSTANCES_json[gabarits_json['flavors'][z]['name']] = 0

        compte_rendu_VOLUMES_json = { }
        for z in range(0,size(volumes_json['volume_types'])):
            compte_rendu_VOLUMES_json[volumes_json['volume_types'][z]['name']] = 0

        compte_rendu_json = {
            "instances": compte_rendu_INSTANCES_json,
            "volumes": compte_rendu_VOLUMES_json
        }

        compte_rendu = open(COMPTE_RENDU,'w')
        json.dump(compte_rendu_json, compte_rendu, indent=2)
        compte_rendu.close()

        # Analyse de l usage des instances
        os.system('python analyze_instances_usage.py ' + tenants_json['tenants'][i]['id'] + ' ' + DATE_DEBUT + ' ' + DATE_FIN + ' ' + ADMIN_TENANT_ID)

        # Analyse de l usage des volumes
        os.system('python analyze_volumes_usage.py ' + tenants_json['tenants'][i]['id'] + ' ' + DATE_DEBUT + ' ' + DATE_FIN)

        # Creation du compte rendu JSON
        if os.path.exists(USAGE_FILE):
            usage = open(USAGE_FILE,'r')
            usage_json = json.load(usage)
            usage.close()

            try :
                project_usage = open('projet-' + tenants_json['tenants'][i]['id'] + '/compte_rendu.json','r')
            except IOError:
                print 'Pas de compte rendu pour le projet ' + tenants_json['tenants'][i]['name']
            else:
                project_usage_json = json.load(project_usage)
                project_usage.close()

                new_usage = {
                  "project_name": tenants_json['tenants'][i]['name'],
                  "project_id": tenants_json['tenants'][i]['id'],
                  "project_usage": project_usage_json
                }

                usage_json.append(new_usage)

                usage = open(USAGE_FILE,'w')
                json.dump(usage_json, usage, indent=2)
                usage.close()
	
	# Generation du rapport PDF
	cmd = 'python create_report.py ' + DATE_DEBUT + ' ' + DATE_FIN + ' ' + USAGE_FILE + ' ' + tenants_json['tenants'][i]['id'] + ' ' + ADMIN_TENANT_ID
	os.system(cmd)

print 'Traitement termine.'

if os.path.exists(FLAVORS_FILE):
    os.remove(FLAVORS_FILE)
if os.path.exists(TENANT_FILE):
    os.remove(TENANT_FILE)
