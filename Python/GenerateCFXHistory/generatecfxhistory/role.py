from enum import auto
from typing import Dict, Optional, List

from common import enums_utils
from abc import ABC, abstractmethod


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


class WorkPackage:
    ADC_DC: "WorkPackage" = None

    def __init__(self, sub_systems: List[SubSystem]):
        self._sub_systems = sub_systems


WorkPackage.ADC_DC = WorkPackage([SubSystem.SW, SubSystem.SW_ANALYSES_SECU, SubSystem.SW_VAL, SubSystem.TCR3, SubSystem.V3])


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
    def full_name(self) -> str:
        return self._full_name


class CfxLibraryBase(ABC):

    @abstractmethod
    def __init__(self) -> None:

        self._cfx_user_by_full_name: Dict[str, CfxUser] = dict()
        self._cfx_user_by_full_name_lower: Dict[str, CfxUser] = dict()

        # add unknown user
        self._unknown_user: CfxUser = self._add_user_with_user(UNKNOWN_USER)

    def _add_user_with_user(self, cfx_user: CfxUser) -> CfxUser:
        self._cfx_user_by_full_name_lower[cfx_user.full_name] = cfx_user
        self._cfx_user_by_full_name[cfx_user.raw_full_name] = cfx_user
        return cfx_user

    @property
    def unknown_user(self) -> CfxUser:
        return self._unknown_user

    @abstractmethod
    def has_user_by_full_name(self, full_name: str) -> bool:
        pass

    @abstractmethod
    def get_cfx_user_by_full_name(self, full_name: str) -> CfxUser:
        pass

    @abstractmethod
    def get_subsystem_from_champfx_fixed_implemented_in(self, champfx_fixed_implemented_in: str) -> Optional[SubSystem]:
        return None


class CfxUserLibrary(CfxLibraryBase):

    def __init__(self, user_and_role_data_text_file_full_path: str, release_subsystem_mapping: dict[SubSystem, list[str]]) -> None:
        super().__init__()
        self._release_subsystem_mapping: dict[SubSystem, list[str]] = release_subsystem_mapping

        with open(user_and_role_data_text_file_full_path, "r", encoding="utf-8") as user_and_role_data_text_file:
            lines = user_and_role_data_text_file.readlines()

        # Iterate over each line
        for line in lines:
            # Split the name and the associated value
            raw_full_name_unstripped, raw_subsystem = line.split("\t")

            raw_subsystem = raw_subsystem.strip()
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

    def _add_user_with_raw_data(self, subsystem: SubSystem, raw_full_name_lower: str, raw_full_name: str) -> CfxUser:
        cfx_user = CfxUser(raw_full_name=raw_full_name, full_name=raw_full_name_lower, subsystem=subsystem)
        return self._add_user_with_user(cfx_user)

    def get_subsystem_from_champfx_fixed_implemented_in(self, champfx_fixed_implemented_in: str) -> Optional[SubSystem]:

        for subsystem, keywords in self._release_subsystem_mapping.items():
            for keyword in keywords:
                if keyword.lower() in champfx_fixed_implemented_in.lower():
                    return subsystem

        # logger_config.print_and_log_warning(f"Could not find subsystem for {champfx_fixed_implemented_in}")
        return None

    def has_user_by_full_name(self, full_name: str) -> bool:
        full_name_to_consider = full_name.lower()
        return full_name_to_consider in self._cfx_user_by_full_name_lower

    def get_cfx_user_by_full_name(self, full_name: str) -> CfxUser:
        full_name_to_consider = full_name.lower()
        return self._cfx_user_by_full_name_lower[full_name_to_consider]


class CfxEmptyUserLibrary(CfxLibraryBase):

    def __init__(self) -> None:
        super().__init__()

    def has_user_by_full_name(self, full_name: str) -> bool:
        return True

    def get_cfx_user_by_full_name(self, full_name: str) -> CfxUser:
        return self.unknown_user

    def get_subsystem_from_champfx_fixed_implemented_in(self, champfx_fixed_implemented_in: str) -> Optional[SubSystem]:
        return self.unknown_user.subsystem


UNKNOWN_USER: CfxUser = CfxUser(raw_full_name="Unknown", full_name="Unknown", subsystem=SubSystem.TBD)
