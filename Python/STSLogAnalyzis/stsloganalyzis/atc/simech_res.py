from dataclasses import dataclass

from datetime import datetime
from typing import List, Self, cast

from stsloganalyzis.atc import atc_logs
from logger import logger_config


@dataclass
class SimechResFile(atc_logs.ATCTestFile):

    def __post_init__(self) -> None:
        super().__post_init__()
        self.variables_line_dictionary: atc_logs.ATCVariablesLineDictionary
        self.all_values_raw_lines: List[str] = []
        self.simulation_start_at_timestamp: datetime
        self.create_dictionary_and_raw_line_values()

    @logger_config.stopwatch_decorator(inform_beginning=True, monitor_ram_usage=True)
    def create_dictionary_and_raw_line_values(self) -> None:
        all_raw_lines = self.open_and_get_all_raw_lines()
        self._compute_simulation_start_at(all_raw_lines=all_raw_lines)
        self.variables_line_dictionary = atc_logs.ATCVariablesLineDictionary(all_raw_lines[0])
        self.all_values_raw_lines = all_raw_lines[1:]

    def _compute_simulation_start_at(self, all_raw_lines: List[str]) -> None:
        for raw_line in all_raw_lines:
            if 'SIMULATION_ENDED;"SIMU_START_AT:' in raw_line:
                raw_date_as_str = raw_line.split('SIMULATION_ENDED;"SIMU_START_AT:')[1].replace('"', "").replace(";", "").strip()
                logger_config.print_and_log_info(f"raw_date_as_str found:{raw_date_as_str}")

                # Thu May 28 12:55:42 2026
                date_format = "%a %b %d %H:%M:%S %Y"
                self.simulation_start_at_timestamp = datetime.strptime(raw_date_as_str, date_format)
                logger_config.print_and_log_info(f"simulation_start_at parsed:{self.simulation_start_at_timestamp}")

                pass

    @logger_config.stopwatch_decorator(inform_beginning=True, monitor_ram_usage=True)
    def compute_all_variables_states(self) -> None:

        pass


class SimechResTestResult(atc_logs.ATCTestResult):

    class Builder(atc_logs.ATCTestResult.Builder):

        def __init__(self, label: str) -> None:
            super().__init__(atc_test_result_created=SimechResTestResult(label))

        def add_file(self, file_full_path: str) -> Self:
            self._atc_test_result_created.all_atc_test_files.append(
                SimechResFile(
                    atc_test_result=self._atc_test_result_created,
                    file_full_path=file_full_path,
                )
            )
            return self
