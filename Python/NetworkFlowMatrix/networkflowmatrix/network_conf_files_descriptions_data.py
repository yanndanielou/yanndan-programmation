import os
from dataclasses import dataclass
from typing import List

from common import file_name_utils

from networkflowmatrix.network_conf_files import (
    EquipmentDefinitionTab,
    ExcelColumnDefinitionByColumnExcelId,
    ExcelColumnDefinitionByColumnTitle,
    ForcedStrValueInformationDefinition,
    InsideTrainEquipmentDefinitionTab,
    MulticastIpDefinitionColumnsInTab,
    TrainByCcIdColumnDefinition,
    UnicastIpDefinitionColumnsInTab,
)

# import ipaddress


INPUT_DOWNLOAD_FOLDER = "Input_Downloaded"


@dataclass
class ExcelInputFileDescription:
    all_tabs_definition: List[EquipmentDefinitionTab]
    excel_file_full_name: str
    rhapsody_id: int

    def __post_init__(self) -> None:
        self.rhapsody_download_link = f"https://rhapsody.siemens.net/livelink/livelink.exe?func=ll&objId={self.rhapsody_id}&objAction=Download"
        self.excel_file_full_path = f"{INPUT_DOWNLOAD_FOLDER}/{self.excel_file_full_name}"
        self.excel_file_name_without_extension, self.excel_file_extension = os.path.splitext(self.excel_file_full_name)
        self.excel_file_name_without_extension = file_name_utils.get_file_name_without_extension_from_full_path(self.excel_file_full_name)
        self.file_name_mask_downloaded = f"{self.excel_file_name_without_extension}*{self.excel_file_extension}"
        pass


class StdRadioNetworkConfV2Description(ExcelInputFileDescription):
    def __init__(self) -> None:

        self.ip_reseau_std_radio_tab: EquipmentDefinitionTab = EquipmentDefinitionTab(
            tab_name="IP RESEAU STD RADIO",
            rows_to_ignore=[0, 1, 2, 3, 4, 6, 7],
            equipment_alternative_name_definition=ExcelColumnDefinitionByColumnTitle("Equip_ID"),
            equipment_ip_definitions=[
                UnicastIpDefinitionColumnsInTab(
                    equipment_vlan_column_definition=ExcelColumnDefinitionByColumnTitle("VLAN ID A"),
                    equipment_ip_address_column_definition=ExcelColumnDefinitionByColumnTitle("Anneau A"),
                    equipment_mask_column_definition=ExcelColumnDefinitionByColumnTitle("Masque A"),
                    equipment_gateway_column_definition=ExcelColumnDefinitionByColumnTitle("Passerelle A"),
                    forced_label="Anneau A",
                    can_be_empty=True,
                ),
            ],
        )
        super().__init__(
            all_tabs_definition=[self.ip_reseau_std_radio_tab],
            excel_file_full_name="NExTEO-S-273000-02-0125-01 Dossier de Configuration Réseau STD Radio - V02-00 Annexe A.xlsx",
            rhapsody_id=92435067,
        )


class RadioLayoutR841Description(ExcelInputFileDescription):
    def __init__(self) -> None:

        self.ip_reseau_std_radio_tab: EquipmentDefinitionTab = EquipmentDefinitionTab(
            tab_name="AP CBTC",
            rows_to_ignore=[],
            equipment_type_definition=ForcedStrValueInformationDefinition("AP"),
            equipment_name_column_definition=ExcelColumnDefinitionByColumnTitle("AP name"),
            equipment_alternative_name_definition=ExcelColumnDefinitionByColumnTitle("N° AP Layout radio"),
            equipment_ip_definitions=[
                UnicastIpDefinitionColumnsInTab(
                    equipment_vlan_column_definition=None,
                    equipment_ip_address_column_definition=ExcelColumnDefinitionByColumnTitle("IP via CSR_A\n(S&D info)"),
                    equipment_mask_column_definition=None,
                    equipment_gateway_column_definition=None,
                    forced_label="IP via CSR_A (S&D info)",
                    can_be_empty=True,
                ),
                UnicastIpDefinitionColumnsInTab(
                    equipment_vlan_column_definition=None,
                    equipment_ip_address_column_definition=ExcelColumnDefinitionByColumnTitle("IP via CSR_B\n(S&D info)"),
                    equipment_mask_column_definition=None,
                    equipment_gateway_column_definition=None,
                    forced_label="IP via CSR_B (S&D info)",
                    can_be_empty=True,
                ),
            ],
        )
        super().__init__(
            all_tabs_definition=[self.ip_reseau_std_radio_tab],
            excel_file_full_name="NEXTEO_LIGNE_InputAirlinkCBTC_8_4_1_V8.xlsm",
            rhapsody_id=-1,
        )


class SolStdNetworkConfV11Description(ExcelInputFileDescription):
    def __init__(self) -> None:

        self.ip_ats_tab: EquipmentDefinitionTab = EquipmentDefinitionTab(
            tab_name="IP ATS",
            equipment_alternative_name_definition=ExcelColumnDefinitionByColumnTitle("Equip_ID"),
            rows_to_ignore=[0, 1, 2, 3, 4, 6, 7],
            equipment_ip_definitions=[UnicastIpDefinitionColumnsInTab(equipment_ip_address_column_definition=ExcelColumnDefinitionByColumnTitle("Adresse IP"))],
        )
        self.ip_reseau_std_tab: EquipmentDefinitionTab = EquipmentDefinitionTab(
            tab_name="IP RESEAU STD",
            equipment_alternative_name_definition=ExcelColumnDefinitionByColumnTitle("Equip_ID"),
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
            equipment_alternative_name_definition=ExcelColumnDefinitionByColumnTitle("Equip_ID"),
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
            equipment_alternative_name_definition=ExcelColumnDefinitionByColumnTitle("Equip_ID"),
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
            equipment_alternative_name_definition=ExcelColumnDefinitionByColumnTitle("Equip_ID"),
            rows_to_ignore=[0, 1, 2, 4, 5],
            equipment_ip_definitions=[
                UnicastIpDefinitionColumnsInTab(can_be_empty=True, gateway_is_optional=True),
            ],
        )
        self.ip_csr_tab: EquipmentDefinitionTab = EquipmentDefinitionTab(
            tab_name="IP CSR",
            equipment_alternative_name_definition=ExcelColumnDefinitionByColumnTitle("Equip_ID"),
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
                    equipment_ip_address_column_definition=ExcelColumnDefinitionByColumnTitle("@IP multicast"),
                    forced_label="Multicast",
                    can_be_empty=True,
                    group_multicast="239.192.0.0",
                ),
            ],
        )
        self.ip_pmb_tab: EquipmentDefinitionTab = EquipmentDefinitionTab(
            tab_name="IP PMB",
            equipment_alternative_name_definition=ExcelColumnDefinitionByColumnTitle("Equip_ID"),
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
        self.ip_pai_tab: EquipmentDefinitionTab = EquipmentDefinitionTab(
            tab_name="IP PAI",
            equipment_alternative_name_definition=ExcelColumnDefinitionByColumnTitle("Equip_ID"),
            equipment_name_column_definition=ExcelColumnDefinitionByColumnTitle("Equipment"),
            rows_to_ignore=[0, 1, 2, 3, 4, 6, 7],
            equipment_ip_definitions=[
                UnicastIpDefinitionColumnsInTab(
                    equipment_vlan_column_definition=ExcelColumnDefinitionByColumnTitle("VLAN ID A"),
                    equipment_ip_address_column_definition=ExcelColumnDefinitionByColumnTitle("Anneau A"),
                    equipment_mask_column_definition=ExcelColumnDefinitionByColumnTitle("Masque A"),
                    equipment_gateway_column_definition=ExcelColumnDefinitionByColumnTitle("Passerelle A"),
                    forced_label="Anneau A",
                    can_be_empty=True,
                    gateway_is_optional=True,
                    mask_is_optional=True,
                ),
                UnicastIpDefinitionColumnsInTab(
                    equipment_vlan_column_definition=ExcelColumnDefinitionByColumnTitle("VLAN ID B"),
                    equipment_ip_address_column_definition=ExcelColumnDefinitionByColumnTitle("Anneau B"),
                    equipment_mask_column_definition=ExcelColumnDefinitionByColumnTitle("Masque B"),
                    equipment_gateway_column_definition=ExcelColumnDefinitionByColumnTitle("Passerelle B"),
                    forced_label="Anneau B",
                    can_be_empty=True,
                    gateway_is_optional=True,
                    mask_is_optional=True,
                ),
            ],
        )
        super().__init__(
            all_tabs_definition=[self.ip_ats_tab, self.ip_reseau_std_tab, self.ip_cbtc_tab, self.ip_mats, self.ip_reseau_pcc, self.ip_csr_tab, self.ip_pmb_tab, self.ip_pai_tab],
            excel_file_full_name="NExTEO-S-271000-02-0125-02 Dossier de Configuration Réseau Sol - V11-00 Annexe A.xlsb",
            rhapsody_id=92403807,
        )


class BordAddressPlanV9Description(ExcelInputFileDescription):
    def __init__(self) -> None:

        self.ip_tu_tab: InsideTrainEquipmentDefinitionTab = InsideTrainEquipmentDefinitionTab(
            tab_name="@IP TU",
            rows_to_ignore=[0, 1, 2, 3, 4, 6],
            train_identifier_definition=TrainByCcIdColumnDefinition(cc_id_column_definition=ExcelColumnDefinitionByColumnExcelId("B")),
            equipment_type_definition=ForcedStrValueInformationDefinition("TU"),
            equipment_name_column_definition=ForcedStrValueInformationDefinition("TU_1"),
            equipment_ip_definitions=[
                UnicastIpDefinitionColumnsInTab(
                    equipment_ip_address_column_definition=ExcelColumnDefinitionByColumnTitle("CPL SUBNET_1"),
                    equipment_gateway_column_definition=None,
                    equipment_mask_column_definition=None,
                    equipment_vlan_column_definition=None,
                    mask_is_optional=True,
                    gateway_is_optional=True,
                )
            ],
        )

        super().__init__(all_tabs_definition=[self.ip_tu_tab], excel_file_full_name="NExTEO-B-272000-02-0125-00 Plan d adressage NExTEO Bord V09-00.xlsm", rhapsody_id=91211232)
