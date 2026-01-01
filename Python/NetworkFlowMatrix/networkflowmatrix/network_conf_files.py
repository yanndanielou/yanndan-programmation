# import ipaddress
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List, Optional, cast
import pandas

from common import excel_utils
from logger import logger_config


if TYPE_CHECKING:
    from networkflowmatrix.equipments import TrainUnbreakableSingleUnit, Equipment, NetworkConfFilesEquipmentsLibrary, NetworkConfFilesDefinedEquipment
    from networkflowmatrix.network_conf_files_descriptions_data import ExcelInputFileDescription


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
    gateway_is_optional: bool
    mask_is_optional: bool

    def check_valid_and_raise_if_error(self) -> None:
        assert self.mask_is_optional or self.mask
        assert self.mask_is_optional or isinstance(self.mask, str)
        assert self.gateway_is_optional or self.gateway
        assert self.gateway_is_optional or isinstance(self.gateway, str)
        assert self.vlan_name
        assert isinstance(self.vlan_name, str) or isinstance(self.vlan_name, int) or isinstance(self.vlan_name, float)


@dataclass
class NetworkConfFilesDefinedMulticastIpAddress(NetworkConfFilesDefinedIpAddress):
    multicast_group: str


class InformationDefinitionBase(ABC):
    @abstractmethod
    def get_value(self, row: pandas.Series) -> Optional[str] | Optional[int]:
        pass


class ForcedNoneValueInformationDefinition(InformationDefinitionBase):

    def get_value(self, row: pandas.Series) -> Optional[str] | Optional[int]:
        return None


@dataclass
class ForcedIntValueInformationDefinition(InformationDefinitionBase):
    value: Optional[int]

    def get_value(self, row: pandas.Series) -> Optional[str] | Optional[int]:
        return self.value


@dataclass
class ForcedStrValueInformationDefinition(InformationDefinitionBase):
    value: Optional[str]


@dataclass
class ExcelColumnDefinitionByColumnNumber(InformationDefinitionBase):
    """Index starts at 0"""

    column_index: int

    def get_value(self, row: pandas.Series) -> str | int:
        return cast(str | int, row.values[self.column_index])


class ExcelColumnDefinitionByColumnExcelId(ExcelColumnDefinitionByColumnNumber):

    def __init__(self, column_excel_identifier: str) -> None:
        super().__init__(column_index=excel_utils.xl_column_name_to_index(column_excel_identifier))
        self.column_excel_identifier = column_excel_identifier


@dataclass
class ExcelColumnDefinitionByColumnTitle(InformationDefinitionBase):
    column_title: str

    def get_value(self, row: pandas.Series) -> str | int:
        assert self.column_title in row, f"Cannot find column with title {self.column_title} among {row.keys}"
        return cast(str | int, row[self.column_title])


@dataclass
class IpDefinitionColumnsInTab(ABC):
    can_be_empty: bool = False
    equipment_ip_address_column_definition: InformationDefinitionBase = field(default_factory=lambda: ExcelColumnDefinitionByColumnTitle("Adresse IP"))
    forced_label: Optional[str] = None
    all_ip_addresses_found: List[NetworkConfFilesDefinedIpAddress] = field(default_factory=list)

    @abstractmethod
    def build_with_row(self, row: pandas.Series) -> NetworkConfFilesDefinedIpAddress:
        pass


@dataclass
class UnicastIpDefinitionColumnsInTab(IpDefinitionColumnsInTab):
    equipment_vlan_column_definition: InformationDefinitionBase = field(default_factory=lambda: ExcelColumnDefinitionByColumnTitle("VLAN ID"))
    equipment_mask_column_definition: InformationDefinitionBase = field(default_factory=lambda: ExcelColumnDefinitionByColumnTitle("Masque"))
    equipment_gateway_column_definition: InformationDefinitionBase = field(default_factory=lambda: ExcelColumnDefinitionByColumnTitle("Passerelle"))
    gateway_is_optional: bool = False
    mask_is_optional: bool = False

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
        assert self.mask_is_optional or equipment_raw_mask and isinstance(equipment_raw_mask, str)

        equipment_raw_gateway: Optional[str] = cast(str, self.equipment_gateway_column_definition.get_value(row))
        if not isinstance(equipment_raw_gateway, str):
            equipment_raw_gateway = None
        assert self.gateway_is_optional or equipment_raw_gateway and isinstance(equipment_raw_gateway, str), f"{equipment_raw_ip_address} has no gateway"

        ip_address = NetworkConfFilesDefinedUnicastIpAddress(
            ip_raw=equipment_raw_ip_address,
            gateway=equipment_raw_gateway,
            vlan_name=equipment_vlan,
            mask=equipment_raw_mask,
            label=equipment_ip_label,
            gateway_is_optional=self.gateway_is_optional,
            mask_is_optional=self.mask_is_optional,
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
    equipment_type_column_definition: InformationDefinitionBase = field(default_factory=lambda: ExcelColumnDefinitionByColumnTitle("Type"))
    equipment_ip_definitions: List["IpDefinitionColumnsInTab"] = field(default_factory=list)
    equipment_name_column_definition: InformationDefinitionBase = field(default_factory=lambda: ExcelColumnDefinitionByColumnTitle("Equipement"))
    equipment_alternative_name_column_definition: InformationDefinitionBase = field(default_factory=lambda: ExcelColumnDefinitionByColumnTitle("Equip_ID"))


class TrainIdentifierDefinition(ABC):

    @abstractmethod
    def get_train(self, row: pandas.Series, equipment_library: "NetworkConfFilesEquipmentsLibrary") -> "TrainUnbreakableSingleUnit":
        pass


class TrainByCcIdColumnDefinition(TrainIdentifierDefinition):

    def __init__(self) -> None:
        self.cc_id_column_definition: InformationDefinitionBase = ExcelColumnDefinitionByColumnTitle("Type")

    def get_train(self, row: pandas.Series, equipment_library: "NetworkConfFilesEquipmentsLibrary") -> "TrainUnbreakableSingleUnit":
        cc_id = self.cc_id_column_definition.get_value(row)
        assert cc_id
        assert isinstance(cc_id, int)
        train = equipment_library.get_existing_train_unbreakable_unit_by_cc_id(cc_id=cc_id)
        assert train
        return train


class TrainByEmuIdColumnDefinition(TrainIdentifierDefinition):

    def __init__(self) -> None:
        self.emu_id_column_definition: InformationDefinitionBase = ExcelColumnDefinitionByColumnTitle("Type")

    def get_train(self, row: pandas.Series, equipment_library: "NetworkConfFilesEquipmentsLibrary") -> "TrainUnbreakableSingleUnit":
        emu_id = self.emu_id_column_definition.get_value(row)
        assert emu_id
        assert isinstance(emu_id, int)
        train = equipment_library.get_existing_train_unbreakable_unit_by_emu_id(emu_id=emu_id)
        assert train
        return train


@dataclass
class InsideTrainEquipmentDefinitionTab(EquipmentDefinitionTab):
    train_identifier_definition: TrainIdentifierDefinition = field(default_factory=TrainByCcIdColumnDefinition)


@dataclass
class GenericConfFile:
    all_equipments: List["NetworkConfFilesDefinedEquipment"]
    equipments_library: "NetworkConfFilesEquipmentsLibrary"
    name: str

    def __post_init__(self) -> None:
        logger_config.print_and_log_info(f"{self.name}: {len(self.all_equipments)} equipment found")
        logger_config.print_and_log_info(f"So far, the library contains {len(self.equipments_library.all_network_conf_files_defined_equipments)} equipments in total")


@dataclass
class NetworkConfFile(GenericConfFile):
    excel_file_full_path: str
    equipment_definition_tabs: List[EquipmentDefinitionTab]

    class Builder:

        @staticmethod
        def build_with_excel_descriptions(equipments_library: "NetworkConfFilesEquipmentsLibrary", excel_descriptions: List["ExcelInputFileDescription"]) -> List["NetworkConfFile"]:
            network_conf_files: List["NetworkConfFile"] = []
            for excel_description in excel_descriptions:
                network_conf_files.append(NetworkConfFile.Builder.build_with_excel_description(equipments_library, excel_description))
            return network_conf_files

        @staticmethod
        def build_with_excel_description(equipments_library: "NetworkConfFilesEquipmentsLibrary", excel_description: "ExcelInputFileDescription") -> "NetworkConfFile":
            return NetworkConfFile.Builder.build_with_excel_file(equipments_library, excel_description.excel_file_full_path, excel_description.all_tabs_definition)

        @staticmethod
        def build_with_excel_file(equipments_library: "NetworkConfFilesEquipmentsLibrary", excel_file_full_path: str, equipment_definition_tabs: List[EquipmentDefinitionTab]) -> "NetworkConfFile":

            for equipment_definition_tab in equipment_definition_tabs:

                with logger_config.stopwatch_with_label(f"Load {excel_file_full_path} sheet {equipment_definition_tab.tab_name}", monitor_ram_usage=True, inform_beginning=True):
                    main_data_frame = pandas.read_excel(excel_file_full_path, skiprows=equipment_definition_tab.rows_to_ignore, sheet_name=equipment_definition_tab.tab_name)
                    logger_config.print_and_log_info(f"{excel_file_full_path} {equipment_definition_tab.tab_name} has {len(main_data_frame)} items")
                    logger_config.print_and_log_info(f" {excel_file_full_path} {equipment_definition_tab.tab_name} columns  {main_data_frame.columns[:4]} ...")

                    all_equipments_found: List[NetworkConfFilesDefinedEquipment] = []

                    for usefull_raw_number, row in main_data_frame.iterrows():

                        equipment_name = cast(str, equipment_definition_tab.equipment_name_column_definition.get_value(row))

                        if isinstance(equipment_name, str):
                            equipment = equipments_library.get_or_create_network_conf_file_eqpt_if_not_exist_by_name(
                                name=equipment_name, source_label_for_creation=f"{excel_file_full_path}/{equipment_definition_tab.tab_name}"
                            )
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

                                equipment.add_ip_address(ip_address)
                                assert len(equipment.ip_addresses) < 10, f"{equipment_name}\n{[ip.ip_raw for ip in equipment.ip_addresses]}\n\n{equipment}"
                        else:
                            logger_config.print_and_log_error(
                                f"In {excel_file_full_path} tab {equipment_definition_tab.tab_name} Could not create {usefull_raw_number+1}th object with invalid id {equipment_name} for row {row}"
                            )

                    for ip_address_definition in equipment_definition_tab.equipment_ip_definitions:
                        assert ip_address_definition.all_ip_addresses_found
                        assert len(ip_address_definition.all_ip_addresses_found) > 1

                    logger_config.print_and_log_info(f"{excel_file_full_path} tab {equipment_definition_tab.tab_name}: {len(all_equipments_found)} equipment found")

            conf_file = NetworkConfFile(
                name=excel_file_full_path,
                equipments_library=equipments_library,
                excel_file_full_path=excel_file_full_path,
                all_equipments=all_equipments_found,
                equipment_definition_tabs=equipment_definition_tabs,
            )

            logger_config.print_and_log_info(f"{excel_file_full_path}: {len(all_equipments_found)} equipment found")
            logger_config.print_and_log_info(f"So far, the library contains {len(equipments_library.all_network_conf_files_defined_equipments)} equipments in total")

            return conf_file
