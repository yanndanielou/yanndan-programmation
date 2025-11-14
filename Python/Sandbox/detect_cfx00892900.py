"""FX00892900	Submitted	Defect	MsgId*scheme.xml: incohérence entre <enumeration id et <field id= pour le champ concerné par l'énumération"""

import pathlib
import re
import xml.etree.ElementTree as ET
from typing import Dict, List, Tuple, cast

from common import file_utils
from logger import logger_config


def extract_enum_fields_regex(xml_file_path: str) -> List[Tuple[str, str, int]]:
    """
    Extracts enumeration IDs and subsequent field classes using regex.
    WARNING: Regex parsing has limitations for complex/nested XML structures.
    """

    with open(xml_file_path, encoding="utf-8") as xml_file:

        xml_str = xml_file.read()

        pattern = r"""
            <enumeration\s+      # Start of enumeration tag
            id="([^"]+)"         # Capture enumeration ID
            [^>]*>               # Rest of opening tag
            .*?                  # Content of enumeration (non-greedy)
            </enumeration>       # End of enumeration
            \s*                  # Any whitespace between tags
            <field\s+            # Start of field tag
            [^>]*                # Any attributes before class
            class="[^"]+"      # Capture class attribute
            [^>]*?
            id="([^"]+)"
        """

        results: List[Tuple[str, str, int]] = []
        for match in re.finditer(pattern, xml_str, re.DOTALL | re.VERBOSE):
            enum_id = match.group(1)
            field_id = match.group(2)
            start_index = match.start(0)
            line_no = xml_str.count("\n", 0, start_index) + 1
            results.append((enum_id, field_id, line_no))

        return results


def get_results_parsing_with_regex(xml_file_path: str) -> Tuple[List[Tuple[str, str, int]], List[Tuple[str, str, int]]]:

    results_ok: List[Tuple[str, str, int]] = []
    results_not_ok: List[Tuple[str, str, int]] = []

    enums_extracted_with_regex = extract_enum_fields_regex(xml_file_path)
    for enum_extracted_with_regex in enums_extracted_with_regex:
        enum_id = enum_extracted_with_regex[0]
        field_id = enum_extracted_with_regex[1]
        line_no = enum_extracted_with_regex[2]

        if enum_id == field_id:
            results_ok.append((enum_id, field_id, line_no))
        else:
            results_not_ok.append((enum_id, field_id, line_no))

    return results_ok, results_not_ok


def get_results_parsing_as_xml(xml_file_path: str) -> Tuple[List[Tuple[str, str, int]], List[Tuple[str, str, int]]]:
    xml_file_name_without_extension = pathlib.Path(xml_file_path).stem
    # logging.debug(f"Load and parse file {xml_file_path}")
    # read file text to compute line numbers
    with open(xml_file_path, encoding="utf-8") as f:
        xml_str = f.read()

    tree = ET.parse(xml_file_path)
    root = tree.getroot()
    parent_map = {c: p for p in root.iter() for c in p}

    results_ok: List[Tuple[str, str, int]] = []
    results_not_ok: List[Tuple[str, str, int]] = []

    all_enumerations = root.findall(".//enumeration")
    for enum in all_enumerations:
        enum_id = cast(str, enum.get("id"))
        parent = parent_map.get(enum)

        assert parent is not None
        siblings = list(parent)

        enum_index = siblings.index(enum)
        assert enum_index + 1 < len(siblings)
        next_sibling = siblings[enum_index + 1]

        assert next_sibling.tag == "field"
        next_sibling_id = cast(str, next_sibling.get("id"))

        # compute line number for the enumeration opening tag by searching in the raw XML
        pattern = rf"<enumeration\b[^>]*\bid=\"{re.escape(enum_id)}\"[^>]*>"
        m = re.search(pattern, xml_str, re.DOTALL)
        line_no = xml_str.count("\n", 0, m.start()) + 1 if m else -1

        if next_sibling_id == enum_id:
            results_ok.append((enum_id, next_sibling_id, line_no))
        else:
            results_not_ok.append((enum_id, next_sibling_id, line_no))
            logger_config.print_and_log_error(f"In {xml_file_name_without_extension}, line {line_no}, the enumeration {enum_id} must be renamed to {next_sibling_id}")

    return results_ok, results_not_ok


def handle_xml_file(xml_file_path: str) -> Tuple[List[Tuple[str, str, int]], List[Tuple[str, str, int]]]:
    # logging.debug(f"processing {xml_file_path}")
    results_ok_parsing_xml_method, results_not_ok_parsing_xml_method = get_results_parsing_as_xml(xml_file_path)

    results_ok_parsing_regex_method, results_not_ok_parsing_regex_method = get_results_parsing_with_regex(xml_file_path)

    # compare ids only (ignore line numbers) to keep parity between both methods
    def strip_line_numbers(lst: List[Tuple[str, str, int]]) -> List[Tuple[str, str]]:
        return [(a, b) for (a, b, _) in lst]

    assert strip_line_numbers(results_ok_parsing_regex_method) == strip_line_numbers(results_ok_parsing_xml_method)
    assert strip_line_numbers(results_not_ok_parsing_regex_method) == strip_line_numbers(results_not_ok_parsing_xml_method)

    return results_ok_parsing_xml_method, results_not_ok_parsing_xml_method


def main() -> None:
    with logger_config.application_logger("detect_CFX00892900"):

        XML_FOLDERS_PATHS = [
            r"inputs_for_tests",
            # r"C:\Users\fr232487\NEXT_ITF_D7_0A\ats_itf_spe\xml",
            # r"C:\Users\fr232487\CBTC_ITF_RL4aGIT_10_31_2025_ats_itf\xml",
        ]

        for xml_folder_path in XML_FOLDERS_PATHS:
            logger_config.print_and_log_info(f"Folder {xml_folder_path}")
            all_results_not_ok: Dict[str, List[Tuple[str, str, int]]] = {}
            all_xml_files = file_utils.get_files_by_directory_and_file_name_mask(directory_path=xml_folder_path, filename_pattern="*.xml")
            logger_config.print_and_log_info(f"{len(all_xml_files)} files found")
            for current_xml_file_path in all_xml_files:

                xml_file_name_without_extension = pathlib.Path(current_xml_file_path).stem
                _, current_xml_results_not_ok = handle_xml_file(current_xml_file_path)
                if current_xml_results_not_ok:
                    all_results_not_ok[xml_file_name_without_extension] = current_xml_results_not_ok

            logger_config.print_and_log_info(f"{all_results_not_ok}")


if __name__ == "__main__":
    main()
