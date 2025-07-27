import datetime
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import timedelta
from enum import auto, Enum
from typing import Any, Dict, List, Optional, Set, cast

import pandas as pd
from common import enums_utils, string_utils, list_utils, file_utils
from dateutil import relativedelta
from logger import logger_config

from generatecfxhistory import cfx_extended_history, role, utils, release_role_mapping, conversions
from generatecfxhistory.constants import State

from abc import ABC, abstractmethod


DEFAULT_CHAMPFX_DETAILS_EXCEL_FILE_FULL_PATH: str = "../Input/extract_cfx_details.xlsx"
DEFAULT_CHAMPFX_STATES_CHANGES_EXCEL_FILE_FULL_PATH: str = "../Input/extract_cfx_change_state.xlsx"
DEFAULT_CHAMPFX_EXTENDED_HISTORY_FILE_FULL_PATH: str = "../Input/cfx_extended_history.txt"
DEFAULT_USER_AND_ROLE_DATA_FILE_FULL_PATH: str = "Input/role_data_next_ats.txt"


class RequestType(enums_utils.NameBasedEnum):
    CHANGE_REQUEST_EXTERNAL = auto()
    DEFECT = auto()
    CHANGE_REQUEST_INTERNAL = auto()
    DEVELOPMENT_REQUEST = auto()
    HAZARD = auto()
    ACTION_ITEM = auto()
    OPEN_POINT = auto()
    DEFECT_INTERNAL = auto()
    CHANGE_REQUEST_PLM = auto()
    CHANGE_REQUEST_PROJECTS = auto()
    MPP = auto()
    TO_BE_ADDED_YDA = auto()


class RejectionCause(Enum):
    NONE = auto()
    NO_FIX_CHANGE = auto()
    DUPLICATE = auto()
    NOT_A_BUG = auto()
    NOT_PART_OF_CONTRACT = auto()
    FORWARDED_TO_SAP_CS = auto()
    NOT_REPRODUCIBLE = auto()
    SOLVED_INDIRECTLY = auto()
    OUT_OF_SCOPE = auto()
    WILL_NOT_BE_FIXED = auto()
    ALREADY_DONE = auto()
    TO_BE_ADDED_YDA = auto()

    def __repr__(self) -> str:
        return self.name

    def __str__(self) -> str:
        return self.name


class Category(Enum):
    SYSTEM = auto()
    SOFTWARE = auto()
    HARDWARE = auto()
    DOCUMENTATION = auto()
    CONFIGURATION_DATA = auto()
    PROCESS = auto()
    TEST_CASE = auto()
    CONSTRAINT_TO_3RD_PARTY = auto()
    NONE = auto()
    TBD = auto()
    MONTAGE = auto()
    TO_BE_ADDED_YDA = auto()

    def __repr__(self) -> str:
        return self.name

    def __str__(self) -> str:
        return self.name


class CfxProject:
    FR_NEXTEO: str = "FR_NEXTEO"
    ATSP: str = "ATSP"


class SecurityRelevant(enums_utils.NameBasedEnum):
    YES = auto()
    NO = auto()
    MITIGATED = auto()
    UNDEFINED = auto()


class ActionType(enums_utils.NameBasedEnum):
    IMPORT = auto()
    RESUBMIT = auto()
    SUBMIT = auto()
    ASSIGN = auto()
    ANALYSE = auto()
    POSTPONE = auto()
    REJECT = auto()
    RESOLVE = auto()
    VERIFY = auto()
    VALIDATE = auto()
    CLOSE = auto()


class OneTimestampResult:
    def __init__(self, all_results_to_display: "AllResultsPerDates", timestamp: datetime.datetime):
        self._timestamp = timestamp
        self.count_by_state: dict[State, int] = defaultdict(int)
        self.all_results_to_display = all_results_to_display

    def add_one_result_for_state(self, state: State) -> None:
        self.count_by_state[state] += 1

    def is_empty(self) -> bool:
        return len(self.count_by_state) > 0

    def consolidate(self) -> None:
        all_states_found = list(self.count_by_state.keys())
        self.all_results_to_display.present_states.update(all_states_found)

    @property
    def timestamp(self) -> datetime.datetime:
        return self._timestamp


class AllResultsPerDates:
    def __init__(self) -> None:
        self.timestamp_results: List[OneTimestampResult] = []
        self.present_states: Set[State] = set()

        self.cumulative_counts: Dict[State, List[int]] = dict()
        self.all_cfx_ids_that_have_matched: set[str] = set()
        self.all_cfx_that_have_matched: set[ChampFXEntry] = set()
        self.at_least_one_cfx_matching_filter_has_been_found = False

    def is_empty(self) -> bool:
        return not self.all_cfx_ids_that_have_matched

    def get_all_timestamps(self) -> List[datetime.datetime]:
        all_timestamps = [results.timestamp for results in self.timestamp_results]
        return all_timestamps

    def present_states_ordered(self) -> List[State]:
        return sorted(self.present_states)

    def get_state_counts_per_timestamp(self) -> List[dict[State, int]]:
        return [results.count_by_state for results in self.timestamp_results]

    def compute_cumulative_counts(self) -> None:
        self.cumulative_counts = {state: [] for state in self.present_states_ordered()}
        for one_timestamp in self.timestamp_results:
            for state in self.present_states_ordered():
                self.cumulative_counts[state].append(one_timestamp.count_by_state[state])


def get_tomorrow_naive() -> datetime.datetime:
    tomorrow_naive = (datetime.datetime.now() + timedelta(days=1)).replace(tzinfo=None)
    return tomorrow_naive


def get_today_naive() -> datetime.datetime:
    today_naive = datetime.datetime.now().replace(tzinfo=None)
    return today_naive


class DatesGenerator:
    def __init__(self) -> None:
        pass

    def get_dates_since(self, start_date: datetime.datetime) -> List[datetime.datetime]:
        all_dates: List[datetime.datetime] = self._compute_dates_since_until_today(start_date=start_date)
        # Add today if not exist
        today_naive = get_today_naive()
        if today_naive not in all_dates:
            all_dates.append(today_naive)

        # Add tomorrow  if not exist
        tomorrow_naive = get_tomorrow_naive()
        if not tomorrow_naive in all_dates:
            all_dates.append(tomorrow_naive)

        logger_config.print_and_log_info(f"Number of dates since:{start_date}: {len(all_dates)}")
        return all_dates

    def _compute_dates_since_until_today(self, start_date: datetime.datetime) -> List[datetime.datetime]:
        return []


class SpecificForTestsDatesGenerator(DatesGenerator):
    def __init__(self, all_dates_to_generate: List[datetime.datetime]) -> None:
        super().__init__()
        self._all_dates_to_generate: List[datetime.datetime] = all_dates_to_generate

    def get_dates_since(self, start_date: datetime.datetime) -> List[datetime.datetime]:
        return self._all_dates_to_generate


class ConstantIntervalDatesGenerator(DatesGenerator):
    def __init__(self, time_delta: relativedelta.relativedelta) -> None:
        super().__init__()
        self._time_delta = time_delta

    def _compute_dates_since_until_today(self, start_date: datetime.datetime) -> List[datetime.datetime]:
        dates = []

        today_naive = get_today_naive()

        # Ensure 'current_date' is naive datetime.datetime
        current_date_iter = start_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0, tzinfo=None)
        while current_date_iter <= today_naive:
            dates.append(current_date_iter)
            current_date_iter = current_date_iter + self._time_delta

        return dates


class DecreasingIntervalDatesGenerator(DatesGenerator):
    def __init__(self) -> None:
        super().__init__()

    def _compute_dates_since_until_today(self, start_date: datetime.datetime) -> List[datetime.datetime]:

        # Ensure 'beginning_of_next_month' is naive datetime.datetime
        today_naive = get_today_naive()

        dates = []

        # Ensure 'current_date' is naive datetime.datetime
        current_date_iter = start_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0, tzinfo=None)

        while current_date_iter <= today_naive:
            dates.append(current_date_iter)

            current_date_delta_with_now = datetime.datetime.now() - current_date_iter
            days_diff = current_date_delta_with_now.days

            # Compare using days to determine the time delta
            if days_diff > 365 * 3:
                time_delta = relativedelta.relativedelta(months=3)

            elif days_diff > 365 * 2:
                time_delta = relativedelta.relativedelta(months=2)

            elif days_diff > 365:
                time_delta = relativedelta.relativedelta(months=1)

            elif days_diff > 180:
                time_delta = relativedelta.relativedelta(weeks=2)

            elif days_diff > 30:
                time_delta = relativedelta.relativedelta(weeks=1)

            elif days_diff > 15:
                time_delta = relativedelta.relativedelta(days=3)

            elif days_diff > 7:
                time_delta = relativedelta.relativedelta(days=2)

            else:
                time_delta = relativedelta.relativedelta(days=1)

            current_date_iter += time_delta

        return dates


@dataclass
class BaseAction:
    _cfx_request: "ChampFXEntry"
    _timestamp: datetime.datetime

    @property
    def timestamp(self) -> datetime.datetime:
        return self._timestamp

    @property
    def cfx_request(self) -> "ChampFXEntry":
        return self._cfx_request


@dataclass
class ChangeCurrentOwnerAction(BaseAction):
    _previous_owner: role.CfxUser
    _new_owner: role.CfxUser

    @property
    def new_owner(self) -> role.CfxUser:
        return self._new_owner

    @property
    def previous_owner(self) -> role.CfxUser:
        return self._previous_owner


@dataclass
class ChangeStateAction(BaseAction):
    _old_state: State
    _new_state: State
    _action: ActionType

    @property
    def new_state(self) -> State:
        return self._new_state

    @property
    def old_state(self) -> State:
        return self._old_state

    @property
    def action(self) -> ActionType:
        return self._action


def convert_cfx_history_element_to_valid_full_name(cfx_history_element_state: str) -> str:
    return cfx_history_element_state.split("(")[0].strip()


def get_earliest_submit_date(cfx_list: List["ChampFXEntry"]) -> datetime.datetime:
    earliest_date = min((oldest_action.timestamp for entry in cfx_list if (oldest_action := entry.get_oldest_change_action_by_new_state(State.SUBMITTED)) is not None), default=None)
    logger_config.print_and_log_info(f"Earliest submit date among {len(cfx_list)} CFX: {earliest_date}")
    return earliest_date


@dataclass
class ChampFxInputs:
    champfx_details_excel_files_full_data_frames: Dict[str, pd.DataFrame]
    champfx_states_changes_excel_files_data_frames: Dict[str, pd.DataFrame]
    cfx_extended_history_files_contents: List[str]
    user_and_role_data_text_file_full_path: Optional[str]


class ChampFxInputsBuilder:
    def __init__(self) -> None:

        self.champfx_details_excel_files_full_paths: List[str] = []
        self.champfx_details_excel_files_full_data_frames: Dict[str, pd.DataFrame] = dict()

        self.champfx_states_changes_excel_files_full_paths: List[str] = []
        self.champfx_states_changes_excel_files_data_frames: Dict[str, pd.DataFrame] = dict()

        self.cfx_extended_history_files_full_paths: List[str] = []
        self.cfx_extended_history_files_contents: List[str] = []

        self.user_and_role_data_text_file_full_path: Optional[str] = None

    def add_champfx_details_excel_file_full_path(self, champfx_details_excel_file_full_path: str) -> "ChampFxInputsBuilder":
        self.champfx_details_excel_files_full_paths.append(champfx_details_excel_file_full_path)
        return self

    def add_champfx_details_excel_files_by_directory_and_file_name_mask(self, directory_path: str, filename_pattern: str) -> "ChampFxInputsBuilder":
        files_found = file_utils.get_files_by_directory_and_file_name_mask(directory_path=directory_path, filename_pattern=filename_pattern)
        for file in files_found:
            self.add_champfx_details_excel_file_full_path(file)
        # [self.add_champfx_details_excel_file_full_path(file) for file in files_found]
        return self

    def add_champfx_states_changes_excel_file_full_path(self, champfx_states_changes_excel_file_full_path: str) -> "ChampFxInputsBuilder":
        self.champfx_states_changes_excel_files_full_paths.append(champfx_states_changes_excel_file_full_path)
        return self

    def add_champfx_states_changes_excel_files_by_directory_and_file_name_mask(self, directory_path: str, filename_pattern: str) -> "ChampFxInputsBuilder":
        files_found = file_utils.get_files_by_directory_and_file_name_mask(directory_path=directory_path, filename_pattern=filename_pattern)
        list(map(self.add_champfx_states_changes_excel_file_full_path, files_found))
        return self

    def add_cfx_extended_history_file_full_path(self, cfx_extended_history_file_full_path: str) -> "ChampFxInputsBuilder":
        self.cfx_extended_history_files_full_paths.append(cfx_extended_history_file_full_path)
        return self

    def set_user_and_role_data_text_file_full_path(self, user_and_role_data_text_file_full_path: str) -> "ChampFxInputsBuilder":
        self.user_and_role_data_text_file_full_path = user_and_role_data_text_file_full_path
        return self

    def set_default_files(self) -> "ChampFxInputsBuilder":
        self.add_champfx_details_excel_file_full_path(DEFAULT_CHAMPFX_DETAILS_EXCEL_FILE_FULL_PATH)
        self.add_champfx_states_changes_excel_file_full_path(DEFAULT_CHAMPFX_STATES_CHANGES_EXCEL_FILE_FULL_PATH)
        self.add_cfx_extended_history_file_full_path(DEFAULT_CHAMPFX_EXTENDED_HISTORY_FILE_FULL_PATH)
        self.set_user_and_role_data_text_file_full_path(DEFAULT_USER_AND_ROLE_DATA_FILE_FULL_PATH)
        return self

    def build(self) -> ChampFxInputs:

        with logger_config.stopwatch_with_label("Build cfx inputs"):
            with logger_config.stopwatch_with_label(f"Open {len(self.champfx_details_excel_files_full_paths)} cfx details files"):
                for i, champfx_details_excel_file_full_path in enumerate(self.champfx_details_excel_files_full_paths):
                    with logger_config.stopwatch_with_label(
                        f"Open {i+1} / {len(self.champfx_details_excel_files_full_paths)} ({round((i+1)/len(self.champfx_details_excel_files_full_paths)*100,2)}%) cfx details excel file {champfx_details_excel_file_full_path}"
                    ):
                        self.champfx_details_excel_files_full_data_frames[champfx_details_excel_file_full_path] = pd.read_excel(champfx_details_excel_file_full_path)

            with logger_config.stopwatch_with_label(f"Open {len(self.champfx_states_changes_excel_files_full_paths)} cfx states changes files"):
                for i, champfx_states_changes_excel_file_full_path in enumerate(self.champfx_states_changes_excel_files_full_paths):
                    with logger_config.stopwatch_with_label(
                        f"Open {i+1} / {len(self.champfx_states_changes_excel_files_full_paths)} ({(i+1)/len(self.champfx_states_changes_excel_files_full_paths)*100:.2f}%) cfx state changes excel file {champfx_states_changes_excel_file_full_path}"
                    ):
                        self.champfx_states_changes_excel_files_data_frames[champfx_states_changes_excel_file_full_path] = pd.read_excel(champfx_states_changes_excel_file_full_path)

            with logger_config.stopwatch_with_label(f"Open {len(self.cfx_extended_history_files_full_paths)} cfx extended history files"):
                for i, cfx_extended_history_file_full_path in enumerate(self.cfx_extended_history_files_full_paths):
                    with logger_config.stopwatch_with_label(f"Open {i+1} / {len(self.cfx_extended_history_files_full_paths)} cfx extended history file {cfx_extended_history_file_full_path}"):
                        with open(cfx_extended_history_file_full_path, "r", encoding="utf-8") as all_cfx_extended_history_text_file:
                            self.cfx_extended_history_files_contents.append(all_cfx_extended_history_text_file.read())

            cfx_inputs = ChampFxInputs(
                champfx_details_excel_files_full_data_frames=self.champfx_details_excel_files_full_data_frames,
                champfx_states_changes_excel_files_data_frames=self.champfx_states_changes_excel_files_data_frames,
                cfx_extended_history_files_contents=self.cfx_extended_history_files_contents,
                user_and_role_data_text_file_full_path=self.user_and_role_data_text_file_full_path,
            )
            return cfx_inputs


class ChampFXLibrary:

    def __init__(
        self,
        cfx_inputs: ChampFxInputs,
        champfx_filters: Optional[List["ChampFXtSaticCriteriaFilter"]] = None,
        label: Optional[str] = None,
    ):
        if champfx_filters is None:
            champfx_filters = []

        self.cfx_inputs = cfx_inputs

        self._champfx_filters = champfx_filters
        self.label = label if label is not None else " ".join([field_filter._label for field_filter in self._champfx_filters])

        self._all_projects: Set[str] = set()

        # self._all_current_owner_modifications_pickle_file_full_path = all_current_owner_modifications_pickle_file_full_path
        # self._all_current_owner_modifications_per_cfx_pickle_file_full_path = all_current_owner_modifications_per_cfx_pickle_file_full_path
        self._champfx_entry_by_id: Dict[str, ChampFXEntry] = dict()
        self._champfx_entries: List[ChampFXEntry] = []

        self._cfx_users_library = (
            role.CfxUserLibrary(cfx_inputs.user_and_role_data_text_file_full_path, release_role_mapping.next_atsp_release_subsystem_mapping)
            if cfx_inputs.user_and_role_data_text_file_full_path
            else role.CfxEmptyUserLibrary()
        )

        with logger_config.stopwatch_with_label("ChampFXLibrary creation and initialisation"):

            with logger_config.stopwatch_with_label("Create ChampFXEntry objects"):
                self.create_or_fill_champfx_entry_with_dataframe(cfx_inputs)
                logger_config.print_and_log_info(f"{len(self.get_all_cfx())} ChampFXEntry objects created")

            with logger_config.stopwatch_with_label("Create state changes objects"):
                change_state_actions_created = self.create_states_changes_with_dataframe(cfx_inputs)
                logger_config.print_and_log_info(f"{len(change_state_actions_created)} ChangeStateAction objects created")

            with logger_config.stopwatch_with_label("Process cfx_extended_histories"):
                self._all_cfx_complete_extended_histories: List[cfx_extended_history.CFXEntryCompleteHistory] = (
                    cfx_extended_history.AllCFXCompleteHistoryExport.parse_full_complete_extended_histories_text_files_contents(cfx_inputs.cfx_extended_history_files_contents, self.get_all_cfx_ids())
                )

            with logger_config.stopwatch_with_label("create current owner modifications"):
                self.create_current_owner_modifications()

    @property
    def cfx_users_library(self) -> role.CfxUserLibrary:
        return self._cfx_users_library

    def create_or_fill_champfx_entry_with_dataframe(self, cfx_inputs: ChampFxInputs) -> None:

        for cfx_details_file_name, cfx_details_data_frame in cfx_inputs.champfx_details_excel_files_full_data_frames.items():

            logger_config.print_and_log_info(f"Process file {cfx_details_file_name}")
            for _, row in cfx_details_data_frame.iterrows():
                cfx_id = row["CFXID"]

                if cfx_id not in self._champfx_entry_by_id:
                    cfx_entry = ChampFXEntryBuilder.build_with_row(row, self)
                    if all(champfx_filter.match_cfx_entry_with_cache(cfx_entry) for champfx_filter in self._champfx_filters):
                        self._champfx_entry_by_id[cfx_id] = cfx_entry
                        self._champfx_entries.append(cfx_entry)
                        self._all_projects.add(cfx_entry._cfx_project_name)

    def create_states_changes_with_dataframe(self, cfx_inputs: ChampFxInputs) -> List[ChangeStateAction]:

        change_state_actions_created: List[ChangeStateAction] = []

        for cfx_states_changes_file_name, cfx_states_changes_data_frame in cfx_inputs.champfx_states_changes_excel_files_data_frames.items():
            logger_config.print_and_log_info(f"Process file {cfx_states_changes_file_name}")
            for _, row in cfx_states_changes_data_frame.iterrows():
                cfx_id = row["CFXID"]

                if cfx_id in self.get_all_cfx_ids():

                    cfx_request = self.get_cfx_by_id(cfx_id)
                    history_raw_old_state: str = row["history.old_state"]
                    history_raw_new_state: str = row["history.new_state"]
                    history_raw_action_timestamp_str = row["history.action_timestamp"]
                    history_raw_action_name: str = row["history.action_name"]

                    if type(history_raw_old_state) is not str:
                        logger_config.print_and_log_error(
                            f"{cfx_id} project {cfx_request._cfx_project_name} ignore change state from {history_raw_old_state} to {history_raw_new_state} {history_raw_action_timestamp_str}  {history_raw_action_name} "
                        )
                        continue

                    old_state: State = conversions.convert_state(history_raw_old_state)
                    new_state: State = conversions.convert_state(history_raw_new_state)
                    action_timestamp = utils.convert_champfx_extract_date(history_raw_action_timestamp_str)
                    history_action = ActionType[history_raw_action_name.upper()]

                    change_state_action = ChangeStateAction(_cfx_request=cfx_request, _old_state=old_state, _new_state=new_state, _timestamp=action_timestamp, _action=history_action)
                    change_state_actions_created.append(change_state_action)

                    cfx_request.add_change_state_action(change_state_action)
                    cfx_request.compute_all_actions_sorted_chronologically()

        return change_state_actions_created

    def create_current_owner_modifications(self) -> List[ChangeCurrentOwnerAction]:

        change_current_owner_actions_created: List[ChangeCurrentOwnerAction] = []

        for cfx_entry_complete_history in self._all_cfx_complete_extended_histories:

            cfx_id = cfx_entry_complete_history.cfx_id

            if cfx_id in self.get_all_cfx_ids():

                cfx_entry = self.get_cfx_by_id(cfx_id)
                for cfx_history_element in cfx_entry_complete_history.history_elements:
                    # cfx_history_element.

                    # Ignore invalid entries

                    for cfx_history_field in cfx_history_element.get_all_current_owner_field_modifications():

                        previous_current_owner_name = convert_cfx_history_element_to_valid_full_name(cfx_history_field.old_state)
                        new_current_owner_name = convert_cfx_history_element_to_valid_full_name(cfx_history_field.new_state)

                        if not previous_current_owner_name or not new_current_owner_name:
                            logger_config.print_and_log_error(f"Invalid current owner change history for {cfx_id}, from {previous_current_owner_name} to {new_current_owner_name}. {cfx_history_field}")

                        previous_owner = self._cfx_users_library.get_cfx_user_by_full_name(previous_current_owner_name) if previous_current_owner_name else self._cfx_users_library.unknown_user
                        new_owner: role.CfxUser = self._cfx_users_library.get_cfx_user_by_full_name(new_current_owner_name) if new_current_owner_name else self._cfx_users_library.unknown_user

                        change_current_owner_action: ChangeCurrentOwnerAction = ChangeCurrentOwnerAction(
                            _cfx_request=cfx_entry, _previous_owner=previous_owner, _new_owner=new_owner, _timestamp=cfx_history_field.change_timestamp.replace(tzinfo=None)
                        )
                        change_current_owner_actions_created.append(change_current_owner_action)
                        cfx_entry.add_change_current_owner_action(change_current_owner_action)

                    cfx_entry.compute_all_current_owner_modifications_chronogically()

        return change_current_owner_actions_created

    def get_all_cfx_by_id_dict(self) -> Dict[str, "ChampFXEntry"]:
        return self._champfx_entry_by_id

    def get_all_cfx(self) -> List["ChampFXEntry"]:
        return self._champfx_entries

    def get_all_cfx_ids(self) -> List[str]:
        return list(self._champfx_entry_by_id.keys())

    def get_cfx_by_id(self, cfx_id: str) -> "ChampFXEntry":
        return self._champfx_entry_by_id[cfx_id]

    def get_cfx_by_state_at_date(self, reference_date: datetime.datetime) -> Dict[State, list["ChampFXEntry"]]:
        result: Dict[State, List[ChampFXEntry]] = {}
        for cfx_entry in self.get_all_cfx():
            state = cfx_entry.get_state_at_date(reference_date)
            if state not in result:
                result[state] = []
            result[state].append(cfx_entry)

        return result

    def gather_state_counts_for_each_date(self, dates_generator: DatesGenerator, cfx_filters: Optional[List["ChampFxFilter"]] = None) -> AllResultsPerDates:

        all_results_to_display: AllResultsPerDates = AllResultsPerDates()

        # First, filter CFX that will never match the filter
        all_cfx_to_consider: List[ChampFXEntry] = []
        if cfx_filters is None:
            all_cfx_to_consider = self.get_all_cfx()
        else:

            all_roles_searched_in_filers = sum(
                [cfx_filter.role_depending_on_date_filter.roles_at_date_allowed if cfx_filter.role_depending_on_date_filter is not None else [] for cfx_filter in cfx_filters], []
            )

            for cfx_entry in self.get_all_cfx():
                if len(all_roles_searched_in_filers) == 0 or list_utils.are_all_elements_of_list_included_in_list(all_roles_searched_in_filers, list(cfx_entry.all_history_current_owner_roles)):

                    if all(cfx_filter.static_criteria_match_cfx_entry(cfx_entry) for cfx_filter in cfx_filters):
                        all_cfx_to_consider.append(cfx_entry)
                else:
                    pass

        logger_config.print_and_log_info(f"Number of CFX to consider:{len(all_cfx_to_consider)}")
        if len(all_cfx_to_consider) == 0:
            logger_config.print_and_log_info(f"No data")
            return all_results_to_display

        timestamps_to_display_data: List[datetime.datetime] = dates_generator.get_dates_since(start_date=get_earliest_submit_date(all_cfx_to_consider).replace(day=1))

        for timestamp_to_display_data in timestamps_to_display_data:
            timestamp_results = OneTimestampResult(timestamp=timestamp_to_display_data, all_results_to_display=all_results_to_display)
            count_by_state: dict[State, int] = defaultdict(int)
            for cfx_entry in all_cfx_to_consider:

                match_all_filters = (
                    True if cfx_filters is None else all(cfx_filter.match_role_depending_on_date_filter_if_filter_exists(cfx_entry, timestamp_to_display_data) for cfx_filter in cfx_filters)
                )
                if match_all_filters:
                    all_results_to_display.all_cfx_ids_that_have_matched.add(cfx_entry.cfx_id)
                    all_results_to_display.all_cfx_that_have_matched.add(cfx_entry)

                    state = cfx_entry.get_state_at_date(timestamp_to_display_data)
                    if state != State.NOT_CREATED_YET:
                        count_by_state[state] += 1
                        timestamp_results.add_one_result_for_state(state=state)
                        all_results_to_display.at_least_one_cfx_matching_filter_has_been_found = True

            if all_results_to_display.at_least_one_cfx_matching_filter_has_been_found:
                all_results_to_display.timestamp_results.append(timestamp_results)

            with logger_config.stopwatch_alert_if_exceeds_duration("consolidate", duration_threshold_to_alert_info_in_s=0.1):
                timestamp_results.consolidate()

        return all_results_to_display


class ChampFXEntryBuilder:

    @staticmethod
    def convert_champfx_security_relevant(raw_str_value: str) -> Optional[SecurityRelevant]:
        if type(raw_str_value) is not str:
            return None
        raw_security_relevant_valid_str_value: Optional[str] = string_utils.text_to_valid_enum_value_text(raw_str_value)
        return SecurityRelevant.UNDEFINED if raw_security_relevant_valid_str_value is None else SecurityRelevant[raw_security_relevant_valid_str_value]

    @staticmethod
    def convert_champfx_rejection_cause(raw_str_value: str) -> Optional[RejectionCause]:
        if type(raw_str_value) is not str:
            return None
        raw_valid_str_value: Optional[str] = string_utils.text_to_valid_enum_value_text(raw_str_value)
        return RejectionCause.NONE if raw_valid_str_value is None else RejectionCause[raw_valid_str_value] if raw_valid_str_value in RejectionCause else RejectionCause.TO_BE_ADDED_YDA

    @staticmethod
    def convert_champfx_request_type(raw_str_value: str) -> RequestType:
        if type(raw_str_value) is not str:
            return None
        raw_valid_str_value: Optional[str] = string_utils.text_to_valid_enum_value_text(raw_str_value)
        return RequestType[raw_valid_str_value] if raw_valid_str_value in RequestType else RequestType.TO_BE_ADDED_YDA

    @staticmethod
    def convert_champfx_category(raw_str_value: str) -> Category:
        if type(raw_str_value) is not str:
            return None
        raw_valid_str_value: str = string_utils.text_to_valid_enum_value_text(raw_str_value)
        return Category[raw_valid_str_value] if raw_valid_str_value in Category else Category.TO_BE_ADDED_YDA

    @staticmethod
    def to_optional_boolean(raw_value: str) -> Optional[bool]:
        if raw_value == "Yes":
            return True
        elif raw_value == "No":
            return False
        return None

    @staticmethod
    def build_with_row(row: pd.Series, cfx_library: ChampFXLibrary) -> "ChampFXEntry":
        cfx_id = row["CFXID"]
        state: State = conversions.convert_state(row["State"])

        raw_project: str = cast(str, row["Project"])
        project_name = string_utils.text_to_valid_enum_value_text(raw_project)

        cfx_project_name = project_name

        raw_safety_relevant: str = row["SafetyRelevant"]
        safety_relevant: Optional[bool] = ChampFXEntryBuilder.to_optional_boolean(raw_safety_relevant)

        raw_security_relevant: str = row["SecurityRelevant"]
        security_relevant: SecurityRelevant = ChampFXEntryBuilder.convert_champfx_security_relevant(raw_security_relevant)

        raw_rejection_cause: str = row["RejectionCause"]
        rejection_cause: RejectionCause = ChampFXEntryBuilder.convert_champfx_rejection_cause(raw_rejection_cause)

        request_type: RequestType = ChampFXEntryBuilder.convert_champfx_request_type(row["RequestType"])

        raw_category: str = row["Category"]
        category: Category = ChampFXEntryBuilder.convert_champfx_category(raw_category) if raw_category else None

        current_owner_raw: str = row["CurrentOwner.FullName"]
        assert cfx_library.cfx_users_library.has_user_by_full_name(current_owner_raw), cfx_id
        current_owner: role.CfxUser = cfx_library.cfx_users_library.get_cfx_user_by_full_name(current_owner_raw)

        fixed_implemented_in_config_unit: str = row["FixedImplementedIn"]
        fixed_implemented_in_subsystem: Optional[role.SubSystem] = (
            cfx_library.cfx_users_library.get_subsystem_from_champfx_fixed_implemented_in(fixed_implemented_in_config_unit) if fixed_implemented_in_config_unit else None
        )

        submit_date_raw: str = row["SubmitDate"]
        submit_date: datetime.datetime = cast(datetime.datetime, utils.convert_champfx_extract_date(submit_date_raw))

        system_structure_config_unit: str = row["SystemStructure"]
        temptative_system_structure: Optional[role.SubSystem] = cfx_library.cfx_users_library.get_subsystem_from_champfx_fixed_implemented_in(system_structure_config_unit)

        assert temptative_system_structure, f"{cfx_id} could not decode system structure {system_structure_config_unit}"
        system_structure: role.SubSystem = temptative_system_structure

        champfx_entry = ChampFXEntry(
            cfx_id=cfx_id,
            state=state,
            fixed_implemented_in_subsystem=fixed_implemented_in_subsystem,
            system_structure_config_unit=system_structure_config_unit,
            fixed_implemented_in_config_unit=fixed_implemented_in_config_unit,
            system_structure_subsystem=system_structure,
            submit_date=submit_date,
            cfx_project_name=cfx_project_name,
            safety_relevant=safety_relevant,
            security_relevant=security_relevant,
            rejection_cause=rejection_cause,
            category=category,
            current_owner=current_owner,
            request_type=request_type,
        )
        return champfx_entry


class ChampFXEntry:
    def __init__(
        self,
        cfx_id: str,
        state: State,
        fixed_implemented_in_subsystem: Optional[role.SubSystem],
        fixed_implemented_in_config_unit: str,
        system_structure_subsystem: role.SubSystem,
        system_structure_config_unit: str,
        submit_date: datetime.datetime,
        cfx_project_name: str,
        safety_relevant: Optional[bool],
        security_relevant: SecurityRelevant,
        rejection_cause: RejectionCause,
        category: Category,
        current_owner: role.CfxUser,
        request_type: RequestType,
    ):
        """

        :type rejection_cause: RejectionCause
        """
        self._submit_date = submit_date
        self._change_state_actions: list[ChangeStateAction] = []
        self._change_state_actions_by_date: Dict[datetime.datetime, ChangeStateAction] = dict()

        self._change_current_owner_actions: list[ChangeCurrentOwnerAction] = []
        self._change_current_owner_actions_by_date: Dict[datetime.datetime, ChangeCurrentOwnerAction] = dict()

        self.cfx_id = cfx_id
        self._state: State = state

        self._fixed_implemented_in_config_unit = fixed_implemented_in_config_unit
        self._fixed_implemented_in_subsystem = fixed_implemented_in_subsystem
        self._system_structure_subsystem = system_structure_subsystem
        self._system_structure_config_unit = system_structure_config_unit
        self._request_type = request_type

        self._current_owner: role.CfxUser = current_owner
        self._current_owner_role: role.SubSystem = self._current_owner.subsystem

        self._rejection_cause = rejection_cause

        self._current_owner_role = current_owner.subsystem

        self._cfx_project_name = cfx_project_name
        self._safety_relevant = safety_relevant
        self._security_relevant = security_relevant
        self._all_change_state_actions_sorted_chronologically: List[ChangeStateAction] = []
        self._all_change_state_actions_sorted_reversed_chronologically: List[ChangeStateAction] = []

        self._all_history_current_owner_roles: set[role.SubSystem] = set()
        self._all_history_current_owner_roles.add(self._current_owner_role)

        self._all_current_owner_modifications_sorted_chronologically: list[ChangeCurrentOwnerAction] = []
        self._all_current_owner_modifications_sorted_reversed_chronologically: list[ChangeCurrentOwnerAction] = []

        self._category = category

        if self._rejection_cause != RejectionCause.NONE:
            self._subsystem = self._system_structure_subsystem
        else:
            self._subsystem = self._fixed_implemented_in_subsystem if self._fixed_implemented_in_subsystem else self._current_owner_role

        self._config_unit: str = self._fixed_implemented_in_config_unit if self._fixed_implemented_in_subsystem else self._system_structure_config_unit

    def __repr__(self) -> str:
        return f"<ChampFXEntry cfx_id={self.cfx_id} _raw_state={self._state} _current_owner_raw={self._current_owner.full_name}>"

    def compute_all_actions_sorted_chronologically(self) -> list[ChangeStateAction]:
        self._all_change_state_actions_sorted_chronologically = [action for _, action in sorted(self._change_state_actions_by_date.items())]
        self._all_change_state_actions_sorted_reversed_chronologically = list(reversed(self._all_change_state_actions_sorted_chronologically))
        return self._all_change_state_actions_sorted_chronologically

    def get_all_change_state_actions_sorted_chronologically(self) -> list[ChangeStateAction]:
        # return sorted(self._change_state_actions_by_date.items())
        return self._all_change_state_actions_sorted_chronologically

    def get_all_change_state_actions_sorted_reversed_chronologically(self) -> list[ChangeStateAction]:
        # return sorted(self._change_state_actions_by_date.items())
        return self._all_change_state_actions_sorted_reversed_chronologically

    def compute_all_current_owner_modifications_chronogically(self) -> None:
        self._all_current_owner_modifications_sorted_chronologically = [action for _, action in sorted(self._change_current_owner_actions_by_date.items())]
        self._all_current_owner_modifications_sorted_reversed_chronologically = list(reversed(self._all_current_owner_modifications_sorted_chronologically))

    def get_all_current_owner_modifications_sorted_chronologically(self) -> list[ChangeCurrentOwnerAction]:
        # return sorted(self._change_state_actions_by_date.items())
        return self._all_current_owner_modifications_sorted_chronologically

    def get_all_current_owner_modifications_sorted_reversed_chronologically(self) -> list[ChangeCurrentOwnerAction]:
        # return sorted(self._change_state_actions_by_date.items())
        return self._all_current_owner_modifications_sorted_reversed_chronologically

    def get_oldest_change_action_by_new_state(self, new_state: State) -> Optional[ChangeStateAction]:
        return next((action for action in self.get_all_change_state_actions_sorted_chronologically() if action.new_state == new_state), None)

    def get_newest_change_action_that_is_before_date(self, reference_date: datetime.datetime) -> Optional[ChangeStateAction]:
        return next((action for action in self.get_all_change_state_actions_sorted_reversed_chronologically() if action.timestamp < reference_date), None)

    def get_newest_current_owner_modification_that_is_before_date(self, reference_date: datetime.datetime) -> Optional[ChangeCurrentOwnerAction]:
        return next((action for action in self.get_all_current_owner_modifications_sorted_reversed_chronologically() if action.timestamp < reference_date), None)

    def add_change_state_action(self, change_state_action: ChangeStateAction) -> None:
        self._change_state_actions.append(change_state_action)
        self._change_state_actions_by_date[change_state_action.timestamp] = change_state_action

    def add_change_current_owner_action(self, change_current_owner_action: ChangeCurrentOwnerAction) -> None:
        self._change_current_owner_actions.append(change_current_owner_action)
        self._change_current_owner_actions_by_date[change_current_owner_action.timestamp] = change_current_owner_action
        self._all_history_current_owner_roles.add(change_current_owner_action.previous_owner.subsystem)
        self._all_history_current_owner_roles.add(change_current_owner_action.new_owner.subsystem)

    @property
    def raw_state(self) -> State:
        return self._state

    def get_current_role_at_date(self, reference_date: datetime.datetime) -> Optional[role.SubSystem]:
        current_owner = self.get_current_owner_at_date(reference_date)
        return None if current_owner is None else current_owner.subsystem

    def get_current_owner_at_date(self, reference_date: datetime.datetime) -> Optional[role.CfxUser]:
        if reference_date < self._submit_date:
            return None

        newest_current_owner_modification_action_that_is_before_date = self.get_newest_current_owner_modification_that_is_before_date(reference_date)
        if newest_current_owner_modification_action_that_is_before_date is not None:
            return newest_current_owner_modification_action_that_is_before_date.new_owner
        return self._current_owner

    def get_state_at_date(self, reference_date: datetime.datetime) -> State:

        newest_change_action_that_is_before_date = self.get_newest_change_action_that_is_before_date(reference_date)
        if newest_change_action_that_is_before_date is None:
            return State.NOT_CREATED_YET
        else:
            return newest_change_action_that_is_before_date.new_state

    @property
    def all_history_current_owner_roles(self) -> set[role.SubSystem]:
        return self._all_history_current_owner_roles


class ChampFXtSaticCriteriaFilter(ABC):
    def __init__(self, label: str = "") -> None:
        self._cache_result_by_cfx: dict[ChampFXEntry, bool] = dict()
        self._number_of_results_obtained_by_cache_usage = 0
        self._label = label

    @abstractmethod
    def match_cfx_entry_without_cache(self, cfx_entry: ChampFXEntry) -> bool:
        """This method must be overridden in child classes."""
        pass

    def match_cfx_entry_with_cache(self, cfx_entry: ChampFXEntry) -> bool:
        if cfx_entry in self._cache_result_by_cfx:
            self._number_of_results_obtained_by_cache_usage += 1
            return self._cache_result_by_cfx[cfx_entry]

        new_result_computed = self.match_cfx_entry_without_cache(cfx_entry)
        self._cache_result_by_cfx[cfx_entry] = new_result_computed
        return new_result_computed


class ChampFXWhitelistFilter(ChampFXtSaticCriteriaFilter, ABC):
    @abstractmethod
    def __init__(
        self,
        label: Optional[str] = None,
    ):
        super().__init__()
        self._cfx_to_treat_whitelist_ids: Set[str] = set()
        self._label: str = "" if label is None else label

    def match_cfx_entry_without_cache(self, cfx_entry: ChampFXEntry) -> bool:
        return cfx_entry.cfx_id in self._cfx_to_treat_whitelist_ids


class ChampFXWhiteListBasedOnListFilter(ChampFXWhitelistFilter):
    def __init__(
        self,
        cfx_to_treat_ids: Optional[Set | List[str]] = None,
        label: Optional[str] = None,
    ):
        super().__init__(label=label)

        if label is None:
            self._label = f"list {len(cfx_to_treat_ids)} white listed"  # type: ignore[no-redef]

        self._cfx_to_treat_whitelist_ids.update(cfx_to_treat_ids)


class ChampFXWhiteListBasedOnFileFilter(ChampFXWhitelistFilter):
    def __init__(self, cfx_to_treat_whitelist_text_file_full_path: str, label: Optional[str] = None):
        super().__init__(label=label)

        self._cfx_to_treat_whitelist_text_file_full_path: str = cfx_to_treat_whitelist_text_file_full_path

        if label is None:
            self._label: str = self._cfx_to_treat_whitelist_text_file_full_path
            self._label = string_utils.right_part_after_last_occurence(self._label, "/")
            self._label = string_utils.right_part_after_last_occurence(self._label, "\\")
            self._label += " "

        with logger_config.stopwatch_with_label(f"Load ChampFXWhiteListBasedOnFileFilter {cfx_to_treat_whitelist_text_file_full_path}"):
            with open(self._cfx_to_treat_whitelist_text_file_full_path, "r", encoding="utf-8") as cfx_known_by_cstmr_text_file:
                self._cfx_to_treat_whitelist_ids.update([line.strip() for line in cfx_known_by_cstmr_text_file.readlines()])
        logger_config.print_and_log_info(f"Number of cfx_to_treat_whitelist_ids:{len(self._cfx_to_treat_whitelist_ids)}")


class ChampFXFieldFilter(ChampFXtSaticCriteriaFilter, ABC):

    @abstractmethod
    def __init__(
        self,
        field_name: str,
        field_label: str,
        field_accepted_values: Optional[List[Any]] = None,
        field_forbidden_values: Optional[List[Any]] = None,
        field_accepted_contained_texts: Optional[List[Any]] = None,
        field_forbidden_contained_texts: Optional[List[Any]] = None,
        forced_label: Optional[str] = None,
    ) -> None:
        super().__init__()
        self.field_name = field_name
        self.field_label = field_label
        self.field_accepted_values = field_accepted_values
        self.field_forbidden_values = field_forbidden_values
        self.field_accepted_contained_texts = field_accepted_contained_texts
        self.field_forbidden_contained_texts = field_forbidden_contained_texts

        if forced_label:
            self._label = forced_label

        else:
            label: str = f"{self.field_label}"

            if self.field_accepted_values:
                label = f"{label} among {self.field_accepted_values}" if len(self.field_accepted_values) > 1 else f"{label} {self.field_accepted_values}"
            elif self.field_forbidden_values:
                label = f"{label} without {self.field_forbidden_values}"
            elif self.field_accepted_contained_texts:
                label = (
                    f"{label} contains texts {self.field_accepted_contained_texts}" if len(self.field_accepted_contained_texts) > 1 else f"{label} contains text {self.field_accepted_contained_texts}"
                )
            elif self.field_forbidden_contained_texts:
                label = (
                    f"{label} does not contain any of text {self.field_forbidden_contained_texts}"
                    if len(self.field_forbidden_contained_texts) > 1
                    else f"{label} does not contain {self.field_forbidden_contained_texts}"
                )

            label = label.translate({ord(i): None for i in "'[]"})
            self._label = label

    def match_cfx_entry_without_cache(self, cfx_entry: ChampFXEntry) -> bool:
        attribute_entry = getattr(cfx_entry, self.field_name)
        if self.field_accepted_values is not None:
            return attribute_entry in self.field_accepted_values
        elif self.field_forbidden_values:
            return attribute_entry not in cast(List[Any], self.field_forbidden_values)
        elif self.field_accepted_contained_texts:
            match_found: bool = any(text in attribute_entry for text in self.field_accepted_contained_texts)
            return match_found
        elif self.field_forbidden_contained_texts:
            match_found: bool = any(text in attribute_entry for text in self.field_forbidden_contained_texts)
            return not match_found
        else:
            return False


class ChampFxFilterFieldSecurityRelevant(ChampFXFieldFilter):
    def __init__(self, field_accepted_values: Optional[List[Any]] = None, field_forbidden_values: Optional[List[Any]] = None, forced_label: Optional[str] = None) -> None:
        super().__init__(
            field_name="_security_relevant",
            field_label="Security Relevant",
            field_accepted_values=field_accepted_values,
            field_forbidden_values=field_forbidden_values,
            forced_label=forced_label,
        )


class ChampFxFilterFieldSafetyRelevant(ChampFXFieldFilter):
    def __init__(self, field_accepted_value: Optional[bool] = None, field_forbidden_value: Optional[bool] = None, forced_label: Optional[str] = None) -> None:
        super().__init__(
            field_name="_safety_relevant",
            field_label="Safety Relevant",
            field_accepted_values=[field_accepted_value],
            field_forbidden_values=[field_forbidden_value],
            forced_label=forced_label,
        )


class ChampFxFilterFieldProject(ChampFXFieldFilter):
    def __init__(self, field_accepted_values: Optional[List[str]] = None, field_forbidden_values: Optional[List[str]] = None, forced_label: Optional[str] = None) -> None:
        super().__init__(
            field_name="_cfx_project_name",
            field_label="Project",
            field_accepted_values=field_accepted_values,
            field_forbidden_values=field_forbidden_values,
            forced_label=forced_label,
        )


class ChampFxFilterFieldSubsystem(ChampFXFieldFilter):
    def __init__(self, field_accepted_values: Optional[List[Any]] = None, field_forbidden_values: Optional[List[Any]] = None, forced_label: Optional[str] = None) -> None:
        super().__init__(
            field_name="_subsystem",
            field_label="Subsystem",
            field_accepted_values=field_accepted_values,
            field_forbidden_values=field_forbidden_values,
            forced_label=forced_label,
        )


class ChampFxFilterFieldCategory(ChampFXFieldFilter):
    def __init__(self, field_accepted_values: Optional[List[Any]] = None, field_forbidden_values: Optional[List[Any]] = None, forced_label: Optional[str] = None) -> None:
        super().__init__(
            field_name="_category",
            field_label="Category",
            field_accepted_values=field_accepted_values,
            field_forbidden_values=field_forbidden_values,
            forced_label=forced_label,
        )


class ChampFxFilterFieldType(ChampFXFieldFilter):
    def __init__(self, field_accepted_values: Optional[List[Any]] = None, field_forbidden_values: Optional[List[Any]] = None, forced_label: Optional[str] = None) -> None:
        super().__init__(
            field_name="_request_type",
            field_label="Type",
            field_accepted_values=field_accepted_values,
            field_forbidden_values=field_forbidden_values,
            forced_label=forced_label,
        )


class ChampFxFilterFieldConfigUnit(ChampFXFieldFilter):
    def __init__(
        self,
        field_accepted_values: Optional[List[Any]] = None,
        field_forbidden_values: Optional[List[Any]] = None,
        field_accepted_contained_texts: Optional[List[Any]] = None,
        field_forbidden_contained_texts: Optional[List[Any]] = None,
        forced_label: Optional[str] = None,
    ) -> None:
        super().__init__(
            field_name="_config_unit",
            field_label="Config Unit",
            field_accepted_values=field_accepted_values,
            field_forbidden_values=field_forbidden_values,
            field_accepted_contained_texts=field_accepted_contained_texts,
            field_forbidden_contained_texts=field_forbidden_contained_texts,
            forced_label=forced_label,
        )


@dataclass
class ChampFXRoleAtSpecificDateFilter:
    timestamp: datetime.datetime
    roles_at_date_allowed: List[role.SubSystem]

    def match_cfx_entry(self, cfx_entry: ChampFXEntry) -> bool:
        role_at_date = cfx_entry.get_current_role_at_date(self.timestamp)
        return role_at_date in self.roles_at_date_allowed


@dataclass
class ChampFXRoleDependingOnDateFilter:
    roles_at_date_allowed: List[role.SubSystem]
    label: str = field(init=False)

    def __post_init__(self) -> None:
        label: str = f"{self.roles_at_date_allowed}"
        self.label = label

    def match_cfx_entry(self, cfx_entry: ChampFXEntry, timestamp: datetime.datetime) -> bool:
        return ChampFXRoleAtSpecificDateFilter(roles_at_date_allowed=self.roles_at_date_allowed, timestamp=timestamp).match_cfx_entry(cfx_entry=cfx_entry)


class ChampFxFilter:

    def __init__(
        self,
        role_depending_on_date_filter: Optional[ChampFXRoleDependingOnDateFilter] = None,
        field_filters: Optional[List[ChampFXFieldFilter]] = None,
        cfx_to_treat_whitelist_text_file_full_path: Optional[str] = None,
        whitelist_filter: Optional[ChampFXWhitelistFilter] = None,
        label: Optional[str] = None,
    ):
        if field_filters is None:
            field_filters = []

        self.role_depending_on_date_filter: Optional[ChampFXRoleDependingOnDateFilter] = role_depending_on_date_filter
        self._field_filters: List[ChampFXFieldFilter] = field_filters
        self._cfx_to_treat_whitelist_text_file_full_path: Optional[str] = cfx_to_treat_whitelist_text_file_full_path
        self._cfx_to_treat_whitelist_ids: Optional[Set[str]] = None
        self.label: str = label if label is not None else ""

        self._static_criteria_filters: List[ChampFXtSaticCriteriaFilter] = [] + self._field_filters

        self._white_list_filter: Optional[ChampFXWhitelistFilter] = (
            ChampFXWhiteListBasedOnFileFilter(cfx_to_treat_whitelist_text_file_full_path) if cfx_to_treat_whitelist_text_file_full_path is not None else whitelist_filter
        )
        if self._white_list_filter is not None:
            self._static_criteria_filters.append(self._white_list_filter)

        self._compute_label()

    def _compute_label(self) -> None:

        label = self.label

        if label is None:
            label = " "
        else:
            label += " "

        if self.role_depending_on_date_filter:
            label = f"{label}role {self.role_depending_on_date_filter.roles_at_date_allowed} per date"

        if len(self._field_filters) > 0:
            label = f"{label}{[field_filter._label for field_filter in self._field_filters]}"

        if self._white_list_filter:
            label = f"{label}{self._white_list_filter._label}"

        label = label.translate({ord(i): None for i in "'[]"})

        self.label = label

    def static_criteria_match_cfx_entry(self, cfx_entry: ChampFXEntry) -> bool:

        if self._white_list_filter is not None:
            if not self._white_list_filter.match_cfx_entry_with_cache(cfx_entry=cfx_entry):
                return False

        for field_filter in self._field_filters:
            if not field_filter.match_cfx_entry_with_cache(cfx_entry=cfx_entry):
                return False

        return True

    def match_role_depending_on_date_filter_if_filter_exists(self, cfx_entry: ChampFXEntry, timestamp: Optional[datetime.datetime] = None) -> bool:
        if self.role_depending_on_date_filter:
            if not self.role_depending_on_date_filter.match_cfx_entry(cfx_entry=cfx_entry, timestamp=cast(datetime.datetime, timestamp)):
                return False

        return True

    def match_cfx_entry(self, cfx_entry: ChampFXEntry, timestamp: Optional[datetime.datetime] = None) -> bool:

        if not self.static_criteria_match_cfx_entry(cfx_entry):
            return False

        if not self.match_role_depending_on_date_filter_if_filter_exists(cfx_entry=cfx_entry, timestamp=cast(datetime.datetime, timestamp)):
            return False

        return True
