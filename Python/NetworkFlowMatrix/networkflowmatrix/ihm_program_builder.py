# import ipaddress
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List, Optional, cast
import pandas

from common import excel_utils
from logger import logger_config

from networkflowmatrix import network_conf_files

if TYPE_CHECKING:
    from networkflowmatrix.equipments import TrainUnbreakableSingleUnit, Equipment, NetworkConfFilesEquipmentsLibrary, NetworkConfFilesDefinedEquipment


@dataclass
class IhmProgrammConfFile(network_conf_files.GenericConfFile):

    class Builder:

        @staticmethod
        def build_with_excel_file(equipments_library: "NetworkConfFilesEquipmentsLibrary", excel_file_full_path: str) -> "IhmProgrammConfFile":

            with logger_config.stopwatch_with_label(f"Load {equipments_library} ihm programm", monitor_ram_usage=True, inform_beginning=True):
                sheet_name = "P2-4"
                main_data_frame = pandas.read_excel(excel_file_full_path, skiprows=range(0, 19), sheet_name=sheet_name)
                logger_config.print_and_log_info(f"{excel_file_full_path}  has {len(main_data_frame)} items")
                logger_config.print_and_log_info(f" {excel_file_full_path}  columns  {main_data_frame.columns[:4]} ...")

                all_equipments_found: List[NetworkConfFilesDefinedEquipment] = []

                previous_module = ""
                previous_gateway = ""
                for usefull_raw_number, row in main_data_frame.iterrows():

                    number_of_null_columns = sum(row.isnull())
                    number_of_na_columns = sum(row.isna())
                    number_of_not_null_columns = sum(row.notnull())
                    number_of_not_na_columns = sum(row.notna())

                    emplacement_raw = cast(str, row["Emplacement"])
                    module_raw = cast(str, row["Module"])
                    chaine_raw = cast(str, row["Chaine"])
                    interface_raw = cast(str, row["Interface"])
                    adresses_raw = cast(str, row["Adresses"])
                    gateway_raw = cast(str, row["Gateway"])
                    mask_raw = cast(str, row["Masque"])

                    module_is_defined = str(module_raw) != "nan"
                    module = module_raw if module_is_defined else previous_module
                    eqpt = equipments_library.get_or_create_network_conf_file_eqpt_if_not_exist_by_name(name=module, source_label_for_creation=f"{excel_file_full_path}/{"P2-4"}")
                    ip_address = adresses_raw.replace("(1)", "").replace(" ", "")
                    try:
                        eqpt.add_ip_address(network_conf_files.NetworkConfFilesDefinedIpAddress(ip_raw=ip_address, label=None))
                    except AssertionError:
                        logger_config.print_and_log_error(f"Could not create IP {ip_address} for {module} in {emplacement_raw} because is already defined for it")

                    if module_is_defined:
                        previous_module = module_raw
                    previous_gateway = gateway_raw

                logger_config.print_and_log_info(f"{excel_file_full_path} tab {sheet_name}: {len(all_equipments_found)} equipment found")

            conf_file = IhmProgrammConfFile(
                name=excel_file_full_path,
                equipments_library=equipments_library,
                all_equipments=all_equipments_found,
            )

            logger_config.print_and_log_info(f"{excel_file_full_path}: {len(all_equipments_found)} equipment found")
            logger_config.print_and_log_info(f"So far, the library contains {len(equipments_library.all_network_conf_files_defined_equipments)} equipments in total")

            return conf_file
