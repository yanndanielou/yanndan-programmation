import datetime
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Self, cast, Tuple, Dict

from logger import logger_config

from stsloganalyzis import (
    common_filters,
)

from common import (
    time_utils,
    file_utils,
)

ATC_LOG_FILES_FIELDS_SEPARATOR = ";"

VARIABLE_STATE_TYPE = str | int | bool


@dataclass
class Equipment:
    raw_name: str

    def __post_init__(self) -> None:
        self.name = self.raw_name
        self.variables_library = EquipmentVariablesLibrary(self)


@dataclass
class Variable:
    equipment: Equipment
    name: str


@dataclass
class VariableState:
    variable: Variable
    value: VARIABLE_STATE_TYPE
    timestamp: Optional[datetime.datetime]


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


@dataclass
class EquipmentVariablesLibrary:
    equipment: Equipment

    def __post_init__(self) -> None:
        self._all_variables: List[Variable] = []

    def get_or_create_variable_by_name(self, variable_name: str) -> Variable:
        all_variable_found = [var for var in self._all_variables if var.name == variable_name]
        if not all_variable_found:
            self._all_variables.append(Variable(equipment=self.equipment, name=variable_name))
            return self.get_or_create_variable_by_name(variable_name=variable_name)

        assert len(all_variable_found) == 0
        return all_variable_found[0]


class ATCVariablesLineDictionary:
    def __init__(self, raw_line: str) -> None:
        self.all_fields = raw_line.split(ATC_LOG_FILES_FIELDS_SEPARATOR)

    @staticmethod
    def get_line_timestamp(all_fields_names_and_values: Dict[str, VARIABLE_STATE_TYPE], value_raw_line: str) -> Optional[datetime.datetime]:
        c_heure_c_decalage_c_decenie_c_jour_as_date = ATCVariablesLineDictionary.get_c_heure_c_decalage_c_decenie_c_jour_as_date(all_fields_names_and_values, value_raw_line)
        assert c_heure_c_decalage_c_decenie_c_jour_as_date is not None
        return c_heure_c_decalage_c_decenie_c_jour_as_date

    @staticmethod
    def get_c_heure_c_decalage_c_decenie_c_jour_as_date(all_fields_names_and_values: Dict[str, VARIABLE_STATE_TYPE], value_raw_line: str) -> Optional[datetime.datetime]:

        c_heure = cast(int, all_fields_names_and_values.get("CHEURE"))
        c_decalage = cast(int, all_fields_names_and_values.get("CDECALAGE"))
        c_decenie = cast(int, all_fields_names_and_values.get("CDECENNIE"))
        c_jour = cast(int, all_fields_names_and_values.get("CJOUR"))

        if any(elem is None for elem in [c_heure, c_decalage, c_decenie, c_jour]):
            return None

        return pert_variable_to_timestamp(c_heure=c_heure, c_decalage=c_decalage, c_decenie=c_decenie, c_jour=c_jour)

    def get_all_fields_names_and_values_in_data_line(self, value_raw_line: str) -> Dict[str, VARIABLE_STATE_TYPE]:

        all_fields_names_and_values: Dict[str, VARIABLE_STATE_TYPE] = dict()
        all_raw_values = value_raw_line.split(ATC_LOG_FILES_FIELDS_SEPARATOR)
        for variable_index, variable_name in enumerate(self.all_fields):
            variable_value = all_raw_values[variable_index]
            assert variable_name not in all_fields_names_and_values
            all_fields_names_and_values[variable_name] = variable_value

        return all_fields_names_and_values


class VariableFilter(ABC):

    def __init__(self, string_filter: common_filters.StringFieldValueBasedFilter) -> None:
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


class ATCTestVariablesLine(ABC):
    def __init__(self, full_raw_line: str) -> None:
        super().__init__()
        pass


@dataclass
class ATCTestFile(ABC):
    file_full_path: str
    atc_test_result: "ATCTestResult"

    @abstractmethod
    def get_equipment_name(self) -> str:
        pass

    def get_equipment(self, test_result: "ATCTestResult") -> Equipment:
        return test_result.equipments_library.get_or_create_equipment_by_name(self.get_equipment_name())

    @abstractmethod
    def get_all_raw_variables_states(self) -> List[VariableState]:
        pass


class ATCTestResult(ABC):
    def __init__(self) -> None:
        self.equipments_library = EquipmentsLibrary()
        self._all_variables: List[Variable] = []
        self.all_variables_states: List[VariableState] = []
        self.all_variables_states_changes: List[VariableStateChange] = []
        self.variables_name_filters: List[VariableNameFilter] = []

    class Builder(ABC):

        def __init__(self) -> None:
            super().__init__()
            self.variables_names_filters: List[VariableNameFilter] = []

        def get_files_full_paths(self, directory_path: str, filename_pattern: str) -> List[str]:
            ret = file_utils.get_files_by_directory_and_file_name_mask(directory_path, filename_pattern, file_sort_order=file_utils.FileSortOrder.TIMESTAMP_OLDER_TO_NEWER)
            return cast(List[str], ret)

        def add_variables_names_filter(self, variables_filter: VariableNameFilter) -> Self:
            self.variables_names_filters.append(variables_filter)
            return self


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


def variable_name_matches_all_filters(variable_name: str, all_filters: List[VariableNameFilter]) -> bool:
    return all(filter.passes(variable_name) for filter in all_filters)
