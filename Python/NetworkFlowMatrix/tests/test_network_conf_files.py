from typing import List, Set, cast

import pytest

from tests import secret_tests_data

from networkflowmatrix.network_conf_files import (
    NetworkConfFile,
)

from networkflowmatrix.equipments import (
    NetworkConfFilesEquipmentsLibrary,
)

from networkflowmatrix.network_conf_files_descriptions_data import (
    SolStdNetworkConfV11Description,
)


@pytest.fixture(scope="session", name="parse_std_sol_dossier_conf_v10_file_and_build_objects_fixture")
def parse_std_sol_dossier_conf_v10_file_and_build_objects() -> NetworkConfFile:
    equipments_library = NetworkConfFilesEquipmentsLibrary()
    dossier_conf = NetworkConfFile.Builder.build_with_excel_file(
        equipments_library=equipments_library,
        excel_file_full_path=SolStdNetworkConfV11Description().excel_file_full_name,
        equipment_definition_tabs=SolStdNetworkConfV11Description().all_tabs_definition,
    )
    return dossier_conf


class TestSolStdNetworkV10ConfFileTabIpCbtcOnly:
    def test_no_error(self) -> None:
        equipments_library = NetworkConfFilesEquipmentsLibrary()
        std_sol_dossier_conf = NetworkConfFile.Builder.build_with_excel_file(
            equipments_library=equipments_library,
            excel_file_full_path=SolStdNetworkConfV11Description().excel_file_full_name,
            equipment_definition_tabs=[SolStdNetworkConfV11Description().ip_cbtc_tab],
        )
        assert std_sol_dossier_conf

    def all_ip_definitions_have_decoded_ip_addresses(self) -> None:
        equipments_library = NetworkConfFilesEquipmentsLibrary()
        std_sol_dossier_conf = NetworkConfFile.Builder.build_with_excel_file(
            equipments_library=equipments_library,
            excel_file_full_path=SolStdNetworkConfV11Description().excel_file_full_name,
            equipment_definition_tabs=[SolStdNetworkConfV11Description().ip_cbtc_tab],
        )
        assert std_sol_dossier_conf


class TestSolStdNetworkV10FullConfFile:
    def test_no_empty_ip_address(self, parse_std_sol_dossier_conf_v10_file_and_build_objects_fixture: NetworkConfFile) -> None:
        for network_conf_files_defined_equipment in parse_std_sol_dossier_conf_v10_file_and_build_objects_fixture.equipments_library.network_conf_files_defined_equipments:
            for ip_address in network_conf_files_defined_equipment.ip_addresses:
                ip_address.check_valid_and_raise_if_error()

    @pytest.mark.parametrize("equipment_name", secret_tests_data.test_equipments_names_with_only_one_ip)
    def test_equipment_with_only_one_ip(self, equipment_name: str, parse_std_sol_dossier_conf_v10_file_and_build_objects_fixture: NetworkConfFile) -> None:
        network_conf_files_defined_equipment = parse_std_sol_dossier_conf_v10_file_and_build_objects_fixture.equipments_library.get_existing_network_conf_file_eqpt_by_name(equipment_name)
        assert network_conf_files_defined_equipment
        assert len(network_conf_files_defined_equipment.ip_addresses) == 1
        for ip_address in network_conf_files_defined_equipment.ip_addresses:
            ip_address.check_valid_and_raise_if_error()

    @pytest.mark.parametrize("equipment_name", secret_tests_data.test_equipments_names_with_only_na_ip)
    def test_equipment_with_na_ip_address(self, equipment_name: str, parse_std_sol_dossier_conf_v10_file_and_build_objects_fixture: NetworkConfFile) -> None:
        equipment_that_must_have_no_address = parse_std_sol_dossier_conf_v10_file_and_build_objects_fixture.equipments_library.get_existing_network_conf_file_eqpt_by_name(equipment_name)
        assert equipment_that_must_have_no_address
        assert not equipment_that_must_have_no_address.ip_addresses

    @pytest.mark.parametrize("equipment_name", secret_tests_data.test_equipments_names_with_only_na_ip)
    def test_pmb_equipment_with_na_ip_address(self, equipment_name: str) -> None:
        equipments_library = NetworkConfFilesEquipmentsLibrary()
        std_sol_dossier_conf = NetworkConfFile.Builder.build_with_excel_file(
            equipments_library=equipments_library,
            excel_file_full_path=SolStdNetworkConfV11Description().excel_file_full_name,
            equipment_definition_tabs=[SolStdNetworkConfV11Description().ip_pmb_tab],
        )
        equipment_that_must_have_no_address = std_sol_dossier_conf.equipments_library.get_existing_network_conf_file_eqpt_by_name(equipment_name)
        assert equipment_that_must_have_no_address
        assert not equipment_that_must_have_no_address.ip_addresses

    def test_all_ip_definitions_have_decoded_ip_addresses(self, parse_std_sol_dossier_conf_v10_file_and_build_objects_fixture: NetworkConfFile) -> None:
        equipments_library = NetworkConfFilesEquipmentsLibrary()
        std_sol_dossier_conf = parse_std_sol_dossier_conf_v10_file_and_build_objects_fixture
        assert std_sol_dossier_conf.equipment_definition_tabs
        for equipment_definition_tab in std_sol_dossier_conf.equipment_definition_tabs:
            assert equipment_definition_tab.equipment_ip_definitions
            for equipment_ip_definition in equipment_definition_tab.equipment_ip_definitions:
                assert equipment_ip_definition.all_ip_addresses_found, f"Tab {equipment_definition_tab.tab_name}"
                assert len(equipment_ip_definition.all_ip_addresses_found) > 1, f"Tab {equipment_definition_tab.tab_name}, {[ip.ip_raw for ip in equipment_ip_definition.all_ip_addresses_found]}"
