from enum import auto
from typing import Dict, Optional

from common import enums_utils

from generatecfxhistory import role_data


class SubSystem(enums_utils.NameBasedEnum):
    SW = auto()
    ATS = auto()
    SSI = auto()
    COC_DE = auto()
    SAF = auto()
    TCM_TC = auto()
    SUBSYS = auto()
    TRACY = auto()
    QUALITE = auto()
    SYSTEME = auto()
    RIVS = auto()
    ATS_EVIDEN = auto()
    RADIO = auto()
    INSTALLATION = auto()
    TCM_TM1 = auto()
    ADONEM = auto()
    TCM_TM2 = auto()
    SW_VAL = auto()
    PROJET = auto()
    SW_ANALYSES_SECU = auto()
    CS = auto()
    ATC_MANAGER = auto()
    RESEAU = auto()
    SCFT = auto()
    ITF_MR = auto()
    TBD = auto()
    GUMPS = auto()
    SW_TESTS_SECU = auto()
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

    @property
    def full_name(self):
        return self._full_name


class CfxUserLibrary:

    def __init__(self) -> None:
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
            formatted_subsystem_text = formatted_subsystem_text.replace("-", "_")
            formatted_subsystem_text = formatted_subsystem_text.upper()

            subsystem = SubSystem[formatted_subsystem_text]

            raw_full_name = raw_full_name_unstripped.strip()
            raw_full_name_lower = raw_full_name.lower()
            self._add_user_with_raw_data(subsystem=subsystem, raw_full_name_lower=raw_full_name_lower, raw_full_name=raw_full_name)

        # add unknown user
        self._unknown_user: CfxUser = self._add_user_with_user(UNKNOWN_USER)

    @property
    def unknown_user(self) -> CfxUser:
        return self._unknown_user

    def _add_user_with_raw_data(self, subsystem: SubSystem, raw_full_name_lower: str, raw_full_name: str) -> CfxUser:
        cfx_user = CfxUser(raw_full_name=raw_full_name, full_name=raw_full_name_lower, subsystem=subsystem)
        return self._add_user_with_user(cfx_user)

    def _add_user_with_user(self, cfx_user: CfxUser) -> CfxUser:
        self._cfx_user_by_full_name_lower[cfx_user.full_name] = cfx_user
        self._cfx_user_by_full_name[cfx_user.raw_full_name] = cfx_user
        return cfx_user

    def get_cfx_user_by_full_name(self, full_name: str) -> CfxUser:
        full_name_to_consider = full_name.lower()
        return self._cfx_user_by_full_name_lower[full_name_to_consider]


def get_subsystem_from_champfx_fixed_implemented_in(champfx_fixed_implemented_in: str) -> Optional[SubSystem]:
    subsystem_mapping = {
        SubSystem.TCR3: ["S003_Component TCR3", "TCR3"],
        SubSystem.SW: [
            "Component MES",
            "Component PAE",
            "Component PAS",
            "Applicatif PAS",
            "S002_Subsystem Automatic Train Control",
            "Module Application PAS",
            "Module Application PAL",
            "S003_Component PAL",
            "S003_Component Atelier de Développement Logiciel",
            "S003_Component Canevas",
            "S004_Module PAI",
        ],
        SubSystem.SUBSYS: [
            "CDB",
            "MDT",
            "Eurobalise",
            "Tiroir Calculateur",
            "Transition par balise",
            "Odotachy",
            "EVC/DMI/JRU",
            "Logiciel de service",
            "Compte à rebour",
            "S003_Component Niveau 3 - Sol",
            "S003_Component Niveau 3 - Bord",
            "S003_Component PPN",
            "S004_Module GenTel",
        ],
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
            "S002_Subsystem SECU IHM",
            "S002_Subsystem RTO",
            "Serveur d'authentification",
            "Boitier PERLE Signalisation NT Durcisssement",
        ],
        SubSystem.COC_DE: ["S002_Subsystem Invariants", "Invariants", "Paramètres", "S003_Component SMT3"],
        SubSystem.TCM_TC: ["SIMECH", "Gumps", "Outils", "XT_OT", "S003_Component TU"],
        SubSystem.RADIO: ["RADIO", "Baie Centrale Radio"],
        SubSystem.ATS_EVIDEN: ["COEUR CK", "FGPT", "MES SIL2"],
        SubSystem.RESEAU: ["Réseau", "Commutateur", "pare-feu"],
        SubSystem.ADONEM: ["ADONEM"],
        SubSystem.TCM_TM1: ["Plateforme", "Usine"],
        SubSystem.TCM_TM2: ["Site"],
        SubSystem.SYSTEME: [
            "S001_System Système NExTEO ATC",
            "S001_System Système NExTEO",
            "Performances du système",
            "Interfaces Signalisation",
            "Interfaces Voie",
            "S003_Component Inferfaces Matériel Roulant",
        ],
        SubSystem.ITF_MR: ["S001_System Système NExTEO ATC", "S002_Subsystem Interfaces_NEXTEO"],
        SubSystem.PROJET: ["Management du projet", "Mise en Service Commerciale NExTEO", "Module Formulaires COVASEC"],
        SubSystem.ATC_MANAGER: ["Matériels complémentaires"],
        SubSystem.SAF: ["Fiabilité"],
        SubSystem.INSTALLATION: ["SBL", "S004_Module Installation"],
    }

    for subsystem, keywords in subsystem_mapping.items():
        for keyword in keywords:
            if keyword.lower() in champfx_fixed_implemented_in.lower():
                return subsystem

    # logger_config.print_and_log_warning(f"Could not find subsystem for {champfx_fixed_implemented_in}")
    return None


UNKNOWN_USER: CfxUser = CfxUser(raw_full_name="Unknown", full_name="Unknown", subsystem=SubSystem.TBD)
