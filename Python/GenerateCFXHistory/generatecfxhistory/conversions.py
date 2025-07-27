from generatecfxhistory.constants import State
from common import string_utils


def convert_state(raw_state: str) -> State:
    match raw_state:
        case "In_Analysis":
            return State.SUBMITTED
        case "Opened":
            return State.SUBMITTED
        case "Qualifying":
            return State.SUBMITTED
        case "WaitingAssignment":
            return State.ANALYSED
        case "SafetyValidation":
            return State.VALIDATED
        case "InVerification":
            return State.RESOLVED
        case "FunctionalValidation":
            return State.RESOLVED
        case "InVerification":
            return State.RESOLVED
        case "InResolution":
            return State.ASSIGNED
        case "InConsultation":
            return State.SUBMITTED
        case "InAnalysis":
            return State.SUBMITTED
        case "In Analysis":
            return State.SUBMITTED
        case "WaitingDecision":
            return State.POSTPONED
        case "Cloning":  # only found for USTS00033443   in 2014
            return State.SUBMITTED
        case "Duplicate":  # only found for USTS00033443   in 2014
            return State.REJECTED

    return State[string_utils.text_to_valid_enum_value_text(raw_state)]
