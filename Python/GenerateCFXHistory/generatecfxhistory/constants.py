from enum import auto, Enum

from typing import cast
from common import enums_utils


class State(enums_utils.NameBasedIntEnum):
    NOT_CREATED_YET = cast("State", auto())
    NO_VALUE = cast("State", auto())
    SUBMITTED = cast("State", auto())
    ANALYSED = cast("State", auto())
    ASSIGNED = cast("State", auto())
    RESOLVED = cast("State", auto())
    REJECTED = cast("State", auto())
    POSTPONED = cast("State", auto())
    VERIFIED = cast("State", auto())
    VALIDATED = cast("State", auto())
    UNKNOWN = cast("State", auto())
    CLOSED = cast("State", auto())


class RequestType(enums_utils.NameBasedEnum):
    CHANGE_REQUEST_EXTERNAL = cast("RequestType", auto())
    DEFECT = cast("RequestType", auto())
    CHANGE_REQUEST_INTERNAL = cast("RequestType", auto())
    DEVELOPMENT_REQUEST = cast("RequestType", auto())
    HAZARD = cast("RequestType", auto())
    ACTION_ITEM = cast("RequestType", auto())
    OPEN_POINT = cast("RequestType", auto())
    DEFECT_INTERNAL = cast("RequestType", auto())
    CHANGE_REQUEST_PLM = cast("RequestType", auto())
    CHANGE_REQUEST_PROJECTS = cast("RequestType", auto())
    MPP = cast("RequestType", auto())
    HINDERING_NOTICE = cast("RequestType", auto())
    FCR = cast("RequestType", auto())
    NCP = cast("RequestType", auto())
    PRE_NC_NOTICE = cast("RequestType", auto())
    TO_BE_ADDED_YDA = cast("RequestType", auto())


class RejectionCause(Enum):
    NONE = cast("RejectionCause", auto())
    NO_FIX_CHANGE = cast("RejectionCause", auto())
    DUPLICATE = cast("RejectionCause", auto())
    NOT_A_BUG = cast("RejectionCause", auto())
    NOT_PART_OF_CONTRACT = cast("RejectionCause", auto())
    FORWARDED_TO_SAP_CS = cast("RejectionCause", auto())
    NOT_REPRODUCIBLE = cast("RejectionCause", auto())
    SOLVED_INDIRECTLY = cast("RejectionCause", auto())
    OUT_OF_SCOPE = cast("RejectionCause", auto())
    WILL_NOT_BE_FIXED = cast("RejectionCause", auto())
    ALREADY_DONE = cast("RejectionCause", auto())
    AFFECTED_PACKAGE_IS_NOT_INSTALLED = cast("RejectionCause", auto())
    SOLVE_BY = cast("RejectionCause", auto())
    SOLVED_BY = cast("RejectionCause", auto())
    SOLVEDBY = cast("RejectionCause", auto())
    SOVED_BY = cast("RejectionCause", auto())
    NA = cast("RejectionCause", auto())
    N_A_CHANGE_REQUEST = cast("RejectionCause", auto())
    PATCH_WITHDREWN = cast("RejectionCause", auto())
    SIMILAR = cast("RejectionCause", auto())
    NO_DATA = cast("RejectionCause", auto())
    WRONG_ASSIGNEMENT = cast("RejectionCause", auto())
    TO_BE_ADDED_YDA = cast("RejectionCause", auto())

    def __repr__(self) -> str:
        return self.name

    def __str__(self) -> str:
        return self.name


class Category(Enum):
    SYSTEM = cast("Category", auto())
    SOFTWARE = cast("Category", auto())
    HARDWARE = cast("Category", auto())
    DOCUMENTATION = cast("Category", auto())
    CONFIGURATION_DATA = cast("Category", auto())
    PROCESS = cast("Category", auto())
    TEST_CASE = cast("Category", auto())
    CONSTRAINT_TO_3RD_PARTY = cast("Category", auto())
    NO_CATEGORY_DEFINED = cast("Category", auto())
    NONE = cast("Category", auto())
    TBD = cast("Category", auto())
    MONTAGE = cast("Category", auto())
    NICHT_IM_LV = cast("Category", auto())
    LIEFERUNG = cast("Category", auto())
    BESCHRIFTUNG = cast("Category", auto())
    RELEVANZ = cast("Category", auto())
    DESIGN = cast("Category", auto())
    TEST_AND_COMISSIONING = cast("Category", auto())
    CHANGE_REQUEST = cast("Category", auto())
    SUPPORT = cast("Category", auto())
    DEVELOPMENT_REQUEST = cast("Category", auto())
    MISSVERSTANDEN = cast("Category", auto())
    TRACK_LAYOUT___TDB___IXL = cast("Category", auto())
    PRODUCT = cast("Category", auto())
    REQUIREMENT = cast("Category", auto())
    POTENTIAL_CLAIM = cast("Category", auto())
    TEST_SYSTEM_HANDLING = cast("Category", auto())
    DOPPELT = cast("Category", auto())
    TO_BE_ADDED_YDA = cast("Category", auto())

    def __repr__(self) -> str:
        return self.name

    def __str__(self) -> str:
        return self.name


class CfxProject:
    FR_NEXTEO: str = "FR_NEXTEO"
    ATSP: str = "ATSP"


class SecurityRelevant(enums_utils.NameBasedEnum):
    YES = cast("SecurityRelevant", auto())
    NO = cast("SecurityRelevant", auto())
    MITIGATED = cast("SecurityRelevant", auto())
    UNDEFINED = cast("SecurityRelevant", auto())


class ActionType(enums_utils.NameBasedEnum):
    IMPORT = cast("ActionType", auto())
    RESUBMIT = cast("ActionType", auto())
    SUBMIT = cast("ActionType", auto())
    ASSIGN = cast("ActionType", auto())
    ANALYSE = cast("ActionType", auto())
    POSTPONE = cast("ActionType", auto())
    REJECT = cast("ActionType", auto())
    RESOLVE = cast("ActionType", auto())
    VERIFY = cast("ActionType", auto())
    VALIDATE = cast("ActionType", auto())
    CLOSE = cast("ActionType", auto())
