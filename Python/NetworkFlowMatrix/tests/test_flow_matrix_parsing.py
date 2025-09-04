import pytest

from networkflowmatrix.data_model import NetworkFlowMatrix, SubSystemInFlowMatrix, EquipmentInFLoxMatrix
from typing import Set, List


@pytest.fixture(scope="session", name="parse_flow_matrix_file_and_build_objects_fixture")
def parse_flow_matrix_file_and_build_objects() -> NetworkFlowMatrix:
    network_flow_matrix = NetworkFlowMatrix.Builder.build_with_excel_file(excel_file_full_path="Input/Matrice_next.xlsm", sheet_name="Matrice_de_Flux_SITE")
    return network_flow_matrix


class TestEquipmentAndSubystemCreationOnTheFlowOfFlowMatrixParsing:
    def test_all_subsystem_names_are_unique(self, parse_flow_matrix_file_and_build_objects_fixture: NetworkFlowMatrix) -> None:
        network_flow_matrix = parse_flow_matrix_file_and_build_objects_fixture
        assert network_flow_matrix
        all_subsystem_names: Set[str] = set()
        for subsystem in SubSystemInFlowMatrix.all_instances:
            assert subsystem.name not in all_subsystem_names
            all_subsystem_names.add(subsystem.name)
        assert len(all_subsystem_names) == len(SubSystemInFlowMatrix.all_instances)

    def test_all_equipment_names_are_unique(self, parse_flow_matrix_file_and_build_objects_fixture: NetworkFlowMatrix) -> None:
        network_flow_matrix = parse_flow_matrix_file_and_build_objects_fixture
        assert network_flow_matrix
        all_equipment_names: Set[str] = set()
        for equipment in EquipmentInFLoxMatrix.all_instances:
            assert equipment.name not in all_equipment_names
            all_equipment_names.add(equipment.name)
        assert len(all_equipment_names) == len(EquipmentInFLoxMatrix.all_instances)
