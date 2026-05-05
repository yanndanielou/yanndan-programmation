from enum import Enum


class RequestType(Enum):
    CHANGE_REQUEST_EXTERNAL = "Change Request, external"
    DEFECT = "Defect"
    CHANGE_REQUEST_INTERNAL = "Change Request, internal"
    DEVELOPMENT_REQUEST = "Development Request"
    HAZARD = "Hazard"
    ACTION_ITEM = "Action Item"
    OPEN_POINT = "Open Point"


class Category(Enum):
    SYSTEM = "System"
    SOFTWARE = "Software"
    HARDWARE = "Hardware"
    DOCUMENTATION = "Documentation"
    CONFIGURATION_DATA = "Configuration Data"


class Severity(Enum):
    TOTAL_FAILURE = "1 - Total failure"
    FAILURE_OF_PARTS = "2 - Failure of parts"
    MINOR_IMPACT_ON_AVAILABILITY = "3 - Minor impact on availability"
    NO_FUNCTIONAL_IMPACT = "4 - No functional impact"


class EnvironmentType(Enum):
    DEVELOPMENT = "Development"
    ENGINEERING = "Engineering"
    SIMULATION = "Simulation"
    TEST_SYSTEM = "Test System"
    CUSTOMER_INSTALLATION = "Customer Installation"


class DetectedInPhase(Enum):
    BID_AND_PROJECT_PLANNING = "Bid and Project Planning"
    RISK_ANALYSIS = "Risk Analysis"
    REQUIREMENTS = "Requirements"
    ARCHITECTURE = "Architecture"
    IMPLEMENTATION_AND_TEST = "Implementation and Test"
    INTEGRATION = "Integration"
    VALIDATION = "Validation"
    ASSESSMENT = "Assessment"
    ENGINEERING = "Engineering"
    PRODUCTION = "Production"
    INSTALLATION = "Installation"
    OPERATION = "Operation"


class SafetyRelevant(Enum):
    YES = "Yes"
    NO = "No"


class SecurityRelevant(Enum):
    YES = "Yes"
    NO = "No"
    MITIGATED = "Mitigated"
