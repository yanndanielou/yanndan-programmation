import pandas as panda
import numpy as np
from pandas import ExcelWriter
from pandas import ExcelFile
import os
import math
import re
import pickle
import xml.etree.ElementTree as ET
from datetime import datetime
import requests
import sys
import joblib


#For logs
#from LoggerConfig import execution_time
import LoggerConfig
import logging
import time
from datetime import timedelta

# Cette classe définie un graphe de topologie ferroviaire. La classe GrapheSingleton permet d'obtenir l'instance d'un singleton réutilisable.
class GrapheSingleton:
    __instance = None
    #Used for sure
    def __new__(cls):
        #logging.info("Start calling __new__ GrapheSingleton")
        if GrapheSingleton.__instance is None:
            GrapheSingleton.__instance = object.__new__(cls)
            GrapheSingleton.__instance.graphe = Graphe()
        return GrapheSingleton.__instance.graphe

    #@execution_time 
    def Load(cls, _nomFichier):
        logging.info("Start calling Load")
        if GrapheSingleton.__instance is None:
            GrapheSingleton.__instance = object.__new__(cls)
        f = open(_nomFichier, "rb")
        GrapheSingleton.__instance.graphe = pickle.load(f)
        f.close()
        return GrapheSingleton.__instance.graphe

    # def Load__disabled_YDA(cls, _nomFichier):
    #    logging.info("Start calling Load")
    #     if GrapheSingleton.__instance is None:
    #         GrapheSingleton.__instance = object.__new__(cls)
    #     # f = open(_nomFichier, "rb")
    #     # SimulationResultsSingleton.__instance.simulationResults = pickle.load(f)
    #     GrapheSingleton.__instance.graphe = joblib.load(_nomFichier)
    #     #f.close()
    #     return GrapheSingleton.__instance.graphe

class Graphe:
    #@execution_time
    def __init__(self):
        logging.info("Start calling __init__ Graphe")
        self.lignes = {}
        self.stations = {}
        self.voies = {}
        self.segments = {}
        self.troncons = {}
        self.PtAs = {}
        self.signals = {}
        self.aiguilles = {}
        self.CDVs = {}
        self.TVDs = {}
        self.JointsCDVs = {}
        self.ExtremitesCDVsLimiteDomaine = {}
        self.pointsDeControle = {}
        self.transitions = {}
        self.missionsElementairesRegulation = {}
        self.missionsElementaires = {}
        self.CBs = {}
        self.pedales = {}
        self.zlpvs = {}
        self.natures = {}
        self.natureParDefaut = None
        self.combinaisonsTypesEspacements = []
        self.couplesMeSePerturbant = []
        self.couplesMeSePerturbantCalculees = []

    # def Save__disabled_YDA(self, _nomFichier):
        logging.info("Start calling Save")
    #     # f = pickle.Pickler(open(_nomFichier,"wb"))
    #     # f.fast = True
    #     # f.dump(self, protocol=pickle.HIGHEST_PROTOCOL)
    #     # f.close()
    #     #f = open(_nomFichier, 'wb')
    #     joblib.dump(self, _nomFichier, 0)
        #f.close()

    #@execution_time 
    def Save__disabled_YDA(self, _nomFichier):
        logging.info("Start calling Save")
        sys.setrecursionlimit(3000)
        f = pickle.Pickler(open(_nomFichier,"wb"))
        f.dump(self)
        #f.close()
        #joblib.dump(self, _nomFichier)

    #@execution_time
    def AjouterLigne__disabled_YDA(self, _nom, _numero, _referentiel, _segmentReference, _orientationGauche, _orientationDroite):
        logging.info("Start calling AjouterLigne")
        LoggerConfig.print_and_log_info("fonction AjouterLigne")
        self.lignes[_nom] = Ligne(_nom, _numero, _referentiel, _segmentReference, _orientationGauche, _orientationDroite)

    #@execution_time 
    def AjouterStation__disabled_YDA(self, _nom):
        logging.info("Start calling AjouterStation")
        LoggerConfig.print_and_log_info("fonction AjouterStation")
        self.stations[_nom] = Station(_nom)
        return self.stations[_nom]

    #@execution_time 
    def AjouterPtA__disabled_YDA(self, _nom, _segment, _abs, _sens):
        logging.info("Start calling AjouterPtA")
        LoggerConfig.print_and_log_info("fonction AjouterPtA")
        self.PtAs[_nom] = PtA(_nom, _segment, _sens, _abs)

    #@execution_time 
    def AjouterSegment__disabled_YDA(self, _nom, _troncon, _voie, _longueur, _origine, _fin, _segment1VoisinAmont, _segment2VoisinAmont, _segment1VoisinAval, _segment2VoisinAval):
        logging.info("Start calling AjouterSegment")
        LoggerConfig.print_and_log_info("fonction AjouterSegment")
        self.segments[_nom] = Segment(_nom, _troncon, _voie, _longueur, _origine, _fin, _segment1VoisinAmont, _segment2VoisinAmont, _segment1VoisinAval, _segment2VoisinAval)

    #@execution_time 
    def AjouterVoie__disabled_YDA(self, _nom, _type, _sensNominal, _voieContinuitePK, _segContinuitePK, _sensIncrementationPK, _PKDebut, _PKFin):
        logging.info("Start calling AjouterVoie")
        LoggerConfig.print_and_log_info("fonction AjouterVoie")
        self.voies[_nom] = Voie(_nom, _type, _sensNominal, _voieContinuitePK, _segContinuitePK, _sensIncrementationPK, _PKDebut, _PKFin)

    #@execution_time    
    def AjouterTroncon__disabled_YDA(self, _nom, _ligne):
        logging.info("Start calling AjouterTroncon")
        LoggerConfig.print_and_log_info("fonction AjouterTroncon")
        self.troncons[_nom] = Troncon(_nom, _ligne)
        return self.troncons[_nom]

    #@execution_time 
    def AjouterSignal__disabled_YDA(self, _nom, _type, _sousType, _segment, _abs, _sens):
        logging.info("Start calling AjouterSignal")
        LoggerConfig.print_and_log_info("fonction AjouterSignal")
        self.signals[_nom] = Signal(_nom, _type, _sousType, _segment, _abs, _sens)

    #@execution_time 
    def AjouterAiguille__disabled_YDA(self, _nom, _posDirecte, _segPointe, _segTalonGauche, _segTalonDroite, _voie, _pk):
        logging.info("Start calling AjouterAiguille")
        LoggerConfig.print_and_log_info("fonction AjouterAiguille")
        self.aiguilles[_nom] = Aiguille(_nom, _posDirecte, _segPointe, _segTalonGauche, _segTalonDroite, _voie, _pk)

    #@execution_time 
    def AjouterCDV__disabled_YDA(self, _nom):
        logging.info("Start calling AjouterCDV")
        LoggerConfig.print_and_log_info("fonction AjouterCDV")
        self.CDVs[_nom] = CDV(_nom)
        return self.CDVs[_nom]

    #@execution_time 
    def AjouterTVD__disabled_YDA(self, _nom, _type, _objet):
        logging.info("Start calling AjouterTVD")
        LoggerConfig.print_and_log_info("fonction AjouterTVD")
        self.TVDs[_nom] = TVD(_nom, _type, _objet)
        return self.TVDs[_nom]

    #@execution_time 
    def AjouterJointCDV__disabled_YDA(self, _cdv1, _cdv2, _segment, _abs):
        logging.info("Start calling AjouterJointCDV")
        LoggerConfig.print_and_log_info("fonction AjouterJointCDV")
        if(_cdv1.nom <= _cdv2.nom):
            nomJointCdv = _cdv1.nom + "#" + _cdv2.nom
            self.JointsCDVs[nomJointCdv] = JointCDV(_cdv1, _cdv2, _segment, _abs)
            return self.JointsCDVs[nomJointCdv]
        else:
            nomJointCdv = _cdv2.nom + "#" + _cdv1.nom
            self.JointsCDVs[nomJointCdv] = JointCDV(_cdv2, _cdv1,  _segment, _abs)
            return self.JointsCDVs[nomJointCdv]

    #@execution_time 
    def RechercherJointCDV__disabled_YDA(self, _cdv1Nom, _cdv2Nom):
        logging.info("Start calling RechercherJointCDV")

        if(_cdv1Nom <= _cdv2Nom):
            nomJointCdv = _cdv1Nom + "#" + _cdv2Nom
            if(_cdv1Nom in self.CDVs and _cdv2Nom in self.CDVs):
                if(nomJointCdv in self.JointsCDVs):
                    return self.JointsCDVs[nomJointCdv]
                else:
                    return None
            else:
                if(_cdv1Nom in self.CDVs):
                    _cdv1 = self.CDVs[_cdv1Nom]
                    for cdv in self.CDVs.values():
                        nomJointCdv = cdv.nom + "#" + _cdv2Nom
                        if(nomJointCdv in self.JointsCDVs and cdv.nomGroupe == _cdv1.nomGroupe):
                            return self.JointsCDVs[nomJointCdv]
                else:
                    _cdv2 = self.CDVs[_cdv2Nom]
                    for cdv in self.CDVs.values():
                        nomJointCdv = _cdv1Nom + "#" + cdv.nom
                        if(nomJointCdv in self.JointsCDVs and cdv.nomGroupe == _cdv2.nomGroupe):
                            return self.JointsCDVs[nomJointCdv]
        else:
            if(_cdv1Nom in self.CDVs and _cdv2Nom in self.CDVs):
                nomJointCdv = _cdv2Nom + "#" + _cdv1Nom
                if(nomJointCdv in self.JointsCDVs):
                    return self.JointsCDVs[nomJointCdv]
                else:
                    return None
            else:
                if(_cdv1Nom in self.CDVs):
                    _cdv1 = self.CDVs[_cdv1Nom]
                    for cdv in self.CDVs.values():
                        nomJointCdv =  _cdv2Nom + "#" + cdv.nom
                        if(nomJointCdv in self.JointsCDVs and cdv.nomGroupe == _cdv1.nomGroupe):
                            return self.JointsCDVs[nomJointCdv]
                else:
                    _cdv2 = self.CDVs[_cdv2Nom]
                    for cdv in self.CDVs.values():
                        nomJointCdv =  cdv.nom + "#" + _cdv1Nom
                        if(nomJointCdv in self.JointsCDVs and cdv.nomGroupe == _cdv2.nomGroupe):
                            return self.JointsCDVs[nomJointCdv]

    #@execution_time 
    def AjouterExtremiteCDVLimiteDomaine__disabled_YDA(self, _cdv, _segment, _abs):
        logging.info("Start calling AjouterExtremiteCDVLimiteDomaine")
        self.ExtremitesCDVsLimiteDomaine[_cdv.nom] = ExtremiteCDVLimiteDomaine(_cdv, _segment, _abs)
        return self.ExtremitesCDVsLimiteDomaine[_cdv.nom]


    #@execution_time 
    def RechercherItinerairesDepuisOrigine__disabled_YDA(self, _signal):
        logging.info("Start calling RechercherItinerairesDepuisOrigine")
        itineraires = []
        for p in self.postes.values():
            for i in p.itineraires:
                if i.origine == _signal:
                    itineraires.append(i)

        return itineraires

    #@execution_time
    def RechercherCheckpoint__disabled_YDA(self, _nom):
        logging.info("Start calling RechercherCheckpoint")
        for pc in self.pointsDeControle.values():
            if(pc.nomCheckPoint == _nom):
                return pc
        return None

    #@execution_time 
    def RechercherItineraire__disabled_YDA(self, _nom):
        logging.info("Start calling RechercherItineraire")
        for p in self.postes.values():
            for i in p.itineraires:
                #print(i.nom + " / " + _nom)
                if i.nom == _nom:
                    return i
        return None

    #@execution_time 
    def EstimerNbChangementVoieME__disabled_YDA(self):
        logging.info("Start calling EstimerNbChangementVoieME")
        for meR in self.missionsElementairesRegulation.values():
            lastVoieParcourue = None
            for segP in meR.segmentsParcourus:
                if(segP.segment.voie is not lastVoieParcourue):
                    lastVoieParcourue = segP.segment.voie
                    meR.nbChangementVoie = meR.nbChangementVoie + 1

    #@execution_time 
    def ProduireCouplesMESePerturbant__disabled_YDA(self):
        logging.info("Start calling ProduireCouplesMESePerturbant")
        self.couplesMeSePerturbant = []
        for mE2 in self.missionsElementaires.values():
            for mE1 in self.missionsElementaires.values():
                segmentCommun = False
                # for segMe1 in mE1.segmentsParcourus[1:-1]:
                #     for segMe2 in mE2.segmentsParcourus[1:-1]:
                #         if(segMe1.segment == segMe2.segment):
                #             if(segMe1.segment != mE1.missionElementaireRegulation.poOrigine.segment and segMe1.segment != mE1.missionElementaireRegulation.poDestination.segment):
                #                 if(segMe2.segment != mE2.missionElementaireRegulation.poOrigine.segment and segMe2.segment != mE2.missionElementaireRegulation.poDestination.segment):
                #                     segmentCommun = True

                tvdEspacementCommun = False
                for sigMe1 in mE1.signaux:
                    if(sigMe1['CommandeSignalAAjouter'] == True):
                        for sigMe2 in mE2.signaux:
                            if(sigMe2['CommandeSignalAAjouter'] == True):
                                for tvdMe1 in sigMe1['CondSignalVert_TVDLibres']:
                                    for tvdMe2 in sigMe2['CondSignalVert_TVDLibres']:
                                        if(tvdMe1 == tvdMe2):
                                            tvdEspacementCommun = True

                #Transit à commander commun
                cmdTransitCommun = False
                # itineraire['condsDispoTransits'] = condsDispoTransits
                # itineraire['reservsTransits'] = reservsTransits

                aiguilleCommune = False
                for itiMe1 in mE1.itineraires:
                    for itiMe2 in mE2.itineraires:
                        aiguillesMe1 = itiMe1['Itineraire'].aiguillesParcourues #+ itiMe1['Itineraire'].aiguillesEnProtection
                        aiguillesMe2 = itiMe2['Itineraire'].aiguillesParcourues #+ itiMe2['Itineraire'].aiguillesEnProtection
                        for aigMe1 in aiguillesMe1:
                            for aigMe2 in aiguillesMe2:
                                if(aigMe1.aiguille == aigMe2.aiguille):
                                    aiguilleCommune = True
                        aiguillesMe1 = itiMe1['Itineraire'].aiguillesParcourues + itiMe1['Itineraire'].aiguillesEnProtection
                        aiguillesMe2 = itiMe2['Itineraire'].aiguillesParcourues + itiMe2['Itineraire'].aiguillesEnProtection
                        for aigMe1 in aiguillesMe1:
                            for aigMe2 in aiguillesMe2:
                                if(aigMe1.aiguille == aigMe2.aiguille and aigMe1.position != aigMe2.position):
                                    aiguilleCommune = True

                condCommCommune = False
                # for itiMe1 in mE1.itineraires:
                #     for itiMe2 in mE2.itineraires:
                #         for tvdMe1 in itiMe1['TVDCondCommutation']: #pour aiguille en position de protection : seulement si incompatible avec position de protection
                #             for tvdMe2 in itiMe2['TVDCondCommutation']:
                #                 if(tvdMe1 == tvdMe2):
                #                     condCommCommune = True

                mEsePerturbent = False
                if(mE1.missionElementaireRegulation == mE2.missionElementaireRegulation):
                    mEsePerturbent = True
                elif(mE1.missionElementaireRegulation.poOrigine == mE2.missionElementaireRegulation.poOrigine):
                    mEsePerturbent = True
                # Les deux missions élémentaires ont au moins un segment en commun, elles peuvent se perturber
                elif(segmentCommun):
                    mEsePerturbent = True
                # Les deux missions élémentaires ont au moins une aiguille en commun, elles peuvent se perturber
                elif(aiguilleCommune):
                    mEsePerturbent = True
                # Les deux missions élémentaires ont au moins un CDV à contrôler en commun, elles peuvent se perturber
                elif(condCommCommune):
                    mEsePerturbent = True
                elif(tvdEspacementCommun):
                    mEsePerturbent = True

                if(mEsePerturbent):
                    coupleSePerturbe = []
                    coupleSePerturbe.append(mE1.missionElementaireRegulation)
                    coupleSePerturbe.append(mE2.missionElementaireRegulation)
                    if(coupleSePerturbe not in self.couplesMeSePerturbant):
                        self.couplesMeSePerturbant.append(coupleSePerturbe)

    #used for sure 
    def SimulerSimpleRunSimulation(self, _url, _stepInSecond, _dwellTimeInSecond, _coeffOnRunTime, mE, modele, output_file, _ignoredMER = None):
        #logging.info("Start calling SimulerSimpleRunSimulation")
        error = ""
        simulationResults = SimulationResultsSingleton()

        travelTimesRequestTree = ET.Element('travelTimesRequest')
        computationStepInSecondTree = ET.SubElement(travelTimesRequestTree, 'computationStepInSecond')
        computationStepInSecondTree.text = str(_stepInSecond)
        dwellTimeInSecondTree = ET.SubElement(travelTimesRequestTree, 'dwellTimeInSecond')
        dwellTimeInSecondTree.text = str(_dwellTimeInSecond)
        simulationTypeTree = ET.SubElement(travelTimesRequestTree, 'simulationType')
        simulationTypeTree.text = "SIMPLE_RUN_PROFILE_SIMULATION"
        trainsTree = ET.SubElement(travelTimesRequestTree, 'trains')
        #train 1
        trainTree_1 = ET.SubElement(trainsTree, 'train')
        blockTypeTree_1 = ET.SubElement(trainTree_1, 'blockType')
        blockTypeTree_1.text = "VB_WITH_MOVING_TARGET"
        elementaryTripIdentifierTree_1 = ET.SubElement(trainTree_1, 'elementaryTripIdentifier')
        elementaryTripIdentifierTree_1.text = mE.nom
        loadCaseTree_1 = ET.SubElement(trainTree_1, 'loadCase')
        loadCaseTree_1.text = "AW0"
        modelTree_1 = ET.SubElement(trainTree_1, 'model')
        modelTree_1.text = modele.nom
        nextElemTrip = mE.FindNextElementaryTrip()
        if(nextElemTrip is not None):
            nextElementaryTripIdentifierTree_1 = ET.SubElement(trainTree_1, 'nextElementaryTripIdentifier')
            nextElementaryTripIdentifierTree_1.text = nextElemTrip.nom
        else:
            if(mE.missionElementaireRegulation.poDestination.isPAFQuai or mE.missionElementaireRegulation.poDestination.isPTA):
                print("Erreur Grave : mission élémentaire " + mE.nom + " sans nextElementaryTrip")
                error = "Erreur Grave : mission élémentaire " + mE.nom + " sans nextElementaryTrip"
                os.system("pause")
                # sys.exit()
        if(_ignoredMER != None and mE.missionElementaireRegulation.nom in _ignoredMER):
            error = "Erreur Grave : mission élémentaire " + mE.nom + " ignorée par la simulation"

        regulationTypeTree_1 = ET.SubElement(trainTree_1, 'regulationType')
        regulationTypeTree_1.text = "ACCELERATED_RUN_PROFILE"
        speedInMeterPerSecondTree_1 = ET.SubElement(trainTree_1, 'speedInMeterPerSecond')
        if(mE.missionElementaireRegulation.poOrigine.isPTES and (mE.missionElementaireRegulation.poOrigine.PTESType == "IN" or mE.missionElementaireRegulation.poOrigine.PTESType == "INOUT")):
            #speedInMeterPerSecondTree_1.text = str(mE.missionElementaireRegulation.poOrigine.vLigne)
            speedInMeterPerSecondTree_1.text = "0.0"
        else:
            speedInMeterPerSecondTree_1.text = "0.0"
        #ET.dump(travelTimesRequestTree)
        simpleRunSimulation = simulationResults.AjouterSimpleRunSimulation(mE.missionElementaireRegulation, modele, 'Normale')
        result = ""
        travelTimesRequestTree_as_str = ET.tostring(travelTimesRequestTree, encoding='utf8', method='xml')
        element = ET.XML(travelTimesRequestTree_as_str)
        ET.indent(element)
        #LoggerConfig.print_and_log_info(ET.tostring(element, encoding='unicode'))
        
        output_file.write("Send to SMT3 \n")
        output_file.write(ET.tostring(element, encoding='unicode'))
        output_file.write("\n")


        headers = {'Content-Type': 'application/xml'}
        full_url = _url + '/SMT3-REST-Server/computeTravelTimes'
        try:
            r = requests.post(full_url, data=ET.tostring(travelTimesRequestTree), headers=headers)
        except:
            print('Erreur de requête au serveur')
            #print(xml)
            quit()
        r.raise_for_status()
        logging.info("HTTP status:" +  str(r.status_code))
        
        element = ET.XML(r.text)
        ET.indent(element)
        #LoggerConfig.print_and_log_info(ET.tostring(element, encoding='unicode'))
        
        output_file.write("Received from SMT3 \n")
        output_file.write(ET.tostring(element, encoding='unicode'))
        output_file.write("\n")



    #@execution_time 
    def ProduireSimplesRuns(self, _url, _stepInSecond, _dwellTimeInSecond, _PasSauvegarde, _coeffOnRunTime, _ignoredMER, numero_premiere_mission_elementaire_a_traiter, numero_derniere_mission_elementaire_a_traiter, now_as_string_for_file_suffix):
        logging.info("Start calling ProduireSimplesRuns")
        start_time_ProduireSimplesRuns = time.time()
        numero_mission_elementaire_courante = 0
        nombre_simulations_smt3_effectuees = 0
        simulationResults = SimulationResultsSingleton()
        nbMissionsElementaires = len(self.missionsElementaires.values())
        
        output_file_name = "output\\ProduireSimplesRuns_xml_inputs_and_output-" + now_as_string_for_file_suffix + ".txt"
        output_file = open(output_file_name, "w")
        logging.info('Create output file:' + output_file_name)


        for mE in self.missionsElementaires.values():
            numero_mission_elementaire_courante = numero_mission_elementaire_courante + 1
            LoggerConfig.print_and_log_info(str(numero_mission_elementaire_courante) + " eme ME " + mE.nom + " sur " + str(nbMissionsElementaires) + " . Avancement:" + str(round(numero_mission_elementaire_courante*100/nbMissionsElementaires,2)) + "%")
            start_time_mission_elementaire = time.time()
            is_current_mission_elementaire_to_be_computed = numero_mission_elementaire_courante >= numero_premiere_mission_elementaire_a_traiter and numero_mission_elementaire_courante <= numero_derniere_mission_elementaire_a_traiter
            if  is_current_mission_elementaire_to_be_computed:
                numero_nature = 0
                for nature in mE.missionElementaireRegulation.naturesTrains:
                    numero_nature = numero_nature + 1
                    numero_modele = 0
                    #LoggerConfig.print_and_log_info(mE.nom = " nature:" + str(nature))
                    #nature = self.natures[natureitem]
                    for modele in nature.modeles:
                        
                        logging.info(mE.nom + " nature " + str(nature) + " modele:" + str(modele))
                        numero_modele = numero_modele + 1
                        if(modele.aSimuler):
                            if((mE.compositionTrain == nature.composition or mE.compositionTrain == "US+UM") and simulationResults.FindSimpleRunSimulation(mE.missionElementaireRegulation, modele) != None):
                                output_file.write(str(numero_mission_elementaire_courante) + " eme mission elementaire " + str(numero_modele) + " : " + str(datetime.now()) + " : Already Exist ["+mE.nom+","+modele.nom+"]")
                                output_file.write("\n")
                                LoggerConfig.print_and_log_info(str(numero_mission_elementaire_courante) + " eme mission elementaire " + str(numero_modele) + " : " + str(datetime.now()) + " : Already Exist ["+mE.nom+","+modele.nom+"]")
                            elif(mE.compositionTrain == nature.composition or mE.compositionTrain == "US+UM"):
                                #Envoi de la requête
                                output_file.write("\n")
                                start_time_SimulerSimpleRunSimulation = time.time()
                                nombre_simulations_smt3_effectuees = nombre_simulations_smt3_effectuees + 1
                                LoggerConfig.print_and_log_info("Lancement simulation " + str(numero_mission_elementaire_courante) + " eme mission elementaire ["+mE.nom+"] " + str(nombre_simulations_smt3_effectuees) + " eme simulation "+ str(numero_modele) + " eme modele : ["+modele.nom+"] ")
                                output_file.write("Lancement simulation " + str(numero_mission_elementaire_courante) + " eme mission elementaire ["+mE.nom+"] " + str(nombre_simulations_smt3_effectuees) + " eme simulation "+ str(numero_modele) + " eme modele : ["+modele.nom+"] " +  " : Simulation ["+mE.nom+","+modele.nom+"] ")

                                self.SimulerSimpleRunSimulation(_url, _stepInSecond, _dwellTimeInSecond, _coeffOnRunTime, mE, modele, output_file, _ignoredMER)
                                elapsed_time_SimulerSimpleRunSimulation = time.time() - start_time_SimulerSimpleRunSimulation 
                                LoggerConfig.print_and_log_info("Simulation " + str(nombre_simulations_smt3_effectuees) + " [" + mE.nom + "," + modele.nom + "]" + ". computed in: " + format(elapsed_time_SimulerSimpleRunSimulation, '.2f') + " s")
                                
                                
                                if elapsed_time_SimulerSimpleRunSimulation > 4:
                                    LoggerConfig.print_and_log_warning("SMT3 was slow for mission elementaire " + str(numero_modele) + " [" + mE.nom + "," + modele.nom + "]" + ". Elapsed: " + format(elapsed_time_SimulerSimpleRunSimulation, '.2f') + " s")
                                
                                if(not (nombre_simulations_smt3_effectuees % _PasSauvegarde)):
                                    LoggerConfig.print_and_log_info("Save output file with partial results")
                                    output_file.flush()
                                    # typically the above line would do. however this is used to ensure that the file is written
                                    os.fsync(output_file.fileno())
            else:
                logging.info(str(numero_mission_elementaire_courante) + " eme mission elementaire a ignorer: " + str(round(numero_mission_elementaire_courante*100/nbMissionsElementaires,2)) + "%")


        logging.info('Close output file:' + output_file_name)
        output_file.close()
        
    #@execution_time 
    def DefinirIntervalMax__disabled_YDA(self, mE1, mE2, modtrain1, modtrain2):
        logging.info("Start calling DefinirIntervalMax")
        headwaySimulation = IntervalResults()
        headwaySimulation.tempsIntervallePerturbeME = "MAX_INTERVAL"
        headwaySimulation.tempsIntervalleNonPerturbeME = "MAX_INTERVAL"
        headwaySimulation.tempsEspacementPerturbeME = "MAX_SPACING"
        headwaySimulation.tempsEspacementNonPerturbeME = "MAX_SPACING"
        for tra in mE2.missionElementaireRegulation.transitions:
            traTime = IntervalEspacementTransition(tra)
            headwaySimulation.transitions.append(traTime)
        return headwaySimulation

    #@execution_time 
    def ExporterCouplesMeSePerturbantCalcules__disabled_YDA(self, _nomFichier):
        logging.info("Start calling ExporterCouplesMeSePerturbantCalcules")
        Dict = {'mE1': [], 'mE2': [], 'Raison': []}
        for couple in self.couplesMeSePerturbantCalculees:
            Dict['mE1'].append(couple[0].nom)
            Dict['mE2'].append(couple[1].nom)
            Dict['Raison'].append(couple[2])

        df = panda.DataFrame(Dict)
        df.to_csv(_nomFichier, sep=';')

    #@execution_time 
    def IsMissionsElementairesSePerturbentParSig__disabled_YDA(self, mE1, mE2):
        logging.info("Start calling IsMissionsElementairesSePerturbentParSig")
        tvdEspacementCommun = False
        for sigMe1 in mE1.signaux:
            if(sigMe1['CommandeSignalAAjouter'] == True):
                for sigMe2 in mE2.signaux:
                    if(sigMe2['CommandeSignalAAjouter'] == True):
                        for tvdMe1 in sigMe1['CondSignalVert_TVDLibres']:
                            for tvdMe2 in sigMe2['CondSignalVert_TVDLibres']:
                                if(tvdMe1 == tvdMe2):
                                    tvdEspacementCommun = True
        aiguilleCommune = False
        for itiMe1 in mE1.itineraires:
            for itiMe2 in mE2.itineraires:
                aiguillesMe1 = itiMe1['Itineraire'].aiguillesParcourues #+ itiMe1['Itineraire'].aiguillesEnProtection
                aiguillesMe2 = itiMe2['Itineraire'].aiguillesParcourues #+ itiMe2['Itineraire'].aiguillesEnProtection
                for aigMe1 in aiguillesMe1:
                    for aigMe2 in aiguillesMe2:
                        if(aigMe1.aiguille == aigMe2.aiguille):
                            aiguilleCommune = True
                aiguillesMe1 = itiMe1['Itineraire'].aiguillesParcourues + itiMe1['Itineraire'].aiguillesEnProtection
                aiguillesMe2 = itiMe2['Itineraire'].aiguillesParcourues + itiMe2['Itineraire'].aiguillesEnProtection
                for aigMe1 in aiguillesMe1:
                    for aigMe2 in aiguillesMe2:
                        if(aigMe1.aiguille == aigMe2.aiguille and aigMe1.position != aigMe2.position):
                            aiguilleCommune = True

        mEsePerturbent = False
        if(mE1.missionElementaireRegulation == mE2.missionElementaireRegulation):
            mEsePerturbent = True
        # Les deux missions élémentaires ont au moins une aiguille en commun, elles peuvent se perturber
        elif(aiguilleCommune):
            mEsePerturbent = True
        # Les deux missions élémentaires ont au moins un CDV à contrôler en commun, elles peuvent se perturber
        elif(tvdEspacementCommun):
            mEsePerturbent = True

        return mEsePerturbent

    #@execution_time 
    def ScoreMissionsElementairesSePerturbent__disabled_YDA(self, mE1, mE2):
        logging.info("Start calling ScoreMissionsElementairesSePerturbent")
        #print(mE1.nom + " vs " + mE2.nom)
        tvdEspacementCommun = 0
        for sigMe1 in mE1.signaux:
            if(sigMe1['CommandeSignalAAjouter'] == True):
                for sigMe2 in mE2.signaux:
                    if(sigMe2['CommandeSignalAAjouter'] == True):
                        for tvdMe1 in sigMe1['CondSignalVert_TVDLibres']:
                            for tvdMe2 in sigMe2['CondSignalVert_TVDLibres']:
                                if(tvdMe1 == tvdMe2):
                                    tvdEspacementCommun = tvdEspacementCommun + 1
        aiguilleCommune = 0
        for itiMe1 in mE1.itineraires:
            for itiMe2 in mE2.itineraires:
                aiguillesMe1 = itiMe1['Itineraire'].aiguillesParcourues #+ itiMe1['Itineraire'].aiguillesEnProtection
                aiguillesMe2 = itiMe2['Itineraire'].aiguillesParcourues #+ itiMe2['Itineraire'].aiguillesEnProtection
                for aigMe1 in aiguillesMe1:
                    for aigMe2 in aiguillesMe2:
                        if(aigMe1.aiguille == aigMe2.aiguille and aigMe1.position == aigMe2.position):
                            aiguilleCommune = aiguilleCommune + 1
                aiguillesMe1 = itiMe1['Itineraire'].aiguillesParcourues + itiMe1['Itineraire'].aiguillesEnProtection
                aiguillesMe2 = itiMe2['Itineraire'].aiguillesParcourues + itiMe2['Itineraire'].aiguillesEnProtection
                for aigMe1 in aiguillesMe1:
                    for aigMe2 in aiguillesMe2:
                        if(aigMe1.aiguille == aigMe2.aiguille and aigMe1.position != aigMe2.position):
                            aiguilleCommune = aiguilleCommune + 1

        poCommun = 0
        arretSurParcours = 0
        sortieDeDomaineSurParcours = 0
        if(mE1.missionElementaireRegulation.transitions[0].pointOptimisationOrigine == mE2.missionElementaireRegulation.transitions[0].pointOptimisationOrigine):
            poCommun = poCommun + 1
        if(mE1.missionElementaireRegulation.transitions[0].pointOptimisationOrigine == mE2.missionElementaireRegulation.transitions[0].pointOptimisationDestination):
            poCommun = poCommun + 1
        if(mE1.missionElementaireRegulation.transitions[0].pointOptimisationDestination == mE2.missionElementaireRegulation.transitions[0].pointOptimisationOrigine):
            poCommun = poCommun + 1

        for tra1 in mE1.missionElementaireRegulation.transitions:
            if(tra1.pointOptimisationDestination == mE2.missionElementaireRegulation.poDestination and not mE2.missionElementaireRegulation.poDestination.isPTES):
                arretSurParcours = arretSurParcours + 1
            if(tra1.pointOptimisationDestination == mE2.missionElementaireRegulation.poDestination and mE2.missionElementaireRegulation.poDestination.isPTES):
                sortieDeDomaineSurParcours = sortieDeDomaineSurParcours + 1
            for tra2 in mE2.missionElementaireRegulation.transitions:
                if(tra1.pointOptimisationDestination == tra2.pointOptimisationDestination):
                    poCommun = poCommun + 1

        for tra in mE2.missionElementaireRegulation.transitions:
            if(tra.pointOptimisationDestination == mE1.missionElementaireRegulation.poDestination and not mE1.missionElementaireRegulation.poDestination.isPTES):
                arretSurParcours = arretSurParcours + 1
            if(tra.pointOptimisationDestination == mE1.missionElementaireRegulation.poDestination and mE1.missionElementaireRegulation.poDestination.isPTES):
                sortieDeDomaineSurParcours = sortieDeDomaineSurParcours + 1

        return tvdEspacementCommun + aiguilleCommune + poCommun * 10 + arretSurParcours * 30 + sortieDeDomaineSurParcours * 5

    #@execution_time 
    def IsMissionsElementairesSePerturbentParPointsOptimisation__disabled_YDA(self, mE1, mE2):
        logging.info("Start calling IsMissionsElementairesSePerturbentParPointsOptimisation")
        poDestinationTransitionCommun = False
        for transition1 in mE1.missionElementaireRegulation.transitions:
            for transition2 in mE2.missionElementaireRegulation.transitions:
                if(transition1.segmentsParcourus[0].sens == transition2.segmentsParcourus[0].sens):
                    if(transition1.pointOptimisationDestination == transition2.pointOptimisationDestination):
                        poDestinationTransitionCommun = True

        mEsePerturbent = False
        if(mE1.missionElementaireRegulation == mE2.missionElementaireRegulation):
            mEsePerturbent = True
        elif(poDestinationTransitionCommun):
            mEsePerturbent = True

        return mEsePerturbent

    #@execution_time 
    def IsMissionsElementairesSePerturbentParTransitions__disabled_YDA(self, mE1, mE2):
        logging.info("Start calling IsMissionsElementairesSePerturbentParTransitions")
        poDestinationTransitionCommun = False
        for transition in mE1.missionElementaireRegulation.transitions:
            if(transition in mE2.missionElementaireRegulation.transitions):
                poDestinationTransitionCommun = True

        mEsePerturbent = False
        if(mE1.missionElementaireRegulation == mE2.missionElementaireRegulation):
            mEsePerturbent = True
        elif(poDestinationTransitionCommun):
            mEsePerturbent = True

        return mEsePerturbent

    #@execution_time 
    def ProduireConfigurationSimulationsPerturbees__disabled_YDA(self):
        logging.info("Start calling ProduireConfigurationSimulationsPerturbees")
        simuAFaire = 0
        simuACopier = 0
        mEconfigureesDone = 0
        nbmEAConfigurer = len(self.missionsElementaires.values())
        simulationResults = SimulationResultsSingleton()
        simulationResults.configurationSimulationsPerturbees = None
        simulationResults.configurationSimulationsPerturbees = {}
        for mE2 in self.missionsElementaires.values():
            mE2.worstMe = None
            for mE1 in self.missionsElementaires.values():
                mEsePerturbent = self.IsMissionsElementairesSePerturbentParTransitions(mE1, mE2)
                if(mEsePerturbent):
                        for combi in self.combinaisonsTypesEspacements:
                            for modtrain2 in combi['ModeleT2']:
                                if(modtrain2.aSimuler):
                                    for modtrain1 in combi['ModeleT1']:
                                        if(modtrain1.aSimuler):
                                            if(modtrain1.nature in mE1.missionElementaireRegulation.naturesTrains and (modtrain1.nature.composition == mE1.compositionTrain or mE1.compositionTrain == "US+UM")):
                                                if(modtrain2.nature in mE2.missionElementaireRegulation.naturesTrains and (modtrain2.nature.composition == mE2.compositionTrain or mE2.compositionTrain == "US+UM") and mE2.missionElementaireRegulation.mode == "Optimisable"):
                                                    linesofT1InMELines = [value for value in modtrain1.nature.lignes if value in mE1.missionElementaireRegulation.lignes]
                                                    linesofT2InMELines = [value for value in modtrain2.nature.lignes if value in mE2.missionElementaireRegulation.lignes]
                                                    key = mE1.nom + "/" + mE2.nom + "/" + modtrain1.nom + "/" + modtrain2.nom + "/Normale/Normale"
                                                    if(len(mE2.missionElementaireRegulation.lignes) > 0 and len(mE1.missionElementaireRegulation.lignes) > 0 and mE1.missionElementaireRegulation.mode == "Optimisable" and len(linesofT1InMELines) > 0 and len(linesofT2InMELines) > 0):
                                                        #Les simulations sont à faire
                                                        #print(key)
                                                        if(key not in simulationResults.configurationSimulationsPerturbees):
                                                            simulationResults.AjouterConfigurationSimulationPerturbee(key, mE1, modtrain1, "Normale",  mE2, modtrain2, "Normale", "")
                                                            simuAFaire = simuAFaire + 1
                                                    else:
                                                        if(mE1.segmentsParcourus[0].sens == mE2.segmentsParcourus[0].sens):
                                                            mE1alternate = mE2.FindWorstElementaryTripWithNature(modtrain1.nature)
                                                            mE1alternateforCompo = mE1alternate

                                                            if(mE1alternate == None):
                                                                mE1alternate = mE2.FindWorstElementaryTripWithNature(modtrain1.nature, mE1.missionElementaireRegulation.poOrigine)
                                                            if(mE1alternate == None):
                                                                mE1alternate = mE1.missionElementaireRegulation

                                                            mE1alternateforCompo = mE1alternate
                                                            if(mE1.compositionTrain == "US"):
                                                                mE1alternateforCompo = self.missionsElementaires["C:" + mE1alternate.nom]
                                                            else:
                                                                mE1alternateforCompo = self.missionsElementaires["L:" + mE1alternate.nom]

                                                            copykey = mE1alternateforCompo.nom + "/" + mE2.nom + "/" + modtrain1.nom + "/" + modtrain2.nom + "/Normale/Normale"
                                                            #print(key + " copy of " + copykey)
                                                            if(copykey not in simulationResults.configurationSimulationsPerturbees):
                                                                simulationResults.AjouterConfigurationSimulationPerturbee(copykey, mE1alternateforCompo, modtrain1, "Normale",  mE2, modtrain2, "Normale", "")
                                                                simuAFaire = simuAFaire + 1
                                                            if(key not in simulationResults.configurationSimulationsPerturbees):
                                                                simulationResults.AjouterConfigurationSimulationPerturbee(key, mE1, modtrain1, "Normale",  mE2, modtrain2, "Normale", copykey)
                                                                simuACopier = simuACopier + 1
                                                        else:
                                                            meContreSens = mE2.FindBestContreSensPerturbanteME(modtrain1.nature.composition, modtrain1.nature)
                                                            if(meContreSens != None):
                                                                copykey = meContreSens.nom + "/" + mE2.nom + "/" + modtrain1.nom + "/" + modtrain2.nom + "/Normale/Normale"
                                                                #print(key + " copy of " + copykey)
                                                                if(copykey not in simulationResults.configurationSimulationsPerturbees):
                                                                    simulationResults.AjouterConfigurationSimulationPerturbee(copykey, meContreSens, modtrain1, "Normale", mE2, modtrain2, "Normale", "")
                                                                    simuAFaire = simuAFaire + 1
                                                                if(key not in simulationResults.configurationSimulationsPerturbees):
                                                                    simulationResults.AjouterConfigurationSimulationPerturbee(key, mE1, modtrain1, "Normale",  mE2, modtrain2, "Normale", copykey)
                                                                    simuACopier = simuACopier + 1

            mEconfigureesDone = mEconfigureesDone + 1
            percent = round((mEconfigureesDone / nbmEAConfigurer)*100.0, 2)
            print("Progression : " + str(percent) + "%")

        print("Simu à faire : " + str(simuAFaire))
        print("Simu à copier : " + str(simuACopier))

    #@execution_time 
    def EstimerNombreDeSimulation__disabledYDA__disabled_YDA(self):
        logging.info("Start calling EstimerNombreDeSimulation__disabledYDA")
        nbModelTrain = 2+8
        nbSimulationSimpleRun = 0
        nbSimulationInterval = 0
        nbSimulationParNbChgVoie = {}
        for mE in self.missionsElementairesRegulation.values():
            for natureMe in mE.naturesTrains:
                for modeleMe in natureMe.modeles:
                    if(modeleMe.aSimuler):
                        nbSimulationSimpleRun = nbSimulationSimpleRun + 1

        nbTypeEspacement = 134

        print("Nombre de MER : " + str(len(self.missionsElementairesRegulation)))
        print("Nombre de simulation SimpleRun : " + str(nbSimulationSimpleRun))

        nbCombinaisonsMe = 0
        nbCombinaisonsMeCalculees = 0
        for mE2 in self.missionsElementaires.values():
            DoByItSelf = False
            DidByItSelf = False
            DoByItSelfReverse = False
            DidByItSelfReverse = False
            for mE1 in self.missionsElementaires.values():
                calculee = False
                segmentCommun = False
                # for segMe1 in mE1.segmentsParcourus[1:-1]:
                #     for segMe2 in mE2.segmentsParcourus[1:-1]:
                #         if(segMe1.segment == segMe2.segment):
                #             if(segMe1.segment != mE1.missionElementaireRegulation.poOrigine.segment and segMe1.segment != mE1.missionElementaireRegulation.poDestination.segment):
                #                 if(segMe2.segment != mE2.missionElementaireRegulation.poOrigine.segment and segMe2.segment != mE2.missionElementaireRegulation.poDestination.segment):
                #                     segmentCommun = True

                tvdEspacementCommun = False
                for sigMe1 in mE1.signaux:
                    if(sigMe1['CommandeSignalAAjouter'] == True):
                        for sigMe2 in mE2.signaux:
                            if(sigMe2['CommandeSignalAAjouter'] == True):
                                for tvdMe1 in sigMe1['CondSignalVert_TVDLibres']:
                                    for tvdMe2 in sigMe2['CondSignalVert_TVDLibres']:
                                        if(tvdMe1 == tvdMe2):
                                            tvdEspacementCommun = True

                #Transit à commander commun
                cmdTransitCommun = False
                # itineraire['condsDispoTransits'] = condsDispoTransits
                # itineraire['reservsTransits'] = reservsTransits

                aiguilleCommune = False
                for itiMe1 in mE1.itineraires:
                    for itiMe2 in mE2.itineraires:
                        aiguillesMe1 = itiMe1['Itineraire'].aiguillesParcourues #+ itiMe1['Itineraire'].aiguillesEnProtection
                        aiguillesMe2 = itiMe2['Itineraire'].aiguillesParcourues #+ itiMe2['Itineraire'].aiguillesEnProtection
                        for aigMe1 in aiguillesMe1:
                            for aigMe2 in aiguillesMe2:
                                if(aigMe1.aiguille == aigMe2.aiguille):
                                    aiguilleCommune = True
                        aiguillesMe1 = itiMe1['Itineraire'].aiguillesParcourues + itiMe1['Itineraire'].aiguillesEnProtection
                        aiguillesMe2 = itiMe2['Itineraire'].aiguillesParcourues + itiMe2['Itineraire'].aiguillesEnProtection
                        for aigMe1 in aiguillesMe1:
                            for aigMe2 in aiguillesMe2:
                                if(aigMe1.aiguille == aigMe2.aiguille and aigMe1.position != aigMe2.position):
                                    aiguilleCommune = True

                condCommCommune = False
                # for itiMe1 in mE1.itineraires:
                #     for itiMe2 in mE2.itineraires:
                #         for tvdMe1 in itiMe1['TVDCondCommutation']: #pour aiguille en position de protection : seulement si incompatible avec position de protection
                #             for tvdMe2 in itiMe2['TVDCondCommutation']:
                #                 if(tvdMe1 == tvdMe2):
                #                     condCommCommune = True

                mEsePerturbent = False
                if(mE1.missionElementaireRegulation == mE2.missionElementaireRegulation):
                    mEsePerturbent = True
                elif(mE1.missionElementaireRegulation.poOrigine == mE2.missionElementaireRegulation.poOrigine):
                    mEsePerturbent = True
                # Les deux missions élémentaires ont au moins un segment en commun, elles peuvent se perturber
                elif(segmentCommun):
                    mEsePerturbent = True
                # Les deux missions élémentaires ont au moins une aiguille en commun, elles peuvent se perturber
                elif(aiguilleCommune):
                    mEsePerturbent = True
                # Les deux missions élémentaires ont au moins un CDV à contrôler en commun, elles peuvent se perturber
                elif(condCommCommune):
                    mEsePerturbent = True
                elif(tvdEspacementCommun):
                    mEsePerturbent = True

                if(mEsePerturbent):
                    #print("Se perturbent")
                    nbCombinaisonsMe = nbCombinaisonsMe + 1
                    if(len(mE2.missionElementaireRegulation.lignes) > 0 and len(mE1.missionElementaireRegulation.lignes) > 0):
                        #print("Se perturbent avec lignes")
                        for combi in self.combinaisonsTypesEspacements:
                            for modtrain2 in combi['ModeleT2']:
                                if(modtrain2.aSimuler):
                                    for modtrain1 in combi['ModeleT1']:
                                        if(modtrain1.aSimuler):
                                            if(modtrain1.nature in mE1.missionElementaireRegulation.naturesTrains and (modtrain1.nature.composition == mE1.compositionTrain or mE1.compositionTrain == "US+UM")):
                                                if(modtrain2.nature in mE2.missionElementaireRegulation.naturesTrains and (modtrain2.nature.composition == mE2.compositionTrain or mE2.compositionTrain == "US+UM") and mE2.missionElementaireRegulation.mode == "Optimisable"):
                                                    linesofT1InMELines = [value for value in modtrain1.nature.lignes if value in mE1.missionElementaireRegulation.lignes]
                                                    linesofT2InMELines = [value for value in modtrain2.nature.lignes if value in mE2.missionElementaireRegulation.lignes]
                                                    #print(str(len(linesofT1InMELines)))
                                                    #print(str(len(linesofT2InMELines)))
                                                    if(mE1.missionElementaireRegulation.mode == "Optimisable" and len(linesofT1InMELines) > 0 and len(linesofT2InMELines) > 0):
                                                        if(mE1 == mE2):
                                                            DidByItSelf = True
                                                        if(mE1.missionElementaireRegulation.segmentsParcourus[0].sens != mE2.missionElementaireRegulation.segmentsParcourus[0].sens):
                                                            DidByItSelfReverse = True
                                                        calculee = True
                                                        coupleSePerturbantCalcule = []
                                                        coupleSePerturbantCalcule.append(mE1.missionElementaireRegulation)
                                                        coupleSePerturbantCalcule.append(mE2.missionElementaireRegulation)
                                                        coupleSePerturbantCalcule.append("Perturbation direct entre deux lignes nominales")
                                                        if(coupleSePerturbantCalcule not in self.couplesMeSePerturbantCalculees):
                                                            self.couplesMeSePerturbantCalculees.append(coupleSePerturbantCalcule)
                                                        nbSimulationInterval = nbSimulationInterval + 1
                                                        if(str(mE2.missionElementaireRegulation.nbChangementVoie) not in nbSimulationParNbChgVoie):
                                                            nbSimulationParNbChgVoie[str(mE2.missionElementaireRegulation.nbChangementVoie)] = 1
                                                        else:
                                                            nbSimulationParNbChgVoie[str(mE2.missionElementaireRegulation.nbChangementVoie)] = nbSimulationParNbChgVoie[str(mE2.missionElementaireRegulation.nbChangementVoie)] + 1
                                                    else:
                                                        DoByItSelf = True
                                                        if(mE1.missionElementaireRegulation.segmentsParcourus[0].sens != mE2.missionElementaireRegulation.segmentsParcourus[0].sens):
                                                            DoByItSelfReverse = True
                    else:
                        DoByItSelf = True
                        if(mE1.missionElementaireRegulation.segmentsParcourus[0].sens != mE2.missionElementaireRegulation.segmentsParcourus[0].sens):
                            DoByItSelfReverse = True

                    if(calculee):
                        nbCombinaisonsMeCalculees = nbCombinaisonsMeCalculees + 1

            if(DoByItSelf == True and DidByItSelf == False):
                if(not calculee):
                    nbCombinaisonsMeCalculees = nbCombinaisonsMeCalculees + 1
                    calculee = True
                for combi in self.combinaisonsTypesEspacements:
                    for modtrain2 in combi['ModeleT2']:
                        if(modtrain2.aSimuler):
                            for modtrain1 in combi['ModeleT1']:
                                if(modtrain1.aSimuler):
                                    if(modtrain1.nature in mE2.missionElementaireRegulation.naturesTrains and (modtrain1.nature.composition == mE2.compositionTrain or mE2.compositionTrain == "US+UM")):
                                        if(modtrain2.nature in mE2.missionElementaireRegulation.naturesTrains and (modtrain2.nature.composition == mE2.compositionTrain or mE2.compositionTrain == "US+UM") and mE2.missionElementaireRegulation.mode == "Optimisable"):
                                            nbSimulationInterval = nbSimulationInterval + 1
                                            coupleSePerturbantCalcule = []
                                            coupleSePerturbantCalcule.append(mE2.missionElementaireRegulation)
                                            coupleSePerturbantCalcule.append(mE2.missionElementaireRegulation)
                                            coupleSePerturbantCalcule.append("Perturbation d'une mE non nominale avec elle même")
                                            if(coupleSePerturbantCalcule not in self.couplesMeSePerturbantCalculees):
                                                self.couplesMeSePerturbantCalculees.append(coupleSePerturbantCalcule)

            if(DoByItSelfReverse == True and DidByItSelfReverse == False):
                if(not calculee):
                    nbCombinaisonsMeCalculees = nbCombinaisonsMeCalculees + 1
                    calculee = True
                for combi in self.combinaisonsTypesEspacements:
                    for modtrain2 in combi['ModeleT2']:
                        if(modtrain2.aSimuler):
                            for modtrain1 in combi['ModeleT1']:
                                if(modtrain1.aSimuler):
                                    if(modtrain1.nature in mE2.missionElementaireRegulation.naturesTrains and (modtrain1.nature.composition == mE2.compositionTrain or mE2.compositionTrain == "US+UM")):
                                        if(modtrain2.nature in mE2.missionElementaireRegulation.naturesTrains and (modtrain2.nature.composition == mE2.compositionTrain or mE2.compositionTrain == "US+UM") and mE2.missionElementaireRegulation.mode == "Optimisable"):
                                            nbSimulationInterval = nbSimulationInterval + 1
                                            coupleSePerturbantCalcule = []
                                            coupleSePerturbantCalcule.append(mE2.missionElementaireRegulation)
                                            coupleSePerturbantCalcule.append(mE2.missionElementaireRegulation)
                                            coupleSePerturbantCalcule.append("Perturbation d'une mE non nominale une mE de sens opposée")
                                            if(coupleSePerturbantCalcule not in self.couplesMeSePerturbantCalculees):
                                                self.couplesMeSePerturbantCalculees.append(coupleSePerturbantCalcule)

        nbSimulationExploit = nbSimulationInterval

        print("Nombre de couples de ME se perturbant : " + str(nbCombinaisonsMe))
        print("Nombre de couples de ME se perturbant calculées : " + str(nbCombinaisonsMeCalculees))
        print("Nombre de simulation Interval : " + str(nbSimulationInterval))
        print("Nombre de simulation Exploitation : " + str(nbSimulationExploit))
        print("Nombre de simulation Total : " + str(nbSimulationSimpleRun + nbSimulationInterval + nbSimulationExploit))
        print("Nombre de simulation par NbChangementVoie :")
        print(str(nbSimulationParNbChgVoie))
    #Cette méthode permet de trouver les CDV à l'intérieur d'un interval sur l'ensemble d'un parcours de segments
    #@execution_time 
    def CDVDansInterval__disabled_YDA(self, ParcoursSegments, OrigineSegment, OrigineAbs, DestinationSegment, DestinationAbs):
        logging.info("Start calling CDVDansInterval")
        CDVList = []
        premierSegTrouve = False
        dernierSegTrouve = False
        sens = None
        segmentsDansParcours = []
        segmentsPrecedentPremierSegDansInterval = []
        segmentsDansInterval = []
        segmentsSuivantDernierSegDansInterval = []
        CdvAAnalyser = {}

        for segment in ParcoursSegments:
            sens = segment.sens
            segmentsDansParcours.append(segment.segment)

            if(premierSegTrouve == False and segment.segment != OrigineSegment):
                segmentsPrecedentPremierSegDansInterval.append(segment.segment)
            elif(premierSegTrouve == False and segment.segment == OrigineSegment):
                premierSegTrouve = True
                segmentsDansInterval.append(segment.segment)
                if(segment.segment == DestinationSegment):
                    #print("Dernier Seg trouve")
                    dernierSegTrouve = True
            elif(premierSegTrouve == True and segment.segment == DestinationSegment):
                #print("Dernier Seg trouve")
                dernierSegTrouve = True
                segmentsDansInterval.append(segment.segment)
            elif(premierSegTrouve == True and dernierSegTrouve == False):
                segmentsDansInterval.append(segment.segment)
            elif(premierSegTrouve == True and dernierSegTrouve == True):
                segmentsSuivantDernierSegDansInterval.append(segment.segment)

        # print("segmentsDansParcours :")
        # for s in segmentsDansParcours:
        #     print(s.nom + ",")
        # print("segmentsDansInterval :")
        # for s in segmentsDansInterval:
        #     print(s.nom + ",")
        # print("segmentsPrecedentPremierSegDansInterval :")
        # for s in segmentsPrecedentPremierSegDansInterval:
        #     print(s.nom + ",")
        # print("segmentsSuivantDernierSegDansInterval :")
        # for s in segmentsSuivantDernierSegDansInterval:
        #     print(s.nom + ",")

        for segment in segmentsDansInterval:
            cdvs = self.RechercherCDVsAvecSegment(segment)
            for cdv in cdvs:
                if(cdv.nom not in CdvAAnalyser):
                    CdvAAnalyser[cdv.nom] = {}
                    CdvAAnalyser[cdv.nom]['NbExtremiteDansInterval'] = 0
                    CdvAAnalyser[cdv.nom]['SurParcoursAvantInterval'] = 0
                    CdvAAnalyser[cdv.nom]['SurParcoursApresInterval'] = 0
                    CdvAAnalyser[cdv.nom]['HorsParcours'] = 0
                    CdvAAnalyser[cdv.nom]['Segment'] = None
                    CdvAAnalyser[cdv.nom]['SegmentPosition'] = None
                    CdvAAnalyser[cdv.nom]['abs'] = None
                    CdvAAnalyser[cdv.nom]['CDV'] = cdv

                    for extremite in cdv.segsExtremites:
                        if(extremite['segment'] in segmentsDansInterval):
                            if(extremite['segment'] == OrigineSegment and extremite['segment'] == DestinationSegment):
                                if(sens == "CROISSANT" and extremite['abs'] >= OrigineAbs and extremite['abs'] <= DestinationAbs):
                                    CdvAAnalyser[cdv.nom]['NbExtremiteDansInterval'] = CdvAAnalyser[cdv.nom]['NbExtremiteDansInterval'] + 1
                                elif(sens == "DECROISSANT" and extremite['abs'] <= OrigineAbs and extremite['abs'] >= DestinationAbs):
                                    CdvAAnalyser[cdv.nom]['NbExtremiteDansInterval'] = CdvAAnalyser[cdv.nom]['NbExtremiteDansInterval'] + 1
                                elif(sens == "CROISSANT" and extremite['abs'] < OrigineAbs):
                                    CdvAAnalyser[cdv.nom]['SurParcoursAvantInterval'] = CdvAAnalyser[cdv.nom]['SurParcoursAvantInterval'] + 1
                                elif(sens == "DECROISSANT" and extremite['abs'] > OrigineAbs):
                                    CdvAAnalyser[cdv.nom]['SurParcoursAvantInterval'] = CdvAAnalyser[cdv.nom]['SurParcoursAvantInterval'] + 1
                                elif(sens == "CROISSANT" and extremite['abs'] > DestinationAbs):
                                    CdvAAnalyser[cdv.nom]['SurParcoursApresInterval'] = CdvAAnalyser[cdv.nom]['SurParcoursApresInterval'] + 1
                                elif(sens == "DECROISSANT" and extremite['abs'] < DestinationAbs):
                                    CdvAAnalyser[cdv.nom]['SurParcoursApresInterval'] = CdvAAnalyser[cdv.nom]['SurParcoursApresInterval'] + 1
                            elif(extremite['segment'] == OrigineSegment):
                                if(sens == "CROISSANT" and extremite['abs'] >= OrigineAbs):
                                    CdvAAnalyser[cdv.nom]['NbExtremiteDansInterval'] = CdvAAnalyser[cdv.nom]['NbExtremiteDansInterval'] + 1
                                elif(sens == "CROISSANT" and extremite['abs'] < OrigineAbs):
                                    CdvAAnalyser[cdv.nom]['SurParcoursAvantInterval'] = CdvAAnalyser[cdv.nom]['SurParcoursAvantInterval'] + 1
                                elif(sens == "DECROISSANT" and extremite['abs'] <= OrigineAbs):
                                    CdvAAnalyser[cdv.nom]['NbExtremiteDansInterval'] = CdvAAnalyser[cdv.nom]['NbExtremiteDansInterval'] + 1
                                elif(sens == "DECROISSANT" and extremite['abs'] > OrigineAbs):
                                    CdvAAnalyser[cdv.nom]['SurParcoursAvantInterval'] = CdvAAnalyser[cdv.nom]['SurParcoursAvantInterval'] + 1
                            elif(extremite['segment'] == DestinationSegment):
                                if(sens == "CROISSANT" and extremite['abs'] <= DestinationAbs):
                                    CdvAAnalyser[cdv.nom]['NbExtremiteDansInterval'] = CdvAAnalyser[cdv.nom]['NbExtremiteDansInterval'] + 1
                                elif(sens == "CROISSANT" and extremite['abs'] > DestinationAbs):
                                    CdvAAnalyser[cdv.nom]['SurParcoursApresInterval'] = CdvAAnalyser[cdv.nom]['SurParcoursApresInterval'] + 1
                                elif(sens == "DECROISSANT" and extremite['abs'] >= DestinationAbs):
                                    CdvAAnalyser[cdv.nom]['NbExtremiteDansInterval'] = CdvAAnalyser[cdv.nom]['NbExtremiteDansInterval'] + 1
                                elif(sens == "DECROISSANT" and extremite['abs'] < DestinationAbs):
                                    CdvAAnalyser[cdv.nom]['SurParcoursApresInterval'] = CdvAAnalyser[cdv.nom]['SurParcoursApresInterval'] + 1
                            else:
                                CdvAAnalyser[cdv.nom]['NbExtremiteDansInterval'] = CdvAAnalyser[cdv.nom]['NbExtremiteDansInterval'] + 1

                        if(extremite['segment'] in segmentsPrecedentPremierSegDansInterval):
                            CdvAAnalyser[cdv.nom]['SurParcoursAvantInterval'] = CdvAAnalyser[cdv.nom]['SurParcoursAvantInterval'] + 1

                        if(extremite['segment'] in segmentsSuivantDernierSegDansInterval):
                            CdvAAnalyser[cdv.nom]['SurParcoursApresInterval'] = CdvAAnalyser[cdv.nom]['SurParcoursApresInterval'] + 1

                        if(extremite['segment'] not in segmentsDansParcours):
                            CdvAAnalyser[cdv.nom]['HorsParcours'] = CdvAAnalyser[cdv.nom]['HorsParcours'] + 1
                        else:
                            segmentPosition = segmentsDansParcours.index(extremite['segment'])
                            if(CdvAAnalyser[cdv.nom]['Segment'] == None):
                                CdvAAnalyser[cdv.nom]['Segment'] = extremite['segment']
                                CdvAAnalyser[cdv.nom]['SegmentPosition'] = segmentPosition
                                CdvAAnalyser[cdv.nom]['abs'] = extremite['abs']
                            elif(segmentPosition > CdvAAnalyser[cdv.nom]['SegmentPosition']):
                                CdvAAnalyser[cdv.nom]['Segment'] = extremite['segment']
                                CdvAAnalyser[cdv.nom]['SegmentPosition'] = segmentPosition
                                CdvAAnalyser[cdv.nom]['abs'] = extremite['abs']
                            elif(segmentPosition == CdvAAnalyser[cdv.nom]['SegmentPosition']):
                                if(sens == "CROISSANT" and extremite['abs'] > CdvAAnalyser[cdv.nom]['abs']):
                                    CdvAAnalyser[cdv.nom]['abs'] = extremite['abs']
                                elif(sens == "DECROISSANT" and extremite['abs'] < CdvAAnalyser[cdv.nom]['abs']):
                                    CdvAAnalyser[cdv.nom]['abs'] = extremite['abs']



        CdvAAnalyserOrdonne = []
        for cdv in CdvAAnalyser.values():
            if(len(CdvAAnalyserOrdonne) < 1):
                CdvAAnalyserOrdonne.append(cdv)
            else:
                k = 0
                continuer = True
                segmentPosition = cdv['SegmentPosition']
                absPosition = cdv['abs']
                for cdvo in CdvAAnalyserOrdonne:
                    if(continuer == True):
                        if(segmentPosition < cdvo['SegmentPosition']):
                            CdvAAnalyserOrdonne.insert(k, cdv)
                            continuer = False
                        elif(segmentPosition == cdvo['SegmentPosition'] and sens == "CROISSANT" and absPosition < cdvo['abs']):
                            CdvAAnalyserOrdonne.insert(k, cdv)
                            continuer = False
                        elif(segmentPosition == cdvo['SegmentPosition'] and sens == "DECROISSANT" and absPosition > cdvo['abs']):
                            CdvAAnalyserOrdonne.insert(k, cdv)
                            continuer = False
                        else:
                            k=k+1
                            if(k>=len(CdvAAnalyserOrdonne)):
                                CdvAAnalyserOrdonne.append(cdv)
                                continuer = False

        for cdv in CdvAAnalyserOrdonne:
            #print("CDV : " + cdv['CDV'].nom)
            if(cdv['NbExtremiteDansInterval'] > 1):
                #print(str(cdv['NbExtremiteDansInterval']) + " Dans interval")
                CDVList.append(cdv['CDV'])
            elif(cdv['NbExtremiteDansInterval'] == 1 and cdv['SurParcoursApresInterval'] >= 1):
                CDVList.append(cdv['CDV'])
                #print(str(cdv['NbExtremiteDansInterval']) + " englobant fin d'interval " + str(cdv['SurParcoursApresInterval']))
            #print(str(cdv))

        #if(sens=="DECROISSANT"):
            #os.system("pause")

        return CDVList

    #Permet d'afficher un graphe
    #@execution_time 
    def print__disabled_YDA(self, _chainePrefixe = ""):
        logging.info("Start calling print")
        print("Graphe :")
        for __o in self.lignes.values():
            __o.print(_chainePrefixe+"+")
        os.system("PAUSE")
        for __o in self.stations.values():
            __o.print(_chainePrefixe+"+")
        os.system("PAUSE")
        for __o in self.PtAs.values():
            __o.print(_chainePrefixe+"+")
        os.system("PAUSE")
        for __o in self.segments.values():
            __o.print(_chainePrefixe+"+")
        os.system("PAUSE")
        for __o in self.voies.values():
            __o.print(_chainePrefixe+"+")
        os.system("PAUSE")
        for __o in self.troncons.values():
            __o.print(_chainePrefixe+"+")
        os.system("PAUSE")
        for __o in self.signals.values():
            __o.print(_chainePrefixe+"+")
        os.system("PAUSE")
        for __o in self.aiguilles.values():
            __o.print(_chainePrefixe+"+")
        os.system("PAUSE")
        for __o in self.CDVs.values():
            __o.print(_chainePrefixe+"+")
        os.system("PAUSE")
        for __o in self.TVDs.values():
            __o.print(_chainePrefixe+"+")

    #Permet de rechercher une aiguille avec ses trois segments de définition
    #@execution_time 
    def RechercherAiguilleAvecSegments__YDA__disabled_YDA(self, _segment1, _segment2, _segment3):
        logging.info("Start calling RechercherAiguilleAvecSegments__YDA")
        for aiguille in self.aiguilles.values():
            if(aiguille.segTalonDroite is _segment1 and aiguille.segTalonGauche is _segment2 and aiguille.segPointe is _segment3):
                return aiguille
            elif(aiguille.segTalonDroite is _segment2 and aiguille.segTalonGauche is _segment3 and aiguille.segPointe is _segment1):
                return aiguille
            elif(aiguille.segTalonDroite is _segment3 and aiguille.segTalonGauche is _segment1 and aiguille.segPointe is _segment2):
                return aiguille
            elif(aiguille.segTalonDroite is _segment2 and aiguille.segTalonGauche is _segment1 and aiguille.segPointe is _segment3):
                return aiguille
            elif(aiguille.segTalonDroite is _segment3 and aiguille.segTalonGauche is _segment2 and aiguille.segPointe is _segment1):
                return aiguille
            elif(aiguille.segTalonDroite is _segment1 and aiguille.segTalonGauche is _segment3 and aiguille.segPointe is _segment2):
                return aiguille

        return None

    #Cette méthode permet de rechercher un quai sur l'ensemble du domaine
    #@execution_time 
    def RechercherQuai__disabled_YDA(self, _nomQuai):
        logging.info("Start calling RechercherQuai")
        for station in self.stations.values():
            if(_nomQuai in station.quais):
                return station.quais[_nomQuai]

        return None

    #Permet de générer les joints de CdV ou les extrémités de CDV en limite de domaine
    #les joints de CdV sont enregistrées dans self.JointsCDVs{} selon un clé prenant la forme d'une chaîne de caractère NomCdv1_NomCdv2 avec NomCdv1 et NomCdv2
    #le nom des deux CDV, et NomCdv1 précède NomCdv2 dans l'alphabet.
    #@execution_time 
    def GenererJointsCDVs__disabled_YDA(self):
        logging.info("Start calling GenererJointsCDVs")
        #On recherche deux CDV qui auraient la même position sur segment dans une de ses extrémités
        for i in self.CDVs.values():
            for j in i.segsExtremites:
                foundExtSeg = False
                for k in self.CDVs.values():
                    for l in k.segsExtremites:
                        if(i!=k):
                            if(j['segment'] == l['segment'] and j['abs'] == l['abs']):
                                foundExtSeg = True
                                self.AjouterJointCDV(i, k, j['segment'], j['abs'])
                            elif(j['segment'] != l['segment']):
                                if(j['segment'].segment1VoisinAval == l['segment'] and j['segment'] == l['segment'].segment1VoisinAmont):
                                    if(j['abs'] == j['segment'].longueur and l['abs'] == 0):
                                        foundExtSeg = True
                                        self.AjouterJointCDV(i, k, j['segment'], j['abs'])
                                if(foundExtSeg == False and j['segment'].segment1VoisinAval == l['segment'] and j['segment'] == l['segment'].segment2VoisinAmont):
                                    if(j['abs'] == j['segment'].longueur and l['abs'] == 0):
                                        foundExtSeg = True
                                        self.AjouterJointCDV(i, k, j['segment'], j['abs'])
                                if(foundExtSeg == False and j['segment'].segment2VoisinAval == l['segment'] and j['segment'] == l['segment'].segment1VoisinAmont):
                                    if(j['abs'] == j['segment'].longueur and l['abs'] == 0):
                                        foundExtSeg = True
                                        self.AjouterJointCDV(i, k, j['segment'], j['abs'])
                                if(foundExtSeg == False and j['segment'].segment2VoisinAval == l['segment'] and j['segment'] == l['segment'].segment2VoisinAmont):
                                    if(j['abs'] == j['segment'].longueur and l['abs'] == 0):
                                        foundExtSeg = True
                                        self.AjouterJointCDV(i, k, j['segment'], j['abs'])
                                if(foundExtSeg == False and j['segment'].segment1VoisinAmont == l['segment'] and j['segment'] == l['segment'].segment1VoisinAval):
                                    if(j['abs'] == 0 and l['abs'] == l['segment'].longueur):
                                        foundExtSeg = True
                                        self.AjouterJointCDV(i, k, j['segment'], j['abs'])
                                if(foundExtSeg == False and j['segment'].segment1VoisinAmont == l['segment'] and j['segment'] == l['segment'].segment2VoisinAval):
                                    if(j['abs'] == 0 and l['abs'] == l['segment'].longueur):
                                        foundExtSeg = True
                                        self.AjouterJointCDV(i, k, j['segment'], j['abs'])
                                if(foundExtSeg == False and j['segment'].segment2VoisinAmont == l['segment'] and j['segment'] == l['segment'].segment1VoisinAval):
                                    if(j['abs'] == 0 and l['abs'] == l['segment'].longueur):
                                        foundExtSeg = True
                                        self.AjouterJointCDV(i, k, j['segment'], j['abs'])
                                if(foundExtSeg == False and j['segment'].segment2VoisinAmont == l['segment'] and j['segment'] == l['segment'].segment2VoisinAval):
                                    if(j['abs'] == 0 and l['abs'] == l['segment'].longueur):
                                        foundExtSeg = True
                                        self.AjouterJointCDV(i, k, j['segment'], j['abs'])

                if(foundExtSeg == False):
                    #Si jamais on ne trouve pas deux CDV adjacents, on défini le CDV comme extrémité limite de domaine
                    self.AjouterExtremiteCDVLimiteDomaine(i, j['segment'], j['abs'])

    #Cette méthode permet de construire le référentiel des positions de CDVs avec toutes les segments
    #@execution_time 
    def ConstruireReferentielPositionsCDV__disabled_YDA(self):
        logging.info("Start calling ConstruireReferentielPositionsCDV")
        for cdv in self.CDVs.values():
            print("CDV : " + cdv.nom)
            branchesOuvertes = []
            branchesAbouties = []
            for i, extremiteCdv in enumerate(cdv.segsExtremites):
                #branche ouverte initiale croissante
                brancheOuverteInitiale = {}
                brancheOuverteInitiale['ProchainSegment'] = extremiteCdv['segment']
                brancheOuverteInitiale['Sens'] = "CROISSANT"
                brancheOuverteInitiale['Segments'] = []
                segmentInitial = {}
                segmentInitial['Segment'] = extremiteCdv['segment']
                segmentInitial['Starting'] = extremiteCdv['abs']
                segmentInitial['End'] = None
                brancheOuverteInitiale['Segments'].append(segmentInitial)
                brancheOuverteInitiale['FromSegment'] = extremiteCdv['segment']
                brancheOuverteInitiale['ToSegment'] = None
                branchesOuvertes.append(brancheOuverteInitiale)
                #branche ouverte initiale décroissante
                # brancheOuverteInitiale = {}
                # brancheOuverteInitiale['ProchainSegment'] = extremiteCdv['segment']
                # brancheOuverteInitiale['Sens'] = "DECROISSANT"
                # brancheOuverteInitiale['Segments'] = []
                # segmentInitial = {}
                # segmentInitial['Segment'] = extremiteCdv['segment']
                # segmentInitial['Starting'] = extremiteCdv['abs']
                # segmentInitial['End'] = None
                # brancheOuverteInitiale['Segments'].append(segmentInitial)
                # brancheOuverteInitiale['FromSegment'] = extremiteCdv['segment']
                # brancheOuverteInitiale['ToSegment'] = None
                # branchesOuvertes.append(brancheOuverteInitiale)

            while(len(branchesOuvertes) > 0 and len(branchesAbouties) < len(cdv.segsExtremites) - 1):

                # for branche in branchesOuvertes:
                #     print("Starting : " + branche['FromSegment'].nom + " Sens : " + branche['Sens'])
                #     print("Segments : ")
                #     for segment in branche['Segments'] :
                #         if(segment['End'] != None):
                #             print(segment['Segment'].nom + "(" + str(segment['Starting']) + "," + str(segment['End']) + ")")
                #         else:
                #             print(segment['Segment'].nom + "(" + str(segment['Starting']) + ",...")

                #os.system("pause")

                brancheOuverte = branchesOuvertes[0]
                del branchesOuvertes[0]

                issueTrouvee = False
                for i, extremiteCdv in enumerate(cdv.segsExtremites):
                    if(extremiteCdv['segment'] != brancheOuverte['Segments'][0]['Segment'] or extremiteCdv['abs'] != brancheOuverte['Segments'][0]['Starting']):
                        if(extremiteCdv['segment'] == brancheOuverte['ProchainSegment']):
                            brancheOuverte['Segments'][-1]['End'] = extremiteCdv['abs']
                            brancheOuverte['ToSegment'] = extremiteCdv['segment']
                            branchesAbouties.append(brancheOuverte)
                            issueTrouvee = True

                #on abandonne les branches ouvertes non abouties ayant plus de 10 segments
                if(issueTrouvee == False and len(brancheOuverte['Segments']) < 10):
                    brancheOuverteNouvelle = {}
                    brancheOuverteNouvelle['Sens'] = brancheOuverte['Sens']
                    brancheOuverteNouvelle['FromSegment'] = brancheOuverte['FromSegment']
                    brancheOuverteNouvelle['ToSegment'] = None

                    if(brancheOuverteNouvelle['Sens'] == "CROISSANT"):
                        if(brancheOuverte['ProchainSegment'].segment1VoisinAval != None):
                            brancheOuverteNouvelle = brancheOuverteNouvelle.copy()
                            brancheOuverteNouvelle['ProchainSegment'] = brancheOuverte['ProchainSegment'].segment1VoisinAval
                            brancheOuverteNouvelle['Segments'] = brancheOuverte['Segments'].copy()
                            brancheOuverteNouvelle['Segments'][-1]['End'] = brancheOuverteNouvelle['Segments'][-1]['Segment'].longueur
                            segmentNouveau = {}
                            segmentNouveau['Segment'] = brancheOuverte['ProchainSegment'].segment1VoisinAval
                            segmentNouveau['Starting'] = 0
                            segmentNouveau['End'] = None
                            brancheOuverteNouvelle['Segments'].append(segmentNouveau)
                            branchesOuvertes.append(brancheOuverteNouvelle)
                        if(brancheOuverte['ProchainSegment'].segment2VoisinAval != None):
                            brancheOuverteNouvelle = brancheOuverteNouvelle.copy()
                            brancheOuverteNouvelle['ProchainSegment'] = brancheOuverte['ProchainSegment'].segment2VoisinAval
                            brancheOuverteNouvelle['Segments'] = brancheOuverte['Segments'].copy()
                            brancheOuverteNouvelle['Segments'][-1]['End'] = brancheOuverteNouvelle['Segments'][-1]['Segment'].longueur
                            segmentNouveau = {}
                            segmentNouveau['Segment'] = brancheOuverte['ProchainSegment'].segment2VoisinAval
                            segmentNouveau['Starting'] = 0
                            segmentNouveau['End'] = None
                            brancheOuverteNouvelle['Segments'].append(segmentNouveau)
                            branchesOuvertes.append(brancheOuverteNouvelle)
                    # else:
                    #     if(brancheOuverte['ProchainSegment'].segment1VoisinAmont != None):
                    #         brancheOuverteNouvelle = brancheOuverteNouvelle.copy()
                    #         brancheOuverteNouvelle['ProchainSegment'] = brancheOuverte['ProchainSegment'].segment1VoisinAmont
                    #         brancheOuverteNouvelle['Segments'] = brancheOuverte['Segments'].copy()
                    #         brancheOuverteNouvelle['Segments'][-1]['End'] = 0
                    #         segmentNouveau = {}
                    #         segmentNouveau['Segment'] = brancheOuverte['ProchainSegment'].segment1VoisinAmont
                    #         segmentNouveau['Starting'] = brancheOuverte['ProchainSegment'].segment1VoisinAmont.longueur
                    #         segmentNouveau['End'] = None
                    #         brancheOuverteNouvelle['Segments'].append(segmentNouveau)
                    #         branchesOuvertes.append(brancheOuverteNouvelle)
                    #     if(brancheOuverte['ProchainSegment'].segment2VoisinAmont != None):
                    #         brancheOuverteNouvelle = brancheOuverteNouvelle.copy()
                    #         brancheOuverteNouvelle['ProchainSegment'] = brancheOuverte['ProchainSegment'].segment2VoisinAmont
                    #         brancheOuverteNouvelle['Segments'] = brancheOuverte['Segments'].copy()
                    #         brancheOuverteNouvelle['Segments'][-1]['End'] = 0
                    #         segmentNouveau = {}
                    #         segmentNouveau['Segment'] = brancheOuverte['ProchainSegment'].segment2VoisinAmont
                    #         segmentNouveau['Starting'] = brancheOuverte['ProchainSegment'].segment2VoisinAmont.longueur
                    #         segmentNouveau['End'] = None
                    #         brancheOuverteNouvelle['Segments'].append(segmentNouveau)
                    #         branchesOuvertes.append(brancheOuverteNouvelle)

            for branche in branchesAbouties:
                #print("Starting : " + branche['FromSegment'].nom + " End : " + branche['ToSegment'].nom + " Sens : " + branche['Sens'])
                #print("Segments : ")
                for segment in branche['Segments'] :
                    #print(segment['Segment'].nom + "(" + str(segment['Starting']) + "," + str(segment['End']) + ")")
                    if(segment['Segment'].nom in cdv.segments):
                        if(segment['Starting'] < cdv.segments[segment['Segment'].nom]['min']):
                            cdv.segments[segment['Segment'].nom]['min'] = branche['Segments']['Starting']
                        if(segment['End'] < cdv.segments[segment['Segment'].nom]['min']):
                            cdv.segments[segment['Segment'].nom]['min'] = segment['End']
                        if(segment['Starting'] > cdv.segments[segment['Segment'].nom]['max']):
                            cdv.segments[segment['Segment'].nom]['max'] = segment['Starting']
                        if(segment['End'] > cdv.segments[segment['Segment'].nom]['max']):
                            cdv.segments[segment['Segment'].nom]['max'] = segment['End']
                    else:
                        cdv.segments[segment['Segment'].nom] = {}
                        if(segment['Starting'] < segment['End']):
                            cdv.segments[segment['Segment'].nom]['min'] = segment['Starting']
                            cdv.segments[segment['Segment'].nom]['max'] = segment['End']
                            cdv.segments[segment['Segment'].nom]['segment'] = segment['Segment']
                        else:
                            cdv.segments[segment['Segment'].nom]['max'] = segment['Starting']
                            cdv.segments[segment['Segment'].nom]['min'] = segment['End']
                            cdv.segments[segment['Segment'].nom]['segment'] = segment['Segment']

        for cdv in self.CDVs.values():
            print(cdv.nom)
            for segment in cdv.segments.values():
                print(segment['segment'].nom + " - " + str(segment['min']) + "/" + str(segment['max']))

        #os.system("pause")


    #Cette méthode permet de rechercher un CDV en fonction d'une position sur un segment
    #@execution_time 
    def RechercherCDVAvecSegmentAbs__disabled_YDA(self, _segment, _abs, _aig = None):
        logging.info("Start calling RechercherCDVAvecSegmentAbs")
        for cdv in self.CDVs.values():
            for segment in cdv.segments.values():
                if(segment['segment'] == _segment):
                    if(_abs <= segment['max'] and _abs >= segment['min']):
                        return cdv

        if(_aig != None):
            if(_segment == _aig.segTalonDroite or _segment == _aig.segTalonGauche):
                for cdv in self.CDVs.values():
                    print("Aig " + _aig.nom + " Seg Pointe " + _aig.segPointe.nom)
                    for segment in cdv.segments.values():
                        print("Segment : " + segment['segment'].nom)
                        if(segment['segment'] == _aig.segPointe):
                            print("Found")
                            if(_abs >= 0.):
                                print("Abs 0 max  " + str(segment['max']) + " min " + str(segment['min']))
                                if(0. <= segment['max'] and 0. >= segment['min']):
                                    print("ok")
                                    return cdv
                            else:
                                print("Abs longueur ("+ str(_aig.segPointe.longueur) +") max  " + str(segment['max']) + " min " + str(segment['min']))
                                if(_aig.segPointe.longueur <= segment['max'] and _aig.segPointe.longueur >= segment['min']):
                                    print("ok")
                                    return cdv

        return None

    #Cette méthode permet de retourner tous les CDV d'un segment
    #@execution_time 
    def RechercherCDVsAvecSegment__disabled_YDA(self, _segment):
        logging.info("Start calling RechercherCDVsAvecSegment")
        cdvs = []
        for cdv in self.CDVs.values():
            for segment in cdv.segments.values():
                if(segment['segment'] == _segment):
                    cdvs.append(cdv)
        return cdvs

    #Cette méthode recherche un TVD correspondant à un CDV
    #@execution_time 
    def RechercherTVDAvecCDV__disabled_YDA(self, _cdv):
        logging.info("Start calling RechercherTVDAvecCDV")
        for tvd in self.TVDs.values():
            if(tvd.objet == _cdv):
                return tvd
        return None

    #@execution_time 
    def GenererSignauxTraversesTransitions__disabled_YDA(self):
        logging.info("Start calling GenererSignauxTraversesTransitions")
        for tra in self.transitions.values():
            transitionOriginelle = True
            for tra1 in tra.pointOptimisationOrigine.transitionsVersCePoint:
                if(tra1.segmentsParcourus[0].sens == tra.segmentsParcourus[0].sens):
                    transitionOriginelle = False

            transitionFinale = True
            for tra1 in tra.pointOptimisationDestination.transitionsDepuisCePoint:
                if(tra1.segmentsParcourus[0].sens == tra.segmentsParcourus[0].sens):
                    transitionFinale = False

            for seg in tra.segmentsParcourus:
                segment = seg.segment
                sens = seg.sens
                signaux = segment.RechercherSignauxSurSegment()

                for sig in signaux:
                    if(sig.sens == sens):
                        itineraires = self.RechercherItinerairesDepuisOrigine(sig)
                        if(len(itineraires) > 0):
                            if(sig.segment == tra.pointOptimisationOrigine.segment and sig.segment != tra.pointOptimisationDestination.segment):
                                if(sens == "CROISSANT" and sig.abs > tra.pointOptimisationOrigine.abs):
                                    tra.signauxTraverses.append(sig)
                                elif(sens == "DECROISSANT" and sig.abs < tra.pointOptimisationOrigine.abs):
                                    tra.signauxTraverses.append(sig)
                                elif(transitionOriginelle):
                                    tra.signauxTraverses.append(sig)
                            elif(sig.segment == tra.pointOptimisationDestination.segment and sig.segment != tra.pointOptimisationOrigine.segment):
                                if(sens == "CROISSANT" and sig.abs < tra.pointOptimisationDestination.abs):
                                    tra.signauxTraverses.append(sig)
                                elif(sens == "DECROISSANT" and sig.abs > tra.pointOptimisationDestination.abs):
                                    tra.signauxTraverses.append(sig)
                                elif(transitionFinale):
                                    tra.signauxTraverses.append(sig)
                            elif(sig.segment == tra.pointOptimisationDestination.segment and sig.segment == tra.pointOptimisationOrigine.segment):
                                if(sens == "CROISSANT" and sig.abs < tra.pointOptimisationDestination.abs and sig.abs > tra.pointOptimisationOrigine.abs):
                                    tra.signauxTraverses.append(sig)
                                elif(sens == "DECROISSANT" and sig.abs > tra.pointOptimisationDestination.abs and sig.abs < tra.pointOptimisationOrigine.abs):
                                    tra.signauxTraverses.append(sig)
                                elif(transitionOriginelle):
                                    tra.signauxTraverses.append(sig)
                                elif(transitionFinale):
                                    tra.signauxTraverses.append(sig)
                            else:
                                tra.signauxTraverses.append(sig)

    #Cette méthode permet de générer les itinéraires à commander des missions élémentaires de régulation
    #@execution_time 
    def GenererItinerairesACommander__disabled_YDA(self):
        logging.info("Start calling GenererItinerairesACommander")
        for me in self.missionsElementairesRegulation.values():
            premierSignalRencontre = None
            positionSegment = 0

            print("mission élémentaire " + me.nom)
            for print_segs_me in me.segmentsParcourus:
                print("Segment " + print_segs_me.segment.nom + " - " + print_segs_me.sens)

            #On recherche le premier signal rencontré
            dernierSegParcouru = False
            for segment in me.segmentsParcourus:
                if(premierSignalRencontre == None):
                    #Pour chaque signal sur ce segment
                    for signal in segment.segment.RechercherSignauxSurSegment():
                        #si on est sur le premier segment parcouru
                        if(positionSegment == 0):
                            itinerairesDontSignalEstOrigine = self.RechercherItinerairesDepuisOrigine(signal)
                            #Si le signal est derrière le PO et orienté dans la direction du parcours de la circulation et qu'il est origine d'itinéraire
                            if(premierSignalRencontre == None and len(itinerairesDontSignalEstOrigine) > 0 and signal.sens == segment.sens and (me.poOrigine.segment == signal.segment and (me.poOrigine.isPTES == True or (signal.abs >= me.poOrigine.abs and signal.sens == "CROISSANT") or (signal.abs <= me.poOrigine.abs and signal.sens == "DECROISSANT")) or me.poOrigine.segment != signal.segment)):
                                #Alors ce signal est le premier signal rencontré.
                                premierSignalRencontre = signal
                        else:
                            itinerairesDontSignalEstOrigine = self.RechercherItinerairesDepuisOrigine(signal)
                            #si le signal est orienté dans la direction du parcours de la circulation et qu'il est origine d'itinéraire
                            if(premierSignalRencontre == None and len(itinerairesDontSignalEstOrigine) > 0 and signal.sens == segment.sens and (dernierSegParcouru == False and (segment.segment != me.poDestination.segment or ((signal.abs < me.poDestination.abs and signal.sens == "CROISSANT") or (signal.abs > me.poDestination.abs and signal.sens == "DECROISSANT"))))):
                                #Alors ce signal est le premier signal rencontré.
                                premierSignalRencontre = signal

                    if(segment.segment == me.poDestination.segment):
                        dernierSegParcouru = True

                    if(premierSignalRencontre == None):
                        positionSegment = positionSegment + 1

            if(premierSignalRencontre != None):
                print("premier signal : " + premierSignalRencontre.nom)

                prochainSignal = premierSignalRencontre
                itinerairesDontProchainSignalEstOrigine = self.RechercherItinerairesDepuisOrigine(prochainSignal)

                #Tant qu'on a pas atteint la fin de mission élémentaire
                itineraireValide = False
                continueSurCetItineraire = True
                ItineraireAjoute = False
                itinerairesACommander = []
                pointOptimisationDestinationAtteint = False
                nbBoucleSurSignal = 0
                error = False
                while(pointOptimisationDestinationAtteint == False and positionSegment < len(me.segmentsParcourus) and error == False):
                    #Pour chaque itinéraire ayant le prochain signal en origine

                    for itineraire in itinerairesDontProchainSignalEstOrigine:
                        print("itineraire " + itineraire.nom)
                        for print_segs_iti in itineraire.segmentsParcourus:
                            print("Segment " + print_segs_iti.segment.nom + " - " + print_segs_iti.sens)

                        positionSegmentSurItineraire = nbBoucleSurSignal
                        continueSurCetItineraire = True
                        ItineraireAjoute = False
                        previousSegmentIti = None
                        while(continueSurCetItineraire == True and pointOptimisationDestinationAtteint == False and ItineraireAjoute == False):
                            positionSegmentSurMePourItineraire = positionSegment+positionSegmentSurItineraire-nbBoucleSurSignal
                            #print("segment de l'iti "+str(positionSegmentSurItineraire) + " " + itineraire.segmentsParcourus[positionSegmentSurItineraire].segment.nom)
                            #print("segment po dest : " + me.poDestination.segment.nom)
                            #if(itineraire.segmentsParcourus[positionSegmentSurItineraire].segment.nom == "SEG_011902"):
                            #print("position segment : " + str(positionSegmentSurMePourItineraire) + " positionSegment : " + str(positionSegment) + " positionSegmentSurItineraire : " + str(positionSegmentSurItineraire) + " nbBoucle : " + str(nbBoucleSurSignal) + " taille nbSegmentParcourusMe : " + str(len(me.segmentsParcourus)) + " taille nbSegmentItineraire : " + str(len(itineraire.segmentsParcourus)))
                            #print("segment de la me : "+str(positionSegmentSurMePourItineraire) + " "  + me.segmentsParcourus[positionSegmentSurMePourItineraire].segment.nom)
                            #print("segment de l'iti' : " + str(positionSegmentSurItineraire) + " " + itineraire.segmentsParcourus[positionSegmentSurItineraire].segment.nom)
                            #print("segment po Destination " + me.poDestination.segment.nom + " abs iti fin " + str(itineraire.destination.abs) + " abs me fin " + str(me.poDestination.abs))
                            #if(previousSegmentIti is not None):
                                #print("previousSegment : " + previousSegmentIti.nom)
                            #Si le point d'optimisation destination est sur le segment de l'itinéraire, et s'il s'agit du dernier segment de l'itinéraire, le po destination est un PTES ou on a parcouru tous les segments de la ME ou sa position est antérieur à la position du point d'optimisation destination
                            #Alors, on a atteint le point d'optimisation destination
                            if(positionSegmentSurItineraire >= len(itineraire.segmentsParcourus)):
                                print("Erreur : Mission Elementaire : " + me.nom)
                                continueSurCetItineraire = False
                                error = True
                                os.system("PAUSE")
                            elif(previousSegmentIti == me.poDestination.segment or itineraire.segmentsParcourus[positionSegmentSurItineraire].segment == me.poDestination.segment and (me.poDestination.isPTES == True or (positionSegmentSurMePourItineraire+1 >= len(me.segmentsParcourus)) or (itineraire.destination.abs >= me.poDestination.abs and itineraire.destination.sens == "CROISSANT") or (itineraire.destination.abs <= me.poDestination.abs and itineraire.destination.sens == "DECROISSANT"))):
                                print("Destination atteinte")
                                pointOptimisationDestinationAtteint = True
                                ItineraireAjoute = True
                                itinerairesACommander.append(itineraire)
                                print("Ajout itinéraire sur parcours: " + itineraire.nom)
                            #Si le prochain segment de l'itinéraire est différent du prochain segment de la mission élémentaire
                            elif(itineraire.segmentsParcourus[positionSegmentSurItineraire] != me.segmentsParcourus[positionSegmentSurMePourItineraire]):
                                continueSurCetItineraire = False
                                print("Mauvais itineraire : on arrête la recherche sur celui ci : " + itineraire.segmentsParcourus[positionSegmentSurItineraire].segment.nom + " - " + me.segmentsParcourus[positionSegmentSurMePourItineraire].segment.nom)
                            #Si on a atteint le dernier segment de l'itinéraire, on continue sur les itineraires à partir de la destination de l'itinéraire, et on incrémente le compteur de segments
                            elif(positionSegmentSurItineraire+1 >= len(itineraire.segmentsParcourus)):
                                print("Fin d'itinéraire")
                                positionSegment = positionSegmentSurMePourItineraire
                                ItineraireAjoute = True
                                itinerairesACommander.append(itineraire)
                                print("Ajout itinéraire sur parcours: " + itineraire.nom)
                                prochainSignal = itineraire.destination
                                print("Nouvelle destination: " + prochainSignal.nom)
                                nbBoucleSurSignal = 0
                                itinerairesDontProchainSignalEstOrigine = self.RechercherItinerairesDepuisOrigine(prochainSignal)
                            else:
                                positionSegmentSurItineraire = positionSegmentSurItineraire + 1
                                previousSegmentIti = itineraire.segmentsParcourus[positionSegmentSurItineraire-1].segment
                                print("On continue sur cet itinéraire")

                            # if(itineraire.nom == "8501-8523"):
                            #     os.system("pause")

                        if(ItineraireAjoute == True):
                            break

                    if(continueSurCetItineraire == False and ItineraireAjoute == False):
                        print("Incrément de la boucle nbBoucleSurSignal")
                        nbBoucleSurSignal = nbBoucleSurSignal + 1


                me.itinerairesAcommander = itinerairesACommander

                for iti in me.itinerairesAcommander:
                    if iti.mode != "Automatique":
                        me.mode = "Non optimisable"

    #Permet de générer les points de contrôle
    #@execution_time 
    def GenererPointsDeControle__disabled_YDA(self):
        logging.info("Start calling GenererPointsDeControle")

        pointDeControle = None
        #Points de controle de type suivi : joint de CdV ou extremite CDV en limite de domaine
        for i in self.JointsCDVs.values():
            print("Ajout Point de contrôle JCDV : " + i.cdv1.nom + " - " + i.cdv2.nom + " @ " + str(i.abs) + " sur " + i.segment.nom)
            key = "PC|"+i.segment.nom+"|"+str(i.abs)
            pointDeControle = PointDeControle(key, i.abs, i.segment)
            self.pointsDeControle[key] = pointDeControle
            pointDeControle.AjouterParticulariteJCDV(i)
        for i in self.ExtremitesCDVsLimiteDomaine.values():
            print("Ajout Point de contrôle ECDVLD : " + i.cdv.nom + " @ " + str(i.abs) + " sur " + i.segment.nom)
            key = "PC|"+i.segment.nom+"|"+str(i.abs)
            pointDeControle = PointDeControle(key, i.abs, i.segment)
            self.pointsDeControle[key] = pointDeControle
            pointDeControle.AjouterParticulariteECDVLD(i)

        #Points de controle de type suivi : pédale
        for i in self.pedales.values():
            print("Ajout Point de contrôle Pedale : " + i.nomSiemens + " @ " + str(i.abs) + " sur " + i.segment.nom)
            key = "PC|"+i.segment.nom+"|"+str(i.abs)
            pointDeControle = PointDeControle(key, i.abs, i.segment)
            self.pointsDeControle[key] = pointDeControle
            pointDeControle.AjouterParticularitePedale(i)

        #Points de contrôles liés aux quais
        for s in self.stations.values():
            for q in s.quais.values():
                #Point de contrôle de type Point d'extrémité de quai
                # key = "PC|" + q.extremite1Seg.nom + "|" + str(q.extremite1Abs)
                # if(key in self.pointsDeControle):
                #     pointDeControle = self.pointsDeControle[key]
                # else:
                #     pointDeControle = PointDeControle(key, q.extremite1Abs, q.extremite1Seg)
                #     self.pointsDeControle[key] = pointDeControle
                # pointDeControle.AjouterParticulariteExtremiteQuai(q, q.extremite1Sens)
                # print("Ajout Point de contrôle Extremite Quai : " + q.nom + " @ " + str(q.extremite1Abs) + " sur " + q.extremite1Seg.nom + " - " + q.extremite1Sens)
                # key = "PC|" + q.extremite2Seg.nom + "|" + str(q.extremite2Abs)
                # if(key in self.pointsDeControle):
                #     pointDeControle = self.pointsDeControle[key]
                # else:
                #     pointDeControle = PointDeControle(key, q.extremite2Abs, q.extremite2Seg)
                #     self.pointsDeControle[key] = pointDeControle
                # pointDeControle.AjouterParticulariteExtremiteQuai(q, q.extremite2Sens)
                # print("Ajout Point de contrôle Extremite Quai : " + q.nom + " @ " + str(q.extremite2Abs) + " sur " + q.extremite2Seg.nom + " - " + q.extremite2Sens)

                #Points de controle de type Point d'arrêt à quai (seulement paf n°1)
                key = "PC|" + q.pafs[1].segment.nom + "|" + str(q.pafs[1].abs)
                if(key in self.pointsDeControle):
                    pointDeControle = self.pointsDeControle[key]
                else:
                    pointDeControle = PointDeControle(key, q.pafs[1].abs, q.pafs[1].segment)
                    self.pointsDeControle[key] = pointDeControle
                pointDeControle.AjouterParticularitePAFQuai(q)
                pointDeControle.AjouterParticularitePointOptimisation(q.nom)
                print("Ajout Point de contrôle PAF Quai : " + q.nom + " @ " + str(q.pafs[1].abs) + " sur " + q.pafs[1].segment.nom)

                #Point de contrôle de type Point de sortie de quai
                #ADU : nécessite d'importer les modèles de train

    #@execution_time 
    def ImporterMissionsElementairesDeRegulation__disabled_YDA(self, __fichierString):
        logging.info("Start calling ImporterMissionsElementairesDeRegulation")
        pc = panda.read_csv(__fichierString, sep=';')

        lastMER = None
        for i in pc.index:
            Nom = None
            po = None
            Mode = None
            next_pc = None
            SensMissionElementaire = None
            ModeControleVitesse = None
            if(isinstance(pc['Nom'][i], str) and pc['Nom'][i] != ""):
                Nom = pc['Nom'][i]
            if(isinstance(pc['Mode'][i], str) and pc['Mode'][i] != ""):
                Mode = pc['Mode'][i]
            if(isinstance(pc['PointOptimisationOrigine'][i], str) and pc['PointOptimisationOrigine'][i] != ""):
                po = self.RechercherPointOptimisation(pc['PointOptimisationOrigine'][i])
            if(isinstance(pc['PointOptimisationDestination'][i], str) and pc['PointOptimisationDestination'][i] != ""):
                next_pc = self.RechercherPointOptimisation(pc['PointOptimisationDestination'][i])
            if(isinstance(pc['SensMissionElementaire'][i], str) and pc['SensMissionElementaire'][i] != ""):
                SensMissionElementaire = pc['SensMissionElementaire'][i]
            if(isinstance(pc['ModeControleVitesse'][i], str) and pc['ModeControleVitesse'][i] != ""):
                ModeControleVitesse = pc['ModeControleVitesse'][i]

            if(Nom != None and po != None and Mode != None and next_pc != None and SensMissionElementaire != None and ModeControleVitesse != None):
                lastMER = self.AjouterMissionElementaireRegulationSimple(Nom, po, next_pc, ModeControleVitesse, SensMissionElementaire)
                po.MERDepuisPO.append(lastMER)
            if(lastMER != None):
                if(isinstance(pc['Lignes'][i], str) and pc['Lignes'][i] != ""):
                    lastMER.lignes.append(pc['Lignes'][i])
                if(isinstance(pc['NaturesTrains'][i], str) and pc['NaturesTrains'][i] != ""):
                    lastMER.naturesTrains.append(self.natures[pc['NaturesTrains'][i]])
                if(isinstance(pc['Segments'][i], str) and pc['Segments'][i] != ""):
                    if(isinstance(pc['SensParcours'][i], str) and pc['SensParcours'][i] != ""):
                        seg = self.segments[pc['Segments'][i]]
                        segPar = ParcoursSegment(seg, pc['SensParcours'][i])
                        lastMER.segmentsParcourus.append(segPar)
                if(isinstance(pc['Transitions'][i], str) and pc['Transitions'][i] != ""):
                    lastMER.transitions.append(self.transitions[pc['Transitions'][i]])
                if(isinstance(pc['ItinerairesACommander'][i], str) and pc['ItinerairesACommander'][i] != ""):
                    itineraire = self.RechercherItineraire(pc['ItinerairesACommander'][i])
                    if(itineraire != None):
                        lastMER.itinerairesAcommander.append(itineraire)
                    else:
                        print("Itineraire " + str(pc['ItinerairesACommander'][i]) + " introuvable !")
                        os.system("pause")

    #@execution_time 
    def ImporterTransitions__disabled_YDA(self, __fichierString):
        logging.info("Start calling ImporterTransitions")
        pc = panda.read_csv(__fichierString, sep=';')

        lastTransition = None
        for i in pc.index:
            nomTransition = None
            po = None
            Mode = None
            next_pc = None
            Longueur = None
            if(isinstance(pc['Nom'][i], str) and pc['Nom'][i] != ""):
                nomTransition = pc['Nom'][i]
            if(isinstance(pc['Mode'][i], str) and pc['Mode'][i] != ""):
                Mode = pc['Mode'][i]
            if(isinstance(pc['PointOptimisationOrigine'][i], str) and pc['PointOptimisationOrigine'][i] != ""):
                po = self.RechercherPointOptimisation(pc['PointOptimisationOrigine'][i])
            if(isinstance(pc['PointOptimisationDestination'][i], str) and pc['PointOptimisationDestination'][i] != ""):
                next_pc = self.RechercherPointOptimisation(pc['PointOptimisationDestination'][i])
            if(math.isnan(pc['Longueur'][i]) == False):
                Longueur = pc['Longueur'][i]
            # if(nomTransition == "PANTIN_2L4_EST|PANTIN_V2"):
            #     print("po : " + po.nomPointOptimisation)
            #     print("NextPC : " + next_pc.nomPointOptimisation)
            #     print("Nom : " + nomTransition + " po : " + po.nomPointOptimisation + " Mode : " + Mode + " NextPC : " + next_pc.nomPointOptimisation + " Longueur : " + str(Longueur))
            if(nomTransition != None and po != None and Mode != None and next_pc != None and Longueur != None):
                lastTransition = self.AjouterTransitionSimple(nomTransition, po, next_pc, Mode, Longueur)
            if(lastTransition != None):
                if(isinstance(pc['Lignes'][i], str) and pc['Lignes'][i] != ""):
                    lastTransition.lignes.append(pc['Lignes'][i])
                if(isinstance(pc['NaturesTrains'][i], str) and pc['NaturesTrains'][i] != ""):
                    lastTransition.naturesTrains.append(pc['NaturesTrains'][i])
                if(isinstance(pc['Checkpoints'][i], str) and pc['Checkpoints'][i] != ""):
                    checkpoint = self.RechercherCheckpoint(pc['Checkpoints'][i])
                    if(checkpoint != None):
                        lastTransition.checkpoints.append(checkpoint)
                # if(isinstance(pc['ControlPoint'][i], str) and pc['ControlPoint'][i] != ""):
                #     lastTransition.controlpoints.append(self.pointsDeControle[pc['ControlPoint'][i]])
                if(isinstance(pc['signauxTraverse'][i], str) and pc['signauxTraverse'][i] != ""):
                    lastTransition.signauxTraverses.append(self.signals[pc['signauxTraverse'][i]])
                if(isinstance(pc['Segments'][i], str) and pc['Segments'][i] != ""):
                    if(isinstance(pc['SensParcours'][i], str) and pc['SensParcours'][i] != ""):
                        seg = self.segments[pc['Segments'][i]]
                        segPar = ParcoursSegment(seg, pc['SensParcours'][i])
                        lastTransition.segmentsParcourus.append(segPar)

        for transition in self.transitions.values():
            transition.pointOptimisationOrigine.transitionsDepuisCePoint.append(transition)
            transition.pointOptimisationDestination.transitionsVersCePoint.append(transition)

            for natureOrigine in transition.pointOptimisationOrigine.naturesTrains:
                if(natureOrigine in transition.pointOptimisationDestination.naturesTrains):
                    if(natureOrigine not in transition.naturesTrains):
                        transition.naturesTrains.append(natureOrigine)

            for ligne in transition.pointOptimisationOrigine.lignes:
                if(ligne in transition.pointOptimisationDestination.lignes):
                    if(ligne not in transition.lignes):
                        transition.lignes.append(ligne)

    #@execution_time 
    def ImporterTrains__disabled_YDA(self, __fichierString):
        logging.info("Start calling ImporterTrains")
        self.natures = {}
        pc = panda.read_csv(__fichierString, sep=';')
        lastNature = None
        for i in pc.index:
            if(isinstance(pc['Nature'][i], str) and pc['Nature'][i] != ""):
                self.natures[pc['Nature'][i]] = NatureTrain(pc['Nature'][i],pc['ParDefaut'][i],pc['Composition'][i])
                lastNature = self.natures[pc['Nature'][i]]
                if(isinstance(pc['Lignes'][i], str) and pc['Lignes'][i] != ""):
                    stringLignes = pc['Lignes'][i].split(",")
                    for itLigne in stringLignes:
                        lastNature.lignes.append(itLigne)
            if(isinstance(pc['Modele'][i], str) and pc['Modele'][i] != ""):
                newModele = ModeleTrain(pc['Modele'][i],pc['ModeConduite'][i],lastNature)
                lastNature.AjouterModele(newModele)
            if(math.isnan(pc['ParDefaut'][i]) == False and pc['ParDefaut'][i] == 1):
                self.natureParDefaut = lastNature
            if(math.isnan(pc['Asimuler'][i]) == False and pc['Asimuler'][i] == 1):
                newModele.aSimuler = True

    #@execution_time 
    def RechercherModeleTrain__disabled_YDA(self, nomModele):
        logging.info("Start calling RechercherModeleTrain")
        for nature in self.natures.values():
            for modele in nature.modeles:
                #print(modele.nom)
                if(modele.nom == nomModele):
                    return modele
        return None

    #@execution_time 
    def ImporterCombiTypesEspacement__disabled_YDA(self, __fichierString):
        logging.info("Start calling ImporterCombiTypesEspacement")
        pc = panda.read_csv(__fichierString, sep=';')
        lastCombi = None
        for i in pc.index:
            if(isinstance(pc['NomCombi'][i], str) and pc['NomCombi'][i] != ""):
                lastCombi = {}
                lastCombi['Nom'] = pc['NomCombi'][i]
                lastCombi['ModeleT1'] = []
                lastCombi['ModeleT2'] = []
                self.combinaisonsTypesEspacements.append(lastCombi)
            if(isinstance(pc['ModeleT1'][i], str) and pc['ModeleT1'][i] != ""):
                modeleTrouve = self.RechercherModeleTrain(pc['ModeleT1'][i])
                if(modeleTrouve is not None):
                    lastCombi['ModeleT1'].append(modeleTrouve)
            if(isinstance(pc['ModeleT2'][i], str) and pc['ModeleT2'][i] != ""):
                modeleTrouve = self.RechercherModeleTrain(pc['ModeleT2'][i])
                if(modeleTrouve is not None):
                    lastCombi['ModeleT2'].append(modeleTrouve)

    #Cette méthode permet d'importer un fichier de points de controle
    #Le format lu est une format csv de type Nom;Segment;abs;CDV_1;CDV_2;DetecteurPassage;NomQuai;DirectionSortieQuai;NatureTrain;nomPointOptimisation;isJCDV;isECDVLD;isDetecteurPassage;isExtremiteQuai;isPAFQuai;isPTES;isPTA;isPointSortieQuai;isPointOptimisation
    #@execution_time 
    def ImporterPointsDeControleCSV__disabled_YDA(self, __fichierString):
        logging.info("Start calling ImporterPointsDeControleCSV")
        pc = panda.read_csv(__fichierString, sep=';')
        for i in pc.index:
            print("point de controle " + pc['Nom'][i])
            pointDeControle = PointDeControle(pc['Nom'][i], pc['abs'][i], self.segments[pc['Segment'][i]])

            if(math.isnan(pc['isJCDV'][i]) == False and pc['isJCDV'][i] == 1):
                jointCDV = self.RechercherJointCDV(pc['CDV_1'][i], pc['CDV_2'][i])
                pointDeControle.AjouterParticulariteJCDV(jointCDV)
            elif(math.isnan(pc['isECDVLD'][i]) == False and pc['isECDVLD'][i] == 1):
                pointDeControle.AjouterParticulariteECDVLD(self.ExtremitesCDVsLimiteDomaine[pc['CDV_1'][i]])

            if(math.isnan(pc['isExtremiteQuai'][i]) == False and pc['isExtremiteQuai'][i] == 1):
                pointDeControle.AjouterParticulariteExtremiteQuai(self.RechercherQuai(pc['NomQuai'][i]), pc['DirectionSortieQuai'][i])

            if(math.isnan(pc['isPAFQuai'][i]) == False and pc['isPAFQuai'][i] == 1):
                pointDeControle.AjouterParticularitePAFQuai(self.RechercherQuai(pc['NomQuai'][i]))

            if(math.isnan(pc['isPTA'][i]) == False and pc['isPTA'][i] == 1):
                pointDeControle.AjouterParticularitePTA()

            if(isinstance(pc['isPTES'][i], int) and math.isnan(pc['isPTES'][i]) == False and pc['isPTES'][i] == 1):
                pointDeControle.AjouterParticularitePTES("INOUT")
            elif(isinstance(pc['isPTES'][i], str) and (pc['isPTES'][i] == "IN" or pc['isPTES'][i] == "OUT" or pc['isPTES'][i] == "INOUT")):
                pointDeControle.AjouterParticularitePTES(pc['isPTES'][i])

            if(math.isnan(pc['isPointOptimisation'][i]) == False and pc['isPointOptimisation'][i] == 1):
                print("est point d'optimisation " + pc['nomPointOptimisation'][i])
                pointDeControle.AjouterParticularitePointOptimisation(pc['nomPointOptimisation'][i])

            if(isinstance(pc['nomCheckPoint'][i], str) and pc['nomCheckPoint'][i] != ""):
                pointDeControle.isCheckPoint = True
                pointDeControle.nomCheckPoint = pc['nomCheckPoint'][i]

            if(isinstance(pc['trains'][i], str) and pc['trains'][i] != ""):
                stringNaturesTrains = pc['trains'][i].split(",")
                for itNatureTrain in stringNaturesTrains:
                    pointDeControle.naturesTrains.append(self.natures[itNatureTrain])

            if(isinstance(pc['Lignes'][i], str) and pc['Lignes'][i] != ""):
                stringLignes = pc['Lignes'][i].split(",")
                for itLigne in stringLignes:
                    pointDeControle.lignes.append(itLigne)

            if(isinstance(pc['SensPriviligie'][i], str) and pc['SensPriviligie'][i] != ""):
                pointDeControle.sensPriviligie = pc['SensPriviligie'][i]

            if(isinstance(pc['PR_CICH'][i], str) and pc['PR_CICH'][i] != ""):
                pointDeControle.PR_CICH = pc['PR_CICH'][i]

            if(isinstance(pc['PR_VOIE'][i], str) and pc['PR_VOIE'][i] != ""):
                pointDeControle.PR_VOIE = pc['PR_VOIE'][i]

            if(isinstance(pc['TransitionsNonOptimisablesForces'][i], str) and pc['TransitionsNonOptimisablesForces'][i] != ""):
                stringTransition = pc['TransitionsNonOptimisablesForces'][i].split(",")
                for itTransition in stringTransition:
                    pointDeControle.transitionsNonOptimisablesForces.append(itTransition)

            self.pointsDeControle[pointDeControle.nom] = pointDeControle

    #@execution_time 
    def ExporterItinerairesInGrapheTransition__disabled_YDA(self, _nomFichier):
        logging.info("Start calling ExporterItinerairesInGrapheTransition")
        Dict = {'Itineraire': [], 'NoeudType': [], 'NoeudID': [], 'NonAmbiguousPreviousNoeudType': [], 'NonAmbiguousPreviousNoeudID': []}

        for p in self.postes.values():
            for i in p.itineraires:
                Dict['Itineraire'].append(i.nom)
                for n in i.noeudsGrapheTransitionsParcourus:
                    if(n.isPointOptimisation):
                        Dict['NoeudType'].append("PointOptimisation")
                        Dict['NoeudID'].append(n.nomPointOptimisation)
                    elif(n.isCheckPoint):
                        Dict['NoeudType'].append("CheckPoint")
                        Dict['NoeudID'].append(n.nomCheckPoint)

                for n in i.nonAmbiguousGrapheTransitionsParcourus:
                    if(n.isPointOptimisation):
                        Dict['NonAmbiguousPreviousNoeudType'].append("PointOptimisation")
                        Dict['NonAmbiguousPreviousNoeudID'].append(n.nomPointOptimisation)
                    elif(n.isCheckPoint):
                        Dict['NonAmbiguousPreviousNoeudType'].append("CheckPoint")
                        Dict['NonAmbiguousPreviousNoeudID'].append(n.nomCheckPoint)

                max = 0
                for value in Dict.values():
                    if(max < len(value)):
                        max = len(value)
                for value in Dict.values():
                    while(len(value) < max):
                        value.append("")
                    value.append("")
        df = panda.DataFrame(Dict)
        df.to_csv(_nomFichier, sep=';')

    #@execution_time 
    def ExporterROAdj__disabled_YDA(self, __fichierString):
        logging.info("Start calling ExporterROAdj")
        ROAdj = []
        ROAdjDict = {'Nom': [], 'ROOrigine': [], 'RODestination': [],'Direction': []}

        for t in self.transitions.values():
            LastRO = "RO_" + t.pointOptimisationOrigine.nomPointOptimisation
            direction = "UP"
            if(t.segmentsParcourus[0].sens == "DECROISSANT"):
                direction = "DOWN"
            if(t.pointOptimisationOrigine.isPAFQuai):
                LastRO = "RO_PLT_" + t.pointOptimisationOrigine.nomPointOptimisation
            for cp in t.checkpoints:
                NextRO = "RO_CP_" + cp.nomCheckPoint
                NextROADJ = LastRO + "_" + NextRO
                if(NextROADJ not in ROAdj):
                    ROAdj.append(NextROADJ)
                    ROAdjDict['Nom'].append(NextROADJ)
                    ROAdjDict['ROOrigine'].append(LastRO)
                    ROAdjDict['RODestination'].append(NextRO)
                    ROAdjDict['Direction'].append(direction)
                LastRO = NextRO

            NextRO = "RO_" + t.pointOptimisationDestination.nomPointOptimisation
            if(t.pointOptimisationDestination.isPAFQuai):
                NextRO = "RO_PLT_" + t.pointOptimisationDestination.nomPointOptimisation
            NextROADJ = LastRO + "_" + NextRO

            if(NextROADJ not in ROAdj):
                ROAdj.append(NextROADJ)
                ROAdjDict['Nom'].append(NextROADJ)
                ROAdjDict['ROOrigine'].append(LastRO)
                ROAdjDict['RODestination'].append(NextRO)
                ROAdjDict['Direction'].append(direction)

        df = panda.DataFrame(ROAdjDict)
        df.to_csv(__fichierString, sep=';')

    
    #Cette méthode permet de rechercher un croisement bon à partir d'une aiguille
    #@execution_time 
    def RechercherCBAvecAiguille__disabled_YDA(self, _aiguille):
        logging.info("Start calling RechercherCBAvecAiguille")
        for cb in self.CBs.values():
            if cb.aiguille == _aiguille:
                return cb
        return None

    
    #
    #Cette méthode permet de transformer les structures string d'ADONF en associations du graphe
    #@execution_time 
    def NormaliserAdonf__disabled_YDA(self):
        logging.info("Start calling NormaliserAdonf")
        print("Normalisation du graphe")
        for __o in self.lignes.values():
            __o.NormaliserAdonf()
        for __o in self.stations.values():
            __o.NormaliserAdonf()
        for __o in self.PtAs.values():
            __o.NormaliserAdonf()
        for __o in self.segments.values():
            __o.NormaliserAdonf()
        for __o in self.voies.values():
            __o.NormaliserAdonf()
        for __o in self.troncons.values():
            __o.NormaliserAdonf()
        for __o in self.signals.values():
            __o.NormaliserAdonf()
        for __o in self.aiguilles.values():
            __o.NormaliserAdonf()
        for __o in self.CDVs.values():
            __o.NormaliserAdonf()
        for __o in self.TVDs.values():
            __o.NormaliserAdonf()
        for __o in self.CBs.values():
            __o.NormaliserAdonf()
        for __o in self.zlpvs.values():
            __o.NormaliserAdonf()
        self.ConstruireReferentielPositionsCDV()

    #Cette méthode permet de construire les missions élémentaires de régulation
    #@execution_time 
    def ConstruireMissionsElementairesDeRegulationParImportation__disabledYDA__disabled_YDA(self, pointsOptimisationsCBTC, fileToImport, _gareTerminus, _lignesSansArret):
        logging.info("Start calling ConstruireMissionsElementairesDeRegulationParImportation__disabledYDA")
        self.missionElementaireRegulation = {}
        #Les missions élémentaires de régulation sont construire en esseyant d'aller d'un quai d'une gare ou d'un PTA ou d'un PTES au quai d'une autre gare ou un autre PTA ou un autre PTES.
        combinaisonsOrigineDestination = {}
        with open(fileToImport, 'r') as f:
            for line in f:
                y = line.split()
                print(y[0])
                combinaisonsOrigineDestination[y[0]] = y[0]

        #Démarrage de la construction du parcours de graphe depuis toutes les origines possibles
        for pointOptimisation in self.pointsDeControle.values():
            if pointOptimisation.isPointOptimisation == True and (pointOptimisation.isPAFQuai == True or pointOptimisation.isPTES == True or pointOptimisation.isPTA == True):
                branchesOuvertes = []
                brancheOuverte = {}
                #Initialisation de la première branche
                brancheOuverte['PointsOptimisationDejaParcourus'] = {}
                brancheOuverte['PointsOptimisationDejaParcourus'][pointOptimisation.nomPointOptimisation] = pointOptimisation
                brancheOuverte['Transitions'] = []
                brancheOuverte['ProchainPointOptimisation'] = pointOptimisation
                brancheOuverte['DerniereVoie'] = pointOptimisation.segment.voie
                brancheOuverte['VoiesParcourues'] = []
                brancheOuverte['Connexe'] = True
                branchesOuvertes.append(brancheOuverte)
                while(len(branchesOuvertes) > 0):
                    #On enregistre la branche parcourue, et on la met dans les branches fermées
                    brancheOuverte = branchesOuvertes[0]

                    prochainPointOptimisation = brancheOuverte['ProchainPointOptimisation']

                    derniereTransitionParcourue = None
                    if(len(brancheOuverte['Transitions']) > 0):
                        derniereTransitionParcourue = brancheOuverte['Transitions'][-1]

                    for transition in prochainPointOptimisation.transitionsDepuisCePoint:
                        #print("transition : " + transition.nom)
                        #if(pointOptimisation.nomPointOptimisation == "ROSA_PARKS_V2" and transition.pointOptimisationDestination.nomPointOptimisation == "HAUSSMANN_SL_V34" and ("MAGENTA_V54" in brancheOuverte['PointsOptimisationDejaParcourus'] or transition.pointOptimisationDestination == "MAGENTA_V54")):
                        # if(pointOptimisation.nomPointOptimisation == "ROSA_PARKS_V2"):
                        #     print("Me building from " + pointOptimisation.nomPointOptimisation + " with end " + transition.pointOptimisationDestination.nomPointOptimisation + " and transitions")
                        #     for point in brancheOuverte['Transitions']:
                        #         print(point.nom)
                        #     print("")
                        #     os.system("pause")
                        if(transition.pointOptimisationDestination.nomPointOptimisation not in brancheOuverte['PointsOptimisationDejaParcourus']):
                            #Si c'est la première transition de la branche, ou que le dernier segment de la dernière transition est orienté de la même façon que le premier segment de la transition, et qu'il s'agit des mêmes segments
                            if(derniereTransitionParcourue is None or (derniereTransitionParcourue.segmentsParcourus[-1] == transition.segmentsParcourus[0])):
                                #print("Depuis PO " + pointOptimisation.nomPointOptimisation + " Parcours transition " + transition.nom)

                                nouvelleBrancheOuverte = {}
                                nouvelleBrancheOuverte['Connexe'] = brancheOuverte['Connexe']
                                nouvelleBrancheOuverte['PointsOptimisationDejaParcourus'] = brancheOuverte['PointsOptimisationDejaParcourus'].copy()
                                nouvelleBrancheOuverte['PointsOptimisationDejaParcourus'][transition.pointOptimisationDestination.nomPointOptimisation] = transition.pointOptimisationDestination

                                #print("point d'opimisation déjà parcourus :")
                                # for i in nouvelleBrancheOuverte['PointsOptimisationDejaParcourus'].values():
                                #     print(i.nomPointOptimisation)

                                nouvelleBrancheOuverte['Transitions'] = brancheOuverte['Transitions'].copy()
                                nouvelleBrancheOuverte['Transitions'].append(transition)

                                # # print("transitions déjà parcourues :")
                                # for i in nouvelleBrancheOuverte['Transitions']:
                                #     print(i.nom)

                                nouvelleBrancheOuverte['ProchainPointOptimisation'] = transition.pointOptimisationDestination

                                nouvelleBrancheOuverte['VoiesParcourues'] = brancheOuverte['VoiesParcourues'].copy()
                                nouvelleBrancheOuverte['DerniereVoie'] = transition.pointOptimisationDestination.segment.voie
                                if(nouvelleBrancheOuverte['DerniereVoie'] != brancheOuverte['DerniereVoie']):
                                    nouvelleBrancheOuverte['VoiesParcourues'].append(brancheOuverte['DerniereVoie'])

                                # print("prochain point d'optimisation : " + transition.pointOptimisationDestination.nomPointOptimisation)

                                #Ajout de la mission élémentaire entre le point d'optimisation d'origine et le point destination de la transition de la branche ouverte, si la combinaison origine-destination correspondante existe
                                key = pointOptimisation.nomPointOptimisation + "#" + transition.pointOptimisationDestination.nomPointOptimisation

                                #Vérification des conditions de sens pour l'origine et la destination
                                condPafQuaiSensOrigine = True
                                if(pointOptimisation.isPAFQuai == True):
                                    quai = self.RechercherQuai(pointOptimisation.nomPointOptimisation)
                                    pafsDuSens = quai.FournirPAFsSens(nouvelleBrancheOuverte['Transitions'][0].segmentsParcourus[0].sens)
                                    if(len(pafsDuSens) < 1):
                                        condPafQuaiSensOrigine = False
                                condPafQuaiSensDestination = True
                                if(transition.pointOptimisationDestination.isPAFQuai == True):
                                    quai = self.RechercherQuai(transition.pointOptimisationDestination.nomPointOptimisation)
                                    pafsDuSens = []
                                    if(quai.station.nom in _gareTerminus):
                                        pafsDuSens = quai.FournirPAFsSens("CROISSANT") + quai.FournirPAFsSens("DECROISSANT")
                                    else:
                                        pafsDuSens = quai.FournirPAFsSens(nouvelleBrancheOuverte['Transitions'][-1].segmentsParcourus[-1].sens)
                                    if(len(pafsDuSens) < 1):
                                        condPafQuaiSensDestination = False
                                if((transition.pointOptimisationDestination.isPTA or transition.pointOptimisationDestination.isPTES or transition.pointOptimisationDestination.isPAFQuai) and condPafQuaiSensOrigine == True and condPafQuaiSensDestination == True):
                                    nouvelleBrancheOuverte['Connexe'] = False
                                    if(key in combinaisonsOrigineDestination):
                                    # print(pointOptimisation.nomPointOptimisation + "#" + transition.pointOptimisationDestination.nomPointOptimisation)
                                        ModeControleVitesse = ""
                                        Sens = ""
                                        if(pointOptimisation.nomPointOptimisation in pointsOptimisationsCBTC and transition.pointOptimisationDestination.nomPointOptimisation in pointsOptimisationsCBTC):
                                            ModeControleVitesse = "KVB+CBTC"
                                        else:
                                            ModeControleVitesse = "KVB"
                                        if(nouvelleBrancheOuverte['Transitions'][0].segmentsParcourus[0].sens == "CROISSANT"):
                                            Sens = "G -> D"
                                        else:
                                            Sens = "D -> G"

                                        initNatureTrain = 0
                                        initLigne = 0
                                        NaturesTrains = []
                                        Lignes = []
                                        mode = "Optimisable"
                                        for t in nouvelleBrancheOuverte['Transitions']:
                                            if(initNatureTrain == 0):
                                                initNatureTrain = 1
                                                NaturesTrains = t.naturesTrains.copy()
                                            else:
                                                newNaturesTrains = []
                                                for nature in t.naturesTrains:
                                                    if(nature in NaturesTrains):
                                                        newNaturesTrains.append(nature)
                                                NaturesTrains = newNaturesTrains
                                            if(initLigne == 0):
                                                initLigne = 1
                                                Lignes = t.lignes.copy()
                                            else:
                                                newLignes = []
                                                for ligne in t.lignes:
                                                    if(ligne in Lignes and ligne not in newLignes):
                                                        newLignes.append(ligne)
                                                Lignes = newLignes
                                            if(t.mode != "Optimisable"):
                                                mode = "Non optimisable"

                                            # print(t.nom + " : " + t.mode + " = " + mode)
                                        #if(len(NaturesTrains) > 0):
                                        if((len(NaturesTrains) > 0 and len(Lignes) > 0) or brancheOuverte['Connexe']):
                                            if(self.natureParDefaut not in NaturesTrains):
                                                NaturesTrains.append(self.natureParDefaut)
                                            if(pointOptimisation.isPAFQuai or pointOptimisation.isPTA or transition.pointOptimisationDestination.isPAFQuai or transition.pointOptimisationDestination.isPTA):
                                                newLignes = []
                                                for ligne in Lignes:
                                                    if(ligne not in _lignesSansArret and ligne not in newLignes):
                                                        newLignes.append(ligne)
                                                Lignes = newLignes
                                            meAjoutee = self.AjouterMissionElementaireRegulation(pointOptimisation, transition.pointOptimisationDestination, nouvelleBrancheOuverte['Transitions'], ModeControleVitesse, Sens, NaturesTrains, Lignes)
                                            meAjoutee.mode = mode
                                            print("Me ajoutée : " + meAjoutee.nom + " mode : " + meAjoutee.mode)
                                            print("")
                                            pointOptimisation.MERDepuisPO.append(meAjoutee)
                                        if(transition.pointOptimisationDestination.isPAFQuai and transition.pointOptimisationDestination.quai.station.nom not in _gareTerminus):
                                            if(nouvelleBrancheOuverte['DerniereVoie'] not in brancheOuverte['VoiesParcourues']):
                                                # print("Transition : " + transition.nom)
                                                branchesOuvertes.append(nouvelleBrancheOuverte)
                                elif(nouvelleBrancheOuverte['DerniereVoie'] not in brancheOuverte['VoiesParcourues']):
                                    branchesOuvertes.append(nouvelleBrancheOuverte)
                                #os.system("pause")

                    del branchesOuvertes[0]
            # if(pointOptimisation.nomPointOptimisation == "PTA_SDP_T3"):
            #     print("PO / PTA_SDP_T3")
            #     os.system("pause")
            # os.system("cls")

    #Cette méthode permet de générer les missions élémentaires (SMT3) à partir des missions élémentaires de régulation
    #@execution_time 
    def GenererMissionsElementaires___YDA__disabled_YDA(self, seuilMauvaisGlissement, dVisi, dBonGlissement, vBonGlissement, dMauvaisGlissement, vMauvaisGlissement, vA, dA, vMav, T_S, dRep, dLibMG, dLibBG, gareTerminus):
        logging.info("Start calling GenererMissionsElementaires___YDA")
        self.missionsElementaires = {}
        for meR in self.missionsElementairesRegulation.values():
            #ADU : on supprime les missions élémentaires qui ne sont pas d'origine et destination un PTA ou PAF
            #if((meR.poOrigine.isPAFQuai or meR.poOrigine.isPTA) and (meR.poDestination.isPAFQuai or meR.poDestination.isPTA)):
            #Ajout des missions trains courts
            #Ajout de la mission CBTC
            mEAjoutee = None
            if(meR.modeControleVitesse == "KVB+CBTC"):
                mEAjoutee = self.AjouterMissionElementaire("C:"+meR.nom, meR, "KVB+CBTC", "US")
            #Ajout de la mission KVB
            else:
                mEAjoutee = self.AjouterMissionElementaire("C:"+meR.nom, meR, "KVB", "US")
            meR.missionsElementaires.append(mEAjoutee)

            #Ajout des missions trains longs
            #Ajout de la mission CBTC
            if(meR.modeControleVitesse == "KVB+CBTC"):
                mEAjoutee = self.AjouterMissionElementaire("L:"+meR.nom, meR, "KVB+CBTC", "UM")
            #Ajout de la mission KVB
            else:
                mEAjoutee = self.AjouterMissionElementaire("L:"+meR.nom, meR, "KVB", "UM")
            meR.missionsElementaires.append(mEAjoutee)

        for sig in self.signals.values():
            sig.GenererCaracteristiqueGlissementSignal(seuilMauvaisGlissement)
        os.system("pause")

        nbME = len(self.missionsElementaires)
        iME = 0
        for me in self.missionsElementaires.values():
            me.GenererOrigineDestination(gareTerminus)
            me.GenererSegmentsParcourus()
            me.GenererTVDsdeQuaiouPTA()
            me.GenererAiguilles(dVisi)
            me.GenererCommandesSignaux(dVisi, dBonGlissement, vBonGlissement, dMauvaisGlissement, vMauvaisGlissement, vA, dA, vMav, T_S, dRep, dLibMG, dLibBG)
            me.GenererTransits(gareTerminus)
            iME = iME + 1
            print("Generation ME : " + str(round(iME*100./nbME,2)) + "%")
            #me.GenererDPafPap()
        os.system("pause")

        # for pc in self.pointsDeControle.values():
        #     if(pc.isPTES and (pc.PTESType == "IN" or pc.PTESType == "INOUT")):
        #         pc.DefinirVLigne()

    #@execution_time 
    def AjouterMissionElementaire__disabled_YDA(self, _nom, _missionElementaireRegulation, _modeControleVitesse, _compositionTrain):
        logging.info("Start calling AjouterMissionElementaire")
        self.missionsElementaires[_nom] = MissionElementaire(_nom, _missionElementaireRegulation, _modeControleVitesse, _compositionTrain)
        return self.missionsElementaires[_nom]

    #Cette méthode permet d'ajouter une mission élémentaire de régulation
    #@execution_time 
    def AjouterMissionElementaireRegulationSimple__disabled_YDA(self, _nom, _poA, _poB, _modeControleVitesse, _sens):
        logging.info("Start calling AjouterMissionElementaireRegulationSimple")
        self.missionsElementairesRegulation[_nom] = MissionElementaireRegulation(_nom, _poA, _poB, [], _modeControleVitesse, _sens, [], [])
        return self.missionsElementairesRegulation[_nom]

    #@execution_time 
    def AjouterMissionElementaireRegulation__disabled_YDA(self, _poA, _poB, _transitions, _modeControleVitesse, _sens, _naturesTrains, _lignes):
        logging.info("Start calling AjouterMissionElementaireRegulation")
        nbPresent = 0
        seulPresent = None
        nomAAjouter = None
        #On vérifie si la transition existe déjà entre A et B
        for i in self.missionsElementairesRegulation.values():
            if i.poOrigine == _poA and i.poDestination == _poB:
                nbPresent = nbPresent + 1
                if(nbPresent == 1):
                    seulPresent = i

        if(nbPresent == 0):
            nomAAjouter = _poA.nomPointOptimisation + "|" + _poB.nomPointOptimisation
            #print(_poA.nomPointOptimisation + "#" + _poB.nomPointOptimisation)
        elif(nbPresent == 1):
            nomAAjouter = _poA.nomPointOptimisation + "|" + _poB.nomPointOptimisation + "@2"
            #On renomme l'ancienne transition seulPresent
            del self.missionsElementairesRegulation[_poA.nomPointOptimisation + "|" + _poB.nomPointOptimisation]
            seulPresent.nom = _poA.nomPointOptimisation + "|" + _poB.nomPointOptimisation + "@1"
            self.missionsElementairesRegulation[seulPresent.nom] = seulPresent
        else:
            nomAAjouter = _poA.nomPointOptimisation + "|" + _poB.nomPointOptimisation + "@" + str(nbPresent + 1)

        self.missionsElementairesRegulation[nomAAjouter] = MissionElementaireRegulation(nomAAjouter, _poA, _poB, _transitions, _modeControleVitesse, _sens, _naturesTrains, _lignes)
        self.missionsElementairesRegulation[nomAAjouter].GenererSegmentsParcourus()
        return self.missionsElementairesRegulation[nomAAjouter]
    #Cette méthode permet de rechercher un point d'optimisation
    #@execution_time 
    def RechercherPointOptimisation__disabled_YDA(self, _nomPointOptimisation):
        logging.info("Start calling RechercherPointOptimisation")
        for i in self.pointsDeControle.values():
            if i.isPointOptimisation == True and i.nomPointOptimisation == _nomPointOptimisation:
                return i
        return None

    #Cette méthode permet de rechercher une transition entre deux points d'optimisation, passant par une liste de segments. Tous les segments de la transition doivent être précisés
    #@execution_time 
    def RechercherTransitionEntreAEtBAvecSegments__disabled_YDA(self, _poA, _poB, _segments):
        logging.info("Start calling RechercherTransitionEntreAEtBAvecSegments")
        #print("Segments initiaux pour transition entre : " + _poA.nomPointOptimisation + " et " + _poB.nomPointOptimisation)
        #for s in _segments:
            #print(s.nom)
        setSegments = set((x.segment) for x in _segments)
        for i in self.transitions.values():
            #print("transition étudiée : " + i.nom)
            if i.pointOptimisationOrigine == _poA and i.pointOptimisationDestination == _poB:
                #print("Mêmes PO, segments :")
                #for s in i.segments:
                    #print(s.nom)
                difference = [ x for x in i.segmentsParcourus if (x.segment) not in setSegments ]

                if(len(difference) == 0):
                    return i

        return None

    #@execution_time 
    def AjouterTransitionSimple__disabled_YDA(self, _nom, _poA, _poB, _mode, _longueur):
        logging.info("Start calling AjouterTransitionSimple")
        self.transitions[_nom] = Transition(_nom, _poA, _poB, [], _mode, [], [])
        self.transitions[_nom].longueur = _longueur

        return self.transitions[_nom]

    #Cette méthode permet d'ajouter une transition (son nom est généré automatiquement à partir du nom des po)
    #@execution_time 
    def AjouterTransition__disabled_YDA(self, _poA, _poB, _segments, _mode, _checkpoints, _controlpoints):
        logging.info("Start calling AjouterTransition")
        nbPresent = 0
        seulPresent = None
        nomAAjouter = None
        #On vérifie si la transition existe déjà entre A et B
        # for i in self.transitions.values():
        #     if i.pointOptimisationOrigine == _poA and i.pointOptimisationDestination == _poB:
        #         nbPresent = nbPresent + 1
        #         if(nbPresent == 1):
        #             seulPresent = i
        #
        # if(nbPresent == 0):
        #     nomAAjouter = _poA.nomPointOptimisation + "|" + _poB.nomPointOptimisation
        # elif(nbPresent == 1):
        #     nomAAjouter = _poA.nomPointOptimisation + "|" + _poB.nomPointOptimisation + "@2"
        #     #On renomme l'ancienne transition seulPresent
        #     del self.transitions[_poA.nomPointOptimisation + "|" + _poB.nomPointOptimisation]
        #     seulPresent.nom = _poA.nomPointOptimisation + "|" + _poB.nomPointOptimisation + "@1"
        #     self.transitions[seulPresent.nom] = seulPresent
        # else:
        #     nomAAjouter = _poA.nomPointOptimisation + "|" + _poB.nomPointOptimisation + "@" + str(nbPresent + 1)
        nomAAjouter = _poA.nomPointOptimisation + "|" + _poB.nomPointOptimisation
        for i in _checkpoints:
            nomAAjouter = nomAAjouter + "/" + i.nomCheckPoint

        print("Ajout de la transition " + nomAAjouter)

        self.transitions[nomAAjouter] = Transition(nomAAjouter, _poA, _poB, _segments, _mode, _checkpoints, _controlpoints)
        return self.transitions[nomAAjouter]

    #Cette méthode permet d'ajouter un croisement bon à une aiguille
    #@execution_time 
    def AjouterCB__disabled_YDA(self, _nom, _aiguille):
        logging.info("Start calling AjouterCB")
        self.CBs[_nom] = CroisementBon(_nom, _aiguille)
        return self.CBs[_nom]

    #Cette méthode permet de connaître les itinéraires empruntant un segment
    #@execution_time 
    def RechercheItinerairesEmpruntantSegment__disabled_YDA(self, _segment):
        logging.info("Start calling RechercheItinerairesEmpruntantSegment")
        listeItineraires = []
        for p in self.postes.values():
            for i in p.itineraires:
                for s in i.segmentsParcourus:
                    if(s.segment == _segment):
                        listeItineraires.append(i)

        return listeItineraires

    #Cette méthode permet d'importer les pédales de DA
    #@execution_time 
    def ImporterPedales__disabled_YDA(self, masquePedaleFile, feuilNom, feuilNom2):
        logging.info("Start calling ImporterPedales")
        fichierExcel = open(masquePedaleFile, "rb")
        colsNames = ['A','B','C','D','E','F']

        #Initialisation de l'ouverture de la feuille Pédales
        print("Ouverture feuille Pédales")
        feuil = panda.read_excel(fichierExcel, sheet_name=feuilNom, skiprows=[0], usecols='A:F', names=colsNames[:colsNames.index('F')+1])

        for i in feuil.index:
            if(isinstance(feuil['A'][i], str) and feuil['A'][i] != ""):
                self.pedales[feuil['A'][i]] = Pedale(feuil['A'][i], str(feuil['B'][i]), feuil['C'][i], feuil['D'][i], feuil['F'][i], feuil['E'][i])

        feuil = panda.read_excel(fichierExcel, sheet_name=feuilNom2, skiprows=[0], usecols='A:F', names=colsNames[:colsNames.index('F')+1])

        for i in feuil.index:
            if(isinstance(feuil['A'][i], str) and feuil['A'][i] != ""):
                self.pedales[feuil['A'][i]] = Pedale(feuil['A'][i], str(feuil['B'][i]), feuil['C'][i], feuil['D'][i], feuil['F'][i])
        fichierExcel.close()

    #@execution_time 
    def DefinirDistanceSansArret__disabled_YDA(self, _tempoAQuai, _tempoTechnique, _vLigne):
        logging.info("Start calling DefinirDistanceSansArret")
        return (_tempoAQuai + _tempoTechnique) * _vLigne

    #@execution_time 
    def DefinirTempsSansArret__disabled_YDA(self, _distance, _vLigne):
        logging.info("Start calling DefinirTempsSansArret")
        return _distance / _vLigne

    #@execution_time 
    def DefinirDistanceAvecArret__disabled_YDA(self, _tempoAQuai, _tempoTechnique, _vLigne, _gFS):
        logging.info("Start calling DefinirDistanceAvecArret")
        dFreinage = (_vLigne*_vLigne)/(2.*_gFS)
        tFreinage = math.sqrt((2.*dFreinage)/_gFS)
        D_return = 0.
        if(tFreinage <= (_tempoAQuai + _tempoTechnique)):
            tVitesseConstante = _tempoAQuai + _tempoTechnique - tFreinage
            dVitesseConstante = tVitesseConstante * _vLigne
            D_return = dVitesseConstante + dFreinage
        else:
            D_return = (((_tempoAQuai + _tempoTechnique)*(_tempoAQuai + _tempoTechnique))*_gFS)/2.
        return D_return

    #@execution_time 
    def DefinirTempsAvecArret__disabled_YDA(self, _distance, _vLigne, _gFS):
        logging.info("Start calling DefinirTempsAvecArret")
        dFreinage = (_vLigne*_vLigne)/(2.*_gFS)
        tFreinage = math.sqrt((2.*dFreinage)/_gFS)
        D_return = 0.
        if(_distance > dFreinage):
            D_return = (_distance - dFreinage)/_vLigne + tFreinage
        else:
            D_return = math.sqrt((2.*_distance)/_gFS)
        return D_return

class NatureTrain:
    #@execution_time 
    def __init__(self, _nom, _pardefaut, _composition):
        logging.info("Start calling __init__")
        self.nom = _nom
        self.pardefaut = _pardefaut
        self.modeles = []
        self.composition = _composition
        self.lignes = []

    #@execution_time 
    def AjouterModele__disabled_YDA(self, _modele):
        logging.info("Start calling AjouterModele")
        self.modeles.append(_modele)

    def __str__(self):
        return f'nom: {self.nom} pardefaut: {self.pardefaut}  composition: {self.composition} '

class ModeleTrain:
    #@execution_time 
    def __init__(self, _nom, _modeconduite, _nature):
        logging.info("Start calling __init__")
        self.nom = _nom
        self.nature = _nature
        self.modeconduite = _modeconduite
        self.aSimuler = False

    def __str__(self):
        return f'nom: {self.nom} nature: [{self.nature}] modeconduite: {self.modeconduite}  aSimuler: {self.aSimuler}'
        
class Pedale:
    #@execution_time 
    def __init____disabled_YDA(self, _nomAtos, _nomSiemens, _segment, _abs, _signal, _direction = None):
        logging.info("Start calling __init__")
        graphe = GrapheSingleton()
        self.nomAtos = _nomAtos
        self.nomSiemens = _nomSiemens
        self.segment = graphe.segments[_segment]
        self.abs = _abs/100.
        self.sens = "BOTH"
        if(_direction == None):
            self.sens = None
        elif(_direction == "UP"):
            self.sens = "CROISSANT"
        else:
            self.sens = "DECROISSANT"
        self.signal = None
        if(_signal in graphe.signals):
            self.signal = graphe.signals[_signal]

class ZLPV:
    #@execution_time 
    def __init____disabled_YDA(self, _nom, _vitesse, _segmentDebut, _absDebut, _segmentFin, _absFin):
        logging.info("Start calling __init__")
        self.nom = _nom
        self.vitesse = _vitesse
        self.segmentDebut = _segmentDebut
        self.absDebut = _absDebut
        self.segmentFin = _segmentFin
        self.absFin = _absFin

    #@execution_time 
    def NormaliserAdonf__disabled_YDA(self):
        logging.info("Start calling NormaliserAdonf")
        graphe = GrapheSingleton()
        self.segmentDebut = graphe.segments[self.segmentDebut]
        self.segmentFin = graphe.segments[self.segmentFin]

class MissionElementaire:
    #@execution_time 
    def __init____disabled_YDA(self, _nom, _missionElementaireRegulation, _modeControleVitesse, _compositionTrain):
        logging.info("Start calling __init__")
        self.nom = _nom
        self.missionElementaireRegulation = _missionElementaireRegulation
        self.modeControleVitesse = _modeControleVitesse
        self.compositionTrain = _compositionTrain
        self.segmentsParcourus = []
        self.origineNom = ""
        self.origine = None
        self.destinationNom = ""
        self.destination = None
        self.itineraires = []
        self.DPafPap = None
        self.contrainteDepartQuai = False
        self.signaux = []
        self.tvdsDeQuaiouPTA = []

    #@execution_time 
    def FindBestContreSensPerturbanteME__disabled_YDA(self, composition, nature):
        logging.info("Start calling FindBestContreSensPerturbanteME")
        graphe = GrapheSingleton()
        maxSimilarityCount = 0
        maxSimilarityME = None
        for me in graphe.missionsElementaires.values():
            countSimilarity = 0
            if(me.segmentsParcourus[0].sens != self.segmentsParcourus[0].sens and (me.compositionTrain == composition or me.compositionTrain == "US+UM") and nature in me.missionElementaireRegulation.naturesTrains):
                if(me.missionElementaireRegulation.poDestination != self.missionElementaireRegulation.poOrigine):
                    for segmentS in self.segmentsParcourus:
                        for segmentO in me.segmentsParcourus:
                            if(segmentS.segment == segmentO.segment):
                                countSimilarity = countSimilarity + 1
                    if(countSimilarity > maxSimilarityCount):
                        maxSimilarityCount = countSimilarity
                        maxSimilarityME = me

        return maxSimilarityME

    #@execution_time 
    def FindWorstElementaryTripWithNature__disabled_YDA(self, natureTrain, _poOrigine = None):
        logging.info("Start calling FindWorstElementaryTripWithNature")
        graphe = GrapheSingleton()

        poOrigine = self.missionElementaireRegulation.poOrigine
        compute = False
        worstMe = None
        if(_poOrigine != None):
            poOrigine = _poOrigine
            compute = True
        if(self.worstMe == None):
            compute = True

        if(compute):
            worstScore = -1
            for MERDepuisPO in poOrigine.MERDepuisPO:
                if(natureTrain in MERDepuisPO.naturesTrains and MERDepuisPO.sens == self.missionElementaireRegulation.sens):
                    score = graphe.ScoreMissionsElementairesSePerturbent(MERDepuisPO.missionsElementaires[0], self)
                    if(score > worstScore):
                        worstScore = score
                        worstMe = MERDepuisPO

            if(_poOrigine == None):
                self.worstMe = worstMe
        else:
            worstMe = self.worstMe
        return worstMe

    #used for sure YDA
    def FindNextElementaryTrip(self, _exceptEnd = None, _minimizeMePerturbationScore = None):
        #logging.info("Start calling FindNextElementaryTrip")
        graphe = GrapheSingleton()
        poDestination = self.missionElementaireRegulation.poDestination
        if(poDestination.isPTES):
            return None
        minMEMemeSens = None
        minMESensInverse = None
        keyDeDivergence = -1
        scoreTotalminMEMemeSens = 9999999
        for MERDepuisDest in poDestination.MERDepuisPO:
            if(MERDepuisDest.poDestination != _exceptEnd):
                if(MERDepuisDest.segmentsParcourus[0].sens == self.segmentsParcourus[0].sens):
                    if(_minimizeMePerturbationScore == None):
                        if(minMEMemeSens is None or len(MERDepuisDest.segmentsParcourus) < len(minMEMemeSens.segmentsParcourus)):
                            minMEMemeSens = MERDepuisDest
                    else:
                        scoreMeANePasPerturber = 0
                        for meANePasPerturber in _minimizeMePerturbationScore:
                            if(meANePasPerturber != None):
                                scoreMeANePasPerturber = scoreMeANePasPerturber + graphe.ScoreMissionsElementairesSePerturbent(MERDepuisDest.missionsElementaires[0], meANePasPerturber)
                        #print(MERDepuisDest.nom + " score : " + str(scoreMeANePasPerturber))
                        if(minMEMemeSens is None or scoreTotalminMEMemeSens > scoreMeANePasPerturber):
                            minMEMemeSens = MERDepuisDest
                            scoreTotalminMEMemeSens = scoreMeANePasPerturber
                else:
                    if(_minimizeMePerturbationScore == None):
                        i = 0
                        for segPI in MERDepuisDest.segmentsParcourus[::-1]:
                            sensPIInverse = "DECROISSANT"
                            if(segPI.sens == "DECROISSANT"):
                                sensPIInverse = "CROISSANT"
                            segPIInverse = ParcoursSegment(segPI.segment, sensPIInverse)
                            if(segPIInverse in self.segmentsParcourus):
                                if(i > keyDeDivergence):
                                    keyDeDivergence = i
                                    minMESensInverse = MERDepuisDest
                                break
                            i = i + 1
                    else:
                        for segPI in MERDepuisDest.segmentsParcourus[::-1]:
                            sensPIInverse = "DECROISSANT"
                            if(segPI.sens == "DECROISSANT"):
                                sensPIInverse = "CROISSANT"
                            segPIInverse = ParcoursSegment(segPI.segment, sensPIInverse)
                            if(segPIInverse in self.segmentsParcourus):
                                scoreMeANePasPerturber = 0
                                for meANePasPerturber in _minimizeMePerturbationScore:
                                    if(meANePasPerturber != None):
                                        scoreMeANePasPerturber = scoreMeANePasPerturber + graphe.ScoreMissionsElementairesSePerturbent(MERDepuisDest.missionsElementaires[0], meANePasPerturber)
                                #print(MERDepuisDest.nom + " si score : " + str(scoreMeANePasPerturber))
                                if(minMESensInverse is None or scoreTotalminMEMemeSens > scoreMeANePasPerturber):
                                    minMESensInverse = MERDepuisDest
                                    scoreTotalminMEMemeSens = scoreMeANePasPerturber

        minME = minMESensInverse
        if(minMEMemeSens is not None):
            minME = minMEMemeSens

        if(minME is None):
            return None

        for me in minME.missionsElementaires:
            if(me.compositionTrain == self.compositionTrain):
                return me

    #@execution_time 
    def GenererOrigineDestination__disabled_YDA(self, gareTerminus):
        logging.info("Start calling GenererOrigineDestination")
        graphe = GrapheSingleton()
        segmentsParcourus = self.missionElementaireRegulation.segmentsParcourus
        #Pour l'origine
        #Si un PtA
        if(self.missionElementaireRegulation.poOrigine.isPTA == True):
            self.origineNom = self.missionElementaireRegulation.poOrigine.nomPointOptimisation
            self.origine = graphe.PtAs[self.missionElementaireRegulation.poOrigine.nomPointOptimisation]
        #Si un PtES
        elif(self.missionElementaireRegulation.poOrigine.isPTES == True):
            self.origineNom = self.missionElementaireRegulation.poOrigine.nomPointOptimisation
            self.origine = self.missionElementaireRegulation.poOrigine
        #Si un PAF de quai
        elif(self.missionElementaireRegulation.poOrigine.isPAFQuai == True):
            #Compter le nombre de PAF de quai de la station dans le sens de la marche
            self.contrainteDepartQuai = True
            quai = graphe.RechercherQuai(self.missionElementaireRegulation.poOrigine.nomPointOptimisation)
            if(quai == None):
                print("Pas de quai trouvé pour " + self.missionElementaireRegulation.poOrigine.nomPointOptimisation)
                os.system("pause")
            pafsDuSens = quai.FournirPAFsSens(segmentsParcourus[0].sens)
            if(len(pafsDuSens) < 1):
                print("Erreur génération de mE ("+self.missionElementaireRegulation.nom+") : aucun paf origine dans ce sens")
                os.system("pause")
            elif(len(pafsDuSens) == 1):
                self.origine = pafsDuSens[0]
                self.origineNom = self.missionElementaireRegulation.poOrigine.quai.nomDCSYS + " - SP" + str(pafsDuSens[0].numero)
            else:
                pafLePlusLoin = None
                pafLeMoinsLoin = None
                for paf in pafsDuSens:
                    #premier paf
                    if(pafLePlusLoin == None or pafLeMoinsLoin == None):
                        pafLePlusLoin = paf
                        pafLeMoinsLoin = paf
                    #selection paf
                    elif(segmentsParcourus[0].sens == "CROISSANT"):
                        if(paf.abs > pafLePlusLoin.abs):
                            pafLePlusLoin = paf
                        if(paf.abs < pafLeMoinsLoin.abs):
                            pafLeMoinsLoin = paf
                    else:
                        if(paf.abs < pafLePlusLoin.abs):
                            pafLePlusLoin = paf
                        if(paf.abs > pafLeMoinsLoin.abs):
                            pafLeMoinsLoin = paf

                if(self.compositionTrain == "US"):
                    self.origine = pafLeMoinsLoin
                    self.origineNom = self.missionElementaireRegulation.poOrigine.quai.nomDCSYS + " - SP" + str(pafLeMoinsLoin.numero)
                else:
                    self.origine = pafLePlusLoin
                    self.origineNom = self.missionElementaireRegulation.poOrigine.quai.nomDCSYS + " - SP" + str(pafLePlusLoin.numero)

                if(pafLePlusLoin == pafLeMoinsLoin):
                    pafLePlusLoin.composition = "US+UM"
                else:
                    pafLePlusLoin.composition = "UM"
                    pafLeMoinsLoin.composition = "US"
        else:
            print("Erreur de génération Origine/Destination mE")
            os.system("pause")

        #Pour la destination
        #Si un PtA
        if(self.missionElementaireRegulation.poDestination.isPTA == True):
            self.destinationNom = self.missionElementaireRegulation.poDestination.nomPointOptimisation
            self.destination = graphe.PtAs[self.missionElementaireRegulation.poDestination.nomPointOptimisation]
        #Si un PtES
        elif(self.missionElementaireRegulation.poDestination.isPTES == True):
            self.destinationNom = self.missionElementaireRegulation.poDestination.nomPointOptimisation
            self.destination = self.missionElementaireRegulation.poDestination
        #Si un PAF de quai
        elif(self.missionElementaireRegulation.poDestination.isPAFQuai == True):
            #Compter le nombre de PAF de quai de la station dans le sens de la marche
            #print("PO de QUAI : " + self.missionElementaireRegulation.poDestination.nomPointOptimisation)
            quai = graphe.RechercherQuai(self.missionElementaireRegulation.poDestination.nomPointOptimisation)
            pafsDuSens = []
            if(quai.station.nom in gareTerminus):
                pafsDuSens = quai.FournirPAFsSensApproche("CROISSANT") + quai.FournirPAFsSensApproche("DECROISSANT")
            else:
                pafsDuSens = quai.FournirPAFsSensApproche(segmentsParcourus[-1].sens)
            if(len(pafsDuSens) < 1):
                print("Erreur génération de mE ("+self.missionElementaireRegulation.nom+") : aucun paf destination dans ce sens")
                os.system("pause")
            elif(len(pafsDuSens) == 1):
                self.destination = pafsDuSens[0]
                self.destinationNom = self.missionElementaireRegulation.poDestination.quai.nomDCSYS + " - SP" + str(pafsDuSens[0].numero)
            else:
                pafLePlusLoin = None
                pafLeMoinsLoin = None
                for paf in pafsDuSens:
                    #premier paf
                    if(pafLePlusLoin == None or pafLeMoinsLoin == None):
                        pafLePlusLoin = paf
                        pafLeMoinsLoin = paf
                    #selection paf
                    elif(quai.station.nom in gareTerminus):
                        if(segmentsParcourus[0].sens == "CROISSANT"):
                            if(paf.abs < pafLePlusLoin.abs):
                                pafLePlusLoin = paf
                            if(paf.abs > pafLeMoinsLoin.abs):
                                pafLeMoinsLoin = paf
                        else:
                            if(paf.abs > pafLePlusLoin.abs):
                                pafLePlusLoin = paf
                            if(paf.abs < pafLeMoinsLoin.abs):
                                pafLeMoinsLoin = paf
                    elif(segmentsParcourus[0].sens == "CROISSANT"):
                        if(paf.abs > pafLePlusLoin.abs):
                            pafLePlusLoin = paf
                        if(paf.abs < pafLeMoinsLoin.abs):
                            pafLeMoinsLoin = paf
                    else:
                        if(paf.abs < pafLePlusLoin.abs):
                            pafLePlusLoin = paf
                        if(paf.abs > pafLeMoinsLoin.abs):
                            pafLeMoinsLoin = paf

                if(self.compositionTrain == "US"):
                    self.destination = pafLeMoinsLoin
                    self.destinationNom = self.missionElementaireRegulation.poDestination.quai.nomDCSYS + " - SP" + str(pafLeMoinsLoin.numero)
                else:
                    self.destination = pafLePlusLoin
                    self.destinationNom = self.missionElementaireRegulation.poDestination.quai.nomDCSYS + " - SP" + str(pafLePlusLoin.numero)
        else:
            print("Erreur de génération Origine/Destination mE")
            os.system("pause")

    #@execution_time 
    def GenererSegmentsParcourus__disabled_YDA(self):
        logging.info("Start calling GenererSegmentsParcourus")
        #Si l'origine est un paf et n'est pas sur le premier segment de la mission élémentaire de régulation, on ajoute le segment de l'origine dans le même sens de parcours
        if(self.missionElementaireRegulation.poOrigine.isPAFQuai == True and self.origine.segment != self.missionElementaireRegulation.segmentsParcourus[0].segment):
            segmentParcouru = ParcoursSegment(self.origine.segment, self.missionElementaireRegulation.segmentsParcourus[0].sens)
            if(segmentParcouru not in self.missionElementaireRegulation.segmentsParcourus):
                self.segmentsParcourus.append(segmentParcouru)
        self.segmentsParcourus = self.segmentsParcourus + self.missionElementaireRegulation.segmentsParcourus
        #Si la destination est un paf et n'est pas sur le dernier segment de la mission élémentaire de régulation, on ajoute le segment destination dans le même sens de parcours
        if(self.missionElementaireRegulation.poDestination.isPAFQuai == True and self.destination.segment != self.missionElementaireRegulation.segmentsParcourus[-1].segment):
            segmentParcouru = ParcoursSegment(self.destination.segment, self.missionElementaireRegulation.segmentsParcourus[-1].sens)
            if(segmentParcouru not in self.segmentsParcourus):
                self.segmentsParcourus.append(segmentParcouru)

        #Ajout du segment précédent le premier segment
        segment = self.segmentsParcourus[0]
        if(segment.sens == "CROISSANT"):
            if(segment.segment.segment1VoisinAmont != None):
                segmentParcouru = ParcoursSegment(segment.segment.segment1VoisinAmont, "CROISSANT")
                if(segmentParcouru not in self.segmentsParcourus):
                    self.segmentsParcourus.insert(0, segmentParcouru)
        elif(segment.sens == "DECROISSANT"):
            if(segment.segment.segment1VoisinAval != None):
                segmentParcouru = ParcoursSegment(segment.segment.segment1VoisinAval, "DECROISSANT")
                if(segmentParcouru not in self.segmentsParcourus):
                    self.segmentsParcourus.insert(0, segmentParcouru)

         #ajout de segment précédent le dernier segment
        segment = self.segmentsParcourus[-1]
        if(segment.sens == "CROISSANT"):
            if(segment.segment.segment1VoisinAval != None):
                segmentParcouru = ParcoursSegment(segment.segment.segment1VoisinAval, "CROISSANT")
                if(segmentParcouru not in self.segmentsParcourus):
                    self.segmentsParcourus.append(segmentParcouru)
        elif(segment.sens == "DECROISSANT"):
            if(segment.segment.segment1VoisinAmont != None):
                segmentParcouru = ParcoursSegment(segment.segment.segment1VoisinAmont, "DECROISSANT")
                if(segmentParcouru not in self.segmentsParcourus):
                    self.segmentsParcourus.append(segmentParcouru)

    #@execution_time 
    def GenererAiguilles__disabled_YDA(self, dVisi):
        logging.info("Start calling GenererAiguilles")
        graphe = GrapheSingleton()
        i = 0
        for itineraire in self.missionElementaireRegulation.itinerairesAcommander:
            i += 1
            #Génération des aiguilles rencontrées et aiguilles associées
            itiItem = {}
            itiItem['Itineraire'] = itineraire
            if(len(itineraire.aiguillesParcourues) > 0):
                itiItem['AiguilleRencontree'] = itineraire.aiguillesParcourues[0]
            else:
                itiItem['AiguilleRencontree'] = None
            if(len(itineraire.aiguillesParcourues) > 1):
                itiItem['AiguillesAssociees'] = itineraire.aiguillesParcourues[1:] + itineraire.aiguillesEnProtection
            else:
                itiItem['AiguillesAssociees'] = itineraire.aiguillesEnProtection

            #Génération des distances de cible fonc et de cible secu
            itiItem['Origine'] = itineraire.origine
            if(isinstance(itiItem['AiguilleRencontree'], PositionAiguille)):
                itiItem['distanceCibleFonc'] = dVisi
                segmentEnCours = ParcoursSegment(itineraire.origine.segment, itineraire.origine.sens)
                if(segmentEnCours not in self.segmentsParcourus):
                    print(itineraire.origine.segment.nom + " " + itineraire.origine.sens + " n'est un segment parcouru de " + self.nom)
                    os.system("pause")
                else:
                    keySegmentEnCours = self.segmentsParcourus.index(segmentEnCours)
                    #Premier segment en cours : distance entre le feu et la fin de segment ou l'aiguille
                    if(segmentEnCours.sens == "CROISSANT"):
                        itiItem['distanceCibleFonc'] = itiItem['distanceCibleFonc'] + segmentEnCours.segment.longueur - itineraire.origine.abs
                    else:
                        itiItem['distanceCibleFonc'] = itiItem['distanceCibleFonc'] + itineraire.origine.abs
                    #Ajout de la taille des segment jusqu'au segment de l'aiguille
                    while((segmentEnCours.segment != itiItem['AiguilleRencontree'].aiguille.segTalonDroite and segmentEnCours.segment != itiItem['AiguilleRencontree'].aiguille.segTalonGauche and segmentEnCours.segment != itiItem['AiguilleRencontree'].aiguille.segPointe) and keySegmentEnCours+1 < len(self.segmentsParcourus)):
                        keySegmentEnCours = keySegmentEnCours + 1
                        segmentEnCours = self.segmentsParcourus[keySegmentEnCours]
                        itiItem['distanceCibleFonc'] = itiItem['distanceCibleFonc'] + segmentEnCours.segment.longueur

                    #génération de la cible secu
                    itiItem['distanceCibleSecu'] = 0
                    if(segmentEnCours.segment == itiItem['AiguilleRencontree'].aiguille.segTalonDroite or segmentEnCours.segment == itiItem['AiguilleRencontree'].aiguille.segTalonGauche):
                        CB = graphe.RechercherCBAvecAiguille(itiItem['AiguilleRencontree'].aiguille)
                        if(CB != None and segmentEnCours.segment.nom in CB.cbSegments):
                            CBsurSegment = CB.cbSegments[segmentEnCours.segment.nom]
                            if(segmentEnCours.sens == "CROISSANT"):
                                itiItem['distanceCibleSecu'] = segmentEnCours.segment.longueur - CBsurSegment['abs']
                            else:
                                itiItem['distanceCibleSecu'] = CBsurSegment['abs']

            #génération des TVD de conditions de commutation d'aiguilles
            itiItem['TVDCondCommutation'] = []
            for aiguille in itineraire.aiguillesParcourues + itineraire.aiguillesEnProtection:
                voieAiguille = aiguille.aiguille.voie
                pkAiguille = aiguille.aiguille.pk
                absSegPosAiguille = CoordVoiePKToSegAbs(voieAiguille, pkAiguille)
                cdv = graphe.RechercherCDVAvecSegmentAbs(absSegPosAiguille['segment'], round(absSegPosAiguille['abs'], 2), aiguille.aiguille)
                tvd = graphe.RechercherTVDAvecCDV(cdv)
                if(tvd == None):
                    if(cdv == None):
                        print("Pas de CDV pour l'aiguille " + aiguille.aiguille.nom + " à la position " + str(round(absSegPosAiguille['abs'], 2)) + " sur segment " + absSegPosAiguille['segment'].nom)
                    else:
                        print("Pas de TVD pour " + cdv.nom)
                    os.system("pause")
                if(tvd not in itiItem['TVDCondCommutation'] and tvd != None):
                    itiItem['TVDCondCommutation'].append(tvd)
                    #print("aiguille : " + aiguille.aiguille.nom)
                    #print("segment : " + absSegPosAiguille['segment'].nom + " abs : " + str(round(absSegPosAiguille['abs'], 2)))

            #Ajout des TVD de quai
            cdvsTransitIti = graphe.CDVDansInterval(self.segmentsParcourus, itineraire.origine.segment, itineraire.origine.abs, itineraire.destination.segment, itineraire.destination.abs)
            for cdv in cdvsTransitIti:
                tvd = graphe.RechercherTVDAvecCDV(cdv)
                if(tvd == None):
                    if(cdv == None):
                        print("Pas de CDV pour les transits de " + aiguille.itineraire.nom)
                    else:
                        print("Pas de TVD pour " + cdv.nom)
                    os.system("pause")
                if(tvd in self.tvdsDeQuaiouPTA and tvd not in itiItem['TVDCondCommutation'] and tvd != None):
                    itiItem['TVDCondCommutation'].append(tvd)

                # if(cdv is None or tvd is None):
                #     print("Pas de cdv/tdv")
                #     os.system("pause")
                # else:
                #     print("cdv : " + cdv.nom)
                #     print("tvd : " + tvd.nom)
            #lorsque la destination est un PTA, ajout du TVD concerné
            if(isinstance(self.destination, PtA) and i == len(self.missionElementaireRegulation.itinerairesAcommander)):
                cdv = graphe.RechercherCDVAvecSegmentAbs(self.destination.segment, self.destination.abs)
                tvd = graphe.RechercherTVDAvecCDV(cdv)
                if(tvd == None):
                    if(cdv == None):
                        print("Pas de CDV pour le PtA " + self.destination.nom)
                    else:
                        print("Pas de TVD pour " + cdv.nom)
                    os.system("pause")
                if(tvd not in itiItem['TVDCondCommutation'] and tvd != None):
                    itiItem['TVDCondCommutation'].append(tvd)

            #génération des TVD des conditions de propagation de cible
            itiItem['TVDCondPropCible'] = []
            for zone in itineraire.zonesEspacementAutomatique:
                itiItem['TVDCondPropCible'].append(zone)

            self.itineraires.append(itiItem)

    #@execution_time 
    def GenererTVDsdeQuaiouPTA__disabled_YDA(self):
        logging.info("Start calling GenererTVDsdeQuaiouPTA")
        graphe = GrapheSingleton()
        for tra in self.missionElementaireRegulation.transitions:
            if(tra.pointOptimisationDestination.isPTA):
            # if(tra.pointOptimisationDestination.isPAFQuai or tra.pointOptimisationDestination.isPTA):
                cdv = graphe.RechercherCDVAvecSegmentAbs(tra.pointOptimisationDestination.segment, tra.pointOptimisationDestination.abs)
                if(cdv != None):
                    tvd = graphe.RechercherTVDAvecCDV(cdv)
                    if(tvd != None):
                        self.tvdsDeQuaiouPTA.append(tvd)

    #Cette méthode permet de générer les conditions de commande des itinéraires et la gestion des transits sur la mission élémentaire
    #@execution_time 
    def GenererTransits__disabled_YDA(self, gareTerminus):
        logging.info("Start calling GenererTransits")
        graphe = GrapheSingleton()
        segOrigine = None
        absOrigine = None
        segDestination = None
        absDestination = None

        # if(self.missionElementaireRegulation.poOrigine.isQuai):
        #     #Récupérer le paf dans le bon sens pour la composition de la mE, afin d'attribuer seg et abs
        #     for paf in self.missionElementaireRegulation.poOrigine.quai.pafs.values():
        #         if(self.missionElementaireRegulation.sens == paf.sens):
        #             if(self.compositionTrain == "US"):
        #                 if(paf.composition == "US+UM" or paf.composition == "US"):
        #                     absOrigine = paf.abs
        #                     segOrigine = paf.segment
        #             else:
        #                 if(paf.composition == "US+UM" or paf.composition == "UM"):
        #                     absOrigine = paf.abs
        #                     segOrigine = paf.segment
        #     if(absOrigine == None or segOrigine == None):
        #         for paf in self.missionElementaireRegulation.poOrigine.quai.pafs.values():
        #             if(self.compositionTrain == "US"):
        #                 if(paf.composition == "US+UM" or paf.composition == "US"):
        #                     absOrigine = paf.abs
        #                     segOrigine = paf.segment
        #             else:
        #                 if(paf.composition == "US+UM" or paf.composition == "UM"):
        #                     absOrigine = paf.abs
        #                     segOrigine = paf.segment
        # else:
        #     segOrigine = self.missionElementaireRegulation.poOrigine.segment
        #     absOrigine = self.missionElementaireRegulation.poOrigine.abs

        # if(self.missionElementaireRegulation.poDestination.isQuai):
        #     #Récupérer le paf dans le bon sens pour la composition de la mE, afin d'attribuer seg et abs
        #     for paf in self.missionElementaireRegulation.poDestination.quai.pafs.values():
        #         if(self.missionElementaireRegulation.sens == paf.sens):
        #             if(self.compositionTrain == "US"):
        #                 if(paf.composition == "US+UM" or paf.composition == "US"):
        #                     absDestination = paf.abs
        #                     segDestination = paf.segment
        #             else:
        #                 if(paf.composition == "US+UM" or paf.composition == "UM"):
        #                     absDestination = paf.abs
        #                     segDestination = paf.segment
        #     if(absDestination == None or segDestination == None):
        #         for paf in self.missionElementaireRegulation.poDestination.quai.pafs.values():
        #             if(self.compositionTrain == "US"):
        #                 if(paf.composition == "US+UM" or paf.composition == "US"):
        #                     absDestination = paf.abs
        #                     segDestination = paf.segment
        #             else:
        #                 if(paf.composition == "US+UM" or paf.composition == "UM"):
        #                     absDestination = paf.abs
        #                     segDestination = paf.segment
        # else:
        #     segDestination = self.missionElementaireRegulation.poOrigine.segment
        #     absDestination = self.missionElementaireRegulation.poOrigine.abs

        for itineraire in self.itineraires:
            condsDispoTransits = []
            reservsTransits = []
            cdvsTransitIti = graphe.CDVDansInterval(self.segmentsParcourus, itineraire['Itineraire'].origine.segment, itineraire['Itineraire'].origine.abs, itineraire['Itineraire'].destination.segment, itineraire['Itineraire'].destination.abs)
            cdvsTransitMission = graphe.CDVDansInterval(self.segmentsParcourus, itineraire['Itineraire'].origine.segment, itineraire['Itineraire'].origine.abs, self.missionElementaireRegulation.poDestination.segment, self.missionElementaireRegulation.poDestination.abs)
            for cdv in cdvsTransitMission:
                if(cdv in cdvsTransitIti):
                    tvd = graphe.RechercherTVDAvecCDV(cdv)
                    if tvd is not None:
                        reservTransit = {}
                        reservTransit['TVD'] = tvd
                        reservTransit['Sens'] = itineraire['Itineraire'].origine.sens
                        reservsTransits.append(reservTransit)
                        if(cdv is cdvsTransitMission[-1] and (self.missionElementaireRegulation.poDestination.isPTA or (self.missionElementaireRegulation.poDestination.isPAFQuai and self.missionElementaireRegulation.poDestination.quai.station.nom in gareTerminus))):
                            condDispoTransit = {}
                            condDispoTransit['TVD'] = tvd
                            condDispoTransit['Sens'] = "DOUBLE_SENS"
                            condsDispoTransits.append(condDispoTransit)
                        elif(tvd in itineraire['TVDCondPropCible'] or tvd in itineraire['TVDCondCommutation']):
                            condDispoTransit = {}
                            condDispoTransit['TVD'] = tvd
                            condDispoTransit['Sens'] = "DOUBLE_SENS"
                            condsDispoTransits.append(condDispoTransit)
                        else:
                            condDispoTransit = {}
                            condDispoTransit['TVD'] = tvd
                            if(itineraire['Itineraire'].origine.sens == "CROISSANT"):
                                condDispoTransit['Sens'] = "DECROISSANT"
                            else:
                                condDispoTransit['Sens'] = "CROISSANT"
                            condsDispoTransits.append(condDispoTransit)
                else:
                    tvd = graphe.RechercherTVDAvecCDV(cdv)
                    if tvd is not None:
                        condDispoTransit = {}
                        condDispoTransit['TVD'] = tvd
                        if(cdv is cdvsTransitMission[-1] and (self.missionElementaireRegulation.poDestination.isPTA or (self.missionElementaireRegulation.poDestination.isPAFQuai and self.missionElementaireRegulation.poDestination.quai.station.nom in gareTerminus))):
                            condDispoTransit['Sens'] = "DOUBLE_SENS"
                        elif(itineraire['Itineraire'].origine.sens == "CROISSANT"):
                            condDispoTransit['Sens'] = "DECROISSANT"
                        else:
                            condDispoTransit['Sens'] = "CROISSANT"
                        condsDispoTransits.append(condDispoTransit)

                itineraire['condsDispoTransits'] = condsDispoTransits
                itineraire['reservsTransits'] = reservsTransits

    #Cette méthode permet de générer la distance PAF PAP
    #ADU : non ajusté en fonction de l'approche du train et du type de paf
    #@execution_time 
    def GenererDPafPap__disabled_YDA(self):
        logging.info("Start calling GenererDPafPap")
        graphe = GrapheSingleton()
        sens = self.missionElementaireRegulation.sens
        segmentFin = self.destination.segment
        absFin = self.destination.abs

        pap = None
        #Recherche du premier signal "fin de voie" derrière le paf
        for signal in segmentFin.RechercherSignauxSurSegment():
            if(signal.type == "FIN_DE_VOIE" and signal.sens == sens):
                if((signal.abs >= absFin and signal.sens == "CROISSANT") or (signal.abs <= absFin and signal.sens == "DECROISSANT")):
                    pap = {}
                    pap['segment'] = signal.segment
                    pap['abs'] = signal.abs

        if(pap != None):
            #recherche d'une aiguille en bout de segment
            aiguilleExtremiteSegment = None
            if(sens == "CROISSANT"):
                if(segmentFin.segment1VoisinAval != None and segmentFin.segment2VoisinAval != None):
                    aiguilleExtremiteSegment = graphe.RechercherAiguilleAvecSegments(segmentFin, segmentFin.segment1VoisinAval, segmentFin.segment2VoisinAval)
            else:
                if(segmentFin.segment1VoisinAmont != None and segmentFin.segment2VoisinAmont != None):
                    aiguilleExtremiteSegment = graphe.RechercherAiguilleAvecSegments(segmentFin, segmentFin.segment1VoisinAmont, segmentFin.segment2VoisinAmont)

            if(aiguilleExtremiteSegment != None):
                #recherche du croisement bon à l'extremité de segment
                croisementBon = graphe.RechercherCBAvecAiguille(aiguilleExtremiteSegment)
                if(segmentFin.nom in croisementBon.cbSegments):
                    pap = {}
                    pap['segment'] = croisementBon.cbSegments[segmentFin.nom]['Segment']
                    pap['abs'] = croisementBon.cbSegments[segmentFin.nom]['abs']

        if(pap == None):
            pap = {}
            pap['segment'] = segmentFin
            if(sens == "CROISSANT"):
                pap['abs'] = segmentFin.longueur
            else:
                pap['abs'] = 0.

        self.DPafPap = abs(absFin - pap['abs'])

    #@execution_time 
    def GenererCommandesSignaux__disabled_YDA(self, _dVisi, _dBonGlissement, _vBonGlissement, _dMauvaisGlissement, _vMauvaisGlissement, _vA, _dA, _vMav, _T_S, _dRep, _DLibMG, _DLibBG):
        logging.info("Start calling GenererCommandesSignaux")
        graphe = GrapheSingleton()
        debut = False
        fin = False

        listeSignaux = []
        #Pour chaque segment parcouru
        Position = 1
        finish = False
        for segment in self.segmentsParcourus:
            signauxSurSegment = segment.segment.RechercherSignauxSurSegment()
            nbSignauxSurSegment = 0
            for signal in signauxSurSegment:
                if(signal.sens == segment.sens and finish == False):
                    if(segment.segment != self.destination.segment or (segment.sens == "CROISSANT" and signal.abs < self.destination.abs) or (segment.sens == "DECROISSANT" and signal.abs > self.destination.abs)):
                        signalInfos = {}
                        signalInfos['Signal'] = signal
                        signalInfos['Segment'] = segment.segment
                        signalInfos['Abs'] = signal.abs
                        #signalInfos['Position'] = Position
                        Position_int = 0
                        for s in signauxSurSegment:
                            if(s.abs < signalInfos['Abs'] and s.sens == "CROISSANT" and s.sens == segment.sens):
                                Position_int = Position_int + 1
                            if(s.abs > signalInfos['Abs'] and s.sens == "DECROISSANT" and s.sens == segment.sens):
                                Position_int = Position_int + 1
                        signalInfos['Position'] = Position + Position_int
                        listeSignaux.append(signalInfos)
                        nbSignauxSurSegment = nbSignauxSurSegment + 1
            Position = Position + nbSignauxSurSegment
            if(segment.segment == self.destination.segment):
                finish = True

        sorted(listeSignaux, key=lambda signal: signal['Position'])

        #print(str(listeSignaux))
        for signal in listeSignaux:

            tvdsTreated = []
            signalInfos = {}
            signalInfos['Signal'] = signal['Signal']
            signalInfos['CibleSecu'] = ""
            signalInfos['CibleFonc'] = _dVisi
            signalInfos['V_mav'] = _vMav
            signalInfos['Drep'] = _dRep
            #ADU : A remplacer (soit distance balise PROX pour MG en KVB, soit balise KVBP, soit 0)
            if(signal['Signal'].typeGlissement == "MauvaisGlissement"):
                signalInfos['DLib'] = _DLibMG
            else:
                signalInfos['DLib'] = _DLibBG
            signalInfos['CommandeSignalAAjouter'] = False
            signalInfos['CondSignalVert_TVDLibres'] = []

            signalInfos['Vapp_BG'] = ""
            signalInfos['Dapp_BG'] = ""
            signalInfos['Vapp_MG'] = ""
            signalInfos['Dapp_MG'] = ""
            if(signal['Signal'].typeGlissement == "BonGlissement" and (signal['Signal'].isCarre or signal['Signal'].isSemaphoreFixe or signal['Signal'].isSemaphoreCli)):
                signalInfos['Vapp_BG'] = _dBonGlissement
                signalInfos['Dapp_BG'] = _vBonGlissement
            elif(signal['Signal'].typeGlissement == "MauvaisGlissement" and (signal['Signal'].isCarre or signal['Signal'].isSemaphoreFixe or signal['Signal'].isSemaphoreCli)):
                signalInfos['Vapp_BG'] = _dBonGlissement
                signalInfos['Dapp_BG'] = _vBonGlissement
                signalInfos['Vapp_MG'] = _dMauvaisGlissement
                signalInfos['Dapp_MG'] = _vMauvaisGlissement

            sigAverASurParcours = False
            for sigAver in signal['Signal'].signauxAnnonceAvertissement:
                #if(sigAver in self.signaux):
                for sigPrecedent in self.signaux:
                    if(sigPrecedent['Signal'] == sigAver):
                        #print(sigAver.nom + " - " + sigPrecedent['Signal'].nom + " : Signal d'avertissement annonce ici")
                        sigAverASurParcours = True
                        #os.system("pause")
                    #else:
                        #print(sigAver.nom + " - " + sigPrecedent['Signal'].nom)

            sigAverSSurParcours = False
            for sig in listeSignaux:
                for sigAver in sig['Signal'].signauxAnnonceSemaphoreCli:
                    if(sigAver == signal):
                        #print(sigAver.nom + " - " + sig.nom + " : Signal d'avertissement semaphore cli ici")
                        sigAverSSurParcours = True
                    #else:
                        #print(sigAver.nom + " - " + sig.nom)
            #os.system("pause")

            if(signal['Signal'].isSemaphoreFixe and not signal['Signal'].isSemaphoreCli):
                signalInfos['T_S'] = _T_S
            elif(signal['Signal'].isSemaphoreFixe and signal['Signal'].isSemaphoreCli and not sigAverSSurParcours):
                signalInfos['T_S'] = _T_S
            else:
                signalInfos['T_S'] = 0

            if(sigAverASurParcours == True):
                signalInfos['V_A'] = _vA
                signalInfos['D_A'] = _dA
            else:
                signalInfos['V_A'] = ""
                signalInfos['D_A'] = ""

            itinerairesSignalOrigine = graphe.RechercherItinerairesDepuisOrigine(signal['Signal'])
            if(signal['Signal'].isCarre and len(itinerairesSignalOrigine) > 0):
                signalInfos['CommandeSignalAAjouter'] = True
                for iti in itinerairesSignalOrigine:
                    for tvd in iti.zonesEspacementAutomatique:
                        if(tvd not in signalInfos['CondSignalVert_TVDLibres']):
                            signalInfos['CondSignalVert_TVDLibres'].append(tvd)

            if(signal['Signal'].isSemaphoreFixe or signal['Signal'].isSemaphoreCli):
                signalInfos['CommandeSignalAAjouter'] = True

                #Recherche des TVD
                next_signal = None
                for sign in listeSignaux:
                    if(next_signal == None and sign['Position'] >= signal['Position'] + 1 and (sign['Signal'].isSemaphoreFixe or sign['Signal'].isSemaphoreCli)):
                        next_signal = sign
                        #print("Signal en cours : " + signal['Signal'].nom + " Signal suivant : " + next_signal['Signal'].nom + " : " + next_signal['Segment'].nom  + " - " + str(next_signal['Abs']))

                CDVList = []
                if(next_signal != None):
                    #print("Recherche des CDV de " + signal['Signal'].nom + " à " + next_signal['Signal'].nom)
                    CDVList = graphe.CDVDansInterval(self.segmentsParcourus, signal['Segment'], signal['Abs'], next_signal['Segment'], next_signal['Abs'])
                else:
                    #print("Recherche des CDV de " + signal['Signal'].nom + " à " + self.destinationNom)
                    CDVList = graphe.CDVDansInterval(self.segmentsParcourus, signal['Segment'], signal['Abs'], self.destination.segment, self.destination.abs)
                    # if(signal['Signal'].sens == "CROISSANT"):
                    #     print("Recherche des CDV de " + signal['Signal'].nom + " à la fin de voie")
                    #     CDVList = graphe.CDVDansInterval(self.segmentsParcourus, signal['Segment'], signal['Abs'], self.segmentsParcourus[-1].segment, self.segmentsParcourus[-1].segment.longueur)
                    # else:
                    #     print("Recherche des CDV de " + signal['Signal'].nom + " à la fin de voie")
                    #     CDVList = graphe.CDVDansInterval(self.segmentsParcourus, signal['Segment'], signal['Abs'], self.segmentsParcourus[-1].segment, 0.0)

                #os.system("pause")

                for cdv in CDVList:
                    tvd = graphe.RechercherTVDAvecCDV(cdv)
                    if(tvd != None and tvd not in signalInfos['CondSignalVert_TVDLibres']):
                        signalInfos['CondSignalVert_TVDLibres'].append(tvd)
            if(len(signalInfos['CondSignalVert_TVDLibres']) > 0):
                self.signaux.append(signalInfos)
            elif(signalInfos['CommandeSignalAAjouter']):
                print("Attention : mE " + self.nom + " signal "+ signal['Signal'].nom +" sans TVD de cantonnement")
                os.system("pause")

class MissionElementaireRegulation:
    #@execution_time 
    def __init____disabled_YDA(self, _nom, _poOrigine, _poDestination, _transitions, _modeControleVitesse, _sens, _naturesTrains, _lignes):
        logging.info("Start calling __init__")
        self.nom = _nom
        self.poOrigine = _poOrigine
        self.poDestination = _poDestination
        self.transitions = _transitions
        self.segmentsParcourus = []
        self.itinerairesAcommander = []
        self.modeControleVitesse = _modeControleVitesse
        self.sens = _sens
        self.mode = ""
        self.naturesTrains = _naturesTrains
        self.lignes = _lignes
        self.nbChangementVoie = 0
        self.missionsElementaires = []
        #self.GenererSegmentsParcourus()

    #@execution_time 
    def GenererSegmentsParcourus__disabled_YDA(self):
        logging.info("Start calling GenererSegmentsParcourus")
        for transition in self.transitions:
            for segment in transition.segmentsParcourus:
                if(len(self.segmentsParcourus) <= 0 or segment != self.segmentsParcourus[-1]):
                        self.segmentsParcourus.append(segment)
        if(self.poOrigine.isPAFQuai):
            for paf in self.poOrigine.quai.pafs.values():
                if(paf.sens == "CROISSANT" and self.sens == "G -> D" or paf.sens == "DECROISSANT" and self.sens == "D -> G"):
                    segment = ParcoursSegment(paf.segment, paf.sens)
                    if(segment not in self.segmentsParcourus):
                        #print("insert of segment " + segment.segment.nom)
                        #os.system("pause")
                        self.segmentsParcourus.insert(0, segment)
        if(self.poDestination.isPAFQuai):
            for paf in self.poDestination.quai.pafs.values():
                if(paf.sens == "CROISSANT" and self.sens == "G -> D" or paf.sens == "DECROISSANT" and self.sens == "D -> G"):
                    segment = ParcoursSegment(paf.segment, paf.sens)
                    if(segment not in self.segmentsParcourus):
                        #print("insert of segment " + segment.segment.nom)
                        #os.system("pause")
                        self.segmentsParcourus.append(segment)
class Transition:
    #@execution_time 
    def __init____disabled_YDA(self, _nom, _poOrigine, _poDestination, _segmentsParcourus, _mode, _checkpoints, _controlpoints):
        logging.info("Start calling __init__")
        self.nom = _nom
        self.pointOptimisationOrigine = _poOrigine
        self.pointOptimisationDestination = _poDestination
        self.segmentsParcourus = _segmentsParcourus
        self.mode = _mode
        self.checkpoints = _checkpoints
        self.naturesTrains = []
        self.lignes = []
        self.longueur = 0.0
        self.controlpoints = _controlpoints
        self.itinerairesACommander = []
        self.signauxTraverses = []

    #@execution_time 
    def definirLongueur__disabled_YDA(self):
        logging.info("Start calling definirLongueur")
        if(len(self.segmentsParcourus) == 1):
            self.longueur = abs(self.pointOptimisationOrigine.abs - self.pointOptimisationDestination.abs)
        else:
            for s in self.segmentsParcourus:
                if(s.segment == self.pointOptimisationOrigine.segment):
                    if(s.sens == "CROISSANT"):
                        self.longueur = s.segment.longueur - self.pointOptimisationOrigine.abs
                    else:
                        self.longueur = self.pointOptimisationOrigine.abs
                elif(s.segment == self.pointOptimisationDestination.segment):
                    if(s.sens == "CROISSANT"):
                        self.longueur = self.longueur + self.pointOptimisationDestination.abs
                    else:
                        self.longueur = self.longueur + (s.segment.longueur - self.pointOptimisationDestination.abs)
                else:
                    self.longueur = self.longueur + s.segment.longueur

    #@execution_time 
    def print__disabled_YDA(self):
        logging.info("Start calling print")
        print("Transition : " + self.nom + " de " + self.pointOptimisationOrigine.nom + " à " + self.pointOptimisationDestination.nom)
        stringSegments = ""
        for s in self.segmentsParcourus:
            stringSegments = stringSegments + s.segment.nom + "(" + s.sens + ")" + ","
        print(stringSegments)

class JointCDV:
    #@execution_time 
    def __init____disabled_YDA(self, _cdv1, _cdv2, _segment, _abs):
        logging.info("Start calling __init__")
        self.cdv1 = _cdv1
        self.cdv2 = _cdv2
        self.segment = _segment
        self.abs = _abs
        self.nomGroupe = None

class ExtremiteCDVLimiteDomaine:
    #@execution_time 
    def __init____disabled_YDA(self, _cdv, _segment, _abs):
        logging.info("Start calling __init__")
        self.cdv = _cdv
        self.segment = _segment
        self.abs = _abs

class PointDeControle:
    #@execution_time 
    def __init____disabled_YDA(self, _nom, _abs, _segment):
        logging.info("Start calling __init__")
        self.nom = _nom
        self.segment = _segment
        self.abs = _abs

        self.jointCDV = None
        self.isJCDV = False

        self.pedale = None

        self.extremiteCDVLimiteDomaine = None
        self.isECDVLD = False

        self.isExtremiteQuai = False
        self.quai = None
        self.sens = None

        self.isPAFQuai = False

        self.isPointOptimisation = False
        self.nomPointOptimisation = None
        self.transitionsDepuisCePoint = []
        self.transitionsVersCePoint = []
        self.sensPriviligie = "BOTH"

        self.isDetecteurPassage = False
        self.isPTES = False
        self.PTESType = "INOUT"
        self.isPTA = False
        self.isPointSortieQuai = False
        self.isCheckPoint = False
        self.nomCheckPoint = None
        self.transitionsNonOptimisablesForces = []

        self.naturesTrains = []
        self.lignes = []
        self.MERDepuisPO = []
        self.vLigne = 120. / 3.6

        self.PR_VOIE = ""
        self.PR_CICH = ""


    #@execution_time 
    def DefinirVLigne__disabled_YDA(self):
        logging.info("Start calling DefinirVLigne")
        graphe = GrapheSingleton()
        vLigneFound = False
        for zlpv in graphe.zlpvs.values():
            if(zlpv.segmentDebut == self.segment):
                if(zlpv.absDebut <= self.abs and (zlpv.segmentFin != self.segment or zlpv.absFin > self.abs)):
                    self.vLigne = zlpv.vitesse
                    vLigneFound = True

        segmentEnCours = self.segment.segment1VoisinAmont
        while vLigneFound == False and segmentEnCours != None:
            zlpvAbs = 0.
            for zlpv in graphe.zlpvs.values():
                if(zlpv.segmentDebut == segmentEnCours and zlpv.absDebut >= zlpvAbs):
                    zlpvAbs = zlpv.absDebut
                    self.vLigne = zlpv.vitesse
                    vLigneFound = True
            segmentEnCours = segmentEnCours.segment1VoisinAmont

    #@execution_time 
    def AjouterParticulariteJCDV__disabled_YDA(self, _jointCDV):
        logging.info("Start calling AjouterParticulariteJCDV")
        self.isJCDV = True
        self.jointCDV = _jointCDV

    #@execution_time 
    def AjouterParticularitePedale__disabled_YDA(self, _pedale):
        logging.info("Start calling AjouterParticularitePedale")
        self.isDetecteurPassage = True
        self.pedale = _pedale

    #@execution_time 
    def AjouterParticulariteECDVLD__disabled_YDA(self, _ECDVLD):
        logging.info("Start calling AjouterParticulariteECDVLD")
        self.isECDVLD = True
        self.extremiteCDVLimiteDomaine = _ECDVLD

    #@execution_time 
    def AjouterParticulariteExtremiteQuai__disabled_YDA(self, _quai, _sens):
        logging.info("Start calling AjouterParticulariteExtremiteQuai")
        self.isExtremiteQuai = True
        self.quai = _quai
        self.sens = _sens

    #@execution_time 
    def AjouterParticularitePAFQuai__disabled_YDA(self, _quai):
        logging.info("Start calling AjouterParticularitePAFQuai")
        self.isPAFQuai = True
        self.quai = _quai

    #@execution_time 
    def AjouterParticularitePointOptimisation__disabled_YDA(self, _nom):
        logging.info("Start calling AjouterParticularitePointOptimisation")
        self.isPointOptimisation = True
        self.nomPointOptimisation = _nom

    #@execution_time 
    def AjouterParticularitePTA__disabled_YDA(self):
        logging.info("Start calling AjouterParticularitePTA")
        self.isPTA = True

    #@execution_time 
    def AjouterParticularitePTES__disabled_YDA(self, _type):
        logging.info("Start calling AjouterParticularitePTES")
        self.isPTES = True
        self.PTESType = _type

class CroisementBon:
    #@execution_time 
    def __init____disabled_YDA(self, _nom, _aiguille):
        logging.info("Start calling __init__")
        self.nom = _nom
        self.aiguille = _aiguille
        self.cbSegments = {}

    #@execution_time 
    def AjouterCB__disabled_YDA(self, _segmentNom, _segment, _abs):
        logging.info("Start calling AjouterCB")
        self.cbSegments[_segmentNom] = {}
        self.cbSegments[_segmentNom]['Segment'] = _segment
        self.cbSegments[_segmentNom]['abs'] = _abs

    #@execution_time 
    def NormaliserAdonf__disabled_YDA(self):
        logging.info("Start calling NormaliserAdonf")
        print("Normalisation cb : " + self.nom)
        #Recuperation du graphe (singleton)
        __graphe = GrapheSingleton()
        self.aiguille = __graphe.aiguilles[self.aiguille]
        for cb in self.cbSegments.values():
            cb['Segment'] = __graphe.segments[cb['Segment']]

class Ligne:
    #@execution_time 
    def __init____disabled_YDA(self, _nom, _numero, _referentiel, _segmentReference, _orientationGauche, _orientationDroite):
        logging.info("Start calling __init__")
        self.nom = _nom
        self.numero = _numero
        self.referentiel = _referentiel
        self.segmentReference = _segmentReference
        self.orientationGauche = _orientationGauche
        self.orientationDroite = _orientationDroite

    #@execution_time 
    def print__disabled_YDA(self, _chainePrefixe = ""):
        logging.info("Start calling print")
        print(_chainePrefixe+"Ligne : " + self.nom)
        print(_chainePrefixe+"-numero : " + str(self.numero))
        print(_chainePrefixe+"-referentiel : " + self.referentiel)
        print(_chainePrefixe+"-segmentReference : " + self.segmentReference.nom)
        print(_chainePrefixe+"-orientationGauche : " + self.orientationGauche)
        print(_chainePrefixe+"-orientationDroite : " + self.orientationDroite)

    #Cette méthode permet de transformer les structures string d'ADONF en associations du graphe
    #@execution_time 
    def NormaliserAdonf__disabled_YDA(self):
        logging.info("Start calling NormaliserAdonf")
        print("Normalisation ligne : " + self.nom)
        #Recuperation du graphe (singleton)
        __graphe = GrapheSingleton()
        self.segmentReference = __graphe.segments[self.segmentReference]

class Station:
    #@execution_time 
    def __init____disabled_YDA(self, _nom):
        logging.info("Start calling __init__")
        self.nom = _nom
        self.quais = {}

    #@execution_time 
    def AjouterQuai__disabled_YDA(self, _nom, _nomDCSYS, _extremite1Seg, _extremite2Seg, _extremite1Abs, _extremite2Abs, _extremite1Sens, _extremite2Sens):
        logging.info("Start calling AjouterQuai")
        self.quais[_nom] = Quai(_nom, _nomDCSYS, _extremite1Seg, _extremite2Seg, _extremite1Abs, _extremite2Abs, _extremite1Sens, _extremite2Sens, self)
        return self.quais[_nom]

    #@execution_time 
    def print__disabled_YDA(self, _chainePrefixe = ""):
        logging.info("Start calling print")
        print(_chainePrefixe+"Station : " + self.nom)
        for __o in self.quais.values():
            __o.print(_chainePrefixe+"+")

    #Cette méthode permet de transformer les structures string d'ADONF en associations du graphe
    #@execution_time 
    def NormaliserAdonf__disabled_YDA(self):
        logging.info("Start calling NormaliserAdonf")
        print("Normalisation station : " + self.nom)
        for __o in self.quais.values():
            __o.NormaliserAdonf()

class Quai:
    #@execution_time 
    def __init____disabled_YDA(self, _nom, _nomDCSYS, _extremite1Seg, _extremite2Seg, _extremite1Abs, _extremite2Abs, _extremite1Sens, _extremite2Sens, _station):
        logging.info("Start calling __init__")
        self.nom = _nom
        self.nomDCSYS = _nomDCSYS
        self.extremite1Seg = _extremite1Seg
        self.extremite2Seg = _extremite2Seg
        self.extremite1Abs = _extremite1Abs
        self.extremite2Abs = _extremite2Abs
        self.extremite1Sens = _extremite1Sens
        self.extremite2Sens = _extremite2Sens
        self.pafs = {}
        self.station = _station

    #@execution_time 
    def AjouterPAF__disabled_YDA(self, _numero, _segment, _abs, _sens, _sensApproche, _typePAF):
        logging.info("Start calling AjouterPAF")
        self.pafs[_numero] = PAFQuai(_numero, _segment, _abs, _sens, _sensApproche, _typePAF)

    #@execution_time 
    def print__disabled_YDA(self, _chainePrefixe = ""):
        logging.info("Start calling print")
        print(_chainePrefixe+"Quai : " + self.nom)
        print(_chainePrefixe+"-extremite1Seg : " + self.extremite1Seg.nom)
        print(_chainePrefixe+"-extremite1Abs : " + str(self.extremite1Abs))
        print(_chainePrefixe+"-extremite1Sens : " + self.extremite1Sens)
        print(_chainePrefixe+"-extremite2Seg : " + self.extremite2Seg.nom)
        print(_chainePrefixe+"-extremite2Abs : " + str(self.extremite2Abs))
        print(_chainePrefixe+"-extremite2Sens : " + self.extremite2Sens)
        for __o in self.pafs.values():
            __o.print(_chainePrefixe+"+")

    #Cette méthode permet de transformer les structures string d'ADONF en associations du graphe
    #@execution_time 
    def NormaliserAdonf__disabled_YDA(self):
        logging.info("Start calling NormaliserAdonf")
        print("Normalisation quai : " + self.nom)
        #Recuperation du graphe (singleton)
        __graphe = GrapheSingleton()
        self.extremite1Seg = __graphe.segments[self.extremite1Seg]
        self.extremite2Seg = __graphe.segments[self.extremite2Seg]
        for __o in self.pafs.values():
            __o.NormaliserAdonf()

    #@execution_time 
    def FournirPAFsSens__disabled_YDA(self, sens):
        logging.info("Start calling FournirPAFsSens")
        pafs = []
        for paf in self.pafs.values():
            if(paf.sensApproche != "DOUBLE_SENS"):
                if(paf.typePAF == "AVANT"):
                    if(paf.sens == sens):
                        pafs.append(paf)
                else:
                    if(paf.sens != sens):
                        pafs.append(paf)
            else:
                pafs.append(paf)

        return pafs

    #@execution_time 
    def FournirPAFsSensApproche__disabled_YDA(self, sens):
        logging.info("Start calling FournirPAFsSensApproche")
        pafs = []
        for paf in self.pafs.values():
            if(paf.sensApproche == sens or paf.sensApproche == "DOUBLE_SENS"):
                pafs.append(paf)

        return pafs

class PointArret:
    #@execution_time 
    def __init____disabled_YDA(self, _segment, _abs, _sens):
        logging.info("Start calling __init__")
        self.segment = _segment
        self.abs = _abs
        self.sens = _sens

    #Cette méthode permet de transformer les structures string d'ADONF en associations du graphe
    #@execution_time 
    def NormaliserAdonf__disabled_YDA(self):
        logging.info("Start calling NormaliserAdonf")
        #Recuperation du graphe (singleton)
        __graphe = GrapheSingleton()
        #print(self.segment + " - " + str(self.abs))
        self.segment = __graphe.segments[self.segment]

class PAFQuai(PointArret):
    #@execution_time 
    def __init____disabled_YDA(self, _numero, _segment, _abs, _sens, _sensApproche, _typePAF):
        logging.info("Start calling __init__")
        PointArret.__init__(self, _segment, _abs, _sens)
        self.numero = _numero
        self.composition = ""
        self.vLigne = 120.
        self.sensApproche = _sensApproche
        self.typePAF = _typePAF

    #@execution_time 
    def print__disabled_YDA(self, _chainePrefixe = ""):
        logging.info("Start calling print")
        print(_chainePrefixe+"PAF : " + str(self.numero))
        print(_chainePrefixe+"-segment : " + self.segment.nom)
        print(_chainePrefixe+"-abs : " + str(self.abs))
        print(_chainePrefixe+"-sens : " + self.sens)

    #@execution_time 
    def NormaliserAdonf__disabled_YDA(self):
        logging.info("Start calling NormaliserAdonf")
        print("Normalisation PAF Quai : " + str(self.numero))
        PointArret.NormaliserAdonf(self)

    #@execution_time 
    def DefinirVLigne__disabled_YDA(self):
        logging.info("Start calling DefinirVLigne")
        graphe = GrapheSingleton()
        vLigneFound = False
        for zlpv in graphe.zlpvs.values():
            if(zlpv.segmentDebut == self.segment):
                if(zlpv.absDebut <= self.abs and (zlpv.segmentFin != self.segment or zlpv.absFin > self.abs)):
                    self.vLigne = zlpv.vitesse
                    vLigneFound = True

        segmentEnCours = self.segment.segment1VoisinAmont
        while vLigneFound == False and segmentEnCours != None:
            zlpvAbs = 0.
            for zlpv in graphe.zlpvs.values():
                if(zlpv.segmentDebut == segmentEnCours and zlpv.absDebut >= zlpvAbs):
                    zlpvAbs = zlpv.absDebut
                    self.vLigne = zlpv.vitesse
                    vLigneFound = True
            segmentEnCours = segmentEnCours.segment1VoisinAmont

class PtA(PointArret):
    #@execution_time 
    def __init____disabled_YDA(self, _nom, _segment, _abs, _sens):
        logging.info("Start calling __init__")
        PointArret.__init__(self, _segment, _abs, _sens)
        self.nom = _nom

    #@execution_time 
    def print__disabled_YDA(self, _chainePrefixe = ""):
        logging.info("Start calling print")
        print(_chainePrefixe+"PtA : " + self.nom)
        print(_chainePrefixe+"-segment : " + self.segment.nom)
        print(_chainePrefixe+"-abs : " + str(self.abs))
        print(_chainePrefixe+"-sens : " + str(self.sens))

    #@execution_time 
    def NormaliserAdonf__disabled_YDA(self):
        logging.info("Start calling NormaliserAdonf")
        print("Normalisation PtA : " + self.nom)
        PointArret.NormaliserAdonf(self)

class Segment:
    #@execution_time 
    def __init____disabled_YDA(self, _nom, _troncon, _voie, _longueur, _origine, _fin, _segment1VoisinAmont, _segment2VoisinAmont, _segment1VoisinAval, _segment2VoisinAval):
        logging.info("Start calling __init__")
        self.nom = _nom
        self.troncon = _troncon
        self.voie = _voie
        self.longueur = _longueur
        self.origine = _origine
        self.fin = _fin
        self.segment1VoisinAmont = _segment1VoisinAmont
        self.segment2VoisinAmont = _segment2VoisinAmont
        self.segment1VoisinAval = _segment1VoisinAval
        self.segment2VoisinAval = _segment2VoisinAval
        self.StructSegmentEstCoude = False
        self.StructDebut = ""
        self.StructFin = ""

    #@execution_time 
    def print__disabled_YDA(self, _chainePrefixe = ""):
        logging.info("Start calling print")
        print(_chainePrefixe+"Segment : " + self.nom)
        print(_chainePrefixe+"-troncon : " + self.troncon.nom)
        print(_chainePrefixe+"-voie : " + self.voie.nom)
        print(_chainePrefixe+"-longueur : " + str(self.longueur))
        print(_chainePrefixe+"-origine : " + str(self.origine))
        print(_chainePrefixe+"-fin : " + str(self.fin))
        if(self.segment1VoisinAmont != None):
            print(_chainePrefixe+"-segment1VoisinAmont : " + self.segment1VoisinAmont.nom)
        if(self.segment2VoisinAmont != None):
            print(_chainePrefixe+"-segment2VoisinAmont : " + self.segment2VoisinAmont.nom)
        if(self.segment1VoisinAval != None):
            print(_chainePrefixe+"-segment1VoisinAval : " + self.segment1VoisinAval.nom)
        if(self.segment2VoisinAval != None):
            print(_chainePrefixe+"-segment2VoisinAval : " + self.segment2VoisinAval.nom)

    #Cette méthode permet de rechercher tous les points de contrôle sur le segment, les points de contrôle sont triés par leur abs selon sensTri
    #@execution_time 
    def RechercherPointsControlesSurSegment__disabled_YDA(self, _sensTri):
        logging.info("Start calling RechercherPointsControlesSurSegment")
        graphe = GrapheSingleton()
        pointsDeControle = []
        for i in graphe.pointsDeControle.values():
            if(i.segment == self):
                pointsDeControle.append(i)

        if(_sensTri == "CROISSANT"):
            pointsDeControle.sort(key=lambda PointDeControle: PointDeControle.abs)
        else:
            pointsDeControle.sort(key=lambda PointDeControle: PointDeControle.abs, reverse=True)

        return pointsDeControle

    #@execution_time 
    def RechercherSignauxSurSegment__disabled_YDA(self):
        logging.info("Start calling RechercherSignauxSurSegment")
        __graphe = GrapheSingleton()
        signauxSurSegment = []
        for signal in __graphe.signals.values():
            if(signal.segment == self):
                signauxSurSegment.append(signal)

        return signauxSurSegment

    #Cette méthode permet de transformer les structures string d'ADONF en associations du graphe
    #@execution_time 
    def NormaliserAdonf__disabled_YDA(self):
        logging.info("Start calling NormaliserAdonf")
        print("Normalisation segment : " + self.nom)
        #Recuperation du graphe (singleton)
        __graphe = GrapheSingleton()
        self.troncon = __graphe.troncons[self.troncon]
        self.voie = __graphe.voies[self.voie]

        if(isinstance(self.segment1VoisinAmont, str) and self.segment1VoisinAmont != ""):
            self.segment1VoisinAmont = __graphe.segments[self.segment1VoisinAmont]
        else:
            self.segment1VoisinAmont = None

        if(isinstance(self.segment2VoisinAmont, str) and self.segment2VoisinAmont != ""):
            self.segment2VoisinAmont = __graphe.segments[self.segment2VoisinAmont]
        else:
            self.segment2VoisinAmont = None

        if(isinstance(self.segment1VoisinAval, str) and self.segment1VoisinAval != ""):
            self.segment1VoisinAval = __graphe.segments[self.segment1VoisinAval]
        else:
            self.segment1VoisinAval = None

        if(isinstance(self.segment2VoisinAval, str) and self.segment2VoisinAval != ""):
            self.segment2VoisinAval = __graphe.segments[self.segment2VoisinAval]
        else:
            self.segment2VoisinAval = None

class Voie:
    #@execution_time 
    def __init____disabled_YDA(self, _nom, _type, _sensNominal, _voieContinuitePK, _segContinuitePK, _sensIncrementationPK, _PKDebut, _PKFin):
        logging.info("Start calling __init__")
        self.nom = _nom
        self.type = _type
        self.sensNominal = _sensNominal
        self.voieContinuitePK = _voieContinuitePK
        self.segContinuitePK = _segContinuitePK
        self.sensIncrementationPK = _sensIncrementationPK
        self.PKDebut = _PKDebut
        self.PKFin = _PKFin
        self.NiveauPlan = 0.
        self.VoiesPrincipales = 'P'

    #@execution_time 
    def print__disabled_YDA(self, _chainePrefixe = ""):
        logging.info("Start calling print")
        print(_chainePrefixe+"Voie : " + self.nom)
        print(_chainePrefixe+"-type : " + self.type)
        print(_chainePrefixe+"-sensNominal : " + str(self.sensNominal))
        if(self.voieContinuitePK != None):
            print(_chainePrefixe+"-voieContinuitePK : " + self.voieContinuitePK.nom)
        if(self.segContinuitePK != None):
            print(_chainePrefixe+"-segContinuitePK : " + self.segContinuitePK.nom)
        print(_chainePrefixe+"-sensIncrementationPK : " + self.sensIncrementationPK)
        print(_chainePrefixe+"-PKDebut : " + str(self.PKDebut))
        print(_chainePrefixe+"-PKFin : " + str(self.PKFin))

    #Cette méthode permet de transformer les structures string d'ADONF en associations du graphe
    #@execution_time 
    def NormaliserAdonf__disabled_YDA(self):
        logging.info("Start calling NormaliserAdonf")
        print("Normalisation voie : " + self.nom)
        #Recuperation du graphe (singleton)
        __graphe = GrapheSingleton()
        if(isinstance(self.voieContinuitePK, str) and self.voieContinuitePK!=""):
            self.voieContinuitePK = __graphe.voies[self.voieContinuitePK]
        else:
            self.voieContinuitePK = None

        if(isinstance(self.segContinuitePK, str) and self.segContinuitePK!=""):
            self.segContinuitePK = __graphe.segments[self.segContinuitePK]
        else:
            self.segContinuitePK = None

class Troncon:
    #@execution_time 
    def __init____disabled_YDA(self, _nom, _ligne):
        logging.info("Start calling __init__")
        self.nom = _nom
        self.ligne = _ligne
        self.extremitesSurVoies = []

    #@execution_time 
    def AjouterExtremiteSurVoie__disabled_YDA(self, _voie, _PKDebut, _PKFin):
        logging.info("Start calling AjouterExtremiteSurVoie")
        __extvoie = {}
        __extvoie['voie'] = _voie
        __extvoie['PKDebut'] = _PKDebut
        __extvoie['PKFin'] = _PKFin
        self.extremitesSurVoies.append(__extvoie)

    #@execution_time 
    def print__disabled_YDA(self, _chainePrefixe = ""):
        logging.info("Start calling print")
        print(_chainePrefixe+"Troncon : " + self.nom)
        print(_chainePrefixe+"-ligne : " + self.ligne.nom)
        for __o in self.extremitesSurVoies:
            print(_chainePrefixe+"+Extremite sur voie : ")
            print(_chainePrefixe+"+-voie : " + __o['voie'].nom)
            print(_chainePrefixe+"+-PKDebut : " + str(__o['PKDebut']))
            print(_chainePrefixe+"+-voie : " + str(__o['PKFin']))

    #Cette méthode permet de transformer les structures string d'ADONF en associations du graphe
    #@execution_time 
    def NormaliserAdonf__disabled_YDA(self):
        logging.info("Start calling NormaliserAdonf")
        print("Normalisation troncon : " + self.nom)
        #Recuperation du graphe (singleton)
        __graphe = GrapheSingleton()
        self.ligne = __graphe.lignes[self.ligne]
        for __o in self.extremitesSurVoies:
            __o['voie'] = __graphe.voies[__o['voie']]

class Signal:
    #@execution_time 
    def __init____disabled_YDA(self, _nom, _type, _sousType, _segment, _abs, _sens):
        logging.info("Start calling __init__")
        self.nom = _nom
        self.type = _type
        self.sousType = _sousType
        self.segment = _segment
        self.abs = _abs
        self.sens = _sens
        self.typeGlissement = "BonGlissement"
        self.isSemaphoreFixe = False
        self.isSemaphoreCli = False
        self.isCarre = False
        self.isCarreViolet = False
        self.isAvertissement = False
        self.signauxAnnonceAvertissement = []
        self.signauxAnnonceSemaphoreCli = []
        self.signauxAnnonceSemaphore = []

    #@execution_time 
    def print__disabled_YDA(self, _chainePrefixe = ""):
        logging.info("Start calling print")
        print(_chainePrefixe+"Signal : " + self.nom)
        print(_chainePrefixe+"-type : " + self.type)
        print(_chainePrefixe+"-sousType : " + str(self.sousType))
        print(_chainePrefixe+"-segment : " + self.segment.nom)
        print(_chainePrefixe+"-abs : " + str(self.abs))
        print(_chainePrefixe+"-sens : " + self.sens)

    #Cette méthode permet de transformer les structures string d'ADONF en associations du graphe
    #@execution_time 
    def NormaliserAdonf__disabled_YDA(self):
        logging.info("Start calling NormaliserAdonf")
        print("Normalisation signal : " + self.nom)
        #Recuperation du graphe (singleton)
        __graphe = GrapheSingleton()
        self.segment = __graphe.segments[self.segment]

    #Permet de générer la caractéristique bon glissement ou mauvais glissement d'un signal
    #@execution_time 
    def GenererCaracteristiqueGlissementSignal__disabled_YDA(self, seuilMauvaisGlissement):
        logging.info("Start calling GenererCaracteristiqueGlissementSignal")
        graphe = GrapheSingleton()
        distanceAParcourirJusquAiguille = 0.0

        #distance à parcourir sur le segment, dans le sens du signal, jusqu'à la fin de segment
        if(self.sens == "CROISSANT"):
            distanceAParcourirJusquAiguille = self.segment.longueur - self.abs
        else:
            distanceAParcourirJusquAiguille = self.abs

        segmentActuel = self.segment
        finDeVoie = False
        prochainSegment = None
        aiguille = None
        continuer = True
        while(continuer == True):
            if(self.sens == "CROISSANT"):
                if(segmentActuel.segment1VoisinAval is not None and segmentActuel.segment2VoisinAval is None):
                    segmentProchain = segmentActuel.segment1VoisinAval
                    if(segmentProchain.segment1VoisinAmont is not None and segmentProchain.segment2VoisinAmont is not None):
                        aiguille = graphe.RechercherAiguilleAvecSegments(segmentProchain, segmentProchain.segment1VoisinAmont, segmentProchain.segment2VoisinAmont)
                        continuer = False
                    else:
                        segmentActuel = segmentProchain
                        distanceAParcourirJusquAiguille = distanceAParcourirJusquAiguille + segmentActuel.longueur
                elif(segmentActuel.segment1VoisinAval is None and segmentActuel.segment2VoisinAval is not None):
                    segmentProchain = segmentActuel.segment2VoisinAval
                    if(segmentProchain.segment1VoisinAmont is not None and segmentProchain.segment2VoisinAmont is not None):
                        aiguille = graphe.RechercherAiguilleAvecSegments(segmentProchain, segmentProchain.segment1VoisinAmont, segmentProchain.segment2VoisinAmont)
                        continuer = False
                    else:
                        segmentActuel = segmentProchain
                        distanceAParcourirJusquAiguille = distanceAParcourirJusquAiguille + segmentActuel.longueur

                elif(segmentActuel.segment1VoisinAval is None and segmentActuel.segment2VoisinAval is None):
                    continuer = False
                    finDeVoie = True
                else:
                    aiguille = graphe.RechercherAiguilleAvecSegments(segmentActuel, segmentActuel.segment1VoisinAval, segmentActuel.segment2VoisinAval)
                    continuer = False
            else:
                if(segmentActuel.segment1VoisinAmont is not None and segmentActuel.segment2VoisinAmont is None):
                    segmentProchain = segmentActuel.segment1VoisinAmont
                    if(segmentProchain.segment1VoisinAval is not None and segmentProchain.segment2VoisinAval is not None):
                        aiguille = graphe.RechercherAiguilleAvecSegments(segmentProchain, segmentProchain.segment1VoisinAval, segmentProchain.segment2VoisinAval)
                        continuer = False
                    else:
                        segmentActuel = segmentProchain
                        distanceAParcourirJusquAiguille = distanceAParcourirJusquAiguille + segmentActuel.longueur
                elif(segmentActuel.segment1VoisinAmont is None and segmentActuel.segment2VoisinAmont is not None):
                    segmentProchain = segmentActuel.segment2VoisinAmont
                    if(segmentProchain.segment1VoisinAval is not None and segmentProchain.segment2VoisinAval is not None):
                        aiguille = graphe.RechercherAiguilleAvecSegments(segmentProchain, segmentProchain.segment1VoisinAval, segmentProchain.segment2VoisinAval)
                        continuer = False
                    else:
                        segmentActuel = segmentProchain
                        distanceAParcourirJusquAiguille = distanceAParcourirJusquAiguille + segmentActuel.longueur
                elif(segmentActuel.segment1VoisinAmont is None and segmentActuel.segment2VoisinAmont is None):
                    continuer = False
                    finDeVoie = True
                else:
                    aiguille = graphe.RechercherAiguilleAvecSegments(segmentActuel, segmentActuel.segment1VoisinAmont, segmentActuel.segment2VoisinAmont)
                    continuer = False

        if(aiguille is not None):
            croisementBon = graphe.RechercherCBAvecAiguille(aiguille)
            if(croisementBon is not None and segmentActuel.nom in croisementBon.cbSegments):
                if(self.sens == "CROISSANT"):
                    distanceAParcourirJusquAiguille = distanceAParcourirJusquAiguille - (segmentActuel.longueur - croisementBon.cbSegments[segmentActuel.nom]['abs'])
                else:
                    distanceAParcourirJusquAiguille = distanceAParcourirJusquAiguille - croisementBon.cbSegments[segmentActuel.nom]['abs']

        if(finDeVoie is False and distanceAParcourirJusquAiguille < seuilMauvaisGlissement and self.isCarre and not self.isCarreViolet):
            self.typeGlissement = "MauvaisGlissement"

        print("Signal " + self.nom + " : " + self.typeGlissement + " (distance : " + str(distanceAParcourirJusquAiguille) + "m)")

class Aiguille:
    #@execution_time 
    def __init____disabled_YDA(self, _nom, _posDirecte, _segPointe, _segTalonGauche, _segTalonDroite, _voie, _pk):
        logging.info("Start calling __init__")
        self.nom = _nom
        self.posDirecte = _posDirecte
        self.segPointe = _segPointe
        self.segTalonGauche = _segTalonGauche
        self.segTalonDroite = _segTalonDroite
        self.voie = _voie
        self.pk = _pk

    #@execution_time 
    def DefinirTVD__disabled_YDA():
        logging.info("Start calling DefinirTVD")
        ADU
    #@execution_time 
    def DefinirCDV__disabled_YDA():
        logging.info("Start calling DefinirCDV")
        ADU

    #@execution_time 
    def print__disabled_YDA(self, _chainePrefixe = ""):
        logging.info("Start calling print")
        print(_chainePrefixe+"Aiguille : " + self.nom)
        print(_chainePrefixe+"-posDirecte : " + self.posDirecte)
        print(_chainePrefixe+"-segPointe : " + self.segPointe.nom)
        print(_chainePrefixe+"-segTalonGauche : " + self.segTalonGauche.nom)
        print(_chainePrefixe+"-segTalonDroite : " + self.segTalonDroite.nom)
        print(_chainePrefixe+"-voie : " + self.voie.nom)
        print(_chainePrefixe+"-pk : " + str(self.pk))

    #Cette méthode permet de transformer les structures string d'ADONF en associations du graphe
    #@execution_time 
    def NormaliserAdonf__disabled_YDA(self):
        logging.info("Start calling NormaliserAdonf")
        print("Normalisation aiguille : " + self.nom)
        #Recuperation du graphe (singleton)
        __graphe = GrapheSingleton()
        self.segPointe = __graphe.segments[self.segPointe]
        self.segTalonGauche = __graphe.segments[self.segTalonGauche]
        self.segTalonDroite = __graphe.segments[self.segTalonDroite]
        self.voie = __graphe.voies[self.voie]
class CDV:
    #@execution_time 
    def __init____disabled_YDA(self, _nom):
        logging.info("Start calling __init__")
        self.nom = _nom
        self.segsExtremites = []
        self.segments = {}

    #@execution_time 
    def AjouterSegmentAExtremite__disabled_YDA(self, _segment, _abs):
        logging.info("Start calling AjouterSegmentAExtremite")
        __segment = {}
        __segment['segment'] = _segment
        __segment['abs'] = _abs
        self.segsExtremites.append(__segment)

    #@execution_time 
    def print__disabled_YDA(self, _chainePrefixe = ""):
        logging.info("Start calling print")
        print(_chainePrefixe+"CDV : " + self.nom)
        for __o in self.segsExtremites:
            print(_chainePrefixe+"+Segment A Extremite : ")
            print(_chainePrefixe+"+-segment : " + __o['segment'].nom)
            print(_chainePrefixe+"+-abs : " + str(__o['abs']))

    #Cette méthode permet de transformer les structures string d'ADONF en associations du graphe
    #@execution_time 
    def NormaliserAdonf__disabled_YDA(self):
        logging.info("Start calling NormaliserAdonf")
        print("Normalisation CDV : " + self.nom)
        #Recuperation du graphe (singleton)
        __graphe = GrapheSingleton()
        for __o in self.segsExtremites:
            __o['segment'] = __graphe.segments[__o['segment']]

class TVD:
    #@execution_time 
    def __init____disabled_YDA(self, _nom, _type, _objet):
        logging.info("Start calling __init__")
        self.nom = _nom
        self.type = _type
        self.objet = _objet
        self.segsExtremites = []

    #@execution_time 
    def AjouterSegmentAExtremite__disabled_YDA(self, _segment, _abs):
        logging.info("Start calling AjouterSegmentAExtremite")
        __segment = {}
        __segment['segment'] = _segment
        __segment['abs'] = _abs
        self.segsExtremites.append(__segment)

    #@execution_time 
    def print__disabled_YDA(self, _chainePrefixe = ""):
        logging.info("Start calling print")
        print(_chainePrefixe+"TVD : " + self.nom)
        print(_chainePrefixe+"-type : " + self.type)
        print(_chainePrefixe+"-objet : " + self.objet)
        for __o in self.segsExtremites:
            print(_chainePrefixe+"+Segment A Extremite : ")
            print(_chainePrefixe+"+-segment : " + __o['segment'].nom)
            print(_chainePrefixe+"+-abs : " + str(__o['abs']))

    #Cette méthode permet de transformer les structures string d'ADONF en associations du graphe
    #@execution_time 
    def NormaliserAdonf__disabled_YDA(self):
        logging.info("Start calling NormaliserAdonf")
        print("Normalisation TVD : " + self.nom)
        #Recuperation du graphe (singleton)
        __graphe = GrapheSingleton()
        for __o in self.segsExtremites:
            __o['segment'] = __graphe.segments[__o['segment']]

        if(self.type == "CDV"):
            self.objet = __graphe.CDVs[self.objet]

#Cette classe représente un ensemble de documents de pièces techniques PT2A, regroupés en repertoires de postes d'enclenchement.
class PT2ADir:
    #@execution_time 
    def __init____disabled_YDA(self, _nomDir):
        logging.info("Start calling __init__")
        self.listePostes = {}
        self.nomDir = _nomDir
        self.signauxIntrouvables = {}
        self.aiguillesIntrouvables = {}
        self.zonesIntrouvables = {}
        self.patternProblems = []

    #@execution_time 
    def AjouterPoste__disabled_YDA(self, _nomPoste):
        logging.info("Start calling AjouterPoste")
        self.listePostes[_nomPoste] = Poste(self, _nomPoste)
        return self.listePostes[_nomPoste]

    #@execution_time 
    def Ouvrir__disabled_YDA(self):
        logging.info("Start calling Ouvrir")
        __patternNomPoste = re.compile("^([0-9]+)$")
        __listDirPostes = os.listdir(self.nomDir)
        for __f in __listDirPostes:
            if(os.path.isdir(self.nomDir + __f) and __patternNomPoste.match(__f)):
                __posteAjoute = self.AjouterPoste(__f)
                __posteAjoute.OuvrirPT2A()

        #for __o in self.listePostes.values():
            #print("Poste " + __o.nom)
            #for __d in __o.PT2ADoc:
                #print("PT2A " + __d.nomFichier)

#A COMPLETER
class PT2BDoc:
    #@execution_time 
    def __init____disabled_YDA(self, _Poste, _PosteDir, _nomFichier, _PT2ADir):
        logging.info("Start calling __init__")
        self.Poste = _Poste
        self.PosteDir = _PosteDir
        self.nomFichier = _nomFichier
        self.PT2ADir = _PT2ADir

#Cette classe représente un document technique PT2A
class PT2ADoc:
    #@execution_time 
    def __init____disabled_YDA(self, _Poste, _PosteDir, _nomFichier, _PT2ADir):
        logging.info("Start calling __init__")
        self.Poste = _Poste
        self.PosteDir = _PosteDir
        self.nomFichier = _nomFichier
        self.PT2ADir = _PT2ADir

    #@execution_time 
    def Ouvrir__disabled_YDA(self):
        logging.info("Start calling Ouvrir")
        print("Poste : " + self.Poste.nom + " Fichier : " + self.nomFichier)

        __colsNames = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z',
            'AA','AB','AC','AD','AE','AF','AG','AH','AI','AJ','AK','AL','AM','AN','AO','AP','AQ','AR','AS','AT','AU','AV','AW','AX','AY','AZ',
            'BA','BB','BC','BD','BE','BF','BG','BH','BI','BJ','BK','BL','BM','BN','BO','BP','BQ','BR','BS','BT','BU','BV','BW','BX','BY','BZ',
            'CA','CB','CC','CD','CE','CF','CG','CH','CI','CJ','CK','CL','CM','CN','CO','CP','CQ','CR','CS','CT','CU','CV','CW','CX','CY','CZ',
            'DA','DB','DC','DD','DE','DF','DG','DH','DI','DJ','DK','DL','DM','DN','DO','DP','DQ','DR','DS','DT','DU','DV','DW','DX','DY','DZ',
            'EA','EB','EC','ED','EE','EF','EG','EH','EI','EJ','EK','EL','EM','EN','EO','EP','EQ','ER','ES','ET','EU','EV','EW','EX','EY','EZ',
            'FA','FB','FC','FD','FE','FF','FG','FH','FI','FJ','FK','FL','FM','FN','FO','FP','FQ','FR','FS','FT','FU','FV','FW','FX','FY','FZ',
            'GA','GB','GC','GD','GE','GF','GG','GH','GI','GJ','GK','GL','GM','GN','GO','GP','GQ','GR','GS','GT','GU','GV','GW','GX','GY','GZ',
            'HA','HB','HC','HD','HE','HF','HG','HH','HI','HJ','HK','HL','HM','HN','HO','HP','HQ','HR','HS','HT','HU','HV','HW','HX','HY','HZ']
        __fichierExcel = self.PosteDir + "\\" + self.nomFichier


        __Pt2aExcel = panda.read_excel(__fichierExcel, usecols='A:Q', names=__colsNames[:__colsNames.index('Q')+1])
        __graphe = GrapheSingleton()
        __itineraireComplet = True
        __itineraireAjoute = None

        print("Itineraire : " + str(__Pt2aExcel['E'][1]))
        __patternItineraire = re.compile("^[ ]*([0-9]+)-([0-9]+)( par ([a-zA-Z0-9]+))*(\([0-9]+\))*$")
        __itineraireInfos = __patternItineraire.match(str(__Pt2aExcel['E'][1]))
        if(__itineraireInfos != None):
            __itineraireNom = __itineraireInfos.group(1) + "-" + __itineraireInfos.group(2)
            __ItineraireJalons = []
            if(__itineraireInfos.group(3) != None):
                __itineraireNom = __itineraireNom + "/" + __itineraireInfos.group(4)

            #Recherche des signaux origine et destination dans le graphe ADONF
            __signalOrigineName = "SIG_" + __itineraireInfos.group(1)
            __signalDestinationName = "SIG_" + __itineraireInfos.group(2)
            __signalDestinationName2 = "B_" + __itineraireInfos.group(2)
            if(__signalOrigineName not in __graphe.signals):
                self.PT2ADir.signauxIntrouvables[__signalOrigineName] = __signalOrigineName
                print("Signal introuvable dans ADONF " + __signalOrigineName)
                __itineraireComplet = False
            if(__signalDestinationName not in __graphe.signals and __signalDestinationName2 not in __graphe.signals):
                self.PT2ADir.signauxIntrouvables[__signalDestinationName] = __signalDestinationName
                print("Signal introuvable dans ADONF " + __signalDestinationName)
                os.system("pause")
                __itineraireComplet = False
            if((__signalDestinationName in __graphe.signals or __signalDestinationName2 in __graphe.signals) and __signalOrigineName in __graphe.signals):
                __signalOrigine = __graphe.signals[__signalOrigineName]
                __signalDestination = None
                if(__signalDestinationName in __graphe.signals):
                    __signalDestination = __graphe.signals[__signalDestinationName]
                else:
                    __signalDestination = __graphe.signals[__signalDestinationName2]
                __itineraireAjoute = Itineraire(__itineraireNom, __signalOrigine, __signalDestination, __ItineraireJalons, self)

        else:
            print("Itineraire dans aucun pattern : " + str(__Pt2aExcel['E'][1]))
            self.PT2ADir.patternProblems.append("(Poste : " + self.Poste.nom + " | Fichier : " + self.nomFichier + ") Itineraire (E1) : " + str(__Pt2aExcel['E'][1]))
            __itineraireComplet = False
            #os.system("PAUSE")

        #Dans une PT2A en page simple, les aiguilles parcourues sont à la ligne 7 et les aiguilles en protection à la ligne 8, dans
        #une PT2A double page, les aiguilles parcourues sont à la ligne 8 et les aiguilles en protection à la ligne 14.
        #on sait qu'une PT2A est double page si Q0 est valorisé
        if(isinstance(__Pt2aExcel['Q'][0], str)):
            __cleAigParc = 8
            __cleAigProt = 14
            __cleZoneEspAuto = 40
        else:
            __cleAigParc = 7
            __cleAigProt = 8
            __cleZoneEspAuto = 18
        #__aiguillePattern = re.compile("^([0-9]+[a-z]*)+(G|D){1}(\([0-9]+\))*$")
        __aiguillePattern = re.compile("^[ ]*[v]*([0-9]+[aA-zZ_]*)+(G|D){1}(\([0-9]+\))*$")
        __aiguilleVirtuelPattern = re.compile("^[ ]*[X|x]([0-9]+)(G|D){1}(\([0-9]+\))*$")
        __taquetPattern = re.compile("^[ ]*[X|x]([0-9]+)(R|N){1}(\([0-9]+\))*$")
        __PosAiguilleEquivalence = {"G":"Gauche", "D":"Droite", "R":"Renversee", "N":"Normale"}
        if(isinstance(__Pt2aExcel['F'][__cleAigParc], str)):
            __aiguillesParcourues = __Pt2aExcel['F'][__cleAigParc].split(";")
            for __itAiguille in __aiguillesParcourues:
                __aiguilleInfos = __aiguillePattern.match(__itAiguille)
                __aiguilleVInfos = __aiguilleVirtuelPattern.match(__itAiguille)
                #if(__aiguilleInfos == None):
                    #__aiguilleInfos = __aiguilleVirtuelPattern.match(__itAiguille)
                __taquetInfos = __taquetPattern.match(__itAiguille)
                if(__aiguilleInfos != None):
                    print("Aiguille parcourue " + __aiguilleInfos.group(1) + " à " + __PosAiguilleEquivalence[__aiguilleInfos.group(2)])
                    #Recherche de l'aiguille parcourue dans le graphe ADONF
                    __aiguilleName = "AIG_" + __aiguilleInfos.group(1)
                    if(__aiguilleName in __graphe.aiguilles):
                        if(__itineraireAjoute != None):
                            __PositionAiguilleAjoutee = PositionAiguille(__graphe.aiguilles[__aiguilleName], __PosAiguilleEquivalence[__aiguilleInfos.group(2)])
                            __itineraireAjoute.AjouterAiguilleParcourue(__PositionAiguilleAjoutee)
                    elif("AIG_x" + __aiguilleInfos.group(1) in __graphe.aiguilles):
                        __aiguilleName = "AIG_x" + __aiguilleInfos.group(1)
                        if(__itineraireAjoute != None):
                            __PositionAiguilleAjoutee = PositionAiguille(__graphe.aiguilles[__aiguilleName], __PosAiguilleEquivalence[__aiguilleInfos.group(2)])
                            __itineraireAjoute.AjouterAiguilleParcourue(__PositionAiguilleAjoutee)
                    elif(__aiguilleName + "V" in __graphe.aiguilles):
                        if(__itineraireAjoute != None):
                            __PositionAiguilleAjoutee = PositionAiguille(__graphe.aiguilles[__aiguilleName + "V"], __PosAiguilleEquivalence[__aiguilleInfos.group(2)])
                            __itineraireAjoute.AjouterAiguilleParcourue(__PositionAiguilleAjoutee)
                    else:
                        self.PT2ADir.aiguillesIntrouvables[__aiguilleName] = __aiguilleName
                        print("Aiguille introuvable dans ADONF " + __aiguilleName)
                        __itineraireComplet = False
                elif(__aiguilleVInfos != None):
                    print("Aiguille virtuelle " + __aiguilleVInfos.group(1) + " à " + __PosAiguilleEquivalence[__aiguilleVInfos.group(2)])
                elif(__taquetInfos != None):
                    print("taquet parcouru " + __taquetInfos.group(1) + " à " + __PosAiguilleEquivalence[__taquetInfos.group(2)])
                else:
                    print("Ag/taquet parcouru dans aucun pattern : " + __itAiguille)
                    self.PT2ADir.patternProblems.append("(Poste : " + self.Poste.nom + " | Fichier : " + self.nomFichier + ") Aiguilles parcouru (F"+str(__cleAigParc)+") : " + __itAiguille)
                    __itineraireComplet = False
                    #os.system("PAUSE")
        if(isinstance(__Pt2aExcel['F'][__cleAigProt], str)):
            __aiguillesEnProtection = __Pt2aExcel['F'][__cleAigProt].split(";")
            for __itAiguille in __aiguillesEnProtection:
                __aiguilleInfos = __aiguillePattern.match(__itAiguille)
                __aiguilleVInfos = __aiguilleVirtuelPattern.match(__itAiguille)
                __taquetInfos = __taquetPattern.match(__itAiguille)
                if(__aiguilleInfos != None):
                    print("Aiguille en protection " + __aiguilleInfos.group(1) + " à " + __PosAiguilleEquivalence[__aiguilleInfos.group(2)])
                    #Recherche de l'aiguille parcourue dans le graphe ADONF
                    __aiguilleName = "AIG_" + __aiguilleInfos.group(1)
                    if(__aiguilleName in __graphe.aiguilles):
                        if(__itineraireAjoute != None):
                            __PositionAiguilleAjoutee = PositionAiguille(__graphe.aiguilles[__aiguilleName], __PosAiguilleEquivalence[__aiguilleInfos.group(2)])
                            __itineraireAjoute.AjouterAiguilleEnProtection(__PositionAiguilleAjoutee)
                    elif(__aiguilleName + "V" in __graphe.aiguilles):
                        if(__itineraireAjoute != None):
                            __PositionAiguilleAjoutee = PositionAiguille(__graphe.aiguilles[__aiguilleName + "V"], __PosAiguilleEquivalence[__aiguilleInfos.group(2)])
                            __itineraireAjoute.AjouterAiguilleEnProtection(__PositionAiguilleAjoutee)
                    else:
                        self.PT2ADir.aiguillesIntrouvables[__aiguilleName] = __aiguilleName
                        print("Aiguille introuvable dans ADONF " + __aiguilleName)
                        __itineraireComplet = False
                elif(__aiguilleVInfos != None):
                    print("Aiguille virtuelle en protection " + __aiguilleVInfos.group(1) + " à " + __PosAiguilleEquivalence[__aiguilleVInfos.group(2)])
                elif(__taquetInfos != None):
                    print("Taquet en protection " + __taquetInfos.group(1) + " à " + __PosAiguilleEquivalence[__taquetInfos.group(2)])
                else:
                    print("Ag/taquet en protection dans aucun pattern : " + __itAiguille)
                    self.PT2ADir.patternProblems.append("(Poste : " + self.Poste.nom + " | Fichier : " + self.nomFichier + ") Aiguilles en protection (F"+str(__cleAigProt)+") : " + __itAiguille)
                    __itineraireComplet = False
                    #os.system("PAUSE")

        __zonePattern = re.compile("^[ ]*([0-9]+)(\([0-9]+\))*$")
        if(isinstance(__Pt2aExcel['F'][__cleZoneEspAuto], str)):
            __zonesEspacementAutomatique = __Pt2aExcel['F'][__cleZoneEspAuto].split(";")
            for __itZone in __zonesEspacementAutomatique:
                __zoneInfos = __zonePattern.match(__itZone)
                if(__zoneInfos != None):
                    print("Zone d'espacement automatique " + __zoneInfos.group(1))
                    #Recherche de la zone dans le graphe ADONF
                    __cdvName = "CDV_z" + __zoneInfos.group(1)
                    __tvdName = "TVD_z" + __zoneInfos.group(1)
                    if(__cdvName not in __graphe.CDVs and __tvdName not in __graphe.TVDs):
                        self.PT2ADir.zonesIntrouvables[__zoneInfos.group(1)] = __zoneInfos.group(1) + " (CDV+TVD)"
                        print("CDV et TVD introuvable dans ADONF " + __zoneInfos.group(1))
                        __itineraireComplet = False
                    elif(__cdvName not in __graphe.CDVs):
                        self.PT2ADir.zonesIntrouvables[__zoneInfos.group(1)] = __zoneInfos.group(1) + " (CDV)"
                        print("CDV introuvable dans ADONF " + __zoneInfos.group(1))
                        __itineraireComplet = False
                    elif(__tvdName not in __graphe.TVDs):
                        self.PT2ADir.zonesIntrouvables[__zoneInfos.group(1)] = __zoneInfos.group(1) + " (TVD)"
                        print("TVD introuvable dans ADONF " + __zoneInfos.group(1))
                        __itineraireComplet = False
                    else:
                        if(__itineraireAjoute != None):
                            __itineraireAjoute.AjouterZoneEspacementAutomatique(__graphe.TVDs[__tvdName])
                else:
                    print("zone d'espacement automatique dans aucun pattern : " + __itZone)
                    self.PT2ADir.patternProblems.append("(Poste : " + self.Poste.nom + " | Fichier : " + self.nomFichier + ") Zones (F"+str(__cleZoneEspAuto)+") : " + __itZone)
                    __itineraireComplet = False
                    #os.system("PAUSE")

        if(__itineraireComplet is True and __itineraireAjoute != None):
            self.Itineraire = __itineraireAjoute
            if(self.Itineraire.GenererSegmentsParcourus() == False):
                self.Poste.AjouterItineraire(__itineraireAjoute)


#Cette classe représente un poste d'enclenchement
class Poste:
    #@execution_time 
    def __init____disabled_YDA(self, _PT2ADir, _nom):
        logging.info("Start calling __init__")
        self.PT2ADir = _PT2ADir
        self.nom = _nom
        self.PT2ADoc = []
        self.itineraires = []

    #@execution_time 
    def OuvrirPT2A__disabled_YDA(self):
        logging.info("Start calling OuvrirPT2A")
        __patternPT2AIti = re.compile("^2A(1|2)-([0-9]+).(?:xlsx?|csv)$")
        __PosteDir = self.PT2ADir.nomDir + self.nom + "\\"
        __listDirPoste = os.listdir(__PosteDir)
        for __f in __listDirPoste:
            print(__PosteDir + __f)
            if(os.path.isfile(__PosteDir + __f) and __patternPT2AIti.match(__f)):
                print("Ouverture")
                __PieceAjoutee = PT2ADoc(self, __PosteDir, __f, self.PT2ADir)
                self.PT2ADoc.append(__PieceAjoutee)
                __PieceAjoutee.Ouvrir()

    #@execution_time 
    def OuvrirPT2B__disabled_YDA(self):
        logging.info("Start calling OuvrirPT2B")
        __patternPT2BAu = re.compile("^2B([0-9]+).xls$")
        __PosteDir = self.PT2ADir.nomDir + self.nom + "\\"
        __listDirPoste = os.listdir(__PosteDir)
        for __f in __listDirPoste:
            if(os.path.isfile(__PosteDir + __f) and __patternPT2BAu.match(__f)):
                __PieceAjoutee = PT2BDoc(self, __PosteDir, __f, self.PT2ADir)
                self.PT2ADoc.append(__PieceAjoutee)
                __PieceAjoutee.Ouvrir()

    #@execution_time 
    def AjouterItineraire__disabled_YDA(self, _itineraire):
        logging.info("Start calling AjouterItineraire")
        self.itineraires.append(_itineraire)

class Autorisation:
    #@execution_time 
    def __init____disabled_YDA(self, _mvtType, _mvtPointA, _mvtPointB, _PT2BDoc):
        logging.info("Start calling __init__")
        self.nom = _nom
        self.mvtType = _mvtType
        self.mvtPointA = _mvtPointA
        self.mvtPointB = _mvtPointB
        self.PT2BDoc = _PT2BDoc
        self.mode = ""
        self.aiguillesParcourues = []
        self.aiguillesEnProtection = []
        self.segmentsParcourusCroissant = []
        self.aiguillesParcouruesOrdonneCroissant = []
        self.segmentsParcourusDecroissant = []
        self.aiguillesParcouruesOrdonneDecroissant = []

    #@execution_time 
    def AjouterAiguilleParcourue__disabled_YDA(self, _aiguille):
        logging.info("Start calling AjouterAiguilleParcourue")
        self.aiguillesParcourues.append(_aiguille)

    #@execution_time 
    def AjouterAiguilleEnProtection__disabled_YDA(self, _aiguille):
        logging.info("Start calling AjouterAiguilleEnProtection")
        self.aiguillesEnProtection.append(_aiguille)

    #Recherche la position d'une aiguille parcourue
    #@execution_time 
    def PositionAiguilleParcourue__disabled_YDA(self, _aiguille):
        logging.info("Start calling PositionAiguilleParcourue")
        for i in self.aiguillesParcourues:
            if(i.aiguille is _aiguille):
                return i.position
        return None

    #Cette méthode permet de générer l'ensemble des segments parcourus sur l'itinéraire
    #A COMPLETER
    #@execution_time 
    def GenererSegmentsParcourus__disabled_YDA(self):
        logging.info("Start calling GenererSegmentsParcourus")
        SegmentSuivant = self.origine.segment
        SensParcoursSegment = self.origine.sens
        SegmentParcouru = ParcoursSegment(SegmentSuivant, SensParcoursSegment)
        self.segmentsParcourus.append(SegmentParcouru)
        error = False
        graphe = GrapheSingleton()
        #TO FIX : Ne fonctionne que si pas de point de dépolarisation entre deux segments
        while(SegmentSuivant is not None and error is False):
            if(SegmentSuivant is not None):
                print(SegmentSuivant.nom)
            if(SensParcoursSegment == "CROISSANT"):
                if(SegmentSuivant.segment1VoisinAmont is not None and SegmentSuivant.segment2VoisinAmont is not None):
                    AiguilleParcourue = graphe.RechercherAiguilleAvecSegments(SegmentSuivant, SegmentSuivant.segment1VoisinAmont, SegmentSuivant.segment2VoisinAmont)
                    if(AiguilleParcourue is not None):
                        PositionAiguilleParcourue = self.PositionAiguilleParcourue(AiguilleParcourue)
                        if(PositionAiguilleParcourue is not None and (PositionAiguilleParcourue is "Gauche" or PositionAiguilleParcourue is "Droite" or PositionAiguilleParcourue is "Renversee" or PositionAiguilleParcourue is "Normale")):
                            if(AiguilleParcourue not in self.aiguillesParcouruesOrdonne):
                                self.aiguillesParcouruesOrdonne.append(AiguilleParcourue)
                            #Aiguille Parcourue par un talon, allant à la pointe
                            if(SegmentSuivant is AiguilleParcourue.segTalonGauche):
                                SegmentSuivant = AiguilleParcourue.segPointe
                                SegmentParcouru = ParcoursSegment(SegmentSuivant, SensParcoursSegment)
                                self.segmentsParcourus.append(SegmentParcouru)
                            else:
                                SegmentSuivant = AiguilleParcourue.segPointe
                                SegmentParcouru = ParcoursSegment(SegmentSuivant, SensParcoursSegment)
                                self.segmentsParcourus.append(SegmentParcouru)
                elif(SegmentSuivant.segment1VoisinAval != None and SegmentSuivant.segment2VoisinAval == None):
                    SegmentSuivant = SegmentSuivant.segment1VoisinAval
                    SegmentParcouru = ParcoursSegment(SegmentSuivant, SensParcoursSegment)
                    self.segmentsParcourus.append(SegmentParcouru)
                elif(SegmentSuivant.segment1VoisinAval == None and SegmentSuivant.segment2VoisinAval != None):
                    SegmentSuivant = SegmentSuivant.segment2VoisinAval
                    SegmentParcouru = ParcoursSegment(SegmentSuivant, SensParcoursSegment)
                    self.segmentsParcourus.append(SegmentParcouru)
                elif(SegmentSuivant.segment1VoisinAval != None and SegmentSuivant.segment2VoisinAval != None):
                    AiguilleParcourue = graphe.RechercherAiguilleAvecSegments(SegmentSuivant, SegmentSuivant.segment1VoisinAval, SegmentSuivant.segment2VoisinAval)
                    if(AiguilleParcourue is not None):
                        PositionAiguilleParcourue = self.PositionAiguilleParcourue(AiguilleParcourue)
                        if(PositionAiguilleParcourue is not None and (PositionAiguilleParcourue is "Gauche" or PositionAiguilleParcourue is "Droite" or PositionAiguilleParcourue is "Renversee" or PositionAiguilleParcourue is "Normale")):
                            if(AiguilleParcourue not in self.aiguillesParcouruesOrdonne):
                                self.aiguillesParcouruesOrdonne.append(AiguilleParcourue)
                            #Aiguille Parcourue par la pointe, pouvant aller au talon gauche ou droite
                            if(SegmentSuivant is AiguilleParcourue.segPointe):
                                if(PositionAiguilleParcourue == "Gauche"):
                                    SegmentSuivant = AiguilleParcourue.segTalonGauche
                                    SegmentParcouru = ParcoursSegment(SegmentSuivant, SensParcoursSegment)
                                    self.segmentsParcourus.append(SegmentParcouru)
                                elif(PositionAiguilleParcourue == "Renversee"):
                                    if(AiguilleParcourue.posDirecte == "GAUCHE"):
                                        SegmentSuivant = AiguilleParcourue.segTalonDroite
                                        SegmentParcouru = ParcoursSegment(SegmentSuivant, SensParcoursSegment)
                                        self.segmentsParcourus.append(SegmentParcouru)
                                    else:
                                        SegmentSuivant = AiguilleParcourue.segTalonGauche
                                        SegmentParcouru = ParcoursSegment(SegmentSuivant, SensParcoursSegment)
                                        self.segmentsParcourus.append(SegmentParcouru)
                                elif(PositionAiguilleParcourue == "Normale"):
                                    if(AiguilleParcourue.posDirecte == "DROITE"):
                                        SegmentSuivant = AiguilleParcourue.segTalonDroite
                                        SegmentParcouru = ParcoursSegment(SegmentSuivant, SensParcoursSegment)
                                        self.segmentsParcourus.append(SegmentParcouru)
                                    else:
                                        SegmentSuivant = AiguilleParcourue.segTalonGauche
                                        SegmentParcouru = ParcoursSegment(SegmentSuivant, SensParcoursSegment)
                                        self.segmentsParcourus.append(SegmentParcouru)
                                else:
                                    SegmentSuivant = AiguilleParcourue.segTalonDroite
                                    SegmentParcouru = ParcoursSegment(SegmentSuivant, SensParcoursSegment)
                                    self.segmentsParcourus.append(SegmentParcouru)
                            #Aiguille Parcourue par un talon, arrivant à la pointe
                            else:
                                SegmentSuivant = AiguilleParcourue.segPointe
                                SegmentParcouru = ParcoursSegment(SegmentSuivant, SensParcoursSegment)
                                self.segmentsParcourus.append(SegmentParcouru)
                        else:
                            SegmentSuivant = None
                    else:
                        print("GenererSegmentsParcourus impossible : AiguilleParcourue = graphe.RechercherAiguilleAvecSegments == None")
                        print("segments : " + SegmentSuivant.nom + "," + SegmentSuivant.segment1VoisinAval.nom + "," + SegmentSuivant.segment2VoisinAval.nom)
                        error = True
                        os.system("PAUSE")
                else:
                    print("GenererSegmentsParcourus impossible : SegmentSuivant.segment1VoisinAval == None and SegmentSuivant.segment2VoisinAval == None")
                    print("SegmentSuivant = " + SegmentSuivant.nom)
                    error = True
                    os.system("PAUSE")

            #Parcours dans le sens décroissant du segment
            else:
                if(SegmentSuivant.segment1VoisinAval is not None and SegmentSuivant.segment2VoisinAval is not None):
                    AiguilleDeConvergence = graphe.RechercherAiguilleAvecSegments(SegmentSuivant, SegmentSuivant.segment1VoisinAval, SegmentSuivant.segment2VoisinAval)
                    PositionAiguilleParcourue = self.PositionAiguilleParcourue(AiguilleDeConvergence)
                    if(AiguilleDeConvergence is not None and AiguilleDeConvergence not in self.aiguillesParcouruesOrdonne and (PositionAiguilleParcourue is "Gauche" or PositionAiguilleParcourue is "Droite")):
                        self.aiguillesParcouruesOrdonne.append(AiguilleDeConvergence)
                if(SegmentSuivant.segment1VoisinAmont != None and SegmentSuivant.segment2VoisinAmont == None):
                    SegmentSuivant = SegmentSuivant.segment1VoisinAmont
                    SegmentParcouru = ParcoursSegment(SegmentSuivant, SensParcoursSegment)
                    self.segmentsParcourus.append(SegmentParcouru)
                elif(SegmentSuivant.segment1VoisinAmont == None and SegmentSuivant.segment2VoisinAmont != None):
                    SegmentSuivant = SegmentSuivant.segment2VoisinAmont
                    SegmentParcouru = ParcoursSegment(SegmentSuivant, SensParcoursSegment)
                    self.segmentsParcourus.append(SegmentParcouru)
                elif(SegmentSuivant.segment1VoisinAmont != None and SegmentSuivant.segment2VoisinAmont != None):
                    AiguilleParcourue = graphe.RechercherAiguilleAvecSegments(SegmentSuivant, SegmentSuivant.segment1VoisinAmont, SegmentSuivant.segment2VoisinAmont)
                    if(AiguilleParcourue is not None):
                        PositionAiguilleParcourue = self.PositionAiguilleParcourue(AiguilleParcourue)
                        if(PositionAiguilleParcourue is not None and (PositionAiguilleParcourue is "Gauche" or PositionAiguilleParcourue is "Droite" or PositionAiguilleParcourue is "Renversee" or PositionAiguilleParcourue is "Normale")):
                            if(AiguilleParcourue not in self.aiguillesParcouruesOrdonne):
                                self.aiguillesParcouruesOrdonne.append(AiguilleParcourue)
                            #Aiguille Parcourue par la pointe, pouvant aller au talon gauche ou droite
                            if(SegmentSuivant is AiguilleParcourue.segPointe):
                                if(PositionAiguilleParcourue == "Gauche"):
                                    SegmentSuivant = AiguilleParcourue.segTalonGauche
                                    SegmentParcouru = ParcoursSegment(SegmentSuivant, SensParcoursSegment)
                                    self.segmentsParcourus.append(SegmentParcouru)
                                elif(PositionAiguilleParcourue == "Renversee"):
                                    if(AiguilleParcourue.posDirecte == "GAUCHE"):
                                        SegmentSuivant = AiguilleParcourue.segTalonDroite
                                        SegmentParcouru = ParcoursSegment(SegmentSuivant, SensParcoursSegment)
                                        self.segmentsParcourus.append(SegmentParcouru)
                                    else:
                                        SegmentSuivant = AiguilleParcourue.segTalonGauche
                                        SegmentParcouru = ParcoursSegment(SegmentSuivant, SensParcoursSegment)
                                        self.segmentsParcourus.append(SegmentParcouru)
                                elif(PositionAiguilleParcourue == "Normale"):
                                    if(AiguilleParcourue.posDirecte == "DROITE"):
                                        SegmentSuivant = AiguilleParcourue.segTalonDroite
                                        SegmentParcouru = ParcoursSegment(SegmentSuivant, SensParcoursSegment)
                                        self.segmentsParcourus.append(SegmentParcouru)
                                    else:
                                        SegmentSuivant = AiguilleParcourue.segTalonGauche
                                        SegmentParcouru = ParcoursSegment(SegmentSuivant, SensParcoursSegment)
                                        self.segmentsParcourus.append(SegmentParcouru)
                                else:
                                    SegmentSuivant = AiguilleParcourue.segTalonDroite
                                    SegmentParcouru = ParcoursSegment(SegmentSuivant, SensParcoursSegment)
                                    self.segmentsParcourus.append(SegmentParcouru)
                            #Aiguille Parcourue par un talon, arrivant à la pointe
                            else:
                                SegmentSuivant = AiguilleParcourue.segPointe
                                SegmentParcouru = ParcoursSegment(SegmentSuivant, SensParcoursSegment)
                                self.segmentsParcourus.append(SegmentParcouru)
                        else:
                            print("GenererSegmentsParcourus impossible : AiguilleParcourue pas dans self.aiguillesParcourues")
                            print("AiguilleParcourue = "  + AiguilleParcourue.nom)
                            error = True
                            os.system("PAUSE")
                    else:
                        print("GenererSegmentsParcourus impossible : AiguilleParcourue = graphe.RechercherAiguilleAvecSegments == None")
                        print("segments : " + SegmentSuivant.nom + "," + SegmentSuivant.segment1VoisinAmont.nom + "," + SegmentSuivant.segment2VoisinAmont.nom)
                        error = True
                        os.system("PAUSE")
                else:
                    print("GenererSegmentsParcourus impossible : SegmentSuivant.segment1VoisinAmont == None and SegmentSuivant.segment2VoisinAmont == None")
                    print("SegmentSuivant = " + SegmentSuivant.nom)
                    error = True
                    os.system("PAUSE")
                if(SegmentSuivant.segment1VoisinAval is not None and SegmentSuivant.segment2VoisinAval is not None):
                    AiguilleDeConvergence = graphe.RechercherAiguilleAvecSegments(SegmentSuivant, SegmentSuivant.segment1VoisinAval, SegmentSuivant.segment2VoisinAval)
                    PositionAiguilleParcourue = self.PositionAiguilleParcourue(AiguilleDeConvergence)
                    if(AiguilleDeConvergence is not None and AiguilleDeConvergence not in self.aiguillesParcouruesOrdonne and (PositionAiguilleParcourue is "Gauche" or PositionAiguilleParcourue is "Droite")):
                        self.aiguillesParcouruesOrdonne.append(AiguilleDeConvergence)

        return error

#Cette classe représente un itinéraire
class Itineraire:
    #@execution_time 
    def __init____disabled_YDA(self, _nom, _origine, _destination, _jalons, _PT2ADoc):
        logging.info("Start calling __init__")
        self.nom = _nom
        self.origine = _origine
        self.destination = _destination
        self.jalons = _jalons
        self.PT2ADoc = _PT2ADoc
        self.mode = ""
        self.aiguillesParcourues = []
        self.aiguillesEnProtection = []
        self.zonesEspacementAutomatique = []
        self.segmentsParcourus = []
        self.aiguillesParcouruesOrdonne = []
        self.noeudsGrapheTransitionsParcourus = []
        self.nonAmbiguousGrapheTransitionsParcourus = []

    #@execution_time 
    def AjouterAiguilleParcourue__disabled_YDA(self, _aiguille):
        logging.info("Start calling AjouterAiguilleParcourue")
        self.aiguillesParcourues.append(_aiguille)

    #@execution_time 
    def AjouterAiguilleEnProtection__disabled_YDA(self, _aiguille):
        logging.info("Start calling AjouterAiguilleEnProtection")
        self.aiguillesEnProtection.append(_aiguille)

    #@execution_time 
    def AjouterZoneEspacementAutomatique__disabled_YDA(self, _tvd):
        logging.info("Start calling AjouterZoneEspacementAutomatique")
        self.zonesEspacementAutomatique.append(_tvd)

    #Recherche la position d'une aiguille parcourue
    #@execution_time 
    def PositionAiguilleParcourue__disabled_YDA(self, _aiguille):
        logging.info("Start calling PositionAiguilleParcourue")
        for i in self.aiguillesParcourues:
            if(i.aiguille is _aiguille):
                return i.position
        return None

    #Cette méthode permet de générer l'ensemble des segments parcourus sur l'itinéraire
    #@execution_time 
    def GenererSegmentsParcourus__disabled_YDA(self):
        logging.info("Start calling GenererSegmentsParcourus")
        SegmentSuivant = self.origine.segment
        SensParcoursSegment = self.origine.sens
        SegmentParcouru = ParcoursSegment(SegmentSuivant, SensParcoursSegment)
        self.segmentsParcourus.append(SegmentParcouru)
        error = False
        graphe = GrapheSingleton()
        #TO FIX : Ne fonctionne que si pas de point de dépolarisation entre deux segments
        while(SegmentSuivant is not self.destination.segment and error is False):
            if(SegmentSuivant is not None):
                print(SegmentSuivant.nom)
            if(SensParcoursSegment == "CROISSANT"):
                if(SegmentSuivant.segment1VoisinAmont is not None and SegmentSuivant.segment2VoisinAmont is not None):
                    AiguilleDeConvergence = graphe.RechercherAiguilleAvecSegments(SegmentSuivant, SegmentSuivant.segment1VoisinAmont, SegmentSuivant.segment2VoisinAmont)
                    PositionAiguilleParcourue = self.PositionAiguilleParcourue(AiguilleDeConvergence)
                    if(AiguilleDeConvergence is not None and AiguilleDeConvergence not in self.aiguillesParcouruesOrdonne and (PositionAiguilleParcourue is "Gauche" or PositionAiguilleParcourue is "Droite")):
                        self.aiguillesParcouruesOrdonne.append(AiguilleDeConvergence)
                if(SegmentSuivant.segment1VoisinAval != None and SegmentSuivant.segment2VoisinAval == None):
                    SegmentSuivant = SegmentSuivant.segment1VoisinAval
                    SegmentParcouru = ParcoursSegment(SegmentSuivant, SensParcoursSegment)
                    self.segmentsParcourus.append(SegmentParcouru)
                elif(SegmentSuivant.segment1VoisinAval == None and SegmentSuivant.segment2VoisinAval != None):
                    SegmentSuivant = SegmentSuivant.segment2VoisinAval
                    SegmentParcouru = ParcoursSegment(SegmentSuivant, SensParcoursSegment)
                    self.segmentsParcourus.append(SegmentParcouru)
                elif(SegmentSuivant.segment1VoisinAval != None and SegmentSuivant.segment2VoisinAval != None):
                    AiguilleParcourue = graphe.RechercherAiguilleAvecSegments(SegmentSuivant, SegmentSuivant.segment1VoisinAval, SegmentSuivant.segment2VoisinAval)
                    if(AiguilleParcourue is not None):
                        PositionAiguilleParcourue = self.PositionAiguilleParcourue(AiguilleParcourue)
                        if(PositionAiguilleParcourue is not None and (PositionAiguilleParcourue is "Gauche" or PositionAiguilleParcourue is "Droite" or PositionAiguilleParcourue is "Renversee" or PositionAiguilleParcourue is "Normale")):
                            if(AiguilleParcourue not in self.aiguillesParcouruesOrdonne):
                                self.aiguillesParcouruesOrdonne.append(AiguilleParcourue)
                            #Aiguille Parcourue par la pointe, pouvant aller au talon gauche ou droite
                            if(SegmentSuivant is AiguilleParcourue.segPointe):
                                if(PositionAiguilleParcourue == "Gauche"):
                                    SegmentSuivant = AiguilleParcourue.segTalonGauche
                                    SegmentParcouru = ParcoursSegment(SegmentSuivant, SensParcoursSegment)
                                    self.segmentsParcourus.append(SegmentParcouru)
                                elif(PositionAiguilleParcourue == "Renversee"):
                                    if(AiguilleParcourue.posDirecte == "GAUCHE"):
                                        SegmentSuivant = AiguilleParcourue.segTalonDroite
                                        SegmentParcouru = ParcoursSegment(SegmentSuivant, SensParcoursSegment)
                                        self.segmentsParcourus.append(SegmentParcouru)
                                    else:
                                        SegmentSuivant = AiguilleParcourue.segTalonGauche
                                        SegmentParcouru = ParcoursSegment(SegmentSuivant, SensParcoursSegment)
                                        self.segmentsParcourus.append(SegmentParcouru)
                                elif(PositionAiguilleParcourue == "Normale"):
                                    if(AiguilleParcourue.posDirecte == "DROITE"):
                                        SegmentSuivant = AiguilleParcourue.segTalonDroite
                                        SegmentParcouru = ParcoursSegment(SegmentSuivant, SensParcoursSegment)
                                        self.segmentsParcourus.append(SegmentParcouru)
                                    else:
                                        SegmentSuivant = AiguilleParcourue.segTalonGauche
                                        SegmentParcouru = ParcoursSegment(SegmentSuivant, SensParcoursSegment)
                                        self.segmentsParcourus.append(SegmentParcouru)
                                else:
                                    SegmentSuivant = AiguilleParcourue.segTalonDroite
                                    SegmentParcouru = ParcoursSegment(SegmentSuivant, SensParcoursSegment)
                                    self.segmentsParcourus.append(SegmentParcouru)
                            #Aiguille Parcourue par un talon, arrivant à la pointe
                            else:
                                SegmentSuivant = AiguilleParcourue.segPointe
                                SegmentParcouru = ParcoursSegment(SegmentSuivant, SensParcoursSegment)
                                self.segmentsParcourus.append(SegmentParcouru)
                        else:
                            print("GenererSegmentsParcourus impossible : AiguilleParcourue pas dans self.aiguillesParcourues")
                            print("AiguilleParcourue = "  + AiguilleParcourue.nom)
                            error = True
                            os.system("PAUSE")
                    else:
                        print("GenererSegmentsParcourus impossible : AiguilleParcourue = graphe.RechercherAiguilleAvecSegments == None")
                        print("segments : " + SegmentSuivant.nom + "," + SegmentSuivant.segment1VoisinAval.nom + "," + SegmentSuivant.segment2VoisinAval.nom)
                        error = True
                        os.system("PAUSE")
                else:
                    print("GenererSegmentsParcourus impossible : SegmentSuivant.segment1VoisinAval == None and SegmentSuivant.segment2VoisinAval == None")
                    print("SegmentSuivant = " + SegmentSuivant.nom)
                    error = True
                    os.system("PAUSE")
                if(SegmentSuivant.segment1VoisinAmont is not None and SegmentSuivant.segment2VoisinAmont is not None):
                    AiguilleDeConvergence = graphe.RechercherAiguilleAvecSegments(SegmentSuivant, SegmentSuivant.segment1VoisinAmont, SegmentSuivant.segment2VoisinAmont)
                    PositionAiguilleParcourue = self.PositionAiguilleParcourue(AiguilleDeConvergence)
                    if(AiguilleDeConvergence is not None and AiguilleDeConvergence not in self.aiguillesParcouruesOrdonne and (PositionAiguilleParcourue is "Gauche" or PositionAiguilleParcourue is "Droite")):
                        self.aiguillesParcouruesOrdonne.append(AiguilleDeConvergence)

            #Parcours dans le sens décroissant du segment
            else:
                if(SegmentSuivant.segment1VoisinAval is not None and SegmentSuivant.segment2VoisinAval is not None):
                    AiguilleDeConvergence = graphe.RechercherAiguilleAvecSegments(SegmentSuivant, SegmentSuivant.segment1VoisinAval, SegmentSuivant.segment2VoisinAval)
                    PositionAiguilleParcourue = self.PositionAiguilleParcourue(AiguilleDeConvergence)
                    if(AiguilleDeConvergence is not None and AiguilleDeConvergence not in self.aiguillesParcouruesOrdonne and (PositionAiguilleParcourue is "Gauche" or PositionAiguilleParcourue is "Droite")):
                        self.aiguillesParcouruesOrdonne.append(AiguilleDeConvergence)
                if(SegmentSuivant.segment1VoisinAmont != None and SegmentSuivant.segment2VoisinAmont == None):
                    SegmentSuivant = SegmentSuivant.segment1VoisinAmont
                    SegmentParcouru = ParcoursSegment(SegmentSuivant, SensParcoursSegment)
                    self.segmentsParcourus.append(SegmentParcouru)
                elif(SegmentSuivant.segment1VoisinAmont == None and SegmentSuivant.segment2VoisinAmont != None):
                    SegmentSuivant = SegmentSuivant.segment2VoisinAmont
                    SegmentParcouru = ParcoursSegment(SegmentSuivant, SensParcoursSegment)
                    self.segmentsParcourus.append(SegmentParcouru)
                elif(SegmentSuivant.segment1VoisinAmont != None and SegmentSuivant.segment2VoisinAmont != None):
                    AiguilleParcourue = graphe.RechercherAiguilleAvecSegments(SegmentSuivant, SegmentSuivant.segment1VoisinAmont, SegmentSuivant.segment2VoisinAmont)
                    if(AiguilleParcourue is not None):
                        PositionAiguilleParcourue = self.PositionAiguilleParcourue(AiguilleParcourue)
                        if(PositionAiguilleParcourue is not None and (PositionAiguilleParcourue is "Gauche" or PositionAiguilleParcourue is "Droite" or PositionAiguilleParcourue is "Renversee" or PositionAiguilleParcourue is "Normale")):
                            if(AiguilleParcourue not in self.aiguillesParcouruesOrdonne):
                                self.aiguillesParcouruesOrdonne.append(AiguilleParcourue)
                            #Aiguille Parcourue par la pointe, pouvant aller au talon gauche ou droite
                            if(SegmentSuivant is AiguilleParcourue.segPointe):
                                if(PositionAiguilleParcourue == "Gauche"):
                                    SegmentSuivant = AiguilleParcourue.segTalonGauche
                                    SegmentParcouru = ParcoursSegment(SegmentSuivant, SensParcoursSegment)
                                    self.segmentsParcourus.append(SegmentParcouru)
                                elif(PositionAiguilleParcourue == "Renversee"):
                                    if(AiguilleParcourue.posDirecte == "GAUCHE"):
                                        SegmentSuivant = AiguilleParcourue.segTalonDroite
                                        SegmentParcouru = ParcoursSegment(SegmentSuivant, SensParcoursSegment)
                                        self.segmentsParcourus.append(SegmentParcouru)
                                    else:
                                        SegmentSuivant = AiguilleParcourue.segTalonGauche
                                        SegmentParcouru = ParcoursSegment(SegmentSuivant, SensParcoursSegment)
                                        self.segmentsParcourus.append(SegmentParcouru)
                                elif(PositionAiguilleParcourue == "Normale"):
                                    if(AiguilleParcourue.posDirecte == "DROITE"):
                                        SegmentSuivant = AiguilleParcourue.segTalonDroite
                                        SegmentParcouru = ParcoursSegment(SegmentSuivant, SensParcoursSegment)
                                        self.segmentsParcourus.append(SegmentParcouru)
                                    else:
                                        SegmentSuivant = AiguilleParcourue.segTalonGauche
                                        SegmentParcouru = ParcoursSegment(SegmentSuivant, SensParcoursSegment)
                                        self.segmentsParcourus.append(SegmentParcouru)
                                else:
                                    SegmentSuivant = AiguilleParcourue.segTalonDroite
                                    SegmentParcouru = ParcoursSegment(SegmentSuivant, SensParcoursSegment)
                                    self.segmentsParcourus.append(SegmentParcouru)
                            #Aiguille Parcourue par un talon, arrivant à la pointe
                            else:
                                SegmentSuivant = AiguilleParcourue.segPointe
                                SegmentParcouru = ParcoursSegment(SegmentSuivant, SensParcoursSegment)
                                self.segmentsParcourus.append(SegmentParcouru)
                        else:
                            print("GenererSegmentsParcourus impossible : AiguilleParcourue pas dans self.aiguillesParcourues")
                            print("AiguilleParcourue = "  + AiguilleParcourue.nom)
                            error = True
                            os.system("PAUSE")
                    else:
                        print("GenererSegmentsParcourus impossible : AiguilleParcourue = graphe.RechercherAiguilleAvecSegments == None")
                        print("segments : " + SegmentSuivant.nom + "," + SegmentSuivant.segment1VoisinAmont.nom + "," + SegmentSuivant.segment2VoisinAmont.nom)
                        error = True
                        os.system("PAUSE")
                else:
                    print("GenererSegmentsParcourus impossible : SegmentSuivant.segment1VoisinAmont == None and SegmentSuivant.segment2VoisinAmont == None")
                    print("SegmentSuivant = " + SegmentSuivant.nom)
                    error = True
                    os.system("PAUSE")
                if(SegmentSuivant.segment1VoisinAval is not None and SegmentSuivant.segment2VoisinAval is not None):
                    AiguilleDeConvergence = graphe.RechercherAiguilleAvecSegments(SegmentSuivant, SegmentSuivant.segment1VoisinAval, SegmentSuivant.segment2VoisinAval)
                    PositionAiguilleParcourue = self.PositionAiguilleParcourue(AiguilleDeConvergence)
                    if(AiguilleDeConvergence is not None and AiguilleDeConvergence not in self.aiguillesParcouruesOrdonne and (PositionAiguilleParcourue is "Gauche" or PositionAiguilleParcourue is "Droite")):
                        self.aiguillesParcouruesOrdonne.append(AiguilleDeConvergence)

        return error

    #@execution_time 
    def InsererInNoeudsGrapheTransitionsParcourus__disabled_YDA(self, node, sens):
        logging.info("Start calling InsererInNoeudsGrapheTransitionsParcourus")
        insere = False
        i = 0
        lastOfSegment = None
        for n in self.noeudsGrapheTransitionsParcourus:
            if(n.segment==node.segment and insere == False):
                if(sens=="CROISSANT"):
                    if(node.abs < n.abs):
                        self.noeudsGrapheTransitionsParcourus.insert(i,node)
                        print("insere")
                        insere = True
                else:
                    if(node.abs > n.abs):
                        self.noeudsGrapheTransitionsParcourus.insert(i,node)
                        print("insere")
                        insere = True
                lastOfSegment = i
            i = i + 1

        if(insere == False):
            if(lastOfSegment != None):
                self.noeudsGrapheTransitionsParcourus.insert(lastOfSegment+1,node)
                print("insere")
            else:
                self.noeudsGrapheTransitionsParcourus.append(node)
                print("insere")

    #@execution_time 
    def InsererNonAmbiguousInNoeudsGrapheTransitionsParcourus__disabled_YDA(self, node, sens):
        logging.info("Start calling InsererNonAmbiguousInNoeudsGrapheTransitionsParcourus")
        insere = False
        i = 0
        lastOfSegment = None
        for n in self.nonAmbiguousGrapheTransitionsParcourus:
            if(n.segment==node.segment and insere == False):
                if(sens=="CROISSANT"):
                    if(node.abs < n.abs):
                        self.nonAmbiguousGrapheTransitionsParcourus.insert(i,node)
                        insere = True
                else:
                    if(node.abs > n.abs):
                        self.nonAmbiguousGrapheTransitionsParcourus.insert(i,node)
                        insere = True
                lastOfSegment = i
            i = i + 1

        if(insere == False):
            if(lastOfSegment != None):
                self.nonAmbiguousGrapheTransitionsParcourus.insert(lastOfSegment+1,node)
            else:
                self.nonAmbiguousGrapheTransitionsParcourus.insert(0,node)

    #@execution_time 
    def GenererNoeudsGrapheTransitionsParcourus__disabled_YDA(self):
        logging.info("Start calling GenererNoeudsGrapheTransitionsParcourus")
        graphe = GrapheSingleton()
        sens = self.origine.sens

        #même sens que signal
        firstSegment = self.segmentsParcourus[0].segment
        continuer = True
        previousSegments = []
        nextSegment = firstSegment
        previousSegments.append(nextSegment)
        while(continuer == True):
            if(sens == "CROISSANT"):
                if(nextSegment.segment1VoisinAmont != None and nextSegment.segment2VoisinAmont == None):
                    nextSegment = nextSegment.segment1VoisinAmont
                    previousSegments.append(nextSegment)
                elif(nextSegment.segment1VoisinAmont == None and nextSegment.segment2VoisinAmont != None):
                    nextSegment = nextSegment.segment2VoisinAmont
                    previousSegments.append(nextSegment)
                else:
                    continuer = False
            elif(sens == "DECROISSANT"):
                if(nextSegment.segment1VoisinAval != None and nextSegment.segment2VoisinAval == None):
                    nextSegment = nextSegment.segment1VoisinAval
                    previousSegments.append(nextSegment)
                elif(nextSegment.segment1VoisinAval == None and nextSegment.segment2VoisinAval != None):
                    nextSegment = nextSegment.segment2VoisinAval
                    previousSegments.append(nextSegment)
                else:
                    continuer = False

        segAfterLastSeg = []
        nextSegment = self.segmentsParcourus[-1].segment
        firstNext = self.segmentsParcourus[-1].segment
        segAfterLastSeg.append(nextSegment)
        continuer = True
        while(continuer == True):
            if(sens == "CROISSANT"):
                if(nextSegment.segment1VoisinAval != None and nextSegment.segment2VoisinAval == None):
                    nextSegment = nextSegment.segment1VoisinAval
                    segAfterLastSeg.append(nextSegment)
                elif(nextSegment.segment1VoisinAval == None and nextSegment.segment2VoisinAval != None):
                    nextSegment = nextSegment.segment2VoisinAval
                    segAfterLastSeg.append(nextSegment)
                else:
                    continuer = False
            elif(sens == "DECROISSANT"):
                if(nextSegment.segment1VoisinAmont != None and nextSegment.segment2VoisinAmont == None):
                    nextSegment = nextSegment.segment1VoisinAmont
                    segAfterLastSeg.append(nextSegment)
                elif(nextSegment.segment1VoisinAmont == None and nextSegment.segment2VoisinAmont != None):
                    nextSegment = nextSegment.segment2VoisinAmont
                    segAfterLastSeg.append(nextSegment)
                else:
                    continuer = False

        for segPar in self.segmentsParcourus:
            for node in graphe.pointsDeControle.values():
                if((node.isPointOptimisation or node.isCheckPoint) and segPar.segment == node.segment):
                    # if(self.nom=="8333-8503/2"):
                    #     print("")
                    #     if(node.isPointOptimisation):
                    #         print(node.nomPointOptimisation)
                    #     if(node.isCheckPoint):
                    #         print(node.nomCheckPoint)
                    if((node.isPTES and ((node.PTESType == "IN" or node.PTESType == "OUT") and node.sensPriviligie == sens) or node.PTESType == "INOUT") or node.isPTES == False):
                        if(sens == "CROISSANT" and node.segment == self.origine.segment and node.segment == self.destination.segment and (node.abs > self.origine.abs and node.abs < self.destination.abs)):
                            self.InsererInNoeudsGrapheTransitionsParcourus(node, sens)
                            print("case 1")
                        elif(sens == "DECROISSANT" and node.segment == self.origine.segment and node.segment == self.destination.segment and (node.abs < self.origine.abs and node.abs > self.destination.abs)):
                            self.InsererInNoeudsGrapheTransitionsParcourus(node, sens)
                            print("case 2")
                        elif(sens == "CROISSANT" and (node.segment == self.origine.segment) and (node.abs > self.origine.abs)):
                            self.InsererInNoeudsGrapheTransitionsParcourus(node, sens)
                            print("case 3")
                        elif(sens == "DECROISSANT" and (node.segment == self.origine.segment) and (node.abs < self.origine.abs)):
                            self.InsererInNoeudsGrapheTransitionsParcourus(node, sens)
                            print("case 4")
                        elif(sens == "CROISSANT" and node.segment == self.destination.segment and (node.abs < self.destination.abs)):
                            self.InsererInNoeudsGrapheTransitionsParcourus(node, sens)
                            print("case 5")
                        elif(sens == "DECROISSANT" and node.segment == self.destination.segment and (node.abs > self.destination.abs)):
                            self.InsererInNoeudsGrapheTransitionsParcourus(node, sens)
                            print("case 6")
                        elif(node.segment != self.origine.segment and node.segment != self.destination.segment):
                            self.InsererInNoeudsGrapheTransitionsParcourus(node, sens)
                            print("case 7")

                    # if(self.nom=="8333-8503/2"):
                    #     print("Origine : " + self.origine.segment.nom + " " + str(self.origine.abs))
                    #     print("Node : " + node.segment.nom + " " + str(node.abs))
                    #     print("Destination : " + self.destination.segment.nom + " " + str(self.destination.abs))
                        #os.system("pause")
        for segPar in segAfterLastSeg:
            for node in graphe.pointsDeControle.values():
                if(node not in self.noeudsGrapheTransitionsParcourus):
                    if(node.isPTES and (node.PTESType == "OUT" or node.PTESType == "INOUT") and segPar == node.segment):
                        if((node.PTESType == "OUT" and node.sensPriviligie == sens) or node.PTESType == "INOUT"):
                            if(self.origine.sens == self.destination.sens and len(graphe.RechercherItinerairesDepuisOrigine(self.destination)) <= 0 or (self.origine.sens != self.destination.sens and segPar == firstNext)):
                                self.InsererInNoeudsGrapheTransitionsParcourus(node, sens)

        for segPar in previousSegments:
            for node in graphe.pointsDeControle.values():
                if(node not in self.noeudsGrapheTransitionsParcourus):
                    if((node.isPTES and ((node.PTESType == "IN" or node.PTESType == "OUT") and node.sensPriviligie == sens) or node.PTESType == "INOUT") or node.isPTES == False):
                        if((node.isPointOptimisation or node.isCheckPoint) and segPar == node.segment):
                            self.InsererNonAmbiguousInNoeudsGrapheTransitionsParcourus(node, sens)
        self.nonAmbiguousGrapheTransitionsParcourus = reversed(self.nonAmbiguousGrapheTransitionsParcourus)
        # if(self.nom=="2630-2484"):
        #     os.system("pause")

class PositionAiguille:
    #@execution_time 
    def __init____disabled_YDA(self, _aiguille, _position):
        logging.info("Start calling __init__")
        self.aiguille = _aiguille
        self.position = _position

    #@execution_time 
    def __eq__(self, other):
        logging.debug("Start calling __eq__")
        if self.aiguille == other.aiguille and self.position == other.position:
            return True
        else:
            return False

class ParcoursSegment:
    #@execution_time 
    def __init__(self, _segment, _sens):
        logging.debug("Start calling __init__ ParcoursSegment")
        self.segment = _segment
        self.sens = _sens

    #@execution_time 
    def __eq__(self, other):
        logging.debug("Start calling __eq__")
        if self.segment == other.segment and self.sens == other.sens:
            return True
        else:
            return False

class SimulationResultsSingleton:
    __instance = None
    #used for sure
    def __new__(cls):
        #logging.info("Start calling __new__ SimulationResultsSingleton")
        if SimulationResultsSingleton.__instance is None:
            SimulationResultsSingleton.__instance = object.__new__(cls)
            SimulationResultsSingleton.__instance.simulationResults = SimulationResults()
        return SimulationResultsSingleton.__instance.simulationResults

    #@execution_time 
    def Load(cls, _nomFichier):
        logging.info("Start calling Load")
        if SimulationResultsSingleton.__instance is None:
            SimulationResultsSingleton.__instance = object.__new__(cls)
        # f = open(_nomFichier, "rb")
        # SimulationResultsSingleton.__instance.simulationResults = pickle.load(f)
        #SimulationResultsSingleton.__instance.simulationResults = joblib.load(_nomFichier)
        #f.close()
        f = open(_nomFichier, "rb")
        SimulationResultsSingleton.__instance.simulationResults = pickle.load(f)
        f.close()
        return SimulationResultsSingleton.__instance.simulationResults


class SimulationResults:
    #@execution_time 
    def __init__(self):
        logging.info("Start calling __init__ SimulationResults")
        self.simplesRunsSimulations = []
        self.configurationSimulationsPerturbees = {}

    #used for sure 
    def AjouterSimpleRunSimulation(self, _mE, _modele, _speedRegulation):
        #logging.info("Start calling AjouterSimpleRunSimulation")
        simpleRunSimulation = SimpleRunSimulation(_mE, _modele, _speedRegulation)
        self.simplesRunsSimulations.append(simpleRunSimulation)
        return simpleRunSimulation

    #@execution_time 
    def AjouterConfigurationSimulationPerturbee__disabled_YDA(self, _key, _mE1, _modele1, _speedRegulation1, _mE2, _modele2, _speedRegulation2, _copyof):
        logging.info("Start calling AjouterConfigurationSimulationPerturbee")
        config = ConfigurationSimulationPerturbee(_key, _mE1, _modele1, _speedRegulation1, _mE2, _modele2, _speedRegulation2, _copyof)
        self.configurationSimulationsPerturbees[_key] = config
        return config

    # def Save__disabled_YDA(self, _nomFichier):
        logging.info("Start calling Save")
    #     # f = pickle.Pickler(open(_nomFichier,"wb"))
    #     # f.fast = True
    #     # f.dump(self, protocol=pickle.HIGHEST_PROTOCOL)
    #     # f.close()
    #     joblib.dump(self, _nomFichier, 0)

    #@execution_time 
    def Save__disabled_YDA(self, _nomFichier):
        logging.info("Start calling Save")
        sys.setrecursionlimit(3000)
        f = pickle.Pickler(open(_nomFichier,"wb"))
        f.dump(self)

    #@execution_time 
    def FindSimpleRunSimulation(self, mE, modeleTrain):
        logging.info("Start calling FindSimpleRunSimulation")
        for simu in self.simplesRunsSimulations:
            if(simu.mE == mE.nom and simu.modele == modeleTrain.nom):
                #print(simu.mE + "==" + mE.nom + "   " + simu.modele + "==" + modeleTrain.nom)
                #rint("found")
                return simu

        return None

    #@execution_time 
    def ExporterSimulationIntervalleEspacement__disabled_YDA(self, _nomFichier, NbObjectPerFile):
        logging.info("Start calling ExporterSimulationIntervalleEspacement")
        i = 0
        j = 1
        graphe = GrapheSingleton()
        Dict = {'ID_Simu': [], 'mE_T1': [], 'NatureTrain_T1': [],'ModeConduite_T1': [], 'SpeedRegulation_T1': [],
        'mE_T2': [], 'NatureTrain_T2': [], 'ModeConduite_T2': [], 'SpeedRegulation_T2': [], 'CopyOf': [], 'Error': [],
        'IntervalleNonPerturbe_mE': [], 'EspacementNonPerturbe_mE': [], 'IntervallePerturbe_mE': [], 'EspacementPerturbe_mE': [],
        'Transitions':[], 'IntervalleNonPerturbe_Transition': [], 'EspacementNonPerturbe_Transition': [], 'IntervallePerturbe_Transition': [], 'EspacementPerturbe_Transition': [],
        'ControlPoints': [],
        'IntervalleNonPerturbe_CP': [], 'EspacementNonPerturbe_CP': [], 'IntervallePerturbe_CP': [], 'EspacementPerturbe_CP': []}

        for simu in self.configurationSimulationsPerturbees.values():
            if(simu.intervalResults != None and (simu.intervalResults.tempsIntervalleNonPerturbeME == 'MAX_INTERVAL' or simu.intervalResults.tempsIntervalleNonPerturbeME > 0.0)):
                Dict['ID_Simu'].append(simu.key)
                Dict['mE_T1'].append(simu.mE1)
                modeleGrapheT1 = graphe.RechercherModeleTrain(simu.modele1)
                Dict['NatureTrain_T1'].append(modeleGrapheT1.nature.nom)
                Dict['ModeConduite_T1'].append(modeleGrapheT1.modeconduite)
                Dict['SpeedRegulation_T1'].append(str(simu.speedRegulation1))
                Dict['mE_T2'].append(simu.mE2)
                modeleGrapheT2 = graphe.RechercherModeleTrain(simu.modele2)
                Dict['NatureTrain_T2'].append(modeleGrapheT2.nature.nom)
                Dict['ModeConduite_T2'].append(modeleGrapheT2.modeconduite)
                Dict['SpeedRegulation_T2'].append(str(simu.speedRegulation2))
                Dict['CopyOf'].append(simu.copyof)
                Dict['Error'].append(simu.intervalResults.error)
                Dict['IntervalleNonPerturbe_mE'].append(str(simu.intervalResults.tempsIntervalleNonPerturbeME))
                Dict['EspacementNonPerturbe_mE'].append(str(simu.intervalResults.tempsEspacementNonPerturbeME))
                Dict['IntervallePerturbe_mE'].append(str(simu.intervalResults.tempsIntervallePerturbeME))
                Dict['EspacementPerturbe_mE'].append(str(simu.intervalResults.tempsEspacementPerturbeME))

                for transition in simu.intervalResults.transitions:
                    Dict['Transitions'].append(transition.transition)
                    Dict['IntervalleNonPerturbe_Transition'].append(str(transition.intervalleNonPerturbe))
                    Dict['EspacementNonPerturbe_Transition'].append(str(transition.espacementNonPerturbe))
                    Dict['IntervallePerturbe_Transition'].append(str(transition.intervallePerturbe))
                    Dict['EspacementPerturbe_Transition'].append(str(transition.espacementPerturbe))

                for pointDeControle in simu.intervalResults.pointsDeControle:
                    pcGraphe = graphe.pointsDeControle[pointDeControle.pointDeControle]
                    Dict['ControlPoints'].append(pcGraphe.nom)
                    # if(pcGraphe.nomPointOptimisation != None):
                    #     Dict['ControlPoints_POName'].append(pcGraphe.nomPointOptimisation)
                    # else:
                    #     Dict['ControlPoints_POName'].append("")
                    #
                    # if(pcGraphe.nomCheckPoint != None):
                    #     Dict['ControlPoints_CPName'].append(pcGraphe.nomCheckPoint)
                    # else:
                    #     Dict['ControlPoints_CPName'].append("")
                    #
                    # Dict['ControlPoints_PRCICH'].append(pcGraphe.PR_CICH)
                    # Dict['ControlPoints_PRVoie'].append(pcGraphe.PR_VOIE)

                    Dict['IntervalleNonPerturbe_CP'].append(str(pointDeControle.intervalleNonPerturbe))
                    Dict['EspacementNonPerturbe_CP'].append(str(pointDeControle.espacementNonPerturbe))
                    Dict['IntervallePerturbe_CP'].append(str(pointDeControle.intervallePerturbe))
                    Dict['EspacementPerturbe_CP'].append(str(pointDeControle.espacementPerturbe))

                max = 0
                for key, value in Dict.items():
                    if(max < len(value)):
                        max = len(value)
                for key, value in Dict.items():
                    while(len(value) < max):
                        value.append("")
                for value in Dict.values():
                    value.append("")

                i = i + 1

                if(not (i % NbObjectPerFile)):
                    df = panda.DataFrame(Dict)
                    df.to_csv(_nomFichier + str(j) + ".csv", sep=';')
                    j = j + 1
                    Dict = {'ID_Simu': [], 'mE_T1': [], 'NatureTrain_T1': [],'ModeConduite_T1': [], 'SpeedRegulation_T1': [],
                    'mE_T2': [], 'NatureTrain_T2': [], 'ModeConduite_T2': [], 'SpeedRegulation_T2': [], 'CopyOf': [], 'Error': [],
                    'IntervalleNonPerturbe_mE': [], 'EspacementNonPerturbe_mE': [], 'IntervallePerturbe_mE': [], 'EspacementPerturbe_mE': [],
                    'Transitions':[], 'IntervalleNonPerturbe_Transition': [], 'EspacementNonPerturbe_Transition': [], 'IntervallePerturbe_Transition': [], 'EspacementPerturbe_Transition': [],
                    'ControlPoints': [], 'ControlPoints_POName': [], 'ControlPoints_CPName': [], 'ControlPoints_PRCICH': [], 'ControlPoints_PRVoie': [],
                    'IntervalleNonPerturbe_CP': [], 'EspacementNonPerturbe_CP': [], 'IntervallePerturbe_CP': [], 'EspacementPerturbe_CP': []}

        df = panda.DataFrame(Dict)
        df.to_csv(_nomFichier + str(j) + ".csv", sep=';')

    #@execution_time 
    def ExporterSimplesRunsSimulations__disabled_YDA(self, _nomFichier):
        logging.info("Start calling ExporterSimplesRunsSimulations")
        graphe = GrapheSingleton()
        Dict = {'mE': [], 'NatureTrain': [], 'ModeConduite': [], 'TempsParcoursME': [], 'SpeedRegulation': [], 'Error': [], 'Transitions': [], 'TransitionsTimesInSeconds': [], 'ControlPoints': [], 'ControlPoints_CumulatedTravelTimeInSeconds': [], 'ControlPoints_SpeedInMeterPerSeconds': []}
        for simu in self.simplesRunsSimulations:
            Dict['mE'].append(simu.mE)
            modeleGraphe = graphe.RechercherModeleTrain(simu.modele)
            Dict['NatureTrain'].append(modeleGraphe.nature.nom)
            Dict['ModeConduite'].append(modeleGraphe.modeconduite)
            Dict['TempsParcoursME'].append(str(simu.tempsParcoursME))
            Dict['SpeedRegulation'].append(str(simu.speedRegulation))
            Dict['Error'].append(simu.error)
            for transition in simu.transitions:
                Dict['Transitions'].append(transition.transition)
                Dict['TransitionsTimesInSeconds'].append(str(transition.temps))
            for pointDeControle in simu.pointsDeControle:
                pcGraphe = graphe.pointsDeControle[pointDeControle.pointDeControle]
                Dict['ControlPoints'].append(pcGraphe.nom)
                # if(pcGraphe.nomPointOptimisation != None):
                #     Dict['ControlPoints_POName'].append(pcGraphe.nomPointOptimisation)
                # else:
                #     Dict['ControlPoints_POName'].append("")
                #
                # if(pcGraphe.nomCheckPoint != None):
                #     Dict['ControlPoints_CPName'].append(pcGraphe.nomCheckPoint)
                # else:
                #     Dict['ControlPoints_CPName'].append("")
                #
                # Dict['ControlPoints_PRCICH'].append(pcGraphe.PR_CICH)
                # Dict['ControlPoints_PRVoie'].append(pcGraphe.PR_VOIE)

                Dict['ControlPoints_CumulatedTravelTimeInSeconds'].append(str(pointDeControle.temps))
                Dict['ControlPoints_SpeedInMeterPerSeconds'].append(str(pointDeControle.vitesse))

            max = 0
            for key, value in Dict.items():
                if(max < len(value)):
                    max = len(value)
            for key, value in Dict.items():
                while(len(value) < max):
                    value.append("")
            for value in Dict.values():
                value.append("")

        df = panda.DataFrame(Dict)
        df.to_csv(_nomFichier, sep=';')


class ConfigurationSimulationPerturbee__YDA:
    #@execution_time 
    def __init____disabled_YDA(self, _key, _mE1, _modele1, _speedRegulation1, _mE2, _modele2, _speedRegulation2, _copyof):
        logging.info("Start calling __init__")
        self.key = _key
        self.mE1 = _mE1.nom
        self.modele1 = _modele1.nom
        self.speedRegulation1 = _speedRegulation1
        self.mE2 = _mE2.nom
        self.modele2 = _modele2.nom
        self.speedRegulation2 = _speedRegulation2
        self.copyof = _copyof
        self.intervalResults = None
        self.tempsPerturbeResults = None

class IntervalResults:
    #@execution_time 
    def __init____disabled_YDA(self):
        logging.info("Start calling __init__")
        self.tempsIntervalleNonPerturbeME = 0.0
        self.tempsEspacementNonPerturbeME = 0.0
        self.tempsIntervallePerturbeME = 0.0
        self.tempsEspacementPerturbeME = 0.0
        self.error = ""
        self.transitions = []
        self.pointsDeControle = []

    #@execution_time 
    def DefinirTempsIntervalleNonPerturbeME__disabled_YDA(self, _headway, _tempsStationnement, _Delta_Espacement):
        logging.info("Start calling DefinirTempsIntervalleNonPerturbeME")
        self.tempsIntervalleNonPerturbeME = _headway
        self.tempsEspacementNonPerturbeME = self.tempsIntervalleNonPerturbeME - _tempsStationnement
        self.tempsIntervallePerturbeME = self.tempsIntervalleNonPerturbeME - _Delta_Espacement
        self.tempsEspacementPerturbeME = self.tempsEspacementNonPerturbeME - _Delta_Espacement

    #@execution_time 
    def AjouterIntervalEspacementPointDeControle__disabled_YDA(self, _pointDeControle, _headway, _tempsStationnement, _Delta_Espacement):
        logging.info("Start calling AjouterIntervalEspacementPointDeControle")
        pointdeControle = IntervalEspacementPointDeControle(_pointDeControle, _headway, _tempsStationnement, _Delta_Espacement)
        espacementPerturbe = pointdeControle.espacementPerturbe
        espacementNonPerturbe = pointdeControle.espacementNonPerturbe
        for iter in self.pointsDeControle:
            if(espacementNonPerturbe < iter.espacementNonPerturbe):
                iter.espacementNonPerturbe = espacementNonPerturbe
            if(espacementPerturbe < iter.espacementPerturbe):
                iter.espacementPerturbe = espacementPerturbe
        self.pointsDeControle.append(pointdeControle)
        return pointdeControle

    #@execution_time 
    def AjouterIntervalEspacementTransition__disabled_YDA(self, _transition, _headway, _tempsStationnement, _Delta_Espacement):
        logging.info("Start calling AjouterIntervalEspacementTransition")
        transition = IntervalEspacementTransition(_transition, _headway, _tempsStationnement, _Delta_Espacement)
        espacementPerturbe = transition.espacementPerturbe
        espacementNonPerturbe = transition.espacementNonPerturbe
        for iter in self.transitions:
            if(espacementNonPerturbe < iter.espacementNonPerturbe):
                iter.espacementNonPerturbe = espacementNonPerturbe
            if(espacementPerturbe < iter.espacementPerturbe):
                iter.espacementPerturbe = espacementPerturbe
        self.transitions.append(transition)
        return transition

class IntervalEspacementTransition:
    #@execution_time 
    def __init____disabled_YDA(self, _transition, _headway = None, _tempsStationnement = None, _Delta_Espacement = None):
        logging.info("Start calling __init__")
        self.transition = _transition.nom
        if(_headway != None and _tempsStationnement != None and _Delta_Espacement != None):
            if(_headway <= 0.0):
                self.intervalleNonPerturbe = 0.0
                self.intervallePerturbe = 0.0
                self.espacementNonPerturbe = 0.0
                self.espacementPerturbe = 0.0
            else:
                self.intervalleNonPerturbe = _headway
                self.intervallePerturbe = self.intervalleNonPerturbe - _Delta_Espacement
                self.espacementNonPerturbe = self.intervalleNonPerturbe - _tempsStationnement
                self.espacementPerturbe = self.espacementNonPerturbe - _Delta_Espacement
        else:
            self.transition = _transition.nom
            self.intervalleNonPerturbe = "MAX_INTERVAL"
            self.intervallePerturbe = "MAX_INTERVAL"
            self.espacementNonPerturbe = "MAX_SPACING"
            self.espacementPerturbe = "MAX_SPACING"

class IntervalEspacementPointDeControle:
    #@execution_time 
    def __init____disabled_YDA(self, _pointDeControle, _headway, _tempsStationnement, _Delta_Espacement):
        logging.info("Start calling __init__")
        self.pointDeControle = _pointDeControle.nom
        if(_headway <= 0.0):
            self.intervalleNonPerturbe = 0.0
            self.intervallePerturbe = 0.0
            self.espacementNonPerturbe = 0.0
            self.espacementPerturbe = 0.0
        else:
            self.intervalleNonPerturbe = _headway
            self.intervallePerturbe = self.intervalleNonPerturbe - _Delta_Espacement
            self.espacementNonPerturbe = self.intervalleNonPerturbe - _tempsStationnement
            self.espacementPerturbe = self.espacementNonPerturbe - _Delta_Espacement

class SimpleRunSimulation:
    #used for sure
    def __init__(self, _mE, _modele, _speedRegulation):
        #logging.info("Start calling __init__ SimpleRunSimulation")
        self.mE = _mE.nom
        self.modele = _modele.nom
        self.tempsParcoursME = 0.0
        self.speedRegulation = _speedRegulation
        self.error = ""
        self.transitions = []
        self.pointsDeControle = []
        self.deltaTimeOrigine = 0.0



#Cette fonction permet de transformer une coordonnée (voie, pk) en coordonnée (segment, abs)
def CoordVoiePKToSegAbs__disabled_YDA(_voie, _pk):
    logging.info("Start calling CoordVoiePKToSegAbs")
    #Recuperation du graphe (singleton)
    __graphe = GrapheSingleton()
    __segmentTrouve = None
    __absTrouve = None
    #Recherche des segments sur la voie _voie
    for __segment in __graphe.segments.values():
        if __segment.voie is _voie:
            #print(__segment.nom + " - " + __segment.voie.nom + " de " + str(__segment.origine) + " à " + str(__segment.fin))
            #Si le PK _pk est compris entre le début et la fin de segment
            if((_pk >= __segment.origine and _pk <= __segment.fin) or (_pk >= __segment.fin and _pk <= __segment.origine)):
                #print("ok")
                __segmentTrouve = __segment
                __absTrouve = abs(_pk - __segment.origine)

    #Retour de la valeur (segment, abs) trouvé, si non trouvé retour de None
    if(__segmentTrouve is None or __absTrouve is None):
        print('segment non trouvé pour ' + _voie.nom + " à " + str(_pk))
        return None
    else:
        __tableTrouve = {}
        __tableTrouve['segment'] = __segmentTrouve
        __tableTrouve['abs'] = __absTrouve
        return __tableTrouve

def remove_proxies():
    logging.info("Start calling remove_proxies")
    # CCO specific
    if 'http_proxy' in os.environ:
        del os.environ['http_proxy']
    if 'https_proxy' in os.environ:
        del os.environ['https_proxy']

def debug():
    return 'debug' in sys.argv

def launchRequest__disabled_YDA(url, xml):
    logging.info("Start calling launchRequest")
    global debug
    headers = {'Content-Type': 'application/xml'}
    try:
        r = requests.post(url + '/SMT3-REST-Server/computeTravelTimes', data=ET.tostring(xml), headers=headers)
    except:
        LoggerConfig.print_and_log_error('Erreur de requête au serveur')
        #print(xml)
        quit()
    r.raise_for_status()
    logging.debug('HTTP status:', r.status_code)
    if debug():
        print(parseString(r.text).toprettyxml())
    print()
    
    LoggerConfig.print_and_log_info("Result:" + r.text)
    #LoggerConfig.print_and_log_info("Result:" + r)
    # récupération du résultat en xml
    return(ET.fromstring(r.text))
