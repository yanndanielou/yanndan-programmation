import os
from dataclasses import dataclass
from typing import List

from common import file_name_utils

from networkflowmatrix.network_conf_files import (
    EquipmentDefinitionTab,
    EquipmentDefinitionColumn,
    InsideTrainEquipmentDefinitionColumn,
    ExcelColumnDefinitionByColumnExcelId,
    ExcelColumnDefinitionByColumnTitle,
    ForcedStrValueInformationDefinition,
    MulticastIpDefinitionColumnsInTab,
    TrainByCcIdColumnDefinition,
    UnicastIpDefinitionColumnsInTab,
)

from networkflowmatrix.groups import GroupDefinition
from collections import namedtuple

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
            equipment_definitions=[
                EquipmentDefinitionColumn(
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
            equipment_definitions=[
                EquipmentDefinitionColumn(
                    equipment_type_definition=ForcedStrValueInformationDefinition("AP"),
                    equipment_name_column_definition=ExcelColumnDefinitionByColumnTitle("AP name"),
                    equipment_alternative_name_definition=ExcelColumnDefinitionByColumnTitle("N° AP Layout radio"),
                    groups_definitions=[
                        GroupDefinition("AP_CPU", "10.202.0.0/16"),
                        GroupDefinition("AP_CPU", "10.207.0.0/16"),
                    ],
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
            rows_to_ignore=[0, 1, 2, 3, 4, 6, 7],
            equipment_definitions=[
                EquipmentDefinitionColumn(
                    equipment_alternative_name_definition=ExcelColumnDefinitionByColumnTitle("Equip_ID"),
                    equipment_ip_definitions=[UnicastIpDefinitionColumnsInTab(equipment_ip_address_column_definition=ExcelColumnDefinitionByColumnTitle("Adresse IP"))],
                )
            ],
        )
        self.ip_reseau_std_tab: EquipmentDefinitionTab = EquipmentDefinitionTab(
            tab_name="IP RESEAU STD",
            rows_to_ignore=[0, 1, 2, 3, 4, 6, 7],
            equipment_definitions=[
                EquipmentDefinitionColumn(
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
            ],
        )
        self.ip_cbtc_tab: EquipmentDefinitionTab = EquipmentDefinitionTab(
            tab_name="IP CBTC",
            rows_to_ignore=[0, 1, 2, 3, 4, 6, 7],
            equipment_definitions=[
                EquipmentDefinitionColumn(
                    equipment_alternative_name_definition=ExcelColumnDefinitionByColumnTitle("Equip_ID"),
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
            ],
        )
        self.ip_mats: EquipmentDefinitionTab = EquipmentDefinitionTab(
            tab_name="IP MATS",
            rows_to_ignore=[0, 1, 2, 3, 4, 6, 7],
            equipment_definitions=[
                EquipmentDefinitionColumn(
                    equipment_alternative_name_definition=ExcelColumnDefinitionByColumnTitle("Equip_ID"),
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
            ],
        )
        self.ip_reseau_pcc: EquipmentDefinitionTab = EquipmentDefinitionTab(
            tab_name="IP RESEAU PCC",
            rows_to_ignore=[0, 1, 2, 4, 5],
            equipment_definitions=[
                EquipmentDefinitionColumn(
                    equipment_alternative_name_definition=ExcelColumnDefinitionByColumnTitle("Equip_ID"),
                    equipment_ip_definitions=[
                        UnicastIpDefinitionColumnsInTab(can_be_empty=True, gateway_is_optional=True),
                    ],
                )
            ],
        )
        self.ip_csr_tab: EquipmentDefinitionTab = EquipmentDefinitionTab(
            tab_name="IP CSR",
            rows_to_ignore=[0, 1, 2, 3, 4, 6, 7],
            equipment_definitions=[
                EquipmentDefinitionColumn(
                    equipment_alternative_name_definition=ExcelColumnDefinitionByColumnTitle("Equip_ID"),
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
            ],
        )
        self.ip_pmb_tab: EquipmentDefinitionTab = EquipmentDefinitionTab(
            tab_name="IP PMB",
            rows_to_ignore=[0, 1, 2, 3, 4, 6, 7],
            equipment_ids_to_ignore=["EVG-P22-PMB", "NSY-P26-PMB", "EVG-P22-IMPR", "NSY-P26-IMPR"],
            equipment_definitions=[
                EquipmentDefinitionColumn(
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
            ],
        )
        self.ip_pai_tab: EquipmentDefinitionTab = EquipmentDefinitionTab(
            tab_name="IP PAI",
            rows_to_ignore=[0, 1, 2, 3, 4, 6, 7],
            equipment_definitions=[
                EquipmentDefinitionColumn(
                    equipment_alternative_name_definition=ExcelColumnDefinitionByColumnTitle("Equip_ID"),
                    equipment_name_column_definition=ExcelColumnDefinitionByColumnTitle("Equipment"),
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
        excel_file_full_name = "NExTEO-B-272000-02-0125-00 Plan d adressage NExTEO Bord V09-00.xlsm"
        all_tabs_definition: List[EquipmentDefinitionTab] = []

        all_tabs_definition.append(
            EquipmentDefinitionTab(
                tab_name="@IP TU",
                rows_to_ignore=[0, 1, 2, 3, 4, 6],
                equipment_definitions=[
                    InsideTrainEquipmentDefinitionColumn(
                        train_identifier_definition=TrainByCcIdColumnDefinition(cc_id_column_definition=ExcelColumnDefinitionByColumnExcelId("B")),
                        equipment_type_definition=ForcedStrValueInformationDefinition("TU"),
                        equipment_name_column_definition=ForcedStrValueInformationDefinition("TU_A"),
                        equipment_ip_definitions=[
                            UnicastIpDefinitionColumnsInTab(
                                equipment_ip_address_column_definition=ExcelColumnDefinitionByColumnTitle("CPL SUBNET_1"),
                                equipment_gateway_column_definition=None,
                                equipment_mask_column_definition=None,
                                equipment_vlan_column_definition=None,
                                mask_is_optional=True,
                                gateway_is_optional=True,
                            ),
                            UnicastIpDefinitionColumnsInTab(
                                equipment_ip_address_column_definition=ExcelColumnDefinitionByColumnTitle("To TU_2"),
                                equipment_gateway_column_definition=None,
                                equipment_mask_column_definition=None,
                                equipment_vlan_column_definition=None,
                                mask_is_optional=True,
                                gateway_is_optional=True,
                            ),
                            UnicastIpDefinitionColumnsInTab(
                                equipment_ip_address_column_definition=ExcelColumnDefinitionByColumnTitle("SERIAL"),
                                equipment_gateway_column_definition=None,
                                equipment_mask_column_definition=None,
                                equipment_vlan_column_definition=None,
                                mask_is_optional=True,
                                gateway_is_optional=True,
                            ),
                            UnicastIpDefinitionColumnsInTab(
                                equipment_ip_address_column_definition=ExcelColumnDefinitionByColumnTitle("MGMT_CSR_1"),
                                equipment_gateway_column_definition=None,
                                equipment_mask_column_definition=None,
                                equipment_vlan_column_definition=None,
                                mask_is_optional=True,
                                gateway_is_optional=True,
                            ),
                            UnicastIpDefinitionColumnsInTab(
                                equipment_ip_address_column_definition=ExcelColumnDefinitionByColumnTitle("MGMT_CSR_2"),
                                equipment_gateway_column_definition=None,
                                equipment_mask_column_definition=None,
                                equipment_vlan_column_definition=None,
                                mask_is_optional=True,
                                gateway_is_optional=True,
                            ),
                        ],
                    )
                ],
            )
        )

        all_tabs_definition.append(
            EquipmentDefinitionTab(
                tab_name="@IP TU",
                rows_to_ignore=[0, 1, 2, 3, 4, 6],
                equipment_definitions=[
                    InsideTrainEquipmentDefinitionColumn(
                        train_identifier_definition=TrainByCcIdColumnDefinition(cc_id_column_definition=ExcelColumnDefinitionByColumnExcelId("B")),
                        equipment_type_definition=ForcedStrValueInformationDefinition("TU"),
                        equipment_name_column_definition=ForcedStrValueInformationDefinition("TU_B"),
                        equipment_ip_definitions=[
                            UnicastIpDefinitionColumnsInTab(
                                equipment_ip_address_column_definition=ExcelColumnDefinitionByColumnTitle("CPL SUBNET_2"),
                                equipment_gateway_column_definition=None,
                                equipment_mask_column_definition=None,
                                equipment_vlan_column_definition=None,
                                mask_is_optional=True,
                                gateway_is_optional=True,
                            ),
                            UnicastIpDefinitionColumnsInTab(
                                equipment_ip_address_column_definition=ExcelColumnDefinitionByColumnTitle("To TU_1"),
                                equipment_gateway_column_definition=None,
                                equipment_mask_column_definition=None,
                                equipment_vlan_column_definition=None,
                                mask_is_optional=True,
                                gateway_is_optional=True,
                            ),
                            UnicastIpDefinitionColumnsInTab(
                                equipment_ip_address_column_definition=ExcelColumnDefinitionByColumnTitle("SERIAL"),
                                equipment_gateway_column_definition=None,
                                equipment_mask_column_definition=None,
                                equipment_vlan_column_definition=None,
                                mask_is_optional=True,
                                gateway_is_optional=True,
                            ),
                            UnicastIpDefinitionColumnsInTab(
                                equipment_ip_address_column_definition=ExcelColumnDefinitionByColumnTitle("MGMT_CSR_1"),
                                equipment_gateway_column_definition=None,
                                equipment_mask_column_definition=None,
                                equipment_vlan_column_definition=None,
                                mask_is_optional=True,
                                gateway_is_optional=True,
                            ),
                            UnicastIpDefinitionColumnsInTab(
                                equipment_ip_address_column_definition=ExcelColumnDefinitionByColumnTitle("MGMT_CSR_2"),
                                equipment_gateway_column_definition=None,
                                equipment_mask_column_definition=None,
                                equipment_vlan_column_definition=None,
                                mask_is_optional=True,
                                gateway_is_optional=True,
                            ),
                        ],
                    )
                ],
            )
        )

        EquipmentInfo = namedtuple("EquipmentInfo", ["name", "goups_definitions", "mask_definition"])
        all_tabs_definition.append(
            EquipmentDefinitionTab(
                tab_name="@IP NExTEO VLAN",
                rows_to_ignore=list(range(0, 13)) + [14, 15],
                equipment_definitions=[
                    InsideTrainEquipmentDefinitionColumn(
                        train_identifier_definition=TrainByCcIdColumnDefinition(cc_id_column_definition=ExcelColumnDefinitionByColumnTitle("CC ID")),
                        equipment_type_definition=ForcedStrValueInformationDefinition(eqpt_info.name),
                        equipment_name_column_definition=ForcedStrValueInformationDefinition(eqpt_info.name),
                        equipment_ip_definitions=[
                            UnicastIpDefinitionColumnsInTab(
                                equipment_ip_address_column_definition=ExcelColumnDefinitionByColumnTitle(eqpt_info.name),
                                equipment_gateway_column_definition=None,
                                equipment_mask_column_definition=eqpt_info.mask_definition,
                                equipment_vlan_column_definition=None,
                                mask_is_optional=True,
                                gateway_is_optional=True,
                            ),
                        ],
                        groups_definitions=eqpt_info.goups_definitions,
                    )
                    for eqpt_info in [
                        EquipmentInfo("PAE_A", [GroupDefinition("PAE", "172.20.0.0/16")], ForcedStrValueInformationDefinition("255.255.255.224 /27)")),
                        EquipmentInfo("PAE_B", [GroupDefinition("PAE", "172.20.0.0/16")], ForcedStrValueInformationDefinition("255.255.255.224 /27)")),
                        EquipmentInfo("PPN_A_1", [GroupDefinition("PPN_A_1", "172.20.0.0/16")], None),
                        EquipmentInfo("PPN_B_1", [GroupDefinition("PPN_B_1", "172.20.0.0/16")], None),
                        EquipmentInfo("PPN_A_2", [GroupDefinition("PPN_A_2", "172.20.0.0/16")], None),
                        EquipmentInfo("PPN_B_2", [GroupDefinition("PPN_B_2", "172.20.0.0/16")], None),
                        EquipmentInfo("TU_A", [GroupDefinition("TU", "172.20.0.0/16")], None),
                        EquipmentInfo("TU_B", [GroupDefinition("TU", "172.20.0.0/16")], None),
                        EquipmentInfo("INT_TOOL", [], None),
                        EquipmentInfo("GW_CBTC", [], None),
                        EquipmentInfo("NBR_A", [GroupDefinition("NBR_A", "172.21.0.0/16")], None),
                        EquipmentInfo("NBR_B", [GroupDefinition("NBR_B", "172.21.0.0/16")], None),
                        EquipmentInfo("AFF_CAR_1", [GroupDefinition("AFFCAR", "172.40.0.0/16")], None),
                        EquipmentInfo("AFF_CAR_2", [GroupDefinition("AFFCAR", "172.40.0.0/16")], None),
                        EquipmentInfo("GW_AFF", [], None),
                        EquipmentInfo("NBR_A_AFF", [], None),
                        EquipmentInfo("NBR_B_AFF", [], None),
                        EquipmentInfo("MPU0_Z11", [], None),
                        EquipmentInfo("MPU0_Z12", [], None),
                        EquipmentInfo("GW_SIE", [], None),
                        EquipmentInfo("NBR_A_SIE", [], None),
                        EquipmentInfo("NBR_B_SIE", [], None),
                    ]
                ],
            )
        )

        all_tabs_definition.append(
            EquipmentDefinitionTab(
                tab_name="@IP Mgt SW",
                rows_to_ignore=list(range(0, 10)) + [11, 12],
                equipment_definitions=[
                    InsideTrainEquipmentDefinitionColumn(
                        train_identifier_definition=TrainByCcIdColumnDefinition(cc_id_column_definition=ExcelColumnDefinitionByColumnTitle("CC ID")),
                        equipment_type_definition=ForcedStrValueInformationDefinition(eqpt),
                        equipment_name_column_definition=ForcedStrValueInformationDefinition(eqpt),
                        equipment_ip_definitions=[
                            UnicastIpDefinitionColumnsInTab(
                                equipment_ip_address_column_definition=ExcelColumnDefinitionByColumnTitle(eqpt),
                                equipment_gateway_column_definition=None,
                                equipment_mask_column_definition=None,
                                equipment_vlan_column_definition=None,
                                mask_is_optional=True,
                                gateway_is_optional=True,
                            ),
                        ],
                    )
                    for eqpt in ["NRS_1_1", "NRS_2_1", "NRS_5_1", "NRS_6_1", "NBR_A", "NBR_B", "NRS_1_2", "NRS_2_2", "GW_Mgt_SW"]
                ],
            )
        )

        super().__init__(
            all_tabs_definition=all_tabs_definition,
            excel_file_full_name=excel_file_full_name,
            rhapsody_id=91211232,
        )
