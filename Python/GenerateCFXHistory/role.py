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
