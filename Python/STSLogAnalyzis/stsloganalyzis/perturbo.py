from dataclasses import dataclass
from typing import List, Self

from stsloganalyzis import atc_logs
from logger import logger_config


@dataclass
class PerturboFile(atc_logs.ATCTestFile):

    equipment_name: str

    def __post_init__(self) -> None:
        self.variables_line_dictionary: atc_logs.ATCVariablesLineDictionary
        self.all_values_raw_lines: List[str] = []
        self.open_and_read_lines()

    @logger_config.stopwatch_decorator(inform_beginning=True, monitor_ram_usage=True)
    def open_and_read_lines(self) -> None:

        with open(self.file_full_path, mode="r", encoding="utf-8") as file:
            all_raw_lines = file.readlines()
            logger_config.print_and_log_info(f"Perturbo file {self.file_full_path} has {len(all_raw_lines)} lines")
            assert all_raw_lines
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

            for variable_name, variable_value in all_fields_names_and_values.items():
                if atc_logs.variable_name_matches_all_filters(variable_name=variable_name, all_filters=self.atc_test_result.variables_name_filters):
                    variable = equipment.variables_library.get_or_create_variable_by_name(variable_name=variable_name)
                    variable_state = atc_logs.VariableState(variable=variable, timestamp=timestamp, value=variable_value)
                    all_variables_states.append(variable_state)

        logger_config.print_and_log_info(f"{len(all_variables_states)} variable states found for equipment {self.equipment_name} in {self.file_full_path}")
        return all_variables_states


class PerturboTestResult(atc_logs.ATCTestResult):

    def __init__(self) -> None:
        super().__init__()
        self.all_perturbo_files: List[PerturboFile] = []

    class Builder(atc_logs.ATCTestResult.Builder):

        def __init__(self) -> None:
            super().__init__()
            self._perturbo_test_created = PerturboTestResult()

        def add_file(self, file_full_path: str, equipment_name: str) -> Self:
            self._perturbo_test_created.all_perturbo_files.append(
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
            self._perturbo_test_created.variables_name_filters = self.variables_names_filters
            return self._perturbo_test_created
