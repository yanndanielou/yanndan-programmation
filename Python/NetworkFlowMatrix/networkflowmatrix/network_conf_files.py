# import ipaddress
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, cast

import pandas
from common import excel_utils
from logger import logger_config


@dataclass
class NetworkConfFilesDefinedIpAddress(ABC):
    ip_raw: str
    label: Optional[str]

    def check_valid_and_raise_if_error(self) -> None:
        assert self.ip_raw
        assert isinstance(self.ip_raw, str)


@dataclass
class NetworkConfFilesDefinedUnicastIpAddress(NetworkConfFilesDefinedIpAddress):
    mask: str
    gateway: Optional[str]
    vlan_name: str | int

    def check_valid_and_raise_if_error(self) -> None:
        assert self.mask
        assert isinstance(self.mask, str)
        assert self.vlan_name
        assert isinstance(self.vlan_name, str) or isinstance(self.vlan_name, int) or isinstance(self.vlan_name, float)


@dataclass
class NetworkConfFilesDefinedMulticastIpAddress(NetworkConfFilesDefinedIpAddress):
    multicast_group: str


class ExcelColumnDefinition(ABC):

    @abstractmethod
    def get_value(self, row: pandas.Series) -> str | int:
        pass


@dataclass
class ExcelColumnDefinitionByColumnNumber(ExcelColumnDefinition):
    """Index starts at 0"""

    column_index: int

    def get_value(self, row: pandas.Series) -> str | int:
        return cast(str | int, row.values[self.column_index])


class ExcelColumnDefinitionByColumnExcelId(ExcelColumnDefinitionByColumnNumber):

    def __init__(self, column_excel_identifier: str) -> None:
        super().__init__(column_index=excel_utils.xl_column_name_to_index(column_excel_identifier))
        self.column_excel_identifier = column_excel_identifier


@dataclass
class ExcelColumnDefinitionByColumnTitle(ExcelColumnDefinition):
    column_title: str

    def get_value(self, row: pandas.Series) -> str | int:
        assert self.column_title in row, f"Cannot find column with title {self.column_title} among {row.keys}"
        return cast(str | int, row[self.column_title])


@dataclass
class IpDefinitionColumnsInTab(ABC):
    can_be_empty: bool = False
    equipment_ip_address_column_definition: ExcelColumnDefinition = field(default_factory=lambda: ExcelColumnDefinitionByColumnTitle("Adresse IP"))
    forced_label: Optional[str] = None
    all_ip_addresses_found: List[NetworkConfFilesDefinedIpAddress] = field(default_factory=list)

    @abstractmethod
    def build_with_row(self, row: pandas.Series) -> NetworkConfFilesDefinedIpAddress:
        pass


@dataclass
class UnicastIpDefinitionColumnsInTab(IpDefinitionColumnsInTab):
    equipment_vlan_column_definition: ExcelColumnDefinition = field(default_factory=lambda: ExcelColumnDefinitionByColumnTitle("VLAN ID"))
    equipment_mask_column_definition: ExcelColumnDefinition = field(default_factory=lambda: ExcelColumnDefinitionByColumnTitle("Masque"))
    equipment_gateway_column_definition: ExcelColumnDefinition = field(default_factory=lambda: ExcelColumnDefinitionByColumnTitle("Passerelle"))
    gateway_is_optional: bool = False

    def build_with_row(self, row: pandas.Series) -> NetworkConfFilesDefinedIpAddress:
        equipment_raw_ip_address = cast(str, self.equipment_ip_address_column_definition.get_value(row))

        assert equipment_raw_ip_address and isinstance(equipment_raw_ip_address, str), f"\n Ip address: {equipment_raw_ip_address}\nRow: {row}"

        # ip_address = NetworkConfFilesDefinedUnicasttIpAddress(ip_raw=)
        equipment_vlan = cast(int, self.equipment_vlan_column_definition.get_value(row))

        assert equipment_vlan
        assert (
            isinstance(equipment_vlan, str) or isinstance(equipment_vlan, int) or isinstance(equipment_vlan, float)
        ), f"{row} {self.equipment_gateway_column_definition} column {self.equipment_vlan_column_definition} is {equipment_vlan}"

        equipment_ip_label = self.forced_label

        equipment_raw_mask = cast(str, self.equipment_mask_column_definition.get_value(row))
        assert equipment_raw_mask and isinstance(equipment_raw_mask, str)

        equipment_raw_gateway: Optional[str] = cast(str, self.equipment_gateway_column_definition.get_value(row))
        if not isinstance(equipment_raw_gateway, str):
            equipment_raw_gateway = None
        assert self.gateway_is_optional or equipment_raw_gateway and isinstance(equipment_raw_gateway, str), f"{equipment_raw_ip_address} has no gateway"

        ip_address = NetworkConfFilesDefinedUnicastIpAddress(
            ip_raw=equipment_raw_ip_address, gateway=equipment_raw_gateway, vlan_name=equipment_vlan, mask=equipment_raw_mask, label=equipment_ip_label
        )
        self.all_ip_addresses_found.append(ip_address)
        return ip_address


@dataclass
class MulticastIpDefinitionColumnsInTab(IpDefinitionColumnsInTab):
    group_multicast: str = ""

    def build_with_row(self, row: pandas.Series) -> NetworkConfFilesDefinedIpAddress:
        equipment_raw_ip_address = cast(str, self.equipment_ip_address_column_definition.get_value(row))
        assert equipment_raw_ip_address and isinstance(equipment_raw_ip_address, str), f"\n Ip address: {equipment_raw_ip_address}\nRow: {row}"

        equipment_ip_label = self.forced_label

        ip_address = NetworkConfFilesDefinedMulticastIpAddress(ip_raw=equipment_raw_ip_address, label=equipment_ip_label, multicast_group=self.group_multicast)
        self.all_ip_addresses_found.append(ip_address)
        return ip_address


@dataclass
class EquipmentDefinitionTab:
    tab_name: str
    rows_to_ignore: List[int]
    equipment_type_column_definition: ExcelColumnDefinition = field(default_factory=lambda: ExcelColumnDefinitionByColumnTitle("Type"))
    equipment_ip_definitions: List["IpDefinitionColumnsInTab"] = field(default_factory=list)
    equipment_name_column_definition: ExcelColumnDefinition = field(default_factory=lambda: ExcelColumnDefinitionByColumnTitle("Equipement"))
    equipment_alternative_name_column_definition: ExcelColumnDefinition = field(default_factory=lambda: ExcelColumnDefinitionByColumnTitle("Equip_ID"))


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

                    ip_address = NetworkConfFilesDefinedUnicastIpAddress(
                        ip_raw=equipment_raw_ip_address, gateway=equipment_raw_gateway, vlan_name=equipment_vlan, mask=equipment_raw_mask, label="Anneau A"
                    )
                    equipment.ip_addresses.append(ip_address)

                    assert len(equipment.ip_addresses) < 3

                    equipment.alternative_identifiers.add(equipment_alternative_identifier)

                radio_std_conf_file = RadioStdNetworkConfFile(
                    equipments_library=equipments_library, excel_file_full_path=excel_file_full_path, ip_definitions_sheet_name=ip_definitions_sheet_name, all_equipments=all_equipments_found
                )

                logger_config.print_and_log_info(f"{excel_file_full_path}: {len(all_equipments_found)} equipment found")

                return radio_std_conf_file


class SolStdNetworkConfV10Description:
    def __init__(self) -> None:

        self.ip_ats_tab: EquipmentDefinitionTab = EquipmentDefinitionTab(
            tab_name="IP ATS",
            equipment_name_column_definition=ExcelColumnDefinitionByColumnTitle("Equipement"),
            rows_to_ignore=[0, 1, 2, 3, 4, 6, 7],
            equipment_ip_definitions=[UnicastIpDefinitionColumnsInTab(equipment_ip_address_column_definition=ExcelColumnDefinitionByColumnTitle("Adresse IP"))],
        )
        self.ip_reseau_std_tab: EquipmentDefinitionTab = EquipmentDefinitionTab(
            tab_name="IP RESEAU STD",
            equipment_name_column_definition=ExcelColumnDefinitionByColumnTitle("Equipement"),
            rows_to_ignore=[0, 1, 2, 3, 4, 6, 7],
            equipment_ip_definitions=[
                UnicastIpDefinitionColumnsInTab(
                    equipment_vlan_column_definition=ExcelColumnDefinitionByColumnTitle("VLAN ID A"),
                    equipment_ip_address_column_definition=ExcelColumnDefinitionByColumnTitle("Anneau A"),
                    equipment_mask_column_definition=ExcelColumnDefinitionByColumnTitle("Masque A"),
                    equipment_gateway_column_definition=ExcelColumnDefinitionByColumnTitle("Passerelle A"),
                    forced_label="Anneau A",
                    can_be_empty=True,
                ),
                UnicastIpDefinitionColumnsInTab(
                    equipment_vlan_column_definition=ExcelColumnDefinitionByColumnTitle("VLAN ID B"),
                    equipment_ip_address_column_definition=ExcelColumnDefinitionByColumnTitle("Anneau B"),
                    equipment_mask_column_definition=ExcelColumnDefinitionByColumnTitle("Masque B"),
                    equipment_gateway_column_definition=ExcelColumnDefinitionByColumnTitle("Passerelle B"),
                    forced_label="Anneau B",
                    can_be_empty=True,
                ),
            ],
        )
        self.ip_cbtc_tab: EquipmentDefinitionTab = EquipmentDefinitionTab(
            tab_name="IP CBTC",
            equipment_name_column_definition=ExcelColumnDefinitionByColumnTitle("Equipement"),
            rows_to_ignore=[0, 1, 2, 3, 4, 6, 7],
            equipment_ip_definitions=[
                UnicastIpDefinitionColumnsInTab(
                    equipment_vlan_column_definition=ExcelColumnDefinitionByColumnTitle("VLAN ID A"),
                    equipment_ip_address_column_definition=ExcelColumnDefinitionByColumnExcelId("G"),
                    equipment_mask_column_definition=ExcelColumnDefinitionByColumnTitle("Masque A"),
                    equipment_gateway_column_definition=ExcelColumnDefinitionByColumnTitle("Passerelle A"),
                    forced_label="Anneau A Unite A",
                    can_be_empty=True,
                ),
                UnicastIpDefinitionColumnsInTab(
                    equipment_vlan_column_definition=ExcelColumnDefinitionByColumnTitle("VLAN ID A"),
                    equipment_ip_address_column_definition=ExcelColumnDefinitionByColumnExcelId("H"),
                    equipment_mask_column_definition=ExcelColumnDefinitionByColumnTitle("Masque A"),
                    equipment_gateway_column_definition=ExcelColumnDefinitionByColumnTitle("Passerelle A"),
                    forced_label="Anneau A Unite B",
                    can_be_empty=True,
                ),
                UnicastIpDefinitionColumnsInTab(
                    equipment_vlan_column_definition=ExcelColumnDefinitionByColumnTitle("VLAN ID B"),
                    equipment_ip_address_column_definition=ExcelColumnDefinitionByColumnExcelId("M"),
                    equipment_mask_column_definition=ExcelColumnDefinitionByColumnTitle("Masque B"),
                    equipment_gateway_column_definition=ExcelColumnDefinitionByColumnTitle("Passerelle B"),
                    forced_label="Anneau B Unite A",
                    can_be_empty=True,
                ),
                UnicastIpDefinitionColumnsInTab(
                    equipment_vlan_column_definition=ExcelColumnDefinitionByColumnTitle("VLAN ID B"),
                    equipment_ip_address_column_definition=ExcelColumnDefinitionByColumnExcelId("N"),
                    equipment_mask_column_definition=ExcelColumnDefinitionByColumnTitle("Masque B"),
                    equipment_gateway_column_definition=ExcelColumnDefinitionByColumnTitle("Passerelle B"),
                    forced_label="Anneau B Unite B",
                    can_be_empty=True,
                ),
                MulticastIpDefinitionColumnsInTab(
                    equipment_ip_address_column_definition=ExcelColumnDefinitionByColumnExcelId("R"), forced_label="Multicast", can_be_empty=True, group_multicast="239.192.0.0"
                ),
            ],
        )
        self.ip_mats: EquipmentDefinitionTab = EquipmentDefinitionTab(
            tab_name="IP MATS",
            equipment_name_column_definition=ExcelColumnDefinitionByColumnTitle("Equipement"),
            rows_to_ignore=[0, 1, 2, 3, 4, 6, 7],
            equipment_ip_definitions=[
                UnicastIpDefinitionColumnsInTab(
                    equipment_vlan_column_definition=ExcelColumnDefinitionByColumnTitle("VLAN ID A"),
                    equipment_ip_address_column_definition=ExcelColumnDefinitionByColumnExcelId("G"),
                    equipment_mask_column_definition=ExcelColumnDefinitionByColumnTitle("Masque A"),
                    equipment_gateway_column_definition=ExcelColumnDefinitionByColumnTitle("Passerelle A"),
                    forced_label="Anneau A Unite A",
                    can_be_empty=True,
                ),
                UnicastIpDefinitionColumnsInTab(
                    equipment_vlan_column_definition=ExcelColumnDefinitionByColumnTitle("VLAN ID A"),
                    equipment_ip_address_column_definition=ExcelColumnDefinitionByColumnExcelId("H"),
                    equipment_mask_column_definition=ExcelColumnDefinitionByColumnTitle("Masque A"),
                    equipment_gateway_column_definition=ExcelColumnDefinitionByColumnTitle("Passerelle A"),
                    forced_label="Anneau A Unite B",
                    can_be_empty=True,
                ),
                UnicastIpDefinitionColumnsInTab(
                    equipment_vlan_column_definition=ExcelColumnDefinitionByColumnTitle("VLAN ID B"),
                    equipment_ip_address_column_definition=ExcelColumnDefinitionByColumnExcelId("M"),
                    equipment_mask_column_definition=ExcelColumnDefinitionByColumnTitle("Masque B"),
                    equipment_gateway_column_definition=ExcelColumnDefinitionByColumnTitle("Passerelle B"),
                    forced_label="Anneau B Unite A",
                    can_be_empty=True,
                ),
                UnicastIpDefinitionColumnsInTab(
                    equipment_vlan_column_definition=ExcelColumnDefinitionByColumnTitle("VLAN ID B"),
                    equipment_ip_address_column_definition=ExcelColumnDefinitionByColumnExcelId("N"),
                    equipment_mask_column_definition=ExcelColumnDefinitionByColumnTitle("Masque B"),
                    equipment_gateway_column_definition=ExcelColumnDefinitionByColumnTitle("Passerelle B"),
                    forced_label="Anneau B Unite B",
                    can_be_empty=True,
                ),
            ],
        )
        self.ip_reseau_pcc: EquipmentDefinitionTab = EquipmentDefinitionTab(
            tab_name="IP RESEAU PCC",
            rows_to_ignore=[0, 1, 2, 4, 5],
            equipment_ip_definitions=[
                UnicastIpDefinitionColumnsInTab(can_be_empty=True, gateway_is_optional=True),
            ],
        )
        self.ip_csr_tab: EquipmentDefinitionTab = EquipmentDefinitionTab(
            tab_name="IP CSR",
            equipment_name_column_definition=ExcelColumnDefinitionByColumnTitle("Equipement"),
            rows_to_ignore=[0, 1, 2, 3, 4, 6, 7],
            equipment_ip_definitions=[
                UnicastIpDefinitionColumnsInTab(
                    equipment_vlan_column_definition=ExcelColumnDefinitionByColumnTitle("VLAN ID A"),
                    equipment_ip_address_column_definition=ExcelColumnDefinitionByColumnTitle("Anneau A"),
                    equipment_mask_column_definition=ExcelColumnDefinitionByColumnTitle("Masque A"),
                    equipment_gateway_column_definition=ExcelColumnDefinitionByColumnTitle("Passerelle A"),
                    forced_label="Anneau A Unite A",
                    can_be_empty=True,
                ),
                UnicastIpDefinitionColumnsInTab(
                    equipment_vlan_column_definition=ExcelColumnDefinitionByColumnTitle("VLAN ID B"),
                    equipment_ip_address_column_definition=ExcelColumnDefinitionByColumnTitle("Anneau B"),
                    equipment_mask_column_definition=ExcelColumnDefinitionByColumnTitle("Masque B"),
                    equipment_gateway_column_definition=ExcelColumnDefinitionByColumnTitle("Passerelle B"),
                    forced_label="Anneau B Unite A",
                    can_be_empty=True,
                ),
                MulticastIpDefinitionColumnsInTab(
                    equipment_ip_address_column_definition=ExcelColumnDefinitionByColumnTitle("@IP multicast"), forced_label="Multicast", can_be_empty=True, group_multicast="239.192.0.0"
                ),
            ],
        )
        self.all_tabs_definition = [self.ip_ats_tab, self.ip_reseau_std_tab, self.ip_cbtc_tab, self.ip_mats, self.ip_reseau_pcc, self.ip_csr_tab]


@dataclass
class SolStdNetworkConfFile(NetworkConfFile):

    equipment_definition_tabs: List[EquipmentDefinitionTab]

    class Builder:

        @staticmethod
        def build_with_excel_file(equipments_library: EquipmentsLibrary, excel_file_full_path: str, equipment_definition_tabs: List[EquipmentDefinitionTab]) -> "SolStdNetworkConfFile":
            """SolStdNetworkConfFile.EquipmentDefinitionTab(tab_name="", row_to_ignore=[0, 1, 2, 3, 4, 6, 7]),
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

                with logger_config.stopwatch_with_label(f"Load {excel_file_full_path} sheet {equipment_definition_tab.tab_name}", monitor_ram_usage=True, inform_beginning=True):
                    main_data_frame = pandas.read_excel(excel_file_full_path, skiprows=equipment_definition_tab.rows_to_ignore, sheet_name=equipment_definition_tab.tab_name)
                    logger_config.print_and_log_info(f"{excel_file_full_path} {equipment_definition_tab.tab_name} has {len(main_data_frame)} items")
                    logger_config.print_and_log_info(f" {excel_file_full_path} {equipment_definition_tab.tab_name} columns  {main_data_frame.columns[:4]} ...")

                    all_equipments_found: List[NetworkConfFilesDefinedEquipment] = []

                    for _, row in main_data_frame.iterrows():

                        equipment_name = cast(str, equipment_definition_tab.equipment_name_column_definition.get_value(row))
                        equipment = equipments_library.get_or_create_if_not_exist_by_name(name=equipment_name)
                        all_equipments_found.append(equipment)

                        equipment_type = cast(str, equipment_definition_tab.equipment_type_column_definition.get_value(row))
                        equipment.equipment_types.add(equipment_type)

                        equipment_alternative_identifier = cast(str, equipment_definition_tab.equipment_alternative_name_column_definition.get_value(row))
                        equipment.alternative_identifiers.add(equipment_alternative_identifier)

                        for ip_address_definition in equipment_definition_tab.equipment_ip_definitions:

                            equipment_raw_ip_address = cast(str, ip_address_definition.equipment_ip_address_column_definition.get_value(row))
                            if not isinstance(equipment_raw_ip_address, str) and ip_address_definition.can_be_empty:
                                continue

                            ip_address = ip_address_definition.build_with_row(row)

                            equipment.ip_addresses.append(ip_address)
                            assert len(equipment.ip_addresses) < 10, f"{equipment_name}\n{[ip.ip_raw for ip in equipment.ip_addresses]}\n\n{equipment}"

                    for ip_address_definition in equipment_definition_tab.equipment_ip_definitions:
                        assert ip_address_definition.all_ip_addresses_found
                        assert len(ip_address_definition.all_ip_addresses_found) > 1

                    logger_config.print_and_log_info(f"{excel_file_full_path} tab {equipment_definition_tab.tab_name}: {len(all_equipments_found)} equipment found")

            radio_std_conf_file = SolStdNetworkConfFile(
                equipments_library=equipments_library, excel_file_full_path=excel_file_full_path, all_equipments=all_equipments_found, equipment_definition_tabs=equipment_definition_tabs
            )

            logger_config.print_and_log_info(f"{excel_file_full_path}: {len(all_equipments_found)} equipment found")

            return radio_std_conf_file
