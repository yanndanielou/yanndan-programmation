"""FX00892900	Submitted	Defect	MsgId*scheme.xml: incohérence entre <enumeration id et <field id= pour le champ concerné par l'énumération"""

from common import file_utils
from logger import logger_config
from common import file_name_utils
import xml.etree.ElementTree as ET
from typing import List, Tuple, Dict
import pathlib
import logging


def handle_xml_file(xml_file_path: str) -> Tuple[List[Tuple[str, str]], List[Tuple[str, str]]]:
    xml_file_name_without_extension = pathlib.Path(xml_file_path).stem

    logging.debug(f"processing {xml_file_path}")

    logging.debug(f"Load and parse file {xml_file_path}")
    tree = ET.parse(xml_file_path)
    root = tree.getroot()
    parent_map = {c: p for p in root.iter() for c in p}

    results_ok: List[Tuple[str, str]] = []
    results_not_ok: List[Tuple[str, str]] = []

    for enum in root.findall(".//enumeration"):
        enum_id = enum.get("id")
        logging.debug(f"Handle enumeration {enum_id}")
        parent = parent_map.get(enum)

        assert parent is not None
        siblings = list(parent)

        enum_index = siblings.index(enum)
        assert enum_index + 1 < len(siblings)
        next_sibling = siblings[enum_index + 1]

        assert next_sibling.tag == "field"
        next_sibling_id = next_sibling.get("id")
        if next_sibling_id == enum_id:
            results_ok.append((enum_id, next_sibling_id))
            logging.debug(f"{xml_file_name_without_extension} next sibling after enumeration {enum_id} is {next_sibling_id}")
        else:
            results_not_ok.append((enum_id, next_sibling_id))
            logger_config.print_and_log_error(f"In {xml_file_name_without_extension}, the enumeration {enum_id} must be renamed to {next_sibling_id}")

    # print(results)
    return results_ok, results_not_ok


if __name__ == "__main__":
    with logger_config.application_logger("detect_CFX00892900"):

        XML_FOLDER_PATH = r"D:\NEXT_PCC_V0_41_NEXT_PCC_BD_V0_40\Data\Xml"

        all_results_not_ok: Dict[str, Tuple[str, str]] = {}
        all_xml_files = file_utils.get_files_by_directory_and_file_name_mask(directory_path=XML_FOLDER_PATH, filename_pattern="*.xml")
        logger_config.print_and_log_info(f"{len(all_xml_files)} files found")
        for current_xml_file_path in all_xml_files:
            xml_file_name_without_extension = pathlib.Path(current_xml_file_path).stem
            xml_results_ok, current_xml_results_not_ok = handle_xml_file(current_xml_file_path)
            if current_xml_results_not_ok:
                all_results_not_ok[xml_file_name_without_extension] = current_xml_results_not_ok

        logger_config.print_and_log_info(f"{all_results_not_ok}")
