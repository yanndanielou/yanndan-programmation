from dataclasses import dataclass
from typing import List, Self, cast

from stsloganalyzis import atc_logs
from logger import logger_config

from common import file_name_utils


@dataclass
class PerturboFile(atc_logs.ATCTestFile):

    equipment_name: str

    def __post_init__(self) -> None:
        super().__post_init__()
        self.variables_line_dictionary: atc_logs.ATCVariablesLineDictionary
        self.all_values_raw_lines: List[str] = []
        self.create_dictionnary_and_raw_line_values()

    @logger_config.stopwatch_decorator(inform_beginning=True, monitor_ram_usage=True)
    def create_dictionnary_and_raw_line_values(self) -> None:
        all_raw_lines = self.open_and_get_all_raw_lines()
        self.variables_line_dictionary = atc_logs.ATCVariablesLineDictionary(all_raw_lines[0])
        self.all_values_raw_lines = all_raw_lines[1:]

    def get_equipment_name(self) -> str:
        return self.equipment_name

    @logger_config.stopwatch_decorator(inform_beginning=True, monitor_ram_usage=True)
    def get_all_raw_variables_states(self) -> List[atc_logs.VariableState]:

        equipment = self.get_equipment(self.atc_test_result)
        assert isinstance(equipment, atc_logs.Equipment)

        all_variables_states: List[atc_logs.VariableState] = []
        for value_raw_line in self.all_values_raw_lines:

            all_fields_names_and_values = self.variables_line_dictionary.get_all_fields_names_and_values_in_data_line(value_raw_line)

            timestamp = self.variables_line_dictionary.get_line_timestamp(all_fields_names_and_values, value_raw_line)

            for variable_name, variable_raw_value in all_fields_names_and_values.items():
                self.atc_test_result.handle_variable_state(timestamp=timestamp, equipment=equipment, variable_name=variable_name, variable_raw_value=variable_raw_value)

        logger_config.print_and_log_info(f"{len(all_variables_states)} variable states found for equipment {self.equipment_name} in {self.file_full_path}")
        return all_variables_states


class PerturboTestResult(atc_logs.ATCTestResult):

    def __init__(self) -> None:
        super().__init__()

    @property
    def all_perturbo_files(self) -> List[PerturboFile]:
        return cast(List[PerturboFile], self.all_atc_test_files)

    class Builder(atc_logs.ATCTestResult.Builder):

        def __init__(self) -> None:
            super().__init__()
            self._perturbo_test_created = PerturboTestResult()

        def with_label(self, label: str) -> Self:
            self._perturbo_test_created.label = label
            return self

        def add_file(self, file_full_path: str, equipment_name: str) -> Self:
            self._perturbo_test_created.all_atc_test_files.append(
                PerturboFile(
                    atc_test_result=self._perturbo_test_created,
                    file_full_path=file_full_path,
                    equipment_name=equipment_name,
                )
            )
            return self

        def add_files(self, directory_path: str, filename_pattern: str, equipment_name: str) -> Self:
            for file_full_path in self.get_files_full_paths(directory_path=directory_path, filename_pattern=filename_pattern):
                self.add_file(file_full_path=file_full_path, equipment_name=equipment_name)
            return self

        def build(self) -> "PerturboTestResult":
            self._perturbo_test_created.variables_names_creation_filters = self.variables_names_creation_filters
            if self._perturbo_test_created.label == "" and len(self._perturbo_test_created.all_atc_test_files) == 1:
                pass

            return self._perturbo_test_created
