from typing import List, Set

import pytest

from tests import secret_tests_data

from networkflowmatrix.network_conf_files import (
    EquipmentsLibrary,
    RadioStdNetworkConfFile,
    SolStdNetworkConfFile,
)


@pytest.fixture(scope="session", name="parse_std_sol_dossier_conf_v10_file_and_build_objects_fixture")
def parse_std_sol_dossier_conf_v10_file_and_build_objects() -> SolStdNetworkConfFile:
    equipments_library = EquipmentsLibrary()
    std_sol_dossier_conf = SolStdNetworkConfFile.Builder.build_with_excel_file(
        equipments_library=equipments_library, excel_file_full_path="Input_Downloaded/NExTEO-S-271000-02-0125-02  Dossier de Configuration Réseau Sol - V10-00 Annexe A.xlsb"
    )
    return std_sol_dossier_conf


class TestSolStdNetworkV10ConfFileTabIpCbtcOnly:
    def test_no_error(self) -> None:
        equipments_library = EquipmentsLibrary()
        std_sol_dossier_conf = SolStdNetworkConfFile.Builder.build_with_excel_file(
            equipments_library=equipments_library,
            excel_file_full_path="Input_Downloaded/NExTEO-S-271000-02-0125-02  Dossier de Configuration Réseau Sol - V10-00 Annexe A.xlsb",
            equipment_definition_tabs=[SolStdNetworkConfFile.IP_CBTC_TAB],
        )
        assert std_sol_dossier_conf


class TestSolStdNetworkV10FullConfFile:
    def test_no_empty_ip_address(self, parse_std_sol_dossier_conf_v10_file_and_build_objects_fixture: SolStdNetworkConfFile) -> None:
        for network_conf_files_defined_equipment in parse_std_sol_dossier_conf_v10_file_and_build_objects_fixture.equipments_library.network_conf_files_defined_equipments:
            for ip_address in network_conf_files_defined_equipment.ip_addresses:
                assert ip_address.vlan_name
                assert ip_address.mask
                assert ip_address.gateway
                assert ip_address.ip_raw

    @pytest.mark.parametrize("equipment_name", secret_tests_data.test_equipments_naùes_with_only_one_ip)
    def test_equipment_with_only_one_ip(self, equipment_name: str, parse_std_sol_dossier_conf_v10_file_and_build_objects_fixture: SolStdNetworkConfFile) -> None:
        network_conf_files_defined_equipment = parse_std_sol_dossier_conf_v10_file_and_build_objects_fixture.equipments_library.get_existing_by_name(equipment_name)
        assert network_conf_files_defined_equipment
        assert len(network_conf_files_defined_equipment.ip_addresses) == 1
        for ip_address in network_conf_files_defined_equipment.ip_addresses:
            assert ip_address.vlan_name
            assert ip_address.mask
            assert ip_address.gateway
            assert ip_address.ip_raw
