# -*-coding:Latin-1 -*

import csv
import datetime
import time

def getDateTimetimeFromStr(time_str):
#Cas o� la dur�e est au format str (hh:mm:ss)
	if isinstance(time_str, str):
		#d�coupage des heures minutes secondes
		duree_split = time_str.split(":")
		
		hours = int(duree_split[0])
		minutes = int(duree_split[1])
		seconds = int(duree_split[2])
		
		return datetime.time(hours, minutes, seconds)
	else:
		print(time_str, "should be str and is", type(time_str))
	

class Course:
	"""Classe repr�sentant une course"""

	categories = dict()
	liste_courreurs = list()
	
	def GetCategorie(cls, nom_categorie):
		"""M�thode de classe permettant de retourner une cat�gorie en fonction de son nom. Cr�e la cat�gorie si elle n'existe pas"""
	
		if nom_categorie in Course.categories.keys():
			return Course.categories[nom_categorie]
		else:
			nouvelle_categorie = Categorie(nom_categorie)
			Course.categories[nom_categorie] = nouvelle_categorie
			return nouvelle_categorie		
	GetCategorie = classmethod(GetCategorie)
	
	def CreerCourreur(cls, classement_officiel, dossard, nom, prenom, classement_categorie, categorie, temps_reel, temps_officiel):
		"""Cr�ation d'un courreur"""
	
		nouveau_courreur = CourreurArrive(classement_officiel, dossard, nom, prenom, classement_categorie, categorie, temps_reel, temps_officiel)
		Course.liste_courreurs.append(nouveau_courreur)
		
	CreerCourreur = classmethod(CreerCourreur)
	



class Categorie:
	"""Classe repr�sentant une cat�gorie"""	
	def __init__(self, nom_categorie):
		"""Constructeur d'une cat�gorie"""
		self.id = nom_categorie
		self.homme = "homme" in nom_categorie.lower()
		self.liste_courreurs = list()
		
		print("Cr�ation de la cat�gorie", nom_categorie, " qui est un homme:", self.homme)
		
	def ajouterCourreur(self, courreur):
		"""Ajout d'un courreur dans une cat�gorie"""
		self.liste_courreurs.append(courreur)
	
	
#
class CourreurArrive:
	"""Classe repr�sentant un coureur arriv�"""


	def __init__(self, classement_officiel, dossard, nom, prenom, classement_categorie, categorie, temps_reel, temps_officiel):
		"""Constructeur de CourreurArrive"""
		self.classement_officiel = classement_officiel
		self.dossard = dossard
		self.nom = nom
		self.prenom = prenom
		self.classement_categorie = classement_categorie
		self.categorie = Course.GetCategorie(categorie)
		self.categorie.ajouterCourreur(self)
		self.temps_reel = getDateTimetimeFromStr(temps_reel)
		self.temps_officiel = getDateTimetimeFromStr(temps_officiel)
		self.attente_dans_sas = datetime.timedelta(hours=self.temps_reel.hour - self.temps_officiel.hour, minutes=self.temps_reel.minute - self.temps_officiel.minute, seconds=self.temps_reel.second - self.temps_officiel.second)


	
####################################################################################
###################			 Programme principal		############################
####################################################################################


#ouverture et lecture du fichier en lecture seule
csvfile = open('D:\\programmation\\Python\\statistiques_resultats_courses\\marathon_paris_2013\\Data\\Resultats marathon 2013.csv', 'r')		
csv_reader = csv.DictReader(csvfile, delimiter=';', quotechar='|')	
for row in csv_reader:
	#print(row)
	classement_officiel = row["CLASS. OFFICIEL"]
	dossard = row["DOSSARD"]
	nom = row["NOM"]
	prenom = row["PR�NOM"]
	classement_categorie = row["CLASS. CAT�GORIE"]
	categorie = row["CAT�GORIE"]
	temps_reel = row["TEMPS R�EL"]
	temps_officiel = row["TEMPS OFFICIEL"]
	
	#Cr�ation du coureur
	nouveau_coureur = CourreurArrive(classement_officiel, dossard, nom, prenom, classement_categorie, categorie, temps_reel, temps_officiel)
		

# affichage du nombre de coureurs par cat�gorie
for nom_cat, cat in Course.categories.items():
	print(len(cat.liste_courreurs), "courreurs dans categorie", nom_cat)



#affichage du nombre d'hommes et de femmes
#print(len(CourreurArrive.liste_hommes), "hommes et ", len(CourreurArrive.liste_femmes), "femmes")
	

#Parcours de la liste des coureurs cr��s


