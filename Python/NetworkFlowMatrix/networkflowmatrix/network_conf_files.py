import ipaddress
from dataclasses import dataclass, field
from typing import List, Optional, Set, Tuple, cast, Dict

import pandas
from logger import logger_config


@dataclass
class NetworkConfFilesDefinedIpAddress:
    ip_raw: str
    mask: str
    gateway: str
    vlan_name: str


@dataclass
class NetworkConfFilesDefinedEquipment:
    name: str
    equipment_types: Set[str] = field(default_factory=set)
    alternative_identifiers: Set[str] = field(default_factory=set)
    ip_addresses: List[NetworkConfFilesDefinedIpAddress] = field(default_factory=list)


class EquipmentsLibrary:
    def __init__(self) -> None:
        self.network_conf_files_defined_equipments: List[NetworkConfFilesDefinedEquipment] = []
        self.network_conf_files_defined_equipments_by_id: Dict[str, NetworkConfFilesDefinedEquipment] = {}

    def is_existing_by_name(self, name: str) -> bool:
        return name in self.network_conf_files_defined_equipments_by_id

    def get_existing_by_name(self, name: str) -> Optional["NetworkConfFilesDefinedEquipment"]:
        if self.is_existing_by_name(name):
            return self.network_conf_files_defined_equipments_by_id[name]
        return None

    def get_or_create_if_not_exist_by_name(self, name: str) -> "NetworkConfFilesDefinedEquipment":
        if self.is_existing_by_name(name):
            return self.network_conf_files_defined_equipments_by_id[name]
        equipment = NetworkConfFilesDefinedEquipment(name=name)
        self.network_conf_files_defined_equipments_by_id[name] = equipment
        self.network_conf_files_defined_equipments.append(equipment)

        return equipment


@dataclass
class NetworkConfFile:
    excel_file_full_path: str
    all_equipments: List[NetworkConfFilesDefinedEquipment]


@dataclass
class RadioStdNetworkConfFile(NetworkConfFile):
    ip_definitions_sheet_name: str

    @staticmethod
    def build_with_excel_file(equipments_library: EquipmentsLibrary, excel_file_full_path: str, ip_definitions_sheet_name: str = "IP RESEAU STD RADIO") -> "RadioStdNetworkConfFile":
        with logger_config.stopwatch_with_label(f"Load {excel_file_full_path}", monitor_ram_usage=True, inform_beginning=True):
            main_data_frame = pandas.read_excel(excel_file_full_path, skiprows=[0, 1, 2, 3, 4, 6, 7], sheet_name=ip_definitions_sheet_name)
            logger_config.print_and_log_info(f"{excel_file_full_path} has {len(main_data_frame)} items")
            logger_config.print_and_log_info(f" {excel_file_full_path} columns  {main_data_frame.columns[:4]} ...")

            all_equipments_found: List[NetworkConfFilesDefinedEquipment] = []

            for _, row in main_data_frame.iterrows():
                equipment_type = cast(str, row["Type"])
                equipment_name = cast(str, row["Equipement"])
                equipment_alternative_identifier = cast(str, row["Equip_ID"])
                equipment_vlan = cast(int, row["VLAN ID A"])
                equipment_raw_ip_address = cast(str, row["Anneau A"])
                equipment_raw_mask = cast(str, row["Masque A"])
                equipment_raw_gateway = cast(str, row["Passerelle A"])

                equipment = equipments_library.get_or_create_if_not_exist_by_name(name=equipment_name)
                all_equipments_found.append(equipment)

                equipment.equipment_types.add(equipment_type)

                ip_address = NetworkConfFilesDefinedIpAddress(ip_raw=equipment_raw_ip_address, gateway=equipment_raw_gateway, vlan_name=equipment_vlan, mask=equipment_raw_mask)
                equipment.ip_addresses.append(ip_address)

                equipment.alternative_identifiers.add(equipment_alternative_identifier)

            radio_std_conf_file = RadioStdNetworkConfFile(excel_file_full_path=excel_file_full_path, ip_definitions_sheet_name=ip_definitions_sheet_name, all_equipments=all_equipments_found)

            logger_config.print_and_log_info(f"{excel_file_full_path}: {len(all_equipments_found)} equipment found")

            return radio_std_conf_file
