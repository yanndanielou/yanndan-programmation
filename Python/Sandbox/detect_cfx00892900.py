"""FX00892900	Submitted	Defect	MsgId*scheme.xml: incohérence entre <enumeration id et <field id= pour le champ concerné par l'énumération"""

from common import file_utils
from logger import logger_config


if __name__ == "__main__":
    with logger_config.application_logger("detect_CFX00892900"):

        XML_FOLDER_PATH = r"D:\NEXT_AutomaticTrainSupervision_Training_Simulator_2025_07_23_a_02h46NEXT\Data\Xml"

        all_xml_files = file_utils.get_files_by_directory_and_file_name_mask(directory_path=XML_FOLDER_PATH, filename_pattern="*.xml")
        logger_config.print_and_log_info(f"{len(all_xml_files)} files found")
        for xml_file_path in all_xml_files:
            logger_config.print_and_log_info(f"processing {xml_file_path}")
