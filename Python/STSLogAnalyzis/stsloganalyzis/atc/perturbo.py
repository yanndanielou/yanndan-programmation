from dataclasses import dataclass
from typing import List, Self, Optional, cast

from stsloganalyzis.atc import atc_logs
from logger import logger_config


@dataclass
class PerturboFile(atc_logs.ATCTestFile):

    equipment_name: str

    def __post_init__(self) -> None:
        super().__post_init__()
        self.variables_line_dictionary: atc_logs.ATCVariablesLineDictionary
        self.all_values_raw_lines: List[str] = []
        self.create_dictionary_and_raw_line_values()

    @logger_config.stopwatch_decorator(inform_beginning=True, monitor_ram_usage=True)
    def create_dictionary_and_raw_line_values(self) -> None:
        all_raw_lines = self.open_and_get_all_raw_lines()
        self.variables_line_dictionary = atc_logs.ATCVariablesLineDictionary(all_raw_lines[0].split(atc_logs.ATC_LOG_FILES_FIELDS_SEPARATOR))
        self.all_values_raw_lines = all_raw_lines[1:]

    def get_equipment_name(self) -> str:
        return self.equipment_name

    def get_equipment(self, test_result: atc_logs.ATCTestResult) -> atc_logs.Equipment:
        return test_result.equipments_library.get_or_create_equipment_by_name(self.get_equipment_name())

    @logger_config.stopwatch_decorator(inform_beginning=True, monitor_ram_usage=True)
    def compute_all_variables_states(self) -> None:

        equipment = self.get_equipment(self.atc_test_result)
        assert isinstance(equipment, atc_logs.Equipment)

        previous_all_fields_names_and_values = None
        for line_number, value_raw_line in enumerate(self.all_values_raw_lines):

            all_fields_names_and_values = self.variables_line_dictionary.get_all_fields_names_and_values_in_data_line(value_raw_line)
            self.add_missing_horodate_fields_and_ensure_incremental_horodate(all_fields_names_and_values, previous_all_fields_names_and_values)

            self.create_result_line_if_needed(
                line_number=line_number,
                horodate=self.variables_line_dictionary.get_horodate_from_cheure_etc(all_fields_names_and_values),
                time_according_to_simulation_start=None,
                equipment=equipment,
                all_fields_names_and_values=all_fields_names_and_values,
            )
            previous_all_fields_names_and_values = all_fields_names_and_values


class PerturboTestResult(atc_logs.ATCTestResult):

    class Builder(atc_logs.ATCTestResult.Builder):

        def __init__(self, label: str) -> None:
            super().__init__(atc_test_result_created=PerturboTestResult(label))

        def add_files(self, directory_path: str, filename_pattern: str, equipment_name: str) -> Self:
            for file_full_path in self.get_files_full_paths(directory_path=directory_path, filename_pattern=filename_pattern):
                self.add_file(file_full_path=file_full_path, equipment_name=equipment_name)
            return self

        def add_file(self, file_full_path: str, equipment_name: str, forced_cdecenie_value: Optional[int] = None, forced_cjour_at_beginning_value: Optional[int] = None) -> Self:
            pert_file = PerturboFile(
                atc_test_result=self._atc_test_result_created,
                file_full_path=file_full_path,
                equipment_name=equipment_name,
            )
            pert_file.forced_cdecenie_value = forced_cdecenie_value
            pert_file.forced_cjour_value = forced_cjour_at_beginning_value
            self._atc_test_result_created.all_atc_test_files.append(pert_file)
            return self
