import time
import sys
from pylab import *
from datetime import datetime
import json
import os.path
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm

DATE_DEBUT = sys.argv[1]
DATE_FIN = sys.argv[2]
USAGE_FILE = sys.argv[3]
TENANT_ID = sys.argv[4]
ADMIN_TENANT_ID = sys.argv[5]

FLAVORS_FILE='flavors.json'
VOLUMES_FILE='volumes_type.json'

date_debut = datetime.strptime(DATE_DEBUT, '%Y-%m-%dT%H:%M:%S')
date_fin = datetime.strptime(DATE_FIN, '%Y-%m-%dT%H:%M:%S')
date_debut_periode = date_debut.strftime("%d-%m-%Y")
date_fin_periode = date_fin.strftime("%d-%m-%Y")

compte_rendu_path = "projet-" + TENANT_ID + "/compte_rendu_du_" + date_debut_periode + "_au_" + date_fin_periode + ".pdf"

montant_total_indicatif = 0

story=[]

instances = [
["<font size=9><b>Type d'instance</b></font>", "<font size=9><b>Jours cumul&eacute;s</b></font>", "<font size=9><b>Prix journalier HT</b></font>", "<font size=9><b>Sous-total HT</b></font>"]
]

volumes = [
["<font size=9><b>Type de volume</b></font>", "<font size=9><b>Jours cumul&eacute;s</b></font>", "<font size=9><b>Prix journalier HT</b></font>", "<font size=9><b>Sous-total HT</b></font>"]
]

os.system('./get_flavors.sh ' + ADMIN_TENANT_ID)
if os.path.exists(FLAVORS_FILE):
	gabarits = open(FLAVORS_FILE,'r')
	gabarits_json = json.load(gabarits)
	gabarits.close()

	gabarits = [ ]
	gabarits_id = [ ]
        for z in range(0,size(gabarits_json['flavors'])):
        	gabarits.append(gabarits_json['flavors'][z]['name'])
		gabarits_id.append(gabarits_json['flavors'][z]['id'])

os.system('./get_volume_types.sh a393857513954f25a53d58436acfa5b0')
if os.path.exists(VOLUMES_FILE):
        volumes_file = open(VOLUMES_FILE,'r')
        volumes_json = json.load(volumes_file)
        volumes_file.close()

	volumes_list = [ ]
	volumes_id_list = [ ]
        for z in range(0,size(volumes_json['volume_types'])):
        	volumes_list.append(volumes_json['volume_types'][z]['name'])
		volumes_id_list.append(volumes_json['volume_types'][z]['id'])

if os.path.exists(USAGE_FILE):
	usage = open(USAGE_FILE,'r')
	usage_json = json.load(usage)
	usage.close()

	for i in range(0,size(usage_json)):
		if usage_json[i]['project_id'] == TENANT_ID:
			nom_projet = usage_json[i]['project_name']
			id_projet = usage_json[i]['project_id']
			for z in range(0,size(gabarits)):
				if not usage_json[i]['project_usage']['instances'][gabarits[z]] == 0:

					cmd = './get_flavors_extra_specs.sh ' + ADMIN_TENANT_ID + ' ' + gabarits_id[z]
					extra_specs = os.popen(cmd)
    					extra_specs_json = json.load(extra_specs)
					day_price = extra_specs_json['extra_specs']['price:day']
					day_price_float = float(day_price)
					sub_total = usage_json[i]['project_usage']['instances'][gabarits[z]] * day_price_float

					ligne_instance = [ gabarits[z],
						"%.4f" % usage_json[i]['project_usage']['instances'][gabarits[z]],
						day_price + ' &euro;',
						"%.4f &euro;" % sub_total
					]
					instances.append(ligne_instance)
					montant_total_indicatif = montant_total_indicatif + sub_total

			for z in range(0,size(volumes_list)):
				if not usage_json[i]['project_usage']['volumes'][volumes_list[z]] == 0:

					cmd = './get_volume_type_infos.sh ' + ADMIN_TENANT_ID + ' ' + volumes_id_list[z]
					extra_specs = os.popen(cmd)
    					extra_specs_json = json.load(extra_specs)
					day_price = extra_specs_json['volume_type']['extra_specs']['price:day']
					day_price_float = float(day_price)
					sub_total = usage_json[i]['project_usage']['volumes'][volumes_list[z]] * day_price_float

					ligne_volume = [ volumes_list[z],
						"%.4f" % usage_json[i]['project_usage']['volumes'][volumes_list[z]],
						day_price + ' &euro;',
						"%.4f &euro;" % sub_total
					]
					volumes.append(ligne_volume)
					montant_total_indicatif = montant_total_indicatif + sub_total

style = TableStyle([('ALIGN',(1,1),(-2,-2),'RIGHT'),
                       ('TEXTCOLOR',(1,1),(-2,-2),colors.red),
                       ('VALIGN',(0,0),(0,-1),'TOP'),
                       ('TEXTCOLOR',(0,0),(0,-1),colors.blue),
                       ('ALIGN',(0,-1),(-1,-1),'CENTER'),
                       ('VALIGN',(0,-1),(-1,-1),'MIDDLE'),
                       ('TEXTCOLOR',(0,-1),(-1,-1),colors.green),
                       ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                       ('BOX', (0,0), (-1,-1), 0.25, colors.black),
                       ])

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='Center', alignment=TA_CENTER))

s = getSampleStyleSheet()
s = s["Normal"]
s.wordWrap = 'CJK'

tab_instances = [[Paragraph(cell, s) for cell in row] for row in instances]
tableau_instances = Table(tab_instances)
tableau_instances.setStyle(style)

tab_volumes = [[Paragraph(cell, s) for cell in row] for row in volumes]
tableau_volumes = Table(tab_volumes)
tableau_volumes.setStyle(style)

doc = SimpleDocTemplate(compte_rendu_path, rightMargin=1.5*cm, leftMargin=1.5*cm, topMargin=1.5*cm, bottomMargin=1.5*cm)

logo = Image('logo_mac_and_co.png', 4*cm, 0.63*cm)
logo.hAlign = 'RIGHT'

titre = "<font size=28>Rapport d'utilisation</font>"

periode = '<font size=12>P&eacute;riode du ' + date_debut_periode + ' au ' + date_fin_periode +'</font>'

info_nom_projet = "<b>Nom du projet :</b> " + nom_projet
info_id_projet = "<b>ID du projet :</b> " + id_projet

texte_titre_tableau_instances = "<font size=11>Utilisation des machines virtuelles :</font>"

texte_titre_tableau_volumes = "<font size=11>Utilisation des volumes de stockage :</font>"

texte_montant_indicatif = "<font size=11><b>Montant total HT indicatif :</b> %.4f &euro;</font>" % montant_total_indicatif

texte_contact = "Contact support : slaporte@macandco.fr"



story.append(logo)
story.append(Spacer(0.1*cm, 1*cm))

story.append(Paragraph(titre, styles["Center"]))
story.append(Spacer(0.1*cm, 1*cm))

story.append(Paragraph(periode, styles["Center"]))
story.append(Spacer(0.1*cm, 1*cm))

story.append(Paragraph(info_nom_projet, styles["Normal"]))
story.append(Spacer(0.1*cm, 0.1*cm))
story.append(Paragraph(info_id_projet, styles["Normal"]))
story.append(Spacer(0.1*cm, 1*cm))

story.append(Paragraph(texte_titre_tableau_instances, styles["Normal"]))
story.append(Spacer(0.1*cm, 0.3*cm))

story.append(tableau_instances)
story.append(Spacer(0.1*cm, 1*cm))

story.append(Paragraph(texte_titre_tableau_volumes, styles["Normal"]))
story.append(Spacer(0.1*cm, 0.3*cm))

story.append(tableau_volumes)
story.append(Spacer(0.1*cm, 2*cm))

story.append(Paragraph(texte_montant_indicatif, styles["Normal"]))
story.append(Spacer(0.1*cm, 2*cm))

story.append(Paragraph(texte_contact, styles["Normal"]))
 
doc.build(story)
