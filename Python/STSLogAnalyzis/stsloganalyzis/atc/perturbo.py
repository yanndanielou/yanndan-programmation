from dataclasses import dataclass
from typing import Self

import line_profiler
from logger import logger_config

from stsloganalyzis.atc import atc_logs


@dataclass
class PerturboFile(atc_logs.ATCTestFile):

    equipment_name: str

    def __post_init__(self) -> None:
        super().__post_init__()
        self.variables_line_dictionary: atc_logs.ATCVariablesLineDictionary
        self.all_values_raw_lines: list[str] = []
        self.create_dictionary_and_raw_line_values()

    @logger_config.stopwatch_decorator(inform_beginning=True, monitor_ram_usage=True)
    def create_dictionary_and_raw_line_values(self) -> None:
        all_raw_lines = self.open_and_get_all_raw_lines()
        self.variables_line_dictionary = atc_logs.ATCVariablesLineDictionary(all_raw_lines[0].split(atc_logs.ATC_LOG_FILES_FIELDS_SEPARATOR))
        self.all_values_raw_lines = all_raw_lines[1:]

    def get_equipment_name(self) -> str:
        return self.equipment_name

    def get_equipment(self, test_result: atc_logs.ATCTestResult) -> atc_logs.Equipment:
        ret = test_result.get_or_create_equipment_by_name_if_allowed(self.get_equipment_name())
        assert ret is not None
        return ret

    @logger_config.stopwatch_decorator(inform_beginning=True, monitor_ram_usage=True)
    @line_profiler.profile
    def compute_all_variables_states(self) -> None:

        equipment = self.atc_test_result.get_or_create_equipment_by_name_if_allowed(self.equipment_name)
        if equipment:
            assert isinstance(equipment, atc_logs.Equipment)

            for line_number, value_raw_line in enumerate(self.all_values_raw_lines):

                all_fields_names_and_raw_values = self.variables_line_dictionary.get_all_fields_names_and_values_in_data_line(value_raw_line, self.atc_test_result)

                self.create_result_line_if_needed(
                    line_number=line_number,
                    time_according_to_simulation_start=None,
                    equipment=equipment,
                    all_fields_names_and_raw_values=all_fields_names_and_raw_values,
                )


class PerturboTestResult(atc_logs.ATCTestResult):

    class Builder(atc_logs.ATCTestResult.Builder):

        def __init__(self, label: str, environment_name: str = "") -> None:
            super().__init__(atc_test_result_created=PerturboTestResult(label, environment_name))

        def add_files(self, directory_path: str, filename_pattern: str, equipment_name: str) -> Self:
            for file_full_path in self.get_files_full_paths(directory_path=directory_path, filename_pattern=filename_pattern):
                self.add_file(file_full_path=file_full_path, equipment_name=equipment_name)
            return self

        def add_file(self, file_full_path: str, equipment_name: str, forced_cdecenie_value: int | None = None, forced_cjour_at_beginning_value: int | None = None) -> Self:
            pert_file = PerturboFile(
                atc_test_result=self._atc_test_result_created,
                file_full_path=file_full_path,
                equipment_name=equipment_name,
                do_not_inform_same_horodate_as_last_line=False,  # Should only happen on SIMECH
            )
            pert_file.forced_cdecenie_value = forced_cdecenie_value
            pert_file.current_forced_cjour_value = forced_cjour_at_beginning_value
            self._atc_test_result_created.all_atc_test_files.append(pert_file)
            return self
