import datetime
import line_profiler
import cProfile, pstats, io
from pstats import SortKey
from warnings import deprecated
from abc import ABC, abstractmethod
from collections import OrderedDict
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Self, cast, Tuple

from common import file_name_utils, file_utils, reports_utils, time_utils, date_time_formats
from logger import logger_config

from stsloganalyzis.common import common_filters

ATC_LOG_FILES_FIELDS_SEPARATOR = ";"

VARIABLE_STATE_TYPE = str | int | bool | datetime.datetime | None


NUMBER_OF_MILLISECONDS_IN_DAY = 24 * 60 * 60 * 100
JUST_BEFORE_MIDNIGHT_IN_MILLISECONDS = NUMBER_OF_MILLISECONDS_IN_DAY - 1000


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
        assert variable_state not in self.states_chronologically_sorted
        if self.initial_state is None:
            self.initial_state = variable_state
        else:
            # if self.states_chronologically_sorted:
            # assert self.states_chronologically_sorted[-1].result_line
            # assert self.states_chronologically_sorted[-1].result_line.horodate
            # assert variable_state.result_line
            # assert variable_state.result_line.horodate
            # assert (
            #    self.states_chronologically_sorted[-1].result_line.horodate < variable_state.result_line.horodate
            # ), f"Return to past from {self.states_chronologically_sorted[-1].result_line.horodate} to {variable_state.result_line.horodate}  for {self.states_chronologically_sorted[-1].result_line.parent_file.file_full_path} in {len(self.states_chronologically_sorted)} th line"

            self.states_chronologically_sorted.append(variable_state)


@dataclass
class VariableState:
    variable: Variable
    value: VARIABLE_STATE_TYPE
    result_line: "ATCTestResultLine"

    def __post_init__(self) -> None:
        self.variable.add_state(self)


@dataclass
class VariableStateChange:
    previous_state: VariableState
    new_state: VariableState

    def __post_init__(self) -> None:
        self.variable.states_changes_chronologically_sorted.append(self)

        self.previous_state_duration = (
            (self.new_state.result_line.horodate - self.previous_state.result_line.horodate)
            if self.previous_state is not None and self.previous_state.result_line.horodate is not None and self.new_state.result_line.horodate is not None
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


@dataclass
class ATCVariablesLineDictionary:
    all_fields_names: List[str]

    @staticmethod
    def get_horodate_from_cheure_etc(all_fields_names_and_values: Dict[str, VARIABLE_STATE_TYPE]) -> Optional[datetime.datetime]:

        c_heure = cast(Optional[int], all_fields_names_and_values.get("CHEURE"))
        c_decalage = cast(int, all_fields_names_and_values.get("CDECALAGE")) or 0
        c_decenie = cast(int, all_fields_names_and_values.get("CDECENNIE")) or 0
        c_jour = cast(int, all_fields_names_and_values.get("CJOUR")) or 0

        if any(elem is None for elem in [c_heure, c_decalage, c_decenie, c_jour]):
            return None

        return pert_variable_to_timestamp(c_heure=cast(int, c_heure), c_decalage=c_decalage, c_decenie=c_decenie, c_jour=c_jour)

    def get_all_fields_names_and_values_in_data_line(self, value_raw_line: str, test_result: "ATCTestResult") -> Dict[str, VARIABLE_STATE_TYPE]:
        all_raw_values = value_raw_line.rstrip().split(ATC_LOG_FILES_FIELDS_SEPARATOR)
        return self.get_all_fields_names_and_values_in_data_raw_fields(all_raw_values=all_raw_values, test_result=test_result)

    def get_all_fields_names_and_values_in_data_raw_fields(self, all_raw_values: List[str], test_result: "ATCTestResult") -> Dict[str, VARIABLE_STATE_TYPE]:
        all_fields_names_and_values: Dict[str, VARIABLE_STATE_TYPE] = dict()

        assert len(all_raw_values) == len(self.all_fields_names)

        for variable_index, variable_name in enumerate(self.all_fields_names):
            if test_result.variable_name_must_be_created(variable_name):
                variable_raw_value = all_raw_values[variable_index]
                assert variable_name not in all_fields_names_and_values
                variable_proper_type_value = convert_to_proper_type(variable_raw_value)
                all_fields_names_and_values[variable_name] = variable_proper_type_value

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
        # self.cached_result_match_by_test_string: Dict[str, bool] = {}

    def passes(self, to_test: str) -> bool:
        # if to_test in self.cached_result_match_by_test_string:
        #    return self.cached_result_match_by_test_string[to_test]

        match = self.string_filter.do_passes(to_test)
        assert isinstance(match, bool)
        # self.cached_result_match_by_test_string[to_test] = match
        # return self.passes(to_test)
        return match

    def print_stats(self) -> None:
        logger_config.print_and_log_info(f"  Filter {self}: ' - rejected {self.string_filter.rejected_count} lines")

    def __str__(self) -> str:
        return f"filter {','.join(self.string_filter.filter_field_values)}"


@dataclass
class ATCTestResultLine(ABC):
    parent_file: "ATCTestFile"
    line_number: int
    horodate: Optional[datetime.datetime]
    time_according_to_simulation_start: Optional[datetime.datetime]
    equipment: Equipment

    all_fields_names_and_values: Dict[str, VARIABLE_STATE_TYPE]

    @line_profiler.profile
    def __post_init__(self) -> None:
        self.all_variables_states: List[VariableState] = []
        self.test_result.result_lines.append(self)

        for variable_name, variable_value in self.all_fields_names_and_values.items():
            self.handle_variable_state(variable_name=variable_name, variable_raw_value=variable_value)

    @property
    @deprecated("not used")
    def best_timestamp(self) -> Optional[datetime.datetime]:
        if self.horodate:
            return self.horodate
        return self.time_according_to_simulation_start

    @line_profiler.profile
    def handle_variable_state(self, variable_name: str, variable_raw_value: VARIABLE_STATE_TYPE) -> None:
        # logger_config.print_and_log_info(f"handle_variable_state, must be kept: {variable_name} {variable_value}")
        variable = self.equipment.variables_library.get_or_create_variable_by_name(variable_name=variable_name)
        variable_state = VariableState(variable=variable, value=variable_raw_value, result_line=self)
        self.all_variables_states.append(variable_state)

    @property
    def test_result(self) -> "ATCTestResult":
        return self.parent_file.atc_test_result


@dataclass
class ATCTestFile(ABC):
    file_full_path: str
    atc_test_result: "ATCTestResult"

    def __post_init__(self) -> None:
        self.file_name = file_name_utils.get_file_name_without_extension_from_full_path(self.file_full_path)
        self.all_lines: List[ATCTestResultLine] = []
        logger_config.print_and_log_info(f"Build {self.file_name}")
        self.forced_cdecenie_value: Optional[int] = None
        self.forced_cjour_value: Optional[int] = None
        self.last_chunk_created_timestamp = datetime.datetime.now()

    def add_missing_horodate_fields_and_ensure_incremental_horodate(
        self, all_fields_names_and_values: Dict[str, VARIABLE_STATE_TYPE], previous_all_fields_names_and_values: Optional[Dict[str, VARIABLE_STATE_TYPE]]
    ) -> Dict[str, VARIABLE_STATE_TYPE]:

        is_previous_line_just_before_midnight = previous_all_fields_names_and_values and cast(int, all_fields_names_and_values.get("CHEURE")) > JUST_BEFORE_MIDNIGHT_IN_MILLISECONDS
        previous_line_cheure = cast(int, previous_all_fields_names_and_values.get("CHEURE")) if previous_all_fields_names_and_values else None
        current_line_initial_cheure = cast(int, all_fields_names_and_values.get("CHEURE"))
        is_current_line_just_after_midnight = current_line_initial_cheure < 100
        change_of_day_detected_with_cheures = previous_line_cheure and is_previous_line_just_before_midnight and is_current_line_just_after_midnight

        if previous_line_cheure and current_line_initial_cheure <= previous_line_cheure and not change_of_day_detected_with_cheures:
            all_fields_names_and_values["CHEURE"] = previous_line_cheure + 1
            logger_config.print_and_log_info(f"Fix Cheure from {current_line_initial_cheure} to {all_fields_names_and_values["CHEURE"]} to avoir return to past")

        if "CJOUR" not in all_fields_names_and_values and self.forced_cjour_value:
            if change_of_day_detected_with_cheures:
                assert previous_all_fields_names_and_values
                logger_config.print_and_log_info(f"Detect new day from {all_fields_names_and_values.get("CHEURE")} to {previous_all_fields_names_and_values.get("CHEURE")}")
                self.forced_cjour_value += 1
            all_fields_names_and_values["CJOUR"] = self.forced_cjour_value

        if "CDECENNIE" not in all_fields_names_and_values and self.forced_cdecenie_value:
            all_fields_names_and_values["CDECENNIE"] = self.forced_cdecenie_value

        return all_fields_names_and_values

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

    @line_profiler.profile
    def create_result_line_if_needed(
        self,
        line_number: int,
        horodate: Optional[datetime.datetime],
        time_according_to_simulation_start: Optional[datetime.datetime],
        equipment: Equipment,
        all_fields_names_and_values: Dict[str, VARIABLE_STATE_TYPE],
    ) -> None:

        def variable_must_be_ignored_because_timestamp_filters(timestamp: datetime.datetime, all_filters: List[common_filters.DatesFilter.DateBetweenFilter]) -> bool:
            return all(filter.do_passes(timestamp) for filter in all_filters) if all_filters else True

        if horodate:
            if not variable_must_be_ignored_because_timestamp_filters(horodate, self.atc_test_result.variables_timestamp_creation_filters):
                return
        if time_according_to_simulation_start:
            if not variable_must_be_ignored_because_timestamp_filters(time_according_to_simulation_start, self.atc_test_result.variables_timestamp_creation_filters):
                return

        self.all_lines.append(
            ATCTestResultLine(
                line_number=line_number,
                parent_file=self,
                horodate=horodate,
                time_according_to_simulation_start=time_according_to_simulation_start,
                equipment=equipment,
                all_fields_names_and_values=all_fields_names_and_values,
            )
        )

        if len(self.all_lines) % 1000 == 0:
            logger_config.print_and_log_info(
                f"{len(self.all_lines)} lines created so far. Duration since last chunk {date_time_formats.format_duration_between_timestamps_to_string(self.last_chunk_created_timestamp,datetime.datetime.now())}"
            )
            self.last_chunk_created_timestamp = datetime.datetime.now()


@dataclass
class ATCTestResult(ABC):
    label: str

    def __post_init__(self) -> None:
        self.equipments_library = EquipmentsLibrary()
        self.all_variables_unsorted: List[Variable] = []
        self.all_variables_states_sorted_by_line_number: List[VariableState] = []
        self._all_variables_states_changes_unsorted: List[VariableStateChange] = []
        self.all_variables_states_changes_sorted_by_timestamp: List[VariableStateChange] = []
        self.variables_names_creation_filters: List[VariableNameFilter] = []
        self.variables_timestamp_creation_filters: List[common_filters.DatesFilter.DateBetweenFilter] = []
        self.output_directory_path = "output"
        self.all_atc_test_files: List[ATCTestFile] = []
        self.result_lines: List[ATCTestResultLine] = []
        self.variable_name_must_be_created_cache_result: Dict[str, bool] = {}

        logger_config.print_and_log_info(f"Build {self.label}")

    @line_profiler.profile
    def variable_name_must_be_created(self, variable_name: str) -> bool:
        if variable_name in self.variable_name_must_be_created_cache_result:
            return self.variable_name_must_be_created_cache_result[variable_name]

        self.variable_name_must_be_created_cache_result[variable_name] = variable_name_must_be_kept_after_filters(variable_name=variable_name, all_filters=self.variables_names_creation_filters)
        return self.variable_name_must_be_created(variable_name=variable_name)

    @logger_config.stopwatch_decorator()
    @line_profiler.profile
    def process(self) -> None:
        for atc_test_file in self.all_atc_test_files:
            atc_test_file.compute_all_variables_states()
            logger_config.print_and_log_info(f"In file {atc_test_file.file_name}, {len(atc_test_file.all_lines)} kept")

        for equipment in self.equipments_library.all_equipments:
            self.all_variables_unsorted += equipment.variables_library.all_variables

        self._compute_variables_states()
        self._compute_variables_states_changes()

        logger_config.print_and_log_info(f"{len(self.all_variables_unsorted)} variables_unsorted")
        logger_config.print_and_log_info(f"{len(self.all_variables_states_sorted_by_line_number)} all_variables_states_sorted_by_line_number")
        logger_config.print_and_log_info(f"{len(self._all_variables_states_changes_unsorted)} _all_variables_states_changes_unsorted")
        logger_config.print_and_log_info(f"{len(self.all_variables_states_changes_sorted_by_timestamp)} all_variables_states_changes_sorted_by_timestamp")

    @logger_config.stopwatch_decorator()
    @line_profiler.profile
    def _compute_variables_states(self) -> None:
        all_variables_unsorted = [state for variable in self.all_variables_unsorted for state in variable.states_chronologically_sorted]
        self.all_variables_states_sorted_by_line_number = sorted(all_variables_unsorted, key=lambda state: state.result_line.line_number)
        assert self.all_variables_states_sorted_by_line_number

    @logger_config.stopwatch_decorator(inform_beginning=True, monitor_ram_usage=True)
    @line_profiler.profile
    def _compute_variables_states_changes(self) -> None:
        for variable in self.all_variables_unsorted:
            previous_state = None
            for state in variable.states_chronologically_sorted:
                if previous_state is not None and state.value != previous_state.value:
                    variable_state_change = VariableStateChange(previous_state, state)
                    self._all_variables_states_changes_unsorted.append(variable_state_change)
                previous_state = state

        with logger_config.stopwatch_with_label("Order states changes"):
            self.all_variables_states_changes_sorted_by_timestamp = sorted(self._all_variables_states_changes_unsorted, key=lambda state_change: state_change.new_state.result_line.line_number)

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
                        "horodate": state_change.new_state.result_line.horodate,
                        "Date according to simulation start": state_change.new_state.result_line.time_according_to_simulation_start,
                        "line": state_change.new_state.result_line.line_number,
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
                        "horodate": state.result_line.horodate,
                        "Date according to simulation start": state.result_line.time_according_to_simulation_start,
                        "line": state.result_line.line_number,
                        "equipment": state.variable.equipment.name,
                        "variable": state.variable.name,
                        "value": state.value,
                    }
                )
                for state in self.all_variables_states_sorted_by_line_number
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
                result_line_dict["horodate"] = result_line.horodate
                result_line_dict["Date according to simulation start"] = result_line.time_according_to_simulation_start
                result_line_dict["line"] = result_line.line_number
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
                        "horodate": state_change.new_state.result_line.horodate,
                        "Date according to simulation start": state_change.new_state.result_line.time_according_to_simulation_start,
                        "line": state_change.new_state.result_line.line_number,
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
                        "horodate": state.result_line.horodate,
                        "Date according to simulation start": state.result_line.time_according_to_simulation_start,
                        "line": state.result_line.line_number,
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

        def build(self) -> "ATCTestResult":

            # pr = cProfile.Profile()
            # pr.enable()

            if self._atc_test_result_created.label == "" and len(self._atc_test_result_created.all_atc_test_files) == 1:
                pass

            self._atc_test_result_created.process()

            # pr.disable()
            # s = io.StringIO()
            # sortby = SortKey.CUMULATIVE
            # ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
            # ps.print_stats()
            # print(s.getvalue())
            # ps.sort_stats(SortKey.TIME, SortKey.CUMULATIVE).print_stats(0.5, "init")
            # ps.print_callees()

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


@line_profiler.profile
def convert_to_proper_type(value: str) -> VARIABLE_STATE_TYPE:
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
