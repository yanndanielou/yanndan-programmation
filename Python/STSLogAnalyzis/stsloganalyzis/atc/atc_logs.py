import datetime
from abc import ABC, abstractmethod
from collections import OrderedDict
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Self, Tuple, cast

from common import file_name_utils, file_utils, reports_utils, time_utils
from logger import logger_config

from stsloganalyzis.common import common_filters

ATC_LOG_FILES_FIELDS_SEPARATOR = ";"

VARIABLE_STATE_TYPE = str | int | bool | datetime.datetime


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

    def __post_init__(self) -> None:
        self.initial_state: Optional["VariableState"] = None
        self.states_chronologically_sorted: List[VariableState] = []
        self.states_changes_chronologically_sorted: List[VariableStateChange] = []

    def add_state(self, variable_state: "VariableState") -> None:
        if self.initial_state is None:
            self.initial_state = variable_state
        else:
            self.states_chronologically_sorted.append(variable_state)


@dataclass
class VariableState:
    variable: Variable
    value: VARIABLE_STATE_TYPE
    timestamp: Optional[datetime.datetime]

    def __post_init__(self) -> None:
        self.variable.states_chronologically_sorted.append(self)


@dataclass
class VariableStateChange:
    previous_state: VariableState
    new_state: VariableState

    def __post_init__(self) -> None:
        self.variable.states_changes_chronologically_sorted.append(self)

        self.previous_state_duration = (
            (self.new_state.timestamp - self.previous_state.timestamp)
            if self.previous_state is not None and self.previous_state.timestamp is not None and self.new_state.timestamp is not None
            else None
        )

    @property
    def variable(self) -> Variable:
        return self.previous_state.variable


class EquipmentsLibrary:
    def __init__(self) -> None:
        self.all_equipments: List[Equipment] = []

    def get_or_create_equipment_by_name(self, equipment_name: str) -> Equipment:
        all_equipment_found = [eqpt for eqpt in self.all_equipments if eqpt.raw_name == equipment_name or eqpt.name == equipment_name]
        if not all_equipment_found:
            self.all_equipments.append(Equipment(raw_name=equipment_name))
            return self.get_or_create_equipment_by_name(equipment_name=equipment_name)

        assert len(all_equipment_found) == 1
        return all_equipment_found[0]


@dataclass
class EquipmentVariablesLibrary:
    equipment: Equipment

    def __post_init__(self) -> None:
        self.all_variables: List[Variable] = []

    def get_or_create_variable_by_name(self, variable_name: str) -> Variable:
        all_variable_found = [var for var in self.all_variables if var.name == variable_name]
        if not all_variable_found:
            self.all_variables.append(Variable(equipment=self.equipment, name=variable_name))
            return self.get_or_create_variable_by_name(variable_name=variable_name)

        assert len(all_variable_found) == 1
        return all_variable_found[0]


class ATCVariablesLineDictionary:
    def __init__(self, raw_line: str) -> None:
        self.all_fields = raw_line.split(ATC_LOG_FILES_FIELDS_SEPARATOR)

    @staticmethod
    def _convert_to_proper_type(value: str) -> VARIABLE_STATE_TYPE:
        """Convert string value to proper type (bool, int, or str)."""
        # Try to convert to bool
        if value.lower() in ("VRAI", "true", "1", "yes", "on"):
            return True
        if value.lower() in ("FAUX", "false", "0", "no", "off"):
            return False

        # Try to convert to int
        try:
            return int(value)
        except ValueError:
            pass

        # Keep as string
        return value

    @staticmethod
    def get_line_timestamp(all_fields_names_and_values: Dict[str, VARIABLE_STATE_TYPE], value_raw_line: str) -> datetime.datetime:
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
        all_raw_values = value_raw_line.rstrip().split(ATC_LOG_FILES_FIELDS_SEPARATOR)
        for variable_index, variable_name in enumerate(self.all_fields):
            variable_value = all_raw_values[variable_index]
            assert variable_name not in all_fields_names_and_values
            all_fields_names_and_values[variable_name] = self._convert_to_proper_type(variable_value)

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


@dataclass
class ATCTestResultLine(ABC):
    timestamp: datetime.datetime
    equipment: Equipment
    test_result: "ATCTestResult"
    all_fields_names_and_values: Dict[str, VARIABLE_STATE_TYPE]

    def __post_init__(self) -> None:
        self.all_variables_states: List[VariableState] = []
        self.test_result.result_lines.append(self)

        for variable_name, variable_value in self.all_fields_names_and_values.items():
            self.handle_variable_state(variable_name=variable_name, variable_value=variable_value)

    def handle_variable_state(self, variable_name: str, variable_value: VARIABLE_STATE_TYPE) -> None:
        # logger_config.print_and_log_info(f"handle_variable_state: {variable_name} {variable_value}")
        if variable_name_must_be_kept_after_filters(variable_name=variable_name, all_filters=self.test_result.variables_names_creation_filters):
            # logger_config.print_and_log_info(f"handle_variable_state, must be kept: {variable_name} {variable_value}")
            variable = self.equipment.variables_library.get_or_create_variable_by_name(variable_name=variable_name)
            variable_state = VariableState(variable=variable, timestamp=self.timestamp, value=variable_value)
            variable.add_state(variable_state)
            self.all_variables_states.append(variable_state)


@dataclass
class ATCTestFile(ABC):
    file_full_path: str
    atc_test_result: "ATCTestResult"

    def __post_init__(self) -> None:
        self.file_name = file_name_utils.get_file_name_without_extension_from_full_path(self.file_full_path)

    @abstractmethod
    def compute_all_variables_states(self) -> None:
        pass

    @logger_config.stopwatch_decorator(inform_beginning=True, monitor_ram_usage=True)
    def open_and_get_all_raw_lines(self) -> List[str]:

        with open(self.file_full_path, mode="r", encoding="ANSI") as file:
            all_raw_lines = file.readlines()
            logger_config.print_and_log_info(f"Perturbo file {self.file_full_path} has {len(all_raw_lines)} lines")
            assert all_raw_lines
            return all_raw_lines


@dataclass
class ATCTestResult(ABC):
    label: str

    def __post_init__(self) -> None:
        self.equipments_library = EquipmentsLibrary()
        self.all_variables_unsorted: List[Variable] = []
        self.all_variables_states_sorted_by_timestamp: List[VariableState] = []
        self._all_variables_states_changes_unsorted: List[VariableStateChange] = []
        self.all_variables_states_changes_sorted_by_timestamp: List[VariableStateChange] = []
        self.variables_names_creation_filters: List[VariableNameFilter] = []
        self.variables_timestamp_creation_filters: List[common_filters.DatesFilter.DateBetweenFilter] = []
        self.output_directory_path = "output"
        self.all_atc_test_files: List[ATCTestFile] = []
        self.result_lines: List[ATCTestResultLine] = []

    @logger_config.stopwatch_decorator()
    def process(self) -> None:
        for atc_test_file in self.all_atc_test_files:
            atc_test_file.compute_all_variables_states()

        for equipment in self.equipments_library.all_equipments:
            self.all_variables_unsorted += equipment.variables_library.all_variables

        self._compute_variables_states()
        self._compute_variables_states_changes()

    @logger_config.stopwatch_decorator()
    def _compute_variables_states(self) -> None:
        all_variables_unsorted = [state for variable in self.all_variables_unsorted for state in variable.states_chronologically_sorted]
        self.all_variables_states_sorted_by_timestamp = sorted(all_variables_unsorted, key=lambda state: state.timestamp or datetime.datetime.min)
        assert self.all_variables_states_sorted_by_timestamp

    @logger_config.stopwatch_decorator(inform_beginning=True, monitor_ram_usage=True)
    def _compute_variables_states_changes(self) -> None:
        for variable in self.all_variables_unsorted:
            previous_state = None
            for state in variable.states_chronologically_sorted:
                if previous_state is not None and state.value != previous_state.value:
                    variable_state_change = VariableStateChange(previous_state, state)
                    self._all_variables_states_changes_unsorted.append(variable_state_change)
                previous_state = state

        with logger_config.stopwatch_with_label("Order states changes"):
            self.all_variables_states_changes_sorted_by_timestamp = sorted(
                self._all_variables_states_changes_unsorted, key=lambda state_change: state_change.new_state.timestamp or datetime.datetime.min
            )

    def create_report_all_variables(self, variables_names_reports_filters: Optional[List[VariableNameFilter]] = None, files_base_name: Optional[str] = None) -> None:
        if variables_names_reports_filters is None:
            variables_names_reports_filters = []

        if files_base_name is None:
            files_base_name = f"{self.label}_all"

        self._create_report_all_variables_state_changes(variables_names_reports_filters=variables_names_reports_filters, files_base_name=files_base_name)
        self._create_report_all_variables_states_variable_by_column(variables_names_reports_filters=variables_names_reports_filters, files_base_name=files_base_name)
        self._create_report_all_variables_states_variable_by_rows(variables_names_reports_filters=variables_names_reports_filters, files_base_name=files_base_name)

    def _create_report_all_variables_state_changes(self, variables_names_reports_filters: List[VariableNameFilter], files_base_name: str) -> None:
        reports_utils.save_rows_to_output_files(
            rows_as_list_dict=[
                OrderedDict(
                    {
                        "date": state_change.new_state.timestamp,
                        "equipment": state_change.variable.equipment.name,
                        "variable": state_change.variable.name,
                        "old_value": state_change.previous_state.value if state_change.previous_state else None,
                        "new_value": state_change.new_state.value,
                        "previous_state_duration": state_change.previous_state_duration,
                    }
                )
                for state_change in self.all_variables_states_changes_sorted_by_timestamp
                if variable_name_must_be_kept_after_filters(state_change.variable.name, variables_names_reports_filters)
            ],
            file_base_name=f"{files_base_name}_state_changes",
            output_directory_path=self.output_directory_path,
            suffix_file_name_by_date=reports_utils.SuffixFileNameByDate.DO_BOTH,
        )

    def _create_report_all_variables_states_variable_by_rows(self, variables_names_reports_filters: List[VariableNameFilter], files_base_name: str) -> None:

        reports_utils.save_rows_to_output_files(
            rows_as_list_dict=[
                OrderedDict(
                    {
                        "date": state.timestamp,
                        "equipment": state.variable.equipment.name,
                        "variable": state.variable.name,
                        "value": state.value,
                    }
                )
                for state in self.all_variables_states_sorted_by_timestamp
                if variable_name_must_be_kept_after_filters(state.variable.name, variables_names_reports_filters)
            ],
            file_base_name=f"{files_base_name}_states_variable_by_rows",
            output_directory_path=self.output_directory_path,
            suffix_file_name_by_date=reports_utils.SuffixFileNameByDate.DO_BOTH,
        )

    def _create_report_all_variables_states_variable_by_column(self, variables_names_reports_filters: List[VariableNameFilter], files_base_name: str) -> None:

        rows_as_list_dict = []
        # for state in self.all_variables_states_sorted_by_timestamp if variable_name_must_be_kept_after_filters(state.variable.name, variables_names_reports_filters):
        for result_line in self.result_lines:
            variables_states = [state for state in result_line.all_variables_states if variable_name_must_be_kept_after_filters(state.variable.name, variables_names_reports_filters)]
            if variables_states:
                result_line_dict: Dict[str, VARIABLE_STATE_TYPE] = OrderedDict()
                rows_as_list_dict.append(result_line_dict)
                result_line_dict["date"] = result_line.timestamp
                result_line_dict["equipment"] = result_line.equipment.name

            for variable_state in variables_states:
                result_line_dict[variable_state.variable.name] = variable_state.value

        reports_utils.save_rows_to_output_files(
            rows_as_list_dict=rows_as_list_dict,
            file_base_name=f"{files_base_name}_states_variable_by_column",
            output_directory_path=self.output_directory_path,
            suffix_file_name_by_date=reports_utils.SuffixFileNameByDate.DO_BOTH,
        )

    def create_report_for_variable(self, variable: Variable, files_base_name: Optional[str] = None) -> None:
        if files_base_name is None:
            files_base_name = f"{self.label}_variable_{variable.name}"

        # all state changes
        reports_utils.save_rows_to_output_files(
            rows_as_list_dict=[
                OrderedDict(
                    {
                        "date": state_change.new_state.timestamp,
                        "old_value": state_change.previous_state.value if state_change.previous_state else None,
                        "new_value": state_change.new_state.value,
                        "previous_state_duration": state_change.previous_state_duration,
                    }
                )
                for state_change in variable.states_changes_chronologically_sorted
            ],
            file_base_name=f"{files_base_name}_state_changes",
            output_directory_path=self.output_directory_path,
            suffix_file_name_by_date=reports_utils.SuffixFileNameByDate.DO_BOTH,
        )

        reports_utils.save_rows_to_output_files(
            rows_as_list_dict=[
                OrderedDict(
                    {
                        "date": state.timestamp,
                        "value": state.value,
                    }
                )
                for state in variable.states_chronologically_sorted
            ],
            file_base_name=f"{files_base_name}_all_states",
            output_directory_path=self.output_directory_path,
            suffix_file_name_by_date=reports_utils.SuffixFileNameByDate.DO_BOTH,
        )

    class Builder(ABC):

        def __init__(self, atc_test_result_created: "ATCTestResult") -> None:
            super().__init__()
            self._atc_test_result_created = atc_test_result_created

        def get_files_full_paths(self, directory_path: str, filename_pattern: str) -> List[str]:
            ret = file_utils.get_files_by_directory_and_file_name_mask(directory_path, filename_pattern, file_sort_order=file_utils.FileSortOrder.TIMESTAMP_OLDER_TO_NEWER)
            return cast(List[str], ret)

        def add_variables_names_creation_filter(self, variables_filter: VariableNameFilter) -> Self:
            self._atc_test_result_created.variables_names_creation_filters.append(variables_filter)
            return self

        def add_timestamp_filter(self, timestamp_filter: common_filters.DatesFilter.DateBetweenFilter) -> Self:
            self._atc_test_result_created.variables_timestamp_creation_filters.append(timestamp_filter)
            return self

        def add_files(self, directory_path: str, filename_pattern: str, equipment_name: str) -> Self:
            for file_full_path in self.get_files_full_paths(directory_path=directory_path, filename_pattern=filename_pattern):
                self.add_file(file_full_path=file_full_path, equipment_name=equipment_name)
            return self

        def build(self) -> "ATCTestResult":
            if self._atc_test_result_created.label == "" and len(self._atc_test_result_created.all_atc_test_files) == 1:
                pass

            self._atc_test_result_created.process()
            return self._atc_test_result_created


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


def variable_name_must_be_kept_after_filters(variable_name: str, all_filters: List[VariableNameFilter]) -> bool:
    # if not all_filters:
    #    return True
    return all(filter.passes(variable_name) for filter in all_filters) if all_filters else True
