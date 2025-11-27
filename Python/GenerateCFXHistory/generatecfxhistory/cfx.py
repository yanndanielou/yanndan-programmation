import datetime
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List, Optional, Set

from common import list_utils
from logger import logger_config

from generatecfxhistory import (
    cfx_extended_history,
    release_role_mapping,
    role,
)
from generatecfxhistory.constants import (
    ActionType,
    RejectionCause,
    State,
)
from generatecfxhistory.filters import ChampFxFilter, ChampFXtStaticCriteriaFilter, ChampFXWhitelistFilter
from generatecfxhistory.inputs import ChampFxInputs, ChampFxCreationData
from generatecfxhistory.dates_generators import DatesGenerator
from generatecfxhistory.results import AllResultsPerDatesWithDebugDetails, OneTimestampResult


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
    _action_type: ActionType

    @property
    def new_state(self) -> State:
        return self._new_state

    @property
    def old_state(self) -> State:
        return self._old_state

    @property
    def action(self) -> ActionType:
        return self._action_type


def convert_cfx_history_element_to_valid_full_name(cfx_history_element_state: str) -> str:
    return cfx_history_element_state.split("(")[0].strip()


def get_earliest_submit_date(cfx_list: List["ChampFXEntry"]) -> datetime.datetime:
    earliest_date = min(entry.get_oldest_submit_date(allow_identical_states=False) for entry in cfx_list)
    logger_config.print_and_log_info(f"Earliest submit date among {len(cfx_list)} CFX: {earliest_date}")
    return earliest_date


class ChampFXLibrary:

    def __init__(
        self,
        cfx_inputs: ChampFxInputs,
        allow_cfx_creation_errors: bool = False,
        champfx_filters: Optional[List["ChampFXtStaticCriteriaFilter"]] = None,
        label: Optional[str] = None,
    ):
        if champfx_filters is None:
            champfx_filters = []

        self.failed_to_create_cfx_ids: List[str] = []

        self.ignore_cfx_creation_errors = allow_cfx_creation_errors

        self.cfx_inputs = cfx_inputs

        self._champfx_filters = champfx_filters
        self.label = label if label is not None else " ".join([field_filter._label for field_filter in self._champfx_filters])

        self._all_projects: Set[str] = set()

        # self._all_current_owner_modifications_pickle_file_full_path = all_current_owner_modifications_pickle_file_full_path
        # self._all_current_owner_modifications_per_cfx_pickle_file_full_path = all_current_owner_modifications_per_cfx_pickle_file_full_path
        self._champfx_entry_by_id: Dict[str, ChampFXEntry] = dict()
        self._champfx_entries: List[ChampFXEntry] = []
        # self._champfx_entries: List[str] = []

        self._cfx_users_library = (
            role.CfxUserLibrary(cfx_inputs.user_and_role_data_text_file_full_path, release_role_mapping.next_atsp_release_subsystem_mapping)
            if cfx_inputs.user_and_role_data_text_file_full_path
            else role.CfxEmptyUserLibrary()
        )

        with logger_config.stopwatch_with_label("ChampFXLibrary creation and initialisation", monitor_ram_usage=True):

            with logger_config.stopwatch_with_label("Create ChampFXEntry objects", monitor_ram_usage=True):
                self.create_or_fill_champfx_entry_with_inputs(cfx_inputs)
                logger_config.print_and_log_info(f"{len(self.get_all_cfx())} ChampFXEntry objects created")

            with logger_config.stopwatch_with_label("Create state changes objects", monitor_ram_usage=True):
                change_state_actions_created = self.create_states_changes_with_inputs(cfx_inputs)
                logger_config.print_and_log_info(f"{len(change_state_actions_created)} ChangeStateAction objects created")

            with logger_config.stopwatch_with_label("compute_all_actions_sorted_chronologically", monitor_ram_usage=True):
                for cfx_entry in self.get_all_cfx():
                    cfx_entry.compute_all_actions_sorted_chronologically()

            with logger_config.stopwatch_with_label("Process cfx_extended_histories", monitor_ram_usage=True):
                self._all_cfx_complete_extended_histories: List[cfx_extended_history.CFXEntryCompleteHistory] = (
                    cfx_extended_history.AllCFXCompleteHistoryExport.parse_full_complete_extended_histories_text_files_contents(cfx_inputs._cfx_extended_history_files_contents, self.get_all_cfx_ids())
                )

            with logger_config.stopwatch_with_label("create current owner modifications", monitor_ram_usage=True):
                self.create_current_owner_modifications()

        logger_config.print_and_log_current_ram_usage(prefix="After cfx library created")

    @property
    def cfx_users_library(self) -> role.CfxLibraryBase:
        return self._cfx_users_library

    @property
    def champfx_filters(self) -> List[ChampFXtStaticCriteriaFilter]:
        return self._champfx_filters

    def create_cfx_entry(self, champfx_creation_data: "ChampFxCreationData") -> "ChampFXEntry":
        cfx_entry = ChampFXEntry(champfx_creational_data=champfx_creation_data)
        if all(champfx_filter.match_cfx_entry_with_cache(cfx_entry) for champfx_filter in self._champfx_filters):
            self._champfx_entry_by_id[cfx_entry.cfx_identifier] = cfx_entry
            self._champfx_entries.append(cfx_entry)
            self._all_projects.add(cfx_entry.cfx_project_name)
        return cfx_entry

    def create_or_fill_champfx_entry_with_inputs(self, cfx_inputs: ChampFxInputs) -> None:

        all_champfx_creation_data = cfx_inputs.get_all_champfx_entry_creation_data(cfx_library=self)
        for champfx_creation_data in all_champfx_creation_data:
            cfx_id = champfx_creation_data.cfx_identifier

            if cfx_id not in self._champfx_entry_by_id:

                if self.ignore_cfx_creation_errors:
                    try:
                        self.create_cfx_entry(champfx_creation_data=champfx_creation_data)
                    except Exception as ex:
                        logger_config.print_and_log_exception(ex)
                        logger_config.print_and_log_error(f"Error when creating cfx {cfx_id}")
                        self.failed_to_create_cfx_ids.append(cfx_id)
                else:
                    self.create_cfx_entry(champfx_creation_data=champfx_creation_data)

    def create_states_changes_with_inputs(self, cfx_inputs: ChampFxInputs) -> List[ChangeStateAction]:

        all_change_state_creation_data = cfx_inputs.get_all_change_state_creation_data(cfx_library=self)
        change_state_actions_created: List[ChangeStateAction] = []

        for change_state_creation_data in all_change_state_creation_data:
            if self.is_cfx_with_id_exists(cfx_id=change_state_creation_data.cfx_identifier):
                cfx_request = self.get_cfx_by_id(change_state_creation_data.cfx_identifier)

                change_state_action = ChangeStateAction(
                    _cfx_request=cfx_request,
                    _old_state=change_state_creation_data.old_state,
                    _new_state=change_state_creation_data.new_state,
                    _timestamp=change_state_creation_data.timestamp,
                    _action_type=change_state_creation_data.action_type,
                )
                cfx_request.add_change_state_action(change_state_action)
                change_state_actions_created.append(change_state_action)

        return change_state_actions_created

    def create_current_owner_modifications(self) -> List[ChangeCurrentOwnerAction]:

        change_current_owner_actions_created: List[ChangeCurrentOwnerAction] = []

        for cfx_entry_complete_history in self._all_cfx_complete_extended_histories:

            cfx_id = cfx_entry_complete_history.cfx_id

            if self.is_cfx_with_id_exists(cfx_id):

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

    @property
    def champfx_entry_by_id(self) -> Dict[str, "ChampFXEntry"]:
        return self._champfx_entry_by_id

    def get_all_cfx(self) -> List["ChampFXEntry"]:
        return self._champfx_entries

    def get_all_cfx_ids(self) -> List[str]:
        return list(self._champfx_entry_by_id.keys())

    def is_cfx_with_id_exists(self, cfx_id: str) -> bool:
        return cfx_id in self._champfx_entry_by_id

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

    def get_all_cfx_matching_filters(self, static_criteria_filters: List[ChampFXtStaticCriteriaFilter]) -> List["ChampFXEntry"]:
        all_cfx_matching: List[ChampFXEntry] = []

        if not static_criteria_filters:
            return self.get_all_cfx()

        else:
            for cfx_entry in self.get_all_cfx():
                if all(cfx_filter.match_cfx_entry_with_cache(cfx_entry) for cfx_filter in static_criteria_filters):
                    all_cfx_matching.append(cfx_entry)

        return all_cfx_matching

    def gather_state_counts_for_each_date(self, dates_generator: DatesGenerator, cfx_filters: Optional[List["ChampFxFilter"]] = None) -> AllResultsPerDatesWithDebugDetails:

        all_results_to_display: AllResultsPerDatesWithDebugDetails = AllResultsPerDatesWithDebugDetails()

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
            logger_config.print_and_log_info("No data")
            return all_results_to_display

        earliest_submit_date = get_earliest_submit_date(all_cfx_to_consider)
        timestamps_to_display_data: List[datetime.datetime] = dates_generator.get_dates_since(start_date=earliest_submit_date.replace(day=1))

        for timestamp_to_display_data in timestamps_to_display_data:
            timestamp_results = OneTimestampResult(timestamp=timestamp_to_display_data, all_results_to_display=all_results_to_display)
            count_by_state: dict[State, int] = defaultdict(int)
            for cfx_entry in all_cfx_to_consider:

                match_all_filters = (
                    True if cfx_filters is None else all(cfx_filter.match_role_depending_on_date_filter_if_filter_exists(cfx_entry, timestamp_to_display_data) for cfx_filter in cfx_filters)
                )
                if match_all_filters:
                    all_results_to_display.all_cfx_ids_that_have_matched.add(cfx_entry.cfx_identifier)
                    all_results_to_display.all_cfx_that_have_matched.add(cfx_entry)

                    state = cfx_entry.get_state_at_date(timestamp_to_display_data)
                    if state != State.NOT_CREATED_YET:
                        count_by_state[state] += 1
                        timestamp_results.add_one_result_for_state(state=state)
                        all_results_to_display.at_least_one_cfx_matching_filter_has_been_found = True

            if all_results_to_display.at_least_one_cfx_matching_filter_has_been_found:
                all_results_to_display.timestamp_results.append(timestamp_results)

            with logger_config.stopwatch_alert_if_exceeds_duration("consolidate", duration_threshold_to_alert_info_in_s=0.1):
                timestamp_results.consolidate_present_states()

        return all_results_to_display


class ChampFXEntry:
    def __init__(
        self,
        champfx_creational_data: ChampFxCreationData,
    ):

        self.submit_date = champfx_creational_data.submit_date
        self._change_state_actions: list[ChangeStateAction] = []
        self._change_state_actions_by_date: Dict[datetime.datetime, ChangeStateAction] = dict()

        self._change_current_owner_actions: list[ChangeCurrentOwnerAction] = []
        self._change_current_owner_actions_by_date: Dict[datetime.datetime, ChangeCurrentOwnerAction] = dict()

        self.cfx_identifier = champfx_creational_data.cfx_identifier
        self.alternative_cfx_identifier = champfx_creational_data.alternative_cfx_identifier
        self._state: State = champfx_creational_data.state

        self._fixed_implemented_in_config_unit = champfx_creational_data.fixed_implemented_in_config_unit
        self._fixed_implemented_in_subsystem = champfx_creational_data.fixed_implemented_in_subsystem
        self._system_structure_subsystem = champfx_creational_data.system_structure_subsystem
        self._system_structure_config_unit = champfx_creational_data.system_structure_config_unit
        self._request_type = champfx_creational_data.request_type

        self._current_owner: role.CfxUser = champfx_creational_data.current_owner
        self._current_owner_role: role.SubSystem = self._current_owner.subsystem

        self._rejection_cause = champfx_creational_data.rejection_cause

        self._current_owner_role = champfx_creational_data.current_owner.subsystem

        self._cfx_project_name = champfx_creational_data.cfx_project_name
        self._safety_relevant = champfx_creational_data.safety_relevant
        self._security_relevant = champfx_creational_data.security_relevant
        self._all_change_state_actions_sorted_chronologically: List[ChangeStateAction] = []
        self._all_change_state_actions_sorted_reversed_chronologically: List[ChangeStateAction] = []

        self._all_history_current_owner_roles: set[role.SubSystem] = set()
        self._all_history_current_owner_roles.add(self._current_owner_role)

        self._all_current_owner_modifications_sorted_chronologically: list[ChangeCurrentOwnerAction] = []
        self._all_current_owner_modifications_sorted_reversed_chronologically: list[ChangeCurrentOwnerAction] = []

        self._category = champfx_creational_data.category

        if self._rejection_cause is not None and self._rejection_cause != RejectionCause.NONE:
            self._subsystem = self._system_structure_subsystem
        else:
            self._subsystem = self._fixed_implemented_in_subsystem if self._fixed_implemented_in_subsystem else self._current_owner_role

        self._config_unit: str = self._fixed_implemented_in_config_unit if self._fixed_implemented_in_subsystem else self._system_structure_config_unit

    def __repr__(self) -> str:
        return f"<ChampFXEntry cfx_id={self.cfx_identifier} _raw_state={self._state} _current_owner_raw={self._current_owner.full_name}>"

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

    def get_oldest_submit_date(self, allow_identical_states: bool) -> datetime.datetime:
        oldest_submit_date_state_change = self.get_oldest_change_state_action_by_new_state(new_state=State.SUBMITTED, allow_identical_states=allow_identical_states)
        if not oldest_submit_date_state_change:
            # logger_config.print_and_log_warning(f"{self.cfx_id} has no change state to submit state")
            if not self.submit_date:
                logger_config.print_and_log_error(f"{self._cfx_project_name} {self.cfx_identifier} has no submit date")
                assert self.get_all_change_state_actions_sorted_chronologically()
                return self.get_all_change_state_actions_sorted_chronologically()[0].timestamp
            return self.submit_date
        return oldest_submit_date_state_change.timestamp

    def get_oldest_change_state_action_by_new_state(self, new_state: State, allow_identical_states: bool) -> Optional[ChangeStateAction]:
        return next(
            (action for action in self.get_all_change_state_actions_sorted_chronologically() if action.new_state == new_state and (allow_identical_states or action.old_state != action.new_state)),
            None,
        )

    def get_newest_change_action_that_is_before_date(self, reference_date: datetime.datetime, allow_identical_states: bool) -> Optional[ChangeStateAction]:
        return next(
            (
                action
                for action in self.get_all_change_state_actions_sorted_reversed_chronologically()
                if action.timestamp < reference_date and (allow_identical_states or action.old_state != action.new_state)
            ),
            None,
        )

    def get_oldest_change_action_that_is_after_date(self, reference_date: datetime.datetime, allow_identical_states: bool) -> Optional[ChangeStateAction]:
        return next(
            (action for action in self.get_all_change_state_actions_sorted_chronologically() if action.timestamp > reference_date and (allow_identical_states or action.old_state != action.new_state)),
            None,
        )

    def get_newest_current_owner_modification_that_is_before_date(self, reference_date: datetime.datetime) -> Optional[ChangeCurrentOwnerAction]:
        return next((action for action in self.get_all_current_owner_modifications_sorted_reversed_chronologically() if action.timestamp < reference_date), None)

    def get_oldest_current_owner_modification_that_is_after_date(self, reference_date: datetime.datetime) -> Optional[ChangeCurrentOwnerAction]:
        return next((action for action in self.get_all_current_owner_modifications_sorted_chronologically() if action.timestamp > reference_date), None)

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

    @property
    def cfx_project_name(self) -> str:
        return self._cfx_project_name

    def get_current_role_at_date(self, reference_date: datetime.datetime) -> Optional[role.SubSystem]:
        current_owner = self.get_current_owner_at_date(reference_date)
        return None if current_owner is None else current_owner.subsystem

    def get_current_owner_at_date(self, reference_date: datetime.datetime) -> Optional[role.CfxUser]:
        if reference_date < self.submit_date:
            return None

        newest_current_owner_modification_action_that_is_before_date = self.get_newest_current_owner_modification_that_is_before_date(reference_date)
        if newest_current_owner_modification_action_that_is_before_date is not None:
            return newest_current_owner_modification_action_that_is_before_date.new_owner

        oldest_current_owner_modification_action_that_is_after_date = self.get_oldest_current_owner_modification_that_is_after_date(reference_date)
        if oldest_current_owner_modification_action_that_is_after_date is not None:
            if oldest_current_owner_modification_action_that_is_after_date.previous_owner is not None:
                return oldest_current_owner_modification_action_that_is_after_date.previous_owner

        return self._current_owner

    def get_state_at_date(self, reference_date: datetime.datetime) -> State:

        newest_change_action_that_is_before_date = self.get_newest_change_action_that_is_before_date(reference_date, allow_identical_states=False)
        if newest_change_action_that_is_before_date is not None:
            return newest_change_action_that_is_before_date.new_state

        if reference_date > self.submit_date:
            oldest_change_action_that_is_after_date = self.get_oldest_change_action_that_is_after_date(reference_date, allow_identical_states=False)
            if oldest_change_action_that_is_after_date:
                return oldest_change_action_that_is_after_date.old_state

            if self._state == State.SUBMITTED:
                return self._state
            # Cas où l'on n'a pour seul historique qu'un changement d'état
            newest_change_action_that_is_before_date = self.get_newest_change_action_that_is_before_date(reference_date, allow_identical_states=True)
            if newest_change_action_that_is_before_date is not None:
                return newest_change_action_that_is_before_date.new_state

            return State.UNKNOWN
        return State.NOT_CREATED_YET

    @property
    def all_history_current_owner_roles(self) -> set[role.SubSystem]:
        return self._all_history_current_owner_roles
