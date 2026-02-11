from enum import Enum, auto


class PolarionUserItemType(Enum):
    USERS = auto()


class PolarionWorkItemType(Enum):
    WORKITEMS = auto()


class PolarionAttributeType(Enum):
    STB = auto()
    SECONDREGARD = auto()
    FNC = auto()
    FAN_TITULAIRE = auto()
    FAN = auto()
    SCNRTEST = auto()
    CONSTAT = auto()
    SDT = auto()
    HEADING = auto()
    SFT = auto()


class PolarionFanDestinataire(Enum):
    TITULAIRE_SIEMENS = auto()


class PolarionFanTestEnvironment(Enum):
    PFB = "PLATEFORME_BORD"


class PolarionSeverity(Enum):
    NON_BLOQUANTE = auto()
    BLOQUANTE_SANS_IMPACT_SECURITE = auto()
    BLOQUANTE_IMPACT_SECURITE = auto()


class PolarionStatus(Enum):
    INITIALISATION_EN_APPROBATION = auto()
    RESULTAT_EN_ANALYSE = auto()
    VERIFIED_REJECTED = auto()
    INITIALISATION_EN_REDACTION = auto()
    INITIALISATION_EN_VERIFICATION = auto()
    REOPENED = auto()
    INPROGRESSSNCF = auto()
    VERIFICATION_EN_APPROBATION_FDMS = auto()
    REPONSE_EN_ACTION_DESTINATAIRE = auto()
    VERIFICATION_EN_INSTRUCTION_I3G = auto()
    NON_APPLICABLE = auto()
    VERIFIED_DONE = auto()
    FICHE_DE_TEST_EN_REDACTION = auto()
    REPONSE_EN_INSTRUCTION_I3G = auto()
    RESULTAT_ANALYSE_KO = auto()
    RESULTAT_ANALYSE_OKC = auto()
    ABANDONNEE = auto()
    INITIALISATION_EN_INSTRUCTION_DESTINATAIRE = auto()
    FICHE_DE_TEST_EN_VERIFICATION = auto()
    INPROGRESS = auto()
    NON_EXEC = auto()
    CLOS = auto()
    REJECTED = auto()
    OPEN = auto()
    DONE = auto()
