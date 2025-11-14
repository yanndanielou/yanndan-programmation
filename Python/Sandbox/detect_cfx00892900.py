"""FX00892900	Submitted	Defect	MsgId*scheme.xml: incohérence entre <enumeration id et <field id= pour le champ concerné par l'énumération"""

from common import file_utils
from logger import logger_config

import xml.etree.ElementTree as ET


def handle_xml_file(xml_file_path: str) -> None:
    logger_config.print_and_log_info(f"processing {xml_file_path}")

    logger_config.print_and_log_info(f"Load and parse file {xml_file_path}")
    tree = ET.parse(xml_file_path)
    root = tree.getroot()
    parent_map = {c: p for p in root.iter() for c in p}

    results = []

    for enum in root.findall(".//enumeration"):
        enum_id = enum.get("id")
        logger_config.print_and_log_info(f"Handle enumeration {enum_id}")
        parent = parent_map.get(enum)

        if parent is not None:
            siblings = list(parent)

            enum_index = siblings.index(enum)
            if enum_index + 1 < len(siblings):
                next_sibling = siblings[enum_index + 1]
                logger_config.print_and_log_info(f"Next sibling after enumeration {enum_id} is {next_sibling.get("class")}")

                if next_sibling.tag == "field":
                    results.append((enum_id, next_sibling.get("class")))

    # print(results)
    pass


if __name__ == "__main__":
    with logger_config.application_logger("detect_CFX00892900"):

        XML_FOLDER_PATH = r"D:\NEXT_PCC_V0_41_NEXT_PCC_BD_V0_40\Data\Xml"

        all_xml_files = file_utils.get_files_by_directory_and_file_name_mask(directory_path=XML_FOLDER_PATH, filename_pattern="*.xml")
        logger_config.print_and_log_info(f"{len(all_xml_files)} files found")
        for xml_file_path in all_xml_files:
            handle_xml_file(xml_file_path)
