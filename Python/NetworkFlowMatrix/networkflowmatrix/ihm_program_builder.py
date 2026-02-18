# import ipaddress
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List, Optional, cast

import pandas
from logger import logger_config

from networkflowmatrix import network_conf_files, seclab, network_entity_provider, revenue_services
from networkflowmatrix.groups import GroupDefinition

if TYPE_CHECKING:
    from networkflowmatrix.equipments import (
        NetworkConfFilesDefinedEquipment,
        NetworkConfFilesEquipmentsLibrary,
    )


@dataclass
class IhmProgrammConfFile(network_conf_files.GenericConfFile):

    class IhmProgrammRevenueServiceByEquipmentName(revenue_services.RevenueServiceToEquipmentMatchingStrategy):

        def get_revenue_service_for_equipment(self, equipment: "NetworkConfFilesDefinedEquipment") -> revenue_services.RevenueService:
            if "diffusion" in equipment.name:
                return revenue_services.RevenueService.ATS3
            elif "PM Type E" in equipment.name:
                return revenue_services.RevenueService.ATS2
            else:
                return revenue_services.RevenueService.ATS1

    class Builder:

        @staticmethod
        def build_with_excel_file(equipments_library: "NetworkConfFilesEquipmentsLibrary", excel_file_full_path: str) -> "IhmProgrammConfFile":

            with logger_config.stopwatch_with_label(f"Load {equipments_library} ihm programm", monitor_ram_usage=True, inform_beginning=True):
                sheet_name = "P2-4"
                main_data_frame = pandas.read_excel(excel_file_full_path, skiprows=range(0, 19), sheet_name=sheet_name)
                logger_config.print_and_log_info(f"{excel_file_full_path}  has {len(main_data_frame)} items")
                logger_config.print_and_log_info(f" {excel_file_full_path}  columns  {main_data_frame.columns[:4]} ...")

                all_equipments_found: List[NetworkConfFilesDefinedEquipment] = []

                last_valid_module = ""
                # last_valid_gateway = ""
                last_valid_location = ""
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

                    location_is_defined = str(emplacement_raw) != "nan"
                    location = emplacement_raw.replace("\n", "\\n") if location_is_defined else last_valid_location

                    module_is_defined = str(module_raw) != "nan"
                    module = module_raw.replace("\n", "\\n") if module_is_defined else last_valid_module
                    name = location + "_" + module
                    equipment = equipments_library.get_or_create_network_conf_file_eqpt_if_not_exist_by_name(
                        name=name,
                        source_label_for_creation=f"{excel_file_full_path}/{"P2-4"}",
                        seclab_side=seclab.SeclabSide.SOL,
                        network_provider=network_entity_provider.NetworkEntityProvider.INFRACOM_OR_INFRANET,
                        revenue_service_definition_strategy=IhmProgrammConfFile.IhmProgrammRevenueServiceByEquipmentName(),
                    )
                    all_equipments_found.append(equipment)
                    ip_address = adresses_raw.replace("(1)", "").replace(" ", "")
                    try:
                        equipment.add_ip_address(
                            network_conf_files.NetworkConfFilesDefinedUnicastIpAddress(
                                ip_raw=ip_address, label=None, mask=mask_raw, gateway=gateway_raw, vlan_name=None, gateway_is_optional=True, mask_is_optional=True
                            )
                        )
                    except AssertionError:
                        logger_config.print_and_log_error(f"Could not create IP {ip_address} for {module} in {location} because is already defined for it")

                    if module_is_defined:
                        last_valid_module = module

                    if location_is_defined:
                        last_valid_location = location

                logger_config.print_and_log_info(f"{excel_file_full_path} tab {sheet_name}: {len(all_equipments_found)} equipment found")

            conf_file = IhmProgrammConfFile(
                name=excel_file_full_path,
                equipments_library=equipments_library,
                all_equipments=all_equipments_found,
            )

            return conf_file


@dataclass
class FdiffClientsConfFile(network_conf_files.GenericConfFile):

    class Builder:

        @staticmethod
        def build_with_excel_file(equipments_library: "NetworkConfFilesEquipmentsLibrary", excel_file_full_path: str) -> "FdiffClientsConfFile":

            with logger_config.stopwatch_with_label(f"Load {equipments_library} fdiff clients", monitor_ram_usage=True, inform_beginning=True):
                sheet_name = "CDIF"
                main_data_frame = pandas.read_excel(excel_file_full_path, skiprows=range(0, 22), sheet_name=sheet_name)
                logger_config.print_and_log_info(f"{excel_file_full_path}  has {len(main_data_frame)} items")
                logger_config.print_and_log_info(f" {excel_file_full_path}  columns  {main_data_frame.columns[:4]} ...")

                all_equipments_found: List[NetworkConfFilesDefinedEquipment] = []

                for usefull_raw_number, row in main_data_frame.iterrows():

                    number_of_not_null_columns = sum(row.notnull())

                    if number_of_not_null_columns == 0:
                        logger_config.print_and_log_warning(f"{excel_file_full_path} : ignore {usefull_raw_number}th row because is null")
                        continue

                    emplacement_raw = cast(str, row["Emplacement Terminal"])
                    terminal_raw = cast(str, row["Terminal"])
                    ip_adress_raw = cast(str, row["@IP des terminaux (2)"])
                    gateway_raw = cast(str, row["Gateway (2)"])
                    mask_raw = cast(str, row["Masque (2)"])

                    if str(ip_adress_raw) == "nan":
                        logger_config.print_and_log_warning(f"{excel_file_full_path} : ignore {usefull_raw_number}th row because missing info")
                        continue

                    equipment = equipments_library.get_or_create_network_conf_file_eqpt_if_not_exist_by_name(
                        name="FDIFF_CLIENT_" + emplacement_raw + "_" + terminal_raw,
                        source_label_for_creation=f"{excel_file_full_path}",
                        seclab_side=seclab.SeclabSide.SOL,
                        network_provider=network_entity_provider.NetworkEntityProvider.INFRANET,
                        revenue_service_definition_strategy=revenue_services.AlwaysATS1RevenueService(),
                    )
                    all_equipments_found.append(equipment)

                    equipment.add_ip_address(
                        network_conf_files.NetworkConfFilesDefinedUnicastIpAddress(
                            ip_raw=ip_adress_raw, label=None, mask=mask_raw, gateway=gateway_raw, vlan_name=None, gateway_is_optional=True, mask_is_optional=True
                        )
                    )
                    equipment.add_equipment_type("CLIENT_FDIFF")

                    group = equipments_library.get_or_create_group(GroupDefinition(name="CLIENT_FDIFF", subnet_and_mask=ip_adress_raw))
                    group.add_equipment(equipment)

                logger_config.print_and_log_info(f"{excel_file_full_path} tab {sheet_name}: {len(all_equipments_found)} equipment found")

            conf_file = FdiffClientsConfFile(
                name=excel_file_full_path,
                equipments_library=equipments_library,
                all_equipments=all_equipments_found,
            )

            return conf_file
