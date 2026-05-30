from dataclasses import dataclass
from typing import List, Self

from stsloganalyzis import atc_logs
from logger import logger_config


@dataclass
class PerturboFile:
    file_full_path: str

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


class PerturboTest(atc_logs.ATCTestResult):

    def __init__(self) -> None:
        super().__init__()
        self.all_perturbo_files: List[PerturboFile] = []

    class Builder(atc_logs.ATCTestResult.Builder):

        def __init__(self) -> None:
            super().__init__()
            self._perturbo_test_created = PerturboTest()

        def add_file(self, file_full_path: str) -> Self:
            self._perturbo_test_created.all_perturbo_files.append(PerturboFile(file_full_path=file_full_path))
            return self

        def build(self) -> "PerturboTest":
            return self._perturbo_test_created
