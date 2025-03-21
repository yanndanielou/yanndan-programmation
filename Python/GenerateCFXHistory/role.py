from enum import Enum, auto

from logger import logger_config

from typing import Dict

from dataclasses import dataclass, field

import role_data

from common import string_utils

sous_lot_data = """
. Pallavee	SW
Nguyen Charles	ATS
Legendart Raphael	ATS
Ettedgui Jonathan	TCM TC
Fan Zhengqing	SW
"""


class SubSystem(Enum):
    SW = auto()
    ATS = auto()
    SSI = auto()
    COC_DE = auto()
    SAF = auto()
    TCM_TC = auto()
    SUBSYS = auto()
    TRACY = auto()
    Qualite = auto()
    Systeme = auto()
    RIVS = auto()
    ATS_Eviden = auto()
    Radio = auto()
    Installation = auto()
    TCM_TM1 = auto()
    ADONEM = auto()
    TCM_TM2 = auto()
    SW_VAL = auto()
    Projet = auto()
    SW_Analyses_secu = auto()
    CS = auto()
    ATC_Manager = auto()
    Reseau = auto()
    SCFT = auto()
    ITF_MR = auto()
    TbD = auto()
    Gumps = auto()
    SW_Tests_secu = auto()
    V3 = auto()
    TCR3 = auto()


class CfxUser:
    def __init__(self, full_name: str, raw_full_name: str, subsystem: SubSystem):
        self._raw_full_name = raw_full_name
        self._full_name = full_name
        self._subsystem: SubSystem = subsystem

    @property
    def subsystem(self) -> SubSystem:
        return self._subsystem

    @property
    def raw_full_name(self) -> str:
        return self._raw_full_name


class CfxUserLibrary:

    def __init__(self):
        self._cfx_user_by_full_name: Dict[str, CfxUser] = dict()
        self._cfx_user_by_full_name_lower: Dict[str, CfxUser] = dict()

        # Split the data into lines
        lines = role_data.ressource_subsystem_data.strip().split("\n")

        # Iterate over each line
        for line in lines:
            # Split the name and the associated value
            raw_full_name_unstripped, raw_subsystem = line.split("\t")

            # formated_subsystem_text = string_utils._diacritics(raw_subsystem.replace(" ", "_").replace("-", "_").replace("(", "").replace(")", ""))
            formatted_subsystem_text = raw_subsystem.replace(" ", "_")
            formatted_subsystem_text = formatted_subsystem_text.replace("-", "_")
            formatted_subsystem_text = formatted_subsystem_text.replace("(", "")
            formatted_subsystem_text = formatted_subsystem_text.replace(")", "")
            formatted_subsystem_text = formatted_subsystem_text.replace("é", "e")
            formatted_subsystem_text = formatted_subsystem_text.replace("è", "e")

            subsystem = SubSystem[formatted_subsystem_text]

            raw_full_name = raw_full_name_unstripped.strip()
            raw_full_name_lower = raw_full_name.lower()
            self._add_user(subsystem=subsystem, raw_full_name_lower=raw_full_name_lower, raw_full_name=raw_full_name)

        # add unknown user
        self._unknown_user: CfxUser = self._add_user(subsystem=SubSystem.TbD, raw_full_name_lower="Unknown", raw_full_name="Unknown")

    @property
    def unknown_user(self) -> CfxUser:
        return self._unknown_user

    def _add_user(self, subsystem: SubSystem, raw_full_name_lower: str, raw_full_name: str) -> CfxUser:
        cfx_user = CfxUser(raw_full_name=raw_full_name, full_name=raw_full_name_lower, subsystem=subsystem)
        self._cfx_user_by_full_name_lower[raw_full_name_lower] = cfx_user
        self._cfx_user_by_full_name[raw_full_name] = cfx_user
        return cfx_user

    def get_cfx_user_by_full_name(self, full_name: str) -> CfxUser:
        full_name_to_consider = full_name.lower()
        return self._cfx_user_by_full_name_lower[full_name_to_consider]


def get_subsystem_from_champfx_fixed_implemented_in(champfx_fixed_implemented_in: str) -> SubSystem:
    subsystem_mapping = {
        SubSystem.TCR3: ["Component PAE", "S003_Component TCR3", "Component PAS", "Component MES", "TCR3"],
        SubSystem.SW: ["Component PAE", "S003_Component TCR3", "Component PAS", "Applicatif PAS", "S002_Subsystem Automatic Train Control", "Module Application PAS", "Module Application PAL"],
        SubSystem.SUBSYS: ["CDB", "MDT", "Eurobalise", "Tiroir Calculateur", "Transition par balise", "Odotachy", "EVC/DMI/JRU", "Logiciel de service", "Compte à rebour"],
        SubSystem.TRACY: ["Cyclos"],
        SubSystem.ATS: [
            "Automatic Train Supervision",
            "S001_System ATSP",
            "Tube",
            "SIMEV",
            "SIFOR",
            "Foxtrot",
            "S003_Component Master",
            "S004_Module Package AD",
            "Module Master",
            "S003_Component Package AD",
            "ATS",
            "Atelier de paramétrage",
        ],
        SubSystem.COC_DE: ["S002_Subsystem Invariants", "Invariants", "Paramètres"],
        SubSystem.TCM_TC: ["SIMECH", "Gumps", "Outils", "XT_OT"],
        SubSystem.Radio: ["RADIO", "Baie Centrale Radio"],
        SubSystem.ATS_Eviden: ["COEUR CK", "FGPT", "MES SIL2"],
        SubSystem.Reseau: ["Réseau", "Commutateur", "pare-feu"],
        SubSystem.ADONEM: ["ADONEM"],
        SubSystem.TCM_TM1: ["Plateforme", "Usine"],
        SubSystem.TCM_TM2: ["Site"],
        SubSystem.Systeme: ["S001_System Système NExTEO ATC", "S001_System Système NExTEO", "Performances du système", "Interfaces Signalisation", "Interfaces Voie"],
        SubSystem.ITF_MR: ["S001_System Système NExTEO ATC", "S002_Subsystem Interfaces_NEXTEO"],
        SubSystem.Projet: ["Management du projet"],
        SubSystem.ATC_Manager: ["Matériels complémentaires"],
        SubSystem.SAF: ["Fiabilité"],
        SubSystem.Installation: ["SBL"],
    }

    for subsystem, keywords in subsystem_mapping.items():
        for keyword in keywords:
            if keyword.lower() in champfx_fixed_implemented_in.lower():
                return subsystem

    return None
