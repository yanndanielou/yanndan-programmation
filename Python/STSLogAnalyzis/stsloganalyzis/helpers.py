from stsloganalyzis import constants


def is_field_name_to_be_ignored(field_name: str) -> bool:
    return field_name in constants.FIELD_FULL_NAMES_TO_EXCLUDE_IN_REPORTS or any(field_name.startswith(prefix) for prefix in constants.FIELD_NAMES_PREFIXES_TO_EXCLUDE_IN_REPORTS)
