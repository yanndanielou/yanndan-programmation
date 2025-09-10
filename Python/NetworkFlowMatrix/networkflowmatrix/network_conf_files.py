# import ipaddress
from dataclasses import dataclass, field
from typing import List, Optional, Set, cast, Dict

from abc import ABC, abstractmethod

import pandas
from logger import logger_config


@dataclass
class IpDefinitionColumnsInTab:
    can_be_empty: bool = False
    equipment_vlan_column_name: str = "VLAN ID"
    equipment_ip_address_column_name: str = "Adresse IP"
    equipment_mask_column_name: str = "Masque"
    equipment_gateway_column_name: str = "Passerelle"
    label_column_name: Optional[str] = None
    forced_label: Optional[str] = None


@dataclass
class EquipmentDefinitionTab:
    tab_name: str
    rows_to_ignore: List[int]
    equipment_type_column_name: str = "Type"
    equipment_ip_definitions: List["IpDefinitionColumnsInTab"] = field(default_factory=list)
    equipment_name_column_name: str = "Equipement"
    equipment_alternative_name_column_name: str = "Equip_ID"


@dataclass
class NetworkConfFilesDefinedIpAddress:
    ip_raw: str
    mask: str
    gateway: str
    vlan_name: str | int
    label: Optional[str]


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
    equipments_library: EquipmentsLibrary


class ExcelColumnDefinition(ABC):

    @abstractmethod
    def get_value(self, row: pandas.Series) -> str | int:
        pass


@dataclass
class ExcelColumnDefinitionByColumnExcelId(ExcelColumnDefinition):
    column_excel_identifier: str

    def get_value(self, row: pandas.Series) -> str | int:
        return cast(str | int, row[self.column_excel_identifier])


@dataclass
class ExcelColumnDefinitionByColumnNumber(ExcelColumnDefinition):
    column_number: int

    def get_value(self, row: pandas.Series) -> str | int:
        pass
        return cast(str | int, row.get(self.column_number))


@dataclass
class ExcelColumnDefinitionByColumnTitle(ExcelColumnDefinition):
    column_title: str

    def get_value(self, row: pandas.Series) -> str | int:
        return cast(str | int, row[self.column_title])


@dataclass
class RadioStdNetworkConfFile(NetworkConfFile):
    ip_definitions_sheet_name: str

    class Builder:

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

                    ip_address = NetworkConfFilesDefinedIpAddress(ip_raw=equipment_raw_ip_address, gateway=equipment_raw_gateway, vlan_name=equipment_vlan, mask=equipment_raw_mask, label="Anneau A")
                    equipment.ip_addresses.append(ip_address)

                    assert len(equipment.ip_addresses) < 3

                    equipment.alternative_identifiers.add(equipment_alternative_identifier)

                radio_std_conf_file = RadioStdNetworkConfFile(
                    equipments_library=equipments_library, excel_file_full_path=excel_file_full_path, ip_definitions_sheet_name=ip_definitions_sheet_name, all_equipments=all_equipments_found
                )

                logger_config.print_and_log_info(f"{excel_file_full_path}: {len(all_equipments_found)} equipment found")

                return radio_std_conf_file


@dataclass
class SolStdNetworkConfFile(NetworkConfFile):

    class Builder:

        @staticmethod
        def build_with_excel_file(
            equipments_library: EquipmentsLibrary, excel_file_full_path: str, equipment_definition_tabs: Optional[List[EquipmentDefinitionTab]] = None
        ) -> "SolStdNetworkConfFile":
            if equipment_definition_tabs is None:
                equipment_definition_tabs = [
                    EquipmentDefinitionTab(
                        tab_name="IP ATS",
                        equipment_name_column_name="Equipement",
                        rows_to_ignore=[0, 1, 2, 3, 4, 6, 7],
                        equipment_ip_definitions=[IpDefinitionColumnsInTab(equipment_ip_address_column_name="Adresse IP")],
                    ),
                    EquipmentDefinitionTab(
                        tab_name="IP RESEAU STD",
                        equipment_name_column_name="Equipement",
                        rows_to_ignore=[0, 1, 2, 3, 4, 6, 7],
                        equipment_ip_definitions=[
                            IpDefinitionColumnsInTab(
                                equipment_vlan_column_name="VLAN ID A",
                                equipment_ip_address_column_name="Anneau A",
                                equipment_mask_column_name="Masque A",
                                equipment_gateway_column_name="Passerelle A",
                                forced_label="Anneau A",
                                can_be_empty=True,
                            ),
                            IpDefinitionColumnsInTab(
                                equipment_vlan_column_name="VLAN ID B",
                                equipment_ip_address_column_name="Anneau B",
                                equipment_mask_column_name="Masque B",
                                equipment_gateway_column_name="Passerelle B",
                                forced_label="Anneau B",
                                can_be_empty=True,
                            ),
                        ],
                    ),
                    EquipmentDefinitionTab(
                        tab_name="IP CBTC",
                        equipment_name_column_name="Equipement",
                        rows_to_ignore=[0, 1, 2, 3, 4, 6, 7],
                        equipment_ip_definitions=[
                            IpDefinitionColumnsInTab(
                                equipment_vlan_column_name="VLAN ID A",
                                equipment_ip_address_column_name="Anneau A",
                                equipment_mask_column_name="Masque A",
                                equipment_gateway_column_name="Passerelle A",
                                forced_label="Anneau A",
                            ),
                            IpDefinitionColumnsInTab(
                                equipment_vlan_column_name="VLAN ID B",
                                equipment_ip_address_column_name="Anneau A",
                                equipment_mask_column_name="Masque B",
                                equipment_gateway_column_name="Passerelle B",
                                forced_label="Anneau B",
                            ),
                        ],
                    ),
                ]
            """                SolStdNetworkConfFile.EquipmentDefinitionTab(tab_name="", row_to_ignore=[0, 1, 2, 3, 4, 6, 7]),
                    SolStdNetworkConfFile.EquipmentDefinitionTab(tab_name="IP CBTC", row_to_ignore=[0, 1, 2, 3, 4, 6, 7]),
                    SolStdNetworkConfFile.EquipmentDefinitionTab(tab_name="IP MATS", row_to_ignore=[0, 1, 2, 3, 4, 6, 7]),
                    SolStdNetworkConfFile.EquipmentDefinitionTab(tab_name="IP RESEAU PCC", row_to_ignore=[0, 1, 2, 3, 4, 6, 7]),
                    SolStdNetworkConfFile.EquipmentDefinitionTab(tab_name="IP CSR", row_to_ignore=[0, 1, 2, 3, 4, 6, 7]),
                    SolStdNetworkConfFile.EquipmentDefinitionTab(tab_name="IP PMB", row_to_ignore=[0, 1, 2, 3, 4, 6, 7]),
                    SolStdNetworkConfFile.EquipmentDefinitionTab(tab_name="IP PAI", row_to_ignore=[0, 1, 2, 3, 4, 6, 7]),

            Returns:
                _type_: _description_
            """
            for equipment_definition_tab in equipment_definition_tabs:

                with logger_config.stopwatch_with_label(f"Load {excel_file_full_path}", monitor_ram_usage=True, inform_beginning=True):
                    main_data_frame = pandas.read_excel(excel_file_full_path, skiprows=equipment_definition_tab.rows_to_ignore, sheet_name=equipment_definition_tab.tab_name)
                    logger_config.print_and_log_info(f"{excel_file_full_path} {equipment_definition_tab.tab_name} has {len(main_data_frame)} items")
                    logger_config.print_and_log_info(f" {excel_file_full_path} {equipment_definition_tab.tab_name} columns  {main_data_frame.columns[:4]} ...")

                    all_equipments_found: List[NetworkConfFilesDefinedEquipment] = []

                    for _, row in main_data_frame.iterrows():

                        equipment_name = cast(str, row[equipment_definition_tab.equipment_name_column_name])
                        equipment = equipments_library.get_or_create_if_not_exist_by_name(name=equipment_name)
                        all_equipments_found.append(equipment)

                        equipment_type = cast(str, row[equipment_definition_tab.equipment_type_column_name])
                        equipment.equipment_types.add(equipment_type)

                        equipment_alternative_identifier = cast(str, row[equipment_definition_tab.equipment_alternative_name_column_name])
                        equipment.alternative_identifiers.add(equipment_alternative_identifier)

                        for ip_address_definition in equipment_definition_tab.equipment_ip_definitions:

                            equipment_raw_ip_address = cast(str, row[ip_address_definition.equipment_ip_address_column_name])
                            if not isinstance(equipment_raw_ip_address, str) and ip_address_definition.can_be_empty:
                                continue

                            equipment_vlan = cast(int, row[ip_address_definition.equipment_vlan_column_name])

                            assert equipment_vlan
                            assert (
                                isinstance(equipment_vlan, str) or isinstance(equipment_vlan, int) or isinstance(equipment_vlan, float)
                            ), f"{equipment_name} {ip_address_definition.equipment_gateway_column_name} column {ip_address_definition.equipment_vlan_column_name} is {equipment_vlan} "

                            assert equipment_raw_ip_address and isinstance(
                                equipment_raw_ip_address, str
                            ), f"\n Ip address: {equipment_raw_ip_address}\n tab:{equipment_definition_tab}\n Equipment: {equipment}\nRow: {row}"

                            equipment_ip_label = cast(str, row[ip_address_definition.label_column_name]) if ip_address_definition.label_column_name else None

                            equipment_raw_mask = cast(str, row[ip_address_definition.equipment_mask_column_name])
                            assert equipment_raw_mask and isinstance(equipment_raw_mask, str)

                            equipment_raw_gateway = cast(str, row[ip_address_definition.equipment_gateway_column_name])
                            assert equipment_raw_gateway and isinstance(equipment_raw_gateway, str)

                            ip_address = NetworkConfFilesDefinedIpAddress(
                                ip_raw=equipment_raw_ip_address, gateway=equipment_raw_gateway, vlan_name=equipment_vlan, mask=equipment_raw_mask, label=equipment_ip_label
                            )
                            equipment.ip_addresses.append(ip_address)
                            assert len(equipment.ip_addresses) < 7, f"{equipment_name} {equipment} {equipment.ip_addresses}"

                    logger_config.print_and_log_info(f"{excel_file_full_path} {equipment_definition_tab.tab_name}: {len(all_equipments_found)} equipment found")

            radio_std_conf_file = SolStdNetworkConfFile(equipments_library=equipments_library, excel_file_full_path=excel_file_full_path, all_equipments=all_equipments_found)

            logger_config.print_and_log_info(f"{excel_file_full_path}: {len(all_equipments_found)} equipment found")

            return radio_std_conf_file
