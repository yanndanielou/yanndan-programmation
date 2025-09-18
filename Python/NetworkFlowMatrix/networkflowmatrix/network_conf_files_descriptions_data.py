# import ipaddress

from networkflowmatrix.network_conf_files import (
    EquipmentDefinitionTab,
    UnicastIpDefinitionColumnsInTab,
    ExcelColumnDefinitionByColumnTitle,
    ExcelColumnDefinitionByColumnExcelId,
    ForcedNoneValueInformationDefinition,
    MulticastIpDefinitionColumnsInTab,
    InsideTrainEquipmentDefinitionTab,
    TrainByCcIdColumnDefinition,
)


class StdRadioNetworkConfV2Description:
    def __init__(self) -> None:

        self.ip_reseau_std_radio_tab: EquipmentDefinitionTab = EquipmentDefinitionTab(
            tab_name="IP RESEAU STD RADIO",
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
            ],
        )
        self.all_tabs_definition = [self.ip_reseau_std_radio_tab]
        self.excel_file_full_path = "Input_Downloaded/NExTEO-S-273000-02-0125-01 Dossier de Configuration Réseau STD Radio - V02-00 Annexe A_diffa.xlsx"


class SolStdNetworkConfV10Description:
    def __init__(self) -> None:

        self.ip_ats_tab: EquipmentDefinitionTab = EquipmentDefinitionTab(
            tab_name="IP ATS",
            rows_to_ignore=[0, 1, 2, 3, 4, 6, 7],
            equipment_ip_definitions=[UnicastIpDefinitionColumnsInTab(equipment_ip_address_column_definition=ExcelColumnDefinitionByColumnTitle("Adresse IP"))],
        )
        self.ip_reseau_std_tab: EquipmentDefinitionTab = EquipmentDefinitionTab(
            tab_name="IP RESEAU STD",
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
        self.ip_pmb_tab: EquipmentDefinitionTab = EquipmentDefinitionTab(
            tab_name="IP PMB",
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
        self.all_tabs_definition = [self.ip_ats_tab, self.ip_reseau_std_tab, self.ip_cbtc_tab, self.ip_mats, self.ip_reseau_pcc, self.ip_csr_tab, self.ip_pmb_tab, self.ip_pai_tab]
        self.excel_file_full_path = "Input_Downloaded/NExTEO-S-271000-02-0125-02  Dossier de Configuration Réseau Sol - V10-00 Annexe A.xlsb"


class BordAdressPlanV9Description:
    def __init__(self) -> None:

        self.ip_tu_tab: InsideTrainEquipmentDefinitionTab = InsideTrainEquipmentDefinitionTab(
            tab_name="@IP TU",
            rows_to_ignore=[0, 1, 2, 3, 4, 6],
            train_identifier_definition=TrainByCcIdColumnDefinition(),
            equipment_ip_definitions=[
                UnicastIpDefinitionColumnsInTab(
                    equipment_ip_address_column_definition=ExcelColumnDefinitionByColumnTitle("CPL SUBNET_1"),
                    equipment_gateway_column_definition=ForcedNoneValueInformationDefinition(),
                    equipment_mask_column_definition=ForcedNoneValueInformationDefinition(),
                    equipment_vlan_column_definition=ForcedNoneValueInformationDefinition(),
                    mask_is_optional=True,
                    gateway_is_optional=True,
                )
            ],
        )
        self.all_tabs_definition = [self.ip_tu_tab]
        self.excel_file_full_path = "Input_Downloaded/NExTEO-B-272000-02-0125-00 Plan d adressage NExTEO Bord  V09-00 (1).xlsm"
