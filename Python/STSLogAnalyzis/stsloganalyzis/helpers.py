from typing import cast, Dict, Optional

from stsloganalyzis import (
    constants,
    line_topology,
)


def is_field_name_to_be_ignored(field_name: str) -> bool:
    return (
        field_name in constants.FIELD_FULL_NAMES_TO_EXCLUDE_IN_REPORTS
        or any(field_name.startswith(prefix) for prefix in constants.FIELD_NAMES_PREFIXES_TO_EXCLUDE_IN_REPORTS)
        or any(field_name.endswith(prefix) for prefix in constants.FIELD_NAMES_POSTFIXES_TO_EXCLUDE_IN_REPORTS)
    )


def decode_one_exact_location(
    decoded_fields_flat_directory: Dict[str, constants.FIELD_TYPE], segment_id_field_name: str, abscissa_field_name: str, railway_line: line_topology.Line
) -> Optional[line_topology.ExactLocation]:

    raw_segment_number = decoded_fields_flat_directory.get(segment_id_field_name)
    assert raw_segment_number is not None, f"Could not find segment {abscissa_field_name}"
    segment_number = cast(int, raw_segment_number)
    if segment_number == 0:
        return None
    segment = railway_line.get_segment(segment_number)
    raw_abscissa = decoded_fields_flat_directory.get(abscissa_field_name)
    abscissa = cast(int, raw_abscissa)
    assert abscissa is not None, f"Could not find abscissa {abscissa_field_name}"
    location = line_topology.ExactLocation(segment=segment, abscissa=abscissa)

    return location
