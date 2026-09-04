import datetime
import statistics
from abc import ABC, abstractmethod
from collections import OrderedDict, defaultdict
from dataclasses import dataclass
from enum import Enum
from typing import Self, cast

import line_profiler
import numpy
from common import (
    date_time_formats,
    file_name_utils,
    file_utils,
    reports_utils,
    time_utils,
)
from logger import logger_config

from stsloganalyzis.common import common_filters

ATC_LOG_FILES_FIELDS_SEPARATOR = ";"

VARIABLE_STATE_TYPE_WITHOUT_NONE = str | int | float | bool | datetime.datetime
VARIABLE_STATE_TYPE_WITH_NONE = VARIABLE_STATE_TYPE_WITHOUT_NONE | None


NUMBER_OF_MILLISECONDS_IN_DAY = 24 * 60 * 60 * 100
JUST_BEFORE_MIDNIGHT_IN_MILLISECONDS = NUMBER_OF_MILLISECONDS_IN_DAY - 1000


class EquipmentType(Enum):
    PAS = "PAS"
    PAL = "PAL"
    PAE = "PAE"


class VariablesTypesLibrary:

    def __init__(self, variable_type_by_name_dictionnary: dict[str, "VariablesTypesLibrary.VariableType"] | None = None) -> None:
        self._variable_type_by_name_dictionary: dict[str, VariablesTypesLibrary.VariableType] = variable_type_by_name_dictionnary if variable_type_by_name_dictionnary else {}

        for i in range(1, 3):
            self.add_variable_type(f"STAB_CPT{i}", VariablesTypesLibrary.VariableType.FLOAT_TYPE)

        self.add_variable_type("TEMPS_AS", VariablesTypesLibrary.VariableType.INT_TYPE)

    def add_variable_type(self, variable_name: str, variable_type: "VariablesTypesLibrary.VariableType") -> None:
        assert variable_name not in self._variable_type_by_name_dictionary
        self._variable_type_by_name_dictionary[variable_name] = variable_type

    def get_known_variable_type(self, variable_name: str) -> "VariablesTypesLibrary.VariableType | None":
        return self._variable_type_by_name_dictionary.get(variable_name)

    class VariableType(Enum):
        INT_TYPE = "INT_TYPE"
        FLOAT_TYPE = "FLOAT_TYPE"


@dataclass
class Equipment:
    raw_name: str

    def __post_init__(self) -> None:
        self.name = self.raw_name
        self.variables_library = EquipmentVariablesLibrary(self)
        self.all_variables_states_changes_unsorted: list[VariableStateChange] = []
        self.all_variables_states_changes_sorted_by_timestamp: list[VariableStateChange] = []
        self.number_of_lines_with_horodate_conflits = 0
        self.equipment_type = (
            # fmt: off
            EquipmentType.PAS if "PAS" in self.raw_name   
            else EquipmentType.PAE if "CC" in self.raw_name
            else EquipmentType.PAE if "PAE" in self.raw_name 
            else EquipmentType.PAL if "PAL" in self.raw_name else None
            # fmt: on
        )
        assert self.equipment_type is not None, f"Could not find type of equipment {self.raw_name}"

    @logger_config.stopwatch_decorator(inform_beginning=True, monitor_ram_usage=True)
    def order_states_changes(self) -> None:
        with logger_config.stopwatch_with_label("Order states changes"):
            self.all_variables_states_changes_sorted_by_timestamp = sorted(self.all_variables_states_changes_unsorted, key=lambda state_change: state_change.new_state.result_line.line_number)

    def print_stats(self) -> None:
        logger_config.print_and_log_info(f"Equipment {self.name} : {len(self.all_variables_states_changes_unsorted)} _all_variables_states_changes_unsorted")
        logger_config.print_and_log_info(f"Equipment {self.name} : {len(self.all_variables_states_changes_sorted_by_timestamp)} all_variables_states_changes_sorted_by_timestamp")


@dataclass
class Variable:
    equipment: Equipment
    name: str
    known_variable_type: VariablesTypesLibrary.VariableType | None

    def __post_init__(self) -> None:
        self.initial_state: None | InstantVariableState = None
        self.instant_states_chronologically_sorted: list[InstantVariableState] = []
        self.states_changes_chronologically_sorted: list[VariableStateChange] = []
        self.continuous_states_chronologically_sorted: list[ContinuousVariableState] = []
        self.number_of_occurrences_by_value: dict[VARIABLE_STATE_TYPE_WITH_NONE, int] = defaultdict(int)
        self._cached_instant_states_best_values: list[VARIABLE_STATE_TYPE_WITH_NONE] | None = None

    @property
    def all_instant_states_best_values(self) -> list[VARIABLE_STATE_TYPE_WITH_NONE]:
        if self._cached_instant_states_best_values is not None:
            return self._cached_instant_states_best_values

        self._cached_instant_states_best_values = [instant_variable_state.best_value for instant_variable_state in self.instant_states_chronologically_sorted]
        return self.all_instant_states_best_values

    @property
    def mean_numeric_values_by_number_occurrences(self) -> float:
        assert self.known_variable_type
        assert self.known_variable_type in [VariablesTypesLibrary.VariableType.INT_TYPE, VariablesTypesLibrary.VariableType.FLOAT_TYPE]
        ret_as_float_64 = numpy.mean(cast(list[int | float], self.all_instant_states_best_values))
        ret_as_float = ret_as_float_64.item()
        return ret_as_float

    @property
    def median_numeric_values_by_number_occurrences(self) -> float:
        assert self.known_variable_type
        assert self.known_variable_type in [VariablesTypesLibrary.VariableType.INT_TYPE, VariablesTypesLibrary.VariableType.FLOAT_TYPE]
        ret_as_float_64 = numpy.median(cast(list[int | float], self.all_instant_states_best_values))
        ret = ret_as_float_64.item()
        return ret

    @property
    def variance_numeric_values_by_number_occurrences(self) -> float:
        assert self.known_variable_type
        assert self.known_variable_type in [VariablesTypesLibrary.VariableType.INT_TYPE, VariablesTypesLibrary.VariableType.FLOAT_TYPE]
        return statistics.pvariance(cast(list[int | float], self.all_instant_states_best_values))

    @property
    def ecart_type_numeric_values_by_number_occurrences(self) -> float:
        assert self.known_variable_type
        assert self.known_variable_type in [VariablesTypesLibrary.VariableType.INT_TYPE, VariablesTypesLibrary.VariableType.FLOAT_TYPE]
        return statistics.pstdev(cast(list[int | float], self.all_instant_states_best_values))

    @property
    def min_numeric_values_by_number_occurrences(self) -> int | float:
        assert self.known_variable_type
        assert self.known_variable_type in [VariablesTypesLibrary.VariableType.INT_TYPE, VariablesTypesLibrary.VariableType.FLOAT_TYPE]
        ret = min(cast(list[int | float], self.all_instant_states_best_values))
        return ret

    @property
    def max_numeric_values_by_number_occurrences(self) -> int | float:
        assert self.known_variable_type
        assert self.known_variable_type in [VariablesTypesLibrary.VariableType.INT_TYPE, VariablesTypesLibrary.VariableType.FLOAT_TYPE]
        ret = max(cast(list[int | float], self.all_instant_states_best_values))
        return ret

    @property
    def deciles_numeric_values_by_number_occurrences(self) -> list[float]:
        assert self.known_variable_type
        assert self.known_variable_type in [VariablesTypesLibrary.VariableType.INT_TYPE, VariablesTypesLibrary.VariableType.FLOAT_TYPE]
        ret = numpy.percentile(cast(list[int | float], self.all_instant_states_best_values), numpy.arange(10, 100, 10))
        return cast(list[float], ret)

    @property
    def centiles_numeric_values_by_number_occurrences(self) -> list[float]:
        assert self.known_variable_type
        assert self.known_variable_type in [VariablesTypesLibrary.VariableType.INT_TYPE, VariablesTypesLibrary.VariableType.FLOAT_TYPE]
        ret = numpy.percentile(cast(list[int | float], self.all_instant_states_best_values), numpy.arange(1, 100, 1))
        return cast(list[float], ret)

    @line_profiler.profile
    def add_state(self, variable_state: "InstantVariableState") -> None:
        self.number_of_occurrences_by_value[variable_state.best_value] += 1
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

            self.instant_states_chronologically_sorted.append(variable_state)


@dataclass
class ContinuousVariableState:
    variable: Variable
    raw_str_value: str

    def __post_init__(self) -> None:
        self.all_instant_variable_states: list[InstantVariableState] = []
        self.value_in_proper_type = self._convert_to_known_type(self.raw_str_value, self.variable.known_variable_type) if self.variable.known_variable_type else None

    @property
    def best_value(self) -> VARIABLE_STATE_TYPE_WITH_NONE:
        return self.value_in_proper_type if self.value_in_proper_type is not None else self.raw_str_value

    def _convert_to_known_type(self, raw_str_value: str, known_variable_type: VariablesTypesLibrary.VariableType) -> VARIABLE_STATE_TYPE_WITH_NONE:
        if known_variable_type == VariablesTypesLibrary.VariableType.INT_TYPE:
            return int(raw_str_value)
        if known_variable_type == VariablesTypesLibrary.VariableType.FLOAT_TYPE:
            return float(raw_str_value)

        assert False, f"Unsupported type {known_variable_type}"


@dataclass
class InstantVariableState:
    result_line: "ATCTestResultLine"
    continuous_variable_state: ContinuousVariableState

    def __post_init__(self) -> None:
        self.variable.add_state(self)
        self.continuous_variable_state.all_instant_variable_states.append(self)

    @property
    def raw_value(self) -> str:
        return self.continuous_variable_state.raw_str_value

    @property
    def best_value(self) -> VARIABLE_STATE_TYPE_WITH_NONE:
        return self.continuous_variable_state.best_value

    @property
    def variable(self) -> Variable:
        return self.continuous_variable_state.variable


@dataclass
class VariableStateChange:
    previous_state: InstantVariableState
    new_state: InstantVariableState

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
        self.all_equipments: list[Equipment] = []

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
        self.all_variables: list[Variable] = []

    def has_variable_with_name(self, variable_name: str) -> bool:
        all_variable_found = [var for var in self.all_variables if var.name == variable_name]
        return all_variable_found is not None

    def get_variable_with_name_if_exists(self, variable_name: str) -> Variable | None:
        all_variable_found = [var for var in self.all_variables if var.name == variable_name]
        if not all_variable_found:
            return None
        assert len(all_variable_found) == 1
        return all_variable_found[0]

    @line_profiler.profile
    def get_or_create_variable_by_name(self, variable_name: str, variables_types_library: VariablesTypesLibrary) -> Variable:
        variable_found = self.get_variable_with_name_if_exists(variable_name)
        if variable_found is None:
            self.all_variables.append(Variable(equipment=self.equipment, name=variable_name, known_variable_type=variables_types_library.get_known_variable_type(variable_name)))
            return cast(Variable, self.get_or_create_variable_by_name(variable_name=variable_name, variables_types_library=variables_types_library))
        return variable_found


@dataclass
class ATCVariablesLineDictionary:
    all_fields_names: list[str]

    @staticmethod
    def get_horodate_from_cheure_etc(all_fields_names_and_raw_values: dict[str, str]) -> None | datetime.datetime:

        c_heure = cast(None | int, all_fields_names_and_raw_values.get("CHEURE"))
        c_decalage = cast(int, all_fields_names_and_raw_values.get("CDECALAGE")) or 0
        c_decenie = cast(int, all_fields_names_and_raw_values.get("CDECENNIE")) or 0
        c_jour = cast(int, all_fields_names_and_raw_values.get("CJOUR")) or 0

        if any(elem is None for elem in [c_heure, c_decalage, c_decenie, c_jour]):
            return None

        return pert_variable_to_timestamp(c_heure=cast(int, c_heure), c_decalage=c_decalage, c_decenie=c_decenie, c_jour=c_jour)

    def get_all_fields_names_and_values_in_data_line(self, value_raw_line: str, test_result: "ATCTestResult") -> dict[str, str]:
        all_raw_values = value_raw_line.rstrip().split(ATC_LOG_FILES_FIELDS_SEPARATOR)
        return self.get_all_fields_names_and_values_in_data_raw_fields(all_raw_values=all_raw_values, test_result=test_result)

    def get_all_fields_names_and_values_in_data_raw_fields(self, all_raw_values: list[str], test_result: "ATCTestResult") -> dict[str, str]:
        all_fields_names_and_raw_values: dict[str, str] = {}

        assert len(all_raw_values) == len(self.all_fields_names), f"Inconsistency in {','.join(all_raw_values)}"

        for variable_index, variable_name in enumerate(self.all_fields_names):
            if test_result.variable_name_must_be_created(variable_name):
                variable_raw_value = all_raw_values[variable_index]
                assert variable_name not in all_fields_names_and_raw_values
                # variable_proper_type_value = convert_to_proper_type(variable_raw_value)
                all_fields_names_and_raw_values[variable_name] = variable_raw_value

        return all_fields_names_and_raw_values


class VariableFilter(ABC):

    def __init__(self, string_filter: common_filters.StringFieldValueBasedFilter) -> None:
        super().__init__()
        self.string_filter = string_filter

    @abstractmethod
    def passes(self, to_test: str) -> bool:
        pass


class VariableNameFilter(VariableFilter):

    def __init__(self, white_or_black_list: common_filters.WhiteOrBlackListFilterType, variables_names: list[str], filter_type: common_filters.StringFilterType) -> None:
        super().__init__(
            string_filter=common_filters.StringFieldValueBasedFilter(
                white_or_black_list=white_or_black_list,
                filter_type=filter_type,
                field_values=variables_names,
            )
        )
        # self.cached_result_match_by_test_string: dict[str, bool] = {}

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


class EquipmentNameFilter(VariableFilter):

    def __init__(self, white_or_black_list: common_filters.WhiteOrBlackListFilterType, variables_names: list[str], filter_type: common_filters.StringFilterType) -> None:
        super().__init__(
            string_filter=common_filters.StringFieldValueBasedFilter(
                white_or_black_list=white_or_black_list,
                filter_type=filter_type,
                field_values=variables_names,
            )
        )

    def passes(self, to_test: str) -> bool:
        match = self.string_filter.do_passes(to_test)
        assert isinstance(match, bool)
        return match

    def print_stats(self) -> None:
        logger_config.print_and_log_info(f"  Filter {self}: ' - rejected {self.string_filter.rejected_count} lines")

    def __str__(self) -> str:
        return f"filter {','.join(self.string_filter.filter_field_values)}"


@dataclass
class ATCTestResultLine:
    parent_file: "ATCTestFile"
    line_number: int
    horodate: None | datetime.datetime
    time_according_to_simulation_start: None | datetime.datetime
    equipment: Equipment

    all_fields_names_and_raw_values: dict[str, str]

    @line_profiler.profile
    def __post_init__(self) -> None:
        self.all_variables_states: list[InstantVariableState] = []
        self.test_result.result_lines.append(self)

        for variable_name, variable_raw_value in self.all_fields_names_and_raw_values.items():
            self.handle_variable_state(variable_name=variable_name, variable_raw_value=variable_raw_value)

    @property
    def best_timestamp(self) -> None | datetime.datetime:
        if self.horodate:
            return self.horodate
        return self.time_according_to_simulation_start

    @line_profiler.profile
    def handle_variable_state(self, variable_name: str, variable_raw_value: str) -> None:
        # logger_config.print_and_log_info(f"handle_variable_state, must be kept: {variable_name} {variable_raw_value}")
        variable = self.equipment.variables_library.get_or_create_variable_by_name(variable_name=variable_name, variables_types_library=self.parent_file.atc_test_result.variables_types_library)
        assert isinstance(variable, Variable)
        previous_variable_continuous_state = variable.continuous_states_chronologically_sorted[-1] if variable.continuous_states_chronologically_sorted else None
        if previous_variable_continuous_state is None or previous_variable_continuous_state.raw_str_value != variable_raw_value:
            variable.continuous_states_chronologically_sorted.append(
                ContinuousVariableState(
                    variable=variable,
                    raw_str_value=variable_raw_value,
                )
            )

        variable_state = InstantVariableState(
            result_line=self,
            continuous_variable_state=variable.continuous_states_chronologically_sorted[-1],
        )
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
        self.all_lines: list[ATCTestResultLine] = []
        logger_config.print_and_log_info(f"Build {self.file_name}")
        self.forced_cdecenie_value: None | int = None
        self.current_forced_cjour_value: None | int = None
        self.last_chunk_created_timestamp = datetime.datetime.now()  # noqa: DTZ005

    def get_last_line_for_equipment(self, equipment: Equipment) -> None | ATCTestResultLine:
        for previous_line_it in reversed(self.all_lines):
            if previous_line_it.equipment == equipment:
                return previous_line_it

        return None

    @line_profiler.profile
    def get_horodate(self, all_fields_names_and_raw_values: dict[str, str], equipment: Equipment) -> None | datetime.datetime:

        if "CHEURE" not in all_fields_names_and_raw_values:
            return None

        previous_line = self.get_last_line_for_equipment(equipment)
        assert previous_line is not self

        if previous_line and previous_line.horodate is None:
            return None

        if previous_line is not None:

            previous_line_cheure = int(cast(str, previous_line.all_fields_names_and_raw_values.get("CHEURE"))) if "CHEURE" in previous_line.all_fields_names_and_raw_values else None

            if previous_line_cheure is not None:
                is_previous_line_just_before_midnight = previous_line.all_fields_names_and_raw_values and previous_line_cheure > JUST_BEFORE_MIDNIGHT_IN_MILLISECONDS
                current_line_initial_cheure = int(cast(str, all_fields_names_and_raw_values.get("CHEURE")))
                is_current_line_just_after_midnight = current_line_initial_cheure < 100

                change_of_day_detected_with_cheures = previous_line_cheure and is_previous_line_just_before_midnight and is_current_line_just_after_midnight

                if previous_line.horodate and "CJOUR" not in all_fields_names_and_raw_values and self.current_forced_cjour_value and change_of_day_detected_with_cheures:
                    assert previous_line.all_fields_names_and_raw_values
                    logger_config.print_and_log_info(f"Detect new day from {all_fields_names_and_raw_values.get("CHEURE")} to {previous_line.all_fields_names_and_raw_values.get("CHEURE")}")
                    self.current_forced_cjour_value += 1

        c_heure = int(cast(str, all_fields_names_and_raw_values.get("CHEURE")))
        c_decalage_used = int(cast(str, all_fields_names_and_raw_values.get("CDECALAGE"))) if "CDECALAGE" in all_fields_names_and_raw_values else 0
        c_decenie_used = (
            self.forced_cdecenie_value
            if self.forced_cdecenie_value is not None
            else int(cast(str, all_fields_names_and_raw_values.get("CDECENNIE"))) if "CDECENNIE" in all_fields_names_and_raw_values else 0
        )
        c_jour_used = self.current_forced_cjour_value if self.current_forced_cjour_value is not None else int(cast(int, all_fields_names_and_raw_values.get("CJOUR"))) or 0

        if any(elem is None for elem in [c_heure, c_decalage_used, c_decenie_used, c_jour_used]):
            return None

        horodate_computed = pert_variable_to_timestamp(c_heure=c_heure, c_decalage=c_decalage_used, c_decenie=c_decenie_used, c_jour=c_jour_used)

        if previous_line and previous_line.horodate and previous_line.horodate >= horodate_computed:
            new_horodate = horodate_computed + datetime.timedelta(milliseconds=1)

            equipment.number_of_lines_with_horodate_conflits += 1

            if horodate_computed == previous_line.horodate:
                logger_config.print_and_log_info(
                    f"Fix horodate for {equipment.name} from {horodate_computed} (CHEURE {all_fields_names_and_raw_values["CHEURE"]}) to {new_horodate} to avoid same date, previous line was {previous_line_cheure}. File:{self.file_name}",
                    do_not_print=True,
                )

            logger_config.print_and_log_warning_if(
                horodate_computed < previous_line.horodate,
                f"Fix horodate for {equipment.name} from {horodate_computed} (CHEURE {all_fields_names_and_raw_values["CHEURE"]}) to {new_horodate} to avoid return to past, previous line was {previous_line_cheure}. File:{self.file_name}",
            )

        return horodate_computed

    @abstractmethod
    def compute_all_variables_states(self) -> None:
        pass

    @logger_config.stopwatch_decorator(inform_beginning=True, monitor_ram_usage=True)
    def open_and_get_all_raw_lines(self) -> list[str]:

        with open(self.file_full_path, mode="r", encoding="ANSI") as file:
            all_raw_lines = file.readlines()
            logger_config.print_and_log_info(f"Perturbo file {self.file_full_path} has {len(all_raw_lines)} lines")
            assert all_raw_lines
            return all_raw_lines

    @line_profiler.profile
    def create_result_line_if_needed(
        self,
        line_number: int,
        time_according_to_simulation_start: None | datetime.datetime,
        equipment: Equipment,
        all_fields_names_and_raw_values: dict[str, str],
    ) -> None:

        def variable_must_be_ignored_because_timestamp_filters(timestamp: datetime.datetime, all_filters: list[common_filters.DatesFilter.DateBetweenFilter]) -> bool:
            return all(filter.do_passes(timestamp) for filter in all_filters) if all_filters else True

        horodate = cast(None | datetime.datetime, self.get_horodate(all_fields_names_and_raw_values, equipment))

        if horodate and not variable_must_be_ignored_because_timestamp_filters(horodate, self.atc_test_result.variables_timestamp_creation_filters):
            return
        if time_according_to_simulation_start and not variable_must_be_ignored_because_timestamp_filters(time_according_to_simulation_start, self.atc_test_result.variables_timestamp_creation_filters):
            return

        self.all_lines.append(
            ATCTestResultLine(
                line_number=line_number,
                parent_file=self,
                horodate=horodate,
                time_according_to_simulation_start=time_according_to_simulation_start,
                equipment=equipment,
                all_fields_names_and_raw_values=all_fields_names_and_raw_values,
            )
        )

        if len(self.all_lines) % 20000 == 0:
            logger_config.print_and_log_info(
                f"{len(self.all_lines)} lines handled so far. Duration since last chunk {date_time_formats.format_duration_between_timestamps_to_string(self.last_chunk_created_timestamp,datetime.datetime.now())}"  # noqa: DTZ005
            )
            self.last_chunk_created_timestamp = datetime.datetime.now()  # noqa: DTZ005


@dataclass
class ATCTestResult(ABC):
    label: str

    def __post_init__(self) -> None:
        self.equipments_library = EquipmentsLibrary()
        self.all_variables_unsorted: list[Variable] = []
        self.all_variables_states_sorted_by_line_number: list[InstantVariableState] = []
        self._all_variables_states_changes_unsorted: list[VariableStateChange] = []
        self.all_variables_states_changes_sorted_by_timestamp: list[VariableStateChange] = []
        self.variables_names_creation_filters: list[VariableNameFilter] = []
        self.variables_timestamp_creation_filters: list[common_filters.DatesFilter.DateBetweenFilter] = []
        self.variables_types_library = VariablesTypesLibrary()
        self.output_directory_path = "output"
        self.all_atc_test_files: list[ATCTestFile] = []
        self.result_lines: list[ATCTestResultLine] = []
        self.variable_name_must_be_created_cache_result: dict[str, bool] = {}

        logger_config.print_and_log_info(f"Build {self.label}")

    @line_profiler.profile
    def variable_name_must_be_created(self, variable_name: str) -> bool:
        if variable_name in self.variable_name_must_be_created_cache_result:
            return self.variable_name_must_be_created_cache_result[variable_name]

        self.variable_name_must_be_created_cache_result[variable_name] = variable_name_must_be_kept_after_filters(variable_name=variable_name, all_filters=self.variables_names_creation_filters)
        return cast(bool, self.variable_name_must_be_created(variable_name=variable_name))

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

        for equipment in self.equipments_library.all_equipments:
            equipment.order_states_changes()
            equipment.print_stats()

        self.print_stats()

    def print_stats(self) -> None:
        logger_config.print_and_log_info(f"{len(self.all_variables_unsorted)} variables_unsorted")
        logger_config.print_and_log_info(f"{len(self.all_variables_states_sorted_by_line_number)} all_variables_states_sorted_by_line_number")
        logger_config.print_and_log_info(f"{len(self._all_variables_states_changes_unsorted)} _all_variables_states_changes_unsorted")
        logger_config.print_and_log_info(f"{len(self.all_variables_states_changes_sorted_by_timestamp)} all_variables_states_changes_sorted_by_timestamp")

        for equipment in self.equipments_library.all_equipments:
            logger_config.print_and_log_info(f"{equipment.name} : {equipment.number_of_lines_with_horodate_conflits} hordate conflicts")

    @logger_config.stopwatch_decorator()
    @line_profiler.profile
    def _compute_variables_states(self) -> None:
        all_variables_unsorted = [state for variable in self.all_variables_unsorted for state in variable.instant_states_chronologically_sorted]
        self.all_variables_states_sorted_by_line_number = sorted(all_variables_unsorted, key=lambda state: state.result_line.line_number)
        assert self.all_variables_states_sorted_by_line_number

    @logger_config.stopwatch_decorator(inform_beginning=True, monitor_ram_usage=True)
    @line_profiler.profile
    def _compute_variables_states_changes(self) -> None:
        for variable in self.all_variables_unsorted:
            previous_state = None
            for state in variable.instant_states_chronologically_sorted:
                if previous_state is not None and state.best_value != previous_state.best_value:
                    variable_state_change = VariableStateChange(previous_state, state)
                    self._all_variables_states_changes_unsorted.append(variable_state_change)
                    variable.equipment.all_variables_states_changes_unsorted.append(variable_state_change)
                previous_state = state

        with logger_config.stopwatch_with_label("Order states changes"):
            self.all_variables_states_changes_sorted_by_timestamp = sorted(self._all_variables_states_changes_unsorted, key=lambda state_change: state_change.new_state.result_line.line_number)

    def create_report_all_variables(
        self,
        variables_names_reports_filters: None | list[VariableNameFilter] = None,
        equipment_names_reports_filters: None | list[EquipmentNameFilter] = None,
        files_base_name: None | str = None,
        create_report_all_variables: bool = True,
        create_report_all_variables_state_changes: bool = True,
        create_report_all_variables_states_variable_by_column: bool = True,
        create_report_all_variables_states_variable_by_rows: bool = True,
    ) -> None:
        if variables_names_reports_filters is None:
            variables_names_reports_filters = []

        if files_base_name is None:
            files_base_name = f"{self.label}_all"

        if equipment_names_reports_filters is None and create_report_all_variables:
            for equipment in self.equipments_library.all_equipments:
                self.create_report_all_variables(
                    variables_names_reports_filters=variables_names_reports_filters,
                    files_base_name=files_base_name + "_" + equipment.name,
                    equipment_names_reports_filters=[
                        EquipmentNameFilter(
                            white_or_black_list=common_filters.WhiteOrBlackListFilterType.WHITELIST,
                            filter_type=common_filters.StringFilterType.EQUALS_TO,
                            variables_names=[equipment.name],
                        )
                    ],
                )

        if create_report_all_variables_state_changes:
            self._create_report_all_variables_state_changes(
                variables_names_reports_filters=variables_names_reports_filters,
                equipment_names_reports_filters=equipment_names_reports_filters,
                files_base_name=files_base_name,
            )

        if create_report_all_variables_states_variable_by_column:
            self._create_report_all_variables_states_variable_by_column(
                variables_names_reports_filters=variables_names_reports_filters,
                equipment_names_reports_filters=equipment_names_reports_filters,
                files_base_name=files_base_name,
            )

        if create_report_all_variables_states_variable_by_rows:
            self._create_report_all_variables_states_variable_by_rows(
                variables_names_reports_filters=variables_names_reports_filters,
                equipment_names_reports_filters=equipment_names_reports_filters,
                files_base_name=files_base_name,
            )

    def _create_report_all_variables_state_changes(
        self,
        variables_names_reports_filters: list[VariableNameFilter],
        files_base_name: str,
        equipment_names_reports_filters: None | list[EquipmentNameFilter] = None,
    ) -> None:
        reports_utils.save_rows_to_output_files(
            rows_as_list_dict=[
                OrderedDict(
                    {
                        "horodate": state_change.new_state.result_line.horodate,
                        "Date according to simulation start": state_change.new_state.result_line.time_according_to_simulation_start,
                        "line": state_change.new_state.result_line.line_number,
                        "equipment": state_change.variable.equipment.name,
                        "variable": state_change.variable.name,
                        "old_value": state_change.previous_state.best_value if state_change.previous_state else None,
                        "new_value": state_change.new_state.best_value,
                        "previous_state_duration": state_change.previous_state_duration,
                    }
                )
                for state_change in self.all_variables_states_changes_sorted_by_timestamp
                if variable_name_must_be_kept_after_filters(state_change.variable.name, variables_names_reports_filters)
                and equipment_must_be_kept_after_filters(state_change.variable.equipment.name, equipment_names_reports_filters)
            ],
            file_base_name=f"{files_base_name}_state_changes",
            output_directory_path=self.output_directory_path,
            suffix_file_name_by_date=reports_utils.SuffixFileNameByDate.NO,
            split_big_files=False,
        )

    def _create_report_all_variables_states_variable_by_rows(
        self,
        variables_names_reports_filters: list[VariableNameFilter],
        files_base_name: str,
        equipment_names_reports_filters: None | list[EquipmentNameFilter] = None,
    ) -> None:

        reports_utils.save_rows_to_output_files(
            rows_as_list_dict=[
                OrderedDict(
                    {
                        "horodate": state.result_line.horodate,
                        "Date according to simulation start": state.result_line.time_according_to_simulation_start,
                        "line": state.result_line.line_number,
                        "equipment": state.variable.equipment.name,
                        "variable": state.variable.name,
                        "value": state.best_value,
                    }
                )
                for state in self.all_variables_states_sorted_by_line_number
                if variable_name_must_be_kept_after_filters(state.variable.name, variables_names_reports_filters)
                and equipment_must_be_kept_after_filters(state.variable.equipment.name, equipment_names_reports_filters)
            ],
            file_base_name=f"{files_base_name}_states_variable_by_rows",
            output_directory_path=self.output_directory_path,
            suffix_file_name_by_date=reports_utils.SuffixFileNameByDate.NO,
            split_big_files=False,
        )

    def _create_report_all_variables_states_variable_by_column(
        self,
        variables_names_reports_filters: list[VariableNameFilter],
        files_base_name: str,
        equipment_names_reports_filters: None | list[EquipmentNameFilter] = None,
    ) -> None:

        rows_as_list_dict = []
        # for state in self.all_variables_states_sorted_by_timestamp if variable_name_must_be_kept_after_filters(state.variable.name, variables_names_reports_filters):
        for result_line in self.result_lines:
            variables_states = [
                state
                for state in result_line.all_variables_states
                if variable_name_must_be_kept_after_filters(state.variable.name, variables_names_reports_filters)
                and equipment_must_be_kept_after_filters(state.variable.equipment.name, equipment_names_reports_filters)
            ]
            if variables_states:
                result_line_dict: dict[str, VARIABLE_STATE_TYPE_WITH_NONE] = OrderedDict()
                rows_as_list_dict.append(result_line_dict)
                result_line_dict["horodate"] = result_line.horodate
                result_line_dict["Date according to simulation start"] = result_line.time_according_to_simulation_start
                result_line_dict["line"] = result_line.line_number
                result_line_dict["equipment"] = result_line.equipment.name

            for variable_state in variables_states:
                result_line_dict[variable_state.variable.name] = variable_state.best_value

        reports_utils.save_rows_to_output_files(
            rows_as_list_dict=rows_as_list_dict,
            file_base_name=f"{files_base_name}_states_variable_by_column",
            output_directory_path=self.output_directory_path,
            suffix_file_name_by_date=reports_utils.SuffixFileNameByDate.NO,
            split_big_files=False,
        )

    def create_report_for_variable(self, variable: Variable, files_base_name: None | str = None) -> None:
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
                        "old_value": state_change.previous_state.best_value if state_change.previous_state else None,
                        "new_value": state_change.new_state.best_value,
                        "previous_state_duration": state_change.previous_state_duration,
                    }
                )
                for state_change in variable.states_changes_chronologically_sorted
            ],
            file_base_name=f"{files_base_name}_state_changes",
            output_directory_path=self.output_directory_path,
            suffix_file_name_by_date=reports_utils.SuffixFileNameByDate.NO,
            split_big_files=False,
        )

        reports_utils.save_rows_to_output_files(
            rows_as_list_dict=[
                OrderedDict(
                    {
                        "horodate": state.result_line.horodate,
                        "Date according to simulation start": state.result_line.time_according_to_simulation_start,
                        "line": state.result_line.line_number,
                        "value": state.best_value,
                    }
                )
                for state in variable.instant_states_chronologically_sorted
            ],
            file_base_name=f"{files_base_name}_all_states",
            output_directory_path=self.output_directory_path,
            suffix_file_name_by_date=reports_utils.SuffixFileNameByDate.NO,
            split_big_files=False,
        )

    class Builder(ABC):

        def __init__(self, atc_test_result_created: "ATCTestResult") -> None:
            super().__init__()
            self._atc_test_result_created = atc_test_result_created

        def get_files_full_paths(self, directory_path: str, filename_pattern: str) -> list[str]:
            ret = file_utils.get_files_by_directory_and_file_name_mask(directory_path, filename_pattern, file_sort_order=file_utils.FileSortOrder.TIMESTAMP_OLDER_TO_NEWER)
            return cast(list[str], ret)

        def add_variables_names_creation_filter(self, variables_filter: VariableNameFilter) -> Self:
            self._atc_test_result_created.variables_names_creation_filters.append(variables_filter)
            return self

        def add_timestamp_filter(self, timestamp_filter: common_filters.DatesFilter.DateBetweenFilter) -> Self:
            self._atc_test_result_created.variables_timestamp_creation_filters.append(timestamp_filter)
            return self

        def add_variables_types_library(self, variables_types_library: VariablesTypesLibrary) -> Self:
            self._atc_test_result_created.variables_types_library = variables_types_library
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
    decade_date = datetime.datetime(start_year, 1, 1) + datetime.timedelta(days=c_jour)  # noqa: DTZ001

    # timestamp = hlf.decode_hlf_to_datetime(time_field_value=c_heure / 10, time_offset_value=c_decalage, decade_field_value=c_decenie, day_on_decade_field_value=c_jour)
    total_milliseconds = c_heure + c_decalage

    hours, minutes, seconds, milliseconds = time_utils.get_hour_minute_seconds_milliseconds_from_total_milliseconds(total_milliseconds=total_milliseconds)

    # Apply the offset for local time
    local_time = decade_date + datetime.timedelta(hours=hours, minutes=minutes, seconds=seconds, milliseconds=milliseconds)

    return local_time


def variable_name_must_be_kept_after_filters(variable_name: str, all_filters: list[VariableNameFilter]) -> bool:
    return all(filter.passes(variable_name) for filter in all_filters) if all_filters else True


def equipment_must_be_kept_after_filters(equipment_name: str, all_filters: None | list[EquipmentNameFilter]) -> bool:
    return all(filter.passes(equipment_name) for filter in all_filters) if all_filters else True


@line_profiler.profile
def convert_to_proper_type(value: str) -> VARIABLE_STATE_TYPE_WITH_NONE:
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
