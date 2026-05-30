import datetime
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Self

from logger import logger_config

from stsloganalyzis import (
    common_filters,
)

from common import (
    time_utils,
    file_utils,
)

ATC_LOG_FILES_FIELDS_SEPARATOR = ";"


@dataclass
class Equipment:
    raw_name: str

    def __post_init__(self) -> None:
        self.name = self.raw_name


@dataclass
class Variable:
    equipment: Equipment
    name: str


@dataclass
class VariableState:
    variable: Variable
    value: str | int | bool
    timestamp: datetime.datetime


@dataclass
class VariableStateChange:
    previous_state: Optional[VariableState]
    new_state: VariableState


class EquipmentsLibrary:
    def __init__(self) -> None:
        self._all_equipments: List[Equipment] = []

    def get_or_create_equipment_by_name(self, equipment_name: str) -> Equipment:
        all_equipment_found = [eqpt for eqpt in self._all_equipments if eqpt.raw_name == equipment_name or eqpt.name == equipment_name]
        if not all_equipment_found:
            self._all_equipments.append(Equipment(raw_name=equipment_name))
            return self.get_or_create_equipment_by_name(equipment_name=equipment_name)

        assert len(all_equipment_found) == 0
        return all_equipment_found[0]


class ATCVariablesLineDictionary:
    def __init__(self, raw_line: str) -> None:
        self.all_fields = raw_line.split(ATC_LOG_FILES_FIELDS_SEPARATOR)


class VariableFilter(ABC):

    def __init__(self, string_filter=common_filters.StringFieldValueBasedFilter) -> None:
        super().__init__()
        self.string_filter = string_filter

    @abstractmethod
    def passes(self, to_test: str) -> bool:
        pass


class VariableNameFilter(VariableFilter):

    def __init__(self, white_or_black_list: common_filters.WhiteOrBlackListFilterType, variables_names: List[str], filter_type: common_filters.StringFilterType) -> None:
        super().__init__(
            string_filter=common_filters.StringFieldValueBasedFilter(
                white_or_black_list=white_or_black_list,
                filter_type=filter_type,
                field_values=variables_names,
            )
        )

    def passes(self, variable_name: str) -> bool:
        match = self.string_filter.do_passes(variable_name)
        assert isinstance(match, bool)
        return match

    def print_stats(self) -> None:
        logger_config.print_and_log_info(f"  Filter {self}: ' - rejected {self.string_filter.rejected_count} lines")

    def __str__(self) -> str:
        return f"filter {','.join(self.string_filter.filter_field_values)}"


class ATCTestResult:
    def __init__(self) -> None:
        self.equipments_library = EquipmentsLibrary()

    class Builder(ABC):

        def __init__(self) -> None:
            super().__init__()
            self.variables_filters: List[VariableFilter] = []

        def add_files(self, directory_path: str, filename_pattern: str) -> Self:
            for file_full_path in file_utils.get_files_by_directory_and_file_name_mask(directory_path, filename_pattern, file_sort_order=file_utils.FileSortOrder.TIMESTAMP_OLDER_TO_NEWER):
                self.add_file(file_full_path=file_full_path)

            return self

        def add_variables_filter(self, variables_filter: VariableFilter) -> Self:
            self.variables_filters.append(variables_filter)
            return self

        @abstractmethod
        def add_file(self, file_full_path: str) -> Self:
            pass


def pert_variable_to_timestamp(c_heure: int, c_decalage: int, c_decenie: int, c_jour: int) -> datetime.datetime:
    """
    Heure de l horodate en milliseconde
    Decalage de l heure (GMT + été hiver) en milliseconde
    """

    # Calculate the start year of the decade
    start_year = 2000 + (c_decenie * 10)

    # Calculate the date by adding the day on decade to start of the decade
    decade_date = datetime.datetime(start_year, 1, 1) + datetime.timedelta(days=c_jour)

    # timestamp = hlf.decode_hlf_to_datetime(time_field_value=c_heure / 10, time_offset_value=c_decalage, decade_field_value=c_decenie, day_on_decade_field_value=c_jour)
    total_milliseconds = c_heure + c_decalage

    hours, minutes, seconds, milliseconds = time_utils.get_hour_minute_seconds_milliseconds_from_total_milliseconds(total_milliseconds=total_milliseconds)

    # Apply the offset for local time
    local_time = decade_date + datetime.timedelta(hours=hours, minutes=minutes, seconds=seconds, milliseconds=milliseconds)

    return local_time
