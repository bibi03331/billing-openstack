import json
import sys
import os.path
from pylab import *

PROJECT_ID=sys.argv[1]
DATE_DEBUT=sys.argv[2]
DATE_FIN=sys.argv[3]
ADMIN_TENANT_ID=sys.argv[4]

TENANT_FILE='tenants.json'
FLAVORS_FILE='flavors.json'
PROJECT_DIR = 'projet-' + PROJECT_ID

# Recuperation de la liste des gabarits
if not os.path.exists(FLAVORS_FILE):
    cmd = './get_flavors.sh ' + ADMIN_TENANT_ID
    os.system(cmd)

gabarits = open(FLAVORS_FILE,'r')
gabarits_json = json.load(gabarits)
gabarits.close()

type_gabarit = [ ]
for i in range(0,size(gabarits_json['flavors'])):
    type_gabarit.append(gabarits_json['flavors'][i]['name'])

for i in range(0,size(type_gabarit)):
    cmd_A = './get_instances_usage.sh ' + PROJECT_ID + ' ' + type_gabarit[i] + ' ' + DATE_DEBUT + ' ' + DATE_FIN
    cmd_B = 'python filtre_instances.py ' + PROJECT_ID + ' ' + type_gabarit[i] + ' ' + DATE_FIN
    os.system(cmd_A)
    os.system(cmd_B)
