from enum import Enum, auto

from logger import logger_config

import role_data


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


def get_subsystem_from_cfx_current_owner(cfx_current_owner: str) -> SubSystem:
    raw_subystem_of_ressource = get_raw_subystem_of_ressource(cfx_current_owner)
    return SubSystem[raw_subystem_of_ressource]


def get_raw_subystem_of_ressource(ressource_name: str) -> str:
    # Split the data into lines
    lines = role_data.ressource_subsystem_data.strip().split("\n")

    # Iterate over each line
    for line in lines:
        # Split the name and the associated value
        first_col, second_col = line.split("\t")

        # Check if the first column matches the given name
        if first_col.strip().lower() == ressource_name.lower():
            return second_col.strip()

    # Return an error message if the name is not found
    logger_config.print_and_log_error(f"Could not get subsystem of {ressource_name}")
    return "Name not found"
