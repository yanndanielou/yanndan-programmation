from typing import Set

import pytest

from networkflowmatrix.data_model import (
    EquipmentInFLowMatrix,
    NetworkFlowMatrix,
    SubSystemInFlowMatrix,
)


@pytest.fixture(scope="session", name="parse_flow_matrix_file_and_build_objects_fixture")
def parse_flow_matrix_file_and_build_objects() -> NetworkFlowMatrix:
    network_flow_matrix = NetworkFlowMatrix.Builder.build_with_excel_file(excel_file_full_path="Input/Matrice_next.xlsm", sheet_name="Matrice_de_Flux_SITE")
    return network_flow_matrix


class TestNoErrorAtBUild:
    def test_parse_flow_matrix_file_and_build_objects(self, parse_flow_matrix_file_and_build_objects_fixture: NetworkFlowMatrix) -> None:
        assert parse_flow_matrix_file_and_build_objects_fixture
        assert parse_flow_matrix_file_and_build_objects_fixture.network_flow_matrix_lines


class TestEquipmentAndSubystemCreationOnTheFlowOfFlowMatrixParsing:
    def test_all_subsystem_names_are_unique(self, parse_flow_matrix_file_and_build_objects_fixture: NetworkFlowMatrix) -> None:
        network_flow_matrix = parse_flow_matrix_file_and_build_objects_fixture
        assert network_flow_matrix
        all_subsystem_names: Set[str] = set()
        for subsystem in network_flow_matrix.all_matrix_flow_subsystems_definitions_instances:
            assert subsystem.name not in all_subsystem_names
            all_subsystem_names.add(subsystem.name)
        assert len(all_subsystem_names) == len(network_flow_matrix.all_matrix_flow_subsystems_definitions_instances)

    def test_all_equipment_names_are_unique(self, parse_flow_matrix_file_and_build_objects_fixture: NetworkFlowMatrix) -> None:
        network_flow_matrix = parse_flow_matrix_file_and_build_objects_fixture
        assert network_flow_matrix
        all_equipment_names: Set[str] = set()
        for equipment in network_flow_matrix.all_matrix_flow_equipments_definitions_instances:
            assert equipment.name not in all_equipment_names
            all_equipment_names.add(equipment.name)
        assert len(all_equipment_names) == len(network_flow_matrix.all_matrix_flow_equipments_definitions_instances)

    def test_all_subsystem_names_trimmed(self, parse_flow_matrix_file_and_build_objects_fixture: NetworkFlowMatrix) -> None:
        network_flow_matrix = parse_flow_matrix_file_and_build_objects_fixture
        assert network_flow_matrix
        for subsystem in network_flow_matrix.all_matrix_flow_subsystems_definitions_instances:
            assert subsystem.name == subsystem.name.strip()

    def test_all_equipment_names_trimmed(self, parse_flow_matrix_file_and_build_objects_fixture: NetworkFlowMatrix) -> None:
        network_flow_matrix = parse_flow_matrix_file_and_build_objects_fixture
        assert network_flow_matrix
        for equipment in network_flow_matrix.all_matrix_flow_equipments_definitions_instances:
            assert equipment.name == equipment.name.strip()

    def test_all_equipment_names_capital_letter_to_ensure_uniqueness(self, parse_flow_matrix_file_and_build_objects_fixture: NetworkFlowMatrix) -> None:
        network_flow_matrix = parse_flow_matrix_file_and_build_objects_fixture
        assert network_flow_matrix
        for equipment in network_flow_matrix.all_matrix_flow_equipments_definitions_instances:
            assert equipment.name == equipment.name.upper()

    def test_all_subsystem_names_capital_letter_to_ensure_uniqueness(self, parse_flow_matrix_file_and_build_objects_fixture: NetworkFlowMatrix) -> None:
        network_flow_matrix = parse_flow_matrix_file_and_build_objects_fixture
        assert network_flow_matrix
        for subsystem in network_flow_matrix.all_matrix_flow_subsystems_definitions_instances:
            assert subsystem.name == subsystem.name.upper()

    def test_all_equipments_have_name(self, parse_flow_matrix_file_and_build_objects_fixture: NetworkFlowMatrix) -> None:
        network_flow_matrix = parse_flow_matrix_file_and_build_objects_fixture
        assert network_flow_matrix
        for equipment in network_flow_matrix.all_matrix_flow_equipments_definitions_instances:
            assert isinstance(equipment.name, str)
            assert equipment.name != ""

    def test_existance_of_equipment_with_several_susbystems(self, parse_flow_matrix_file_and_build_objects_fixture: NetworkFlowMatrix) -> None:
        network_flow_matrix = parse_flow_matrix_file_and_build_objects_fixture
        equipments_with_several_subsystems = [
            equipment for equipment in network_flow_matrix.all_matrix_flow_equipments_definitions_instances if len(equipment.all_subsystems_detected_in_flow_matrix) > 1
        ]
        assert equipments_with_several_subsystems

    def test_all_equipments_of_each_subsystem_has_the_subsystem(self, parse_flow_matrix_file_and_build_objects_fixture: NetworkFlowMatrix) -> None:
        network_flow_matrix = parse_flow_matrix_file_and_build_objects_fixture
        for subsystem in network_flow_matrix.all_matrix_flow_subsystems_definitions_instances:
            for equipment in subsystem.all_equipments_detected_in_flow_matrix:
                assert subsystem in equipment.all_subsystems_detected_in_flow_matrix

    def test_all_subsystem_of_each_equipment_has_the_equipment(self, parse_flow_matrix_file_and_build_objects_fixture: NetworkFlowMatrix) -> None:
        network_flow_matrix = parse_flow_matrix_file_and_build_objects_fixture
        for equipment in network_flow_matrix.all_matrix_flow_equipments_definitions_instances:
            for subsystem in equipment.all_subsystems_detected_in_flow_matrix:
                assert (
                    equipment in subsystem.all_equipments_detected_in_flow_matrix
                ), f"{equipment.name} not found in list of equipments {[eqpt.name for eqpt in subsystem.all_equipments_detected_in_flow_matrix]} of subsystem {subsystem.name}"
