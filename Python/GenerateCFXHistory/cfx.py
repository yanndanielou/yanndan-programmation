import pandas as pd
import math
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import auto
from typing import Any, Dict, List, Optional, Set, cast

from common import enums_utils
from dateutil import relativedelta
from logger import logger_config

import cfx_extended_history
import role
import utils

DEFAULT_CHAMPFX_DETAILS_EXCEL_FILE_FULL_PATH: str = "Input/extract_cfx_details.xlsx"
DEFAULT_CHAMPFX_STATES_CHANGES_EXCEL_FILE_FULL_PATH: str = "Input/extract_cfx_change_state.xlsx"
DEFAULT_CHAMPFX_EXTENDED_HISTORY_FILE_FULL_PATH: str = "Input/cfx_extended_history.txt"


class CfxProject(enums_utils.NameBasedEnum):
    FR_NEXTEO = auto()
    ATSP = auto()


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


class State(enums_utils.NameBasedIntEnum):
    NOT_CREATED_YET = auto()
    NO_VALUE = auto()
    SUBMITTED = auto()
    ANALYSED = auto()
    ASSIGNED = auto()
    RESOLVED = auto()
    REJECTED = auto()
    POSTPONED = auto()
    VERIFIED = auto()
    VALIDATED = auto()
    CLOSED = auto()


@dataclass
class BaseAction:
    _cfx_request: "ChampFXEntry"
    _timestamp: datetime

    @property
    def timestamp(self) -> datetime:
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


class ChampFXLibrary:

    def __init__(
        self,
        champfx_details_excel_file_full_path: str = DEFAULT_CHAMPFX_DETAILS_EXCEL_FILE_FULL_PATH,
        champfx_states_changes_excel_file_full_path: str = DEFAULT_CHAMPFX_STATES_CHANGES_EXCEL_FILE_FULL_PATH,
        # all_current_owner_modifications_pickle_file_full_path: str = "Input/all_current_owner_modifications.pkl",
        # all_current_owner_modifications_per_cfx_pickle_file_full_path: str = "Input/all_current_owner_modifications_per_cfx.pkl",
        champfx_filter: Optional["ChampFxFilter"] = None,
        label: Optional[str] = None,
    ):

        self.label = label if label is not None else "" if label is None and champfx_filter is None else champfx_filter.label

        self._champfx_filter: Optional["ChampFxFilter"] = champfx_filter
        # self._all_current_owner_modifications_pickle_file_full_path = all_current_owner_modifications_pickle_file_full_path
        # self._all_current_owner_modifications_per_cfx_pickle_file_full_path = all_current_owner_modifications_per_cfx_pickle_file_full_path
        self._champfx_entry_by_id: Dict[str, ChampFXEntry] = dict()
        self._champfx_entries: List[ChampFXEntry] = []

        with logger_config.stopwatch_with_label("Load CfxUserLibrary"):
            self._cfx_users_library: role.CfxUserLibrary = role.CfxUserLibrary()

        with logger_config.stopwatch_with_label("ChampFXLibrary creation and initialisation"):

            with logger_config.stopwatch_with_label(f"Open cfx details excel file {champfx_details_excel_file_full_path}"):
                cfx_details_data_frame = pd.read_excel(champfx_details_excel_file_full_path)

            with logger_config.stopwatch_with_label(f"Open cfx state changes excel file {champfx_states_changes_excel_file_full_path}"):
                cfx_states_changes_data_frame = pd.read_excel(champfx_states_changes_excel_file_full_path)

            with logger_config.stopwatch_with_label("Create ChampFXEntry objects"):
                self.create_or_fill_champfx_entry_with_dataframe(cfx_details_data_frame)
                logger_config.print_and_log_info(f"{len(self.get_all_cfx())} ChampFXEntry objects created")

            all_cfx_complete_extended_histories_text_file_path = DEFAULT_CHAMPFX_EXTENDED_HISTORY_FILE_FULL_PATH
            with logger_config.stopwatch_with_label(f"Load cfx_extended_history {all_cfx_complete_extended_histories_text_file_path}"):
                self._all_cfx_complete_extended_histories: List[cfx_extended_history.CFXEntryCompleteHistory] = (
                    cfx_extended_history.AllCFXCompleteHistoryExport.parse_full_complete_extended_histories_text_file(all_cfx_complete_extended_histories_text_file_path, self.get_all_cfx_ids())
                )

            with logger_config.stopwatch_with_label("Create state changes objects"):
                change_state_actions_created = self.create_states_changes_with_dataframe(cfx_states_changes_data_frame)
                logger_config.print_and_log_info(f"{len(change_state_actions_created)} ChangeStateAction objects created")

            with logger_config.stopwatch_with_label("ChampFXLibrary process_current_owner_role"):
                list(map(lambda champ_fx: champ_fx.process_current_owner_role(self), self.get_all_cfx()))

            with logger_config.stopwatch_with_label("create current owner modifications"):
                self.create_current_owner_modifications()

            with logger_config.stopwatch_with_label("ChampFXLibrary process_subsystem_from_fixed_implemented_in"):
                list(map(lambda champ_fx: champ_fx.process_subsystem_from_fixed_implemented_in(), self.get_all_cfx()))

            with logger_config.stopwatch_with_label("ChampFXLibrary process_subsystem"):
                list(map(lambda champ_fx: champ_fx.process_subsystem(), self.get_all_cfx()))

    def create_or_fill_champfx_entry_with_dataframe(self, cfx_details_data_frame: pd.DataFrame) -> None:
        for _, row in cfx_details_data_frame.iterrows():
            cfx_id = row["CFXID"]

            if cfx_id in self._champfx_entry_by_id:
                cfx_entry = self._champfx_entry_by_id[cfx_id]
                cfx_entry._current_owner
            else:
                cfx_entry = ChampFXEntryBuilder.build_with_row(row)
                if self._champfx_filter is None or self._champfx_filter.match_cfx_entry(cfx_entry):
                    self._champfx_entry_by_id[cfx_id] = cfx_entry
                    self._champfx_entries.append(cfx_entry)

    def create_states_changes_with_dataframe(self, cfx_states_changes_data_frame: pd.DataFrame) -> List[ChangeStateAction]:
        change_state_actions_created: List[ChangeStateAction] = []

        for _, row in cfx_states_changes_data_frame.iterrows():
            cfx_id = row["CFXID"]

            if cfx_id in self.get_all_cfx_ids():

                cfx_request = self.get_cfx_by_id(cfx_id)
                history_raw_old_state: str = row["history.old_state"]
                old_state: State = State[history_raw_old_state.upper()]
                history_raw_new_state: str = row["history.new_state"]
                new_state: State = State[history_raw_new_state.upper()]
                history_raw_action_timestamp_str = row["history.action_timestamp"]
                action_timestamp = utils.convert_champfx_extract_date(history_raw_action_timestamp_str)
                history_raw_action_name: str = row["history.action_name"]
                history_action = ActionType[history_raw_action_name.upper()]
                change_state_actions_created.append(history_action)

                change_state_action = ChangeStateAction(_cfx_request=cfx_request, _old_state=old_state, _new_state=new_state, _timestamp=action_timestamp, _action=history_action)

                cfx_request.add_change_state_action(change_state_action)

        return change_state_actions_created

    def convert_cfx_history_element_to_valid_full_name(self, cfx_history_element_state: str) -> str:
        return cfx_history_element_state.split("(")[0].strip()

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

                        previous_current_owner_name = self.convert_cfx_history_element_to_valid_full_name(cfx_history_field.old_state)
                        new_current_owner_name = self.convert_cfx_history_element_to_valid_full_name(cfx_history_field.new_state)

                        if not previous_current_owner_name or not new_current_owner_name:
                            logger_config.print_and_log_error(f"Invalid current owner change history for {cfx_id}, from {previous_current_owner_name} to {new_current_owner_name}. {cfx_history_field}")

                        previous_owner = self._cfx_users_library.get_cfx_user_by_full_name(previous_current_owner_name) if previous_current_owner_name else self._cfx_users_library.unknown_user
                        new_owner: role.CfxUser = self._cfx_users_library.get_cfx_user_by_full_name(new_current_owner_name) if new_current_owner_name else self._cfx_users_library.unknown_user

                        change_current_owner_action: ChangeCurrentOwnerAction = ChangeCurrentOwnerAction(
                            _cfx_request=cfx_entry, _previous_owner=previous_owner, _new_owner=new_owner, _timestamp=cfx_history_field.change_timestamp.replace(tzinfo=None)
                        )
                        change_current_owner_actions_created.append(change_current_owner_action)
                        cfx_entry.add_change_current_owner_action(change_current_owner_action)

        return change_current_owner_actions_created

    def get_all_cfx_by_id_dict(self) -> Dict[str, "ChampFXEntry"]:
        return self._champfx_entry_by_id

    def get_all_cfx(self) -> List["ChampFXEntry"]:
        return self._champfx_entries

    def get_all_cfx_ids(self) -> List[str]:
        return list(self._champfx_entry_by_id.keys())

    def get_cfx_by_id(self, cfx_id: str) -> "ChampFXEntry":
        return self._champfx_entry_by_id[cfx_id]

    def get_cfx_by_state_at_date(self, reference_date: datetime) -> Dict[State, list["ChampFXEntry"]]:
        result: Dict[State, List[ChampFXEntry]] = {}
        for cfx_entry in self.get_all_cfx():
            state = cfx_entry.get_state_at_date(reference_date)
            if state not in result:
                result[state] = []
            result[state].append(cfx_entry)

        return result

    def get_earliest_submit_date(self) -> datetime:
        earliest_date = min(entry.get_oldest_change_action_by_new_state(State.SUBMITTED).timestamp for entry in self.get_all_cfx())
        return earliest_date

    def get_tenth_days_since_earliest_submit_date(self) -> List[datetime]:
        earliest_cfx_date = self.get_earliest_submit_date()

        earliest_date_considered = earliest_cfx_date.replace(day=1)

        # Ensure 'beginning_of_next_month' is naive datetime
        beginning_of_next_month = (datetime.now() + relativedelta.relativedelta(months=1)).replace(day=1, hour=0, minute=0, second=0, microsecond=0, tzinfo=None)
        dates = []

        # Ensure 'current_date' is naive datetime
        current_date_iter = earliest_date_considered.replace(day=1, hour=0, minute=0, second=0, microsecond=0, tzinfo=None)
        while current_date_iter <= beginning_of_next_month:
            dates.append(current_date_iter)
            current_date_iter = current_date_iter + timedelta(days=10)

        return dates

    def get_months_since_earliest_submit_date(self) -> List[datetime]:
        earliest_cfx_date = self.get_earliest_submit_date()

        earliest_date_considered = earliest_cfx_date.replace(day=1)

        # Ensure 'beginning_of_next_month' is naive datetime
        beginning_of_next_month = (datetime.now() + relativedelta.relativedelta(months=1)).replace(day=1, hour=0, minute=0, second=0, microsecond=0, tzinfo=None)
        months = []

        # Ensure 'current_date' is naive datetime
        current_date_iter = earliest_date_considered.replace(day=1, hour=0, minute=0, second=0, microsecond=0, tzinfo=None)
        while current_date_iter <= beginning_of_next_month:
            months.append(current_date_iter)
            # Move to the first day of the next month
            if current_date_iter.month == 12:
                current_date_iter = current_date_iter.replace(year=current_date_iter.year + 1, month=1)
            else:
                current_date_iter = current_date_iter.replace(month=current_date_iter.month + 1)

        return months


class ChampFXEntryBuilder:

    @staticmethod
    def convert_champfx_security_relevant(raw_security_relevant: str) -> SecurityRelevant:
        security_relevant: SecurityRelevant = (
            SecurityRelevant.UNDEFINED if type(raw_security_relevant) is not str and math.isnan(raw_security_relevant) else SecurityRelevant[raw_security_relevant.upper()]
        )
        return security_relevant

    @staticmethod
    def to_optional_boolean(raw_value: str) -> Optional[bool]:
        if raw_value == "Yes":
            return True
        elif raw_value == "No":
            return False
        return None

    @staticmethod
    def build_with_row(row: pd.Series) -> "ChampFXEntry":
        cfx_id = row["CFXID"]
        raw_state: State = State[(row["State"].upper())]
        fixed_implemented_in: str = row["FixedImplementedIn"]
        current_owner_raw: str = row["CurrentOwner.FullName"]
        submit_date_raw: str = row["SubmitDate"]
        raw_project: str = cast(str, row["Project"])
        cfx_project = CfxProject[raw_project]
        raw_safety_relevant: str = row["SafetyRelevant"]
        safety_relevant: Optional[bool] = ChampFXEntryBuilder.to_optional_boolean(raw_safety_relevant)

        raw_security_relevant: str = row["SecurityRelevant"]
        security_relevant: SecurityRelevant = ChampFXEntryBuilder.convert_champfx_security_relevant(raw_security_relevant)

        champfx_entry = ChampFXEntry(
            cfx_id=cfx_id,
            raw_state=raw_state,
            fixed_implemented_in=fixed_implemented_in,
            current_owner_raw=current_owner_raw,
            submit_date_raw=submit_date_raw,
            cfx_project=cfx_project,
            safety_relevant=safety_relevant,
            security_relevant=security_relevant,
        )
        return champfx_entry


class ChampFXEntry:
    def __init__(
        self,
        cfx_id: str,
        raw_state: State,
        fixed_implemented_in: str,
        current_owner_raw: str,
        submit_date_raw: str,
        cfx_project: CfxProject,
        safety_relevant: Optional[bool],
        security_relevant: SecurityRelevant,
    ):
        self._change_state_actions: list[ChangeStateAction] = []
        self._change_state_actions_by_date: Dict[datetime, ChangeStateAction] = dict()

        self._change_current_owner_actions: list[ChangeCurrentOwnerAction] = []
        self._change_current_owner_actions_by_date: Dict[datetime, ChangeCurrentOwnerAction] = dict()

        self.cfx_id = cfx_id
        self._raw_state: State = raw_state
        self._fixed_implemented_in: str = fixed_implemented_in
        self._current_owner_raw: str = current_owner_raw
        self._current_owner: role.CfxUser = role.UNKNOWN_USER
        self._current_owner_role: role.SubSystem = role.UNKNOWN_USER.subsystem

        self._subsystem: role.SubSystem.TBD

        self._subsystem_from_fixed_implemented_in: role.SubSystem = role.SubSystem.TBD
        self._submit_date: datetime = utils.convert_champfx_extract_date(submit_date_raw)

        self._cfx_project = cfx_project
        self._safety_relevant = safety_relevant
        self._security_relevant = security_relevant

    def __repr__(self) -> str:
        return f"<ChampFXEntry cfx_id={self.cfx_id} _raw_state={self._raw_state} _current_owner_raw={self._current_owner_raw}>"

    def get_all_actions_sorted_chronologically(self) -> list[ChangeStateAction]:
        # return sorted(self._change_state_actions_by_date.items())
        return [action for _, action in sorted(self._change_state_actions_by_date.items())]

    def get_all_current_owner_modifications_sorted_chronologically(self) -> list[ChangeCurrentOwnerAction]:
        # return sorted(self._change_state_actions_by_date.items())
        return [action for _, action in sorted(self._change_current_owner_actions_by_date.items())]

    def get_oldest_change_action_by_new_state(self, new_state: State) -> Optional[ChangeStateAction]:
        return next((action for action in self.get_all_actions_sorted_chronologically() if action.new_state == new_state), None)

    def get_newest_change_action_that_is_before_date(self, reference_date: datetime) -> Optional[ChangeStateAction]:
        return next((action for action in reversed(self.get_all_actions_sorted_chronologically()) if action.timestamp < reference_date), None)

    def get_newest_current_owner_modification_that_is_before_date(self, reference_date: datetime) -> Optional[ChangeCurrentOwnerAction]:
        return next((action for action in reversed(self.get_all_current_owner_modifications_sorted_chronologically()) if action.timestamp < reference_date), None)

    def add_change_state_action(self, change_state_action: ChangeStateAction) -> None:
        self._change_state_actions.append(change_state_action)
        self._change_state_actions_by_date[change_state_action.timestamp] = change_state_action

    def add_change_current_owner_action(self, change_current_owner_action: ChangeCurrentOwnerAction) -> None:
        self._change_current_owner_actions.append(change_current_owner_action)
        self._change_current_owner_actions_by_date[change_current_owner_action.timestamp] = change_current_owner_action

    @property
    def raw_state(self) -> State:
        return self._raw_state

    def process_current_owner_role(self, cfx_library: ChampFXLibrary) -> role.SubSystem:
        self._current_owner = cfx_library._cfx_users_library.get_cfx_user_by_full_name(self._current_owner_raw)
        self._current_owner_role: role.SubSystem = self._current_owner._subsystem

        return self._current_owner_role

    def process_subsystem(self) -> None:
        self._subsystem = self._subsystem_from_fixed_implemented_in if self._subsystem_from_fixed_implemented_in else self._current_owner_role

    def process_subsystem_from_fixed_implemented_in(self) -> Optional[role.SubSystem]:
        if self._fixed_implemented_in:
            self._subsystem_from_fixed_implemented_in = role.get_subsystem_from_champfx_fixed_implemented_in(self._fixed_implemented_in)
            return self._subsystem_from_fixed_implemented_in
        return None

    def get_current_role_at_date(self, reference_date: datetime) -> Optional[role.SubSystem]:
        current_owner = self.get_current_owner_at_date(reference_date)
        return None if current_owner is None else current_owner.subsystem

    def get_current_owner_at_date(self, reference_date: datetime) -> Optional[role.CfxUser]:
        if reference_date < self._submit_date:
            return None

        newest_current_owner_modification_action_that_is_before_date = self.get_newest_current_owner_modification_that_is_before_date(reference_date)
        if newest_current_owner_modification_action_that_is_before_date is not None:
            return newest_current_owner_modification_action_that_is_before_date.new_owner
        return self._current_owner

    def get_state_at_date(self, reference_date: datetime) -> State:

        newest_change_action_that_is_before_date = self.get_newest_change_action_that_is_before_date(reference_date)
        if newest_change_action_that_is_before_date is None:
            return State.NOT_CREATED_YET
        else:
            return newest_change_action_that_is_before_date.new_state


class ChampFXtSaticCriteriaFilter:
    def __init__(self) -> None:
        self._cache_result_by_cfx: dict[ChampFXEntry, bool] = dict()
        self._number_of_results_obtained_by_cache_usage = 0

    def match_cfx_entry_without_cache(self, cfx_entry: ChampFXEntry) -> bool:
        return NotImplemented

    def match_cfx_entry_with_cache(self, cfx_entry: ChampFXEntry) -> bool:
        if cfx_entry in self._cache_result_by_cfx:
            self._number_of_results_obtained_by_cache_usage += 1
            return self._cache_result_by_cfx[cfx_entry]

        new_result_computed = self.match_cfx_entry_without_cache(cfx_entry)
        self._cache_result_by_cfx[cfx_entry] = new_result_computed
        return new_result_computed


class ChampFXWhitelistFilter(ChampFXtSaticCriteriaFilter):
    def __init__(
        self,
        cfx_to_treat_whitelist_text_file_full_path: Optional[str] = None,
        cfx_to_treat_ids: Optional[Set[str]] = None,
    ):
        super().__init__()
        self._cfx_to_treat_whitelist_text_file_full_path: Optional[str] = cfx_to_treat_whitelist_text_file_full_path
        self._cfx_to_treat_whitelist_ids: Set[str] = set()

        if self._cfx_to_treat_whitelist_text_file_full_path is not None:
            self.label: str = f"list {self._cfx_to_treat_whitelist_text_file_full_path.replace("/", " ").replace("\\", " ")}"
            self._cfx_to_treat_whitelist_ids = set()
            with logger_config.stopwatch_with_label(f"Load CfxUserLibrary {cfx_to_treat_whitelist_text_file_full_path}"):
                with open(self._cfx_to_treat_whitelist_text_file_full_path, "r", encoding="utf-8") as cfx_known_by_cstmr_text_file:
                    self._cfx_to_treat_whitelist_ids = [line.strip() for line in cfx_known_by_cstmr_text_file.readlines()]
            logger_config.print_and_log_info(f"Number of cfx_to_treat_whitelist_ids:{len(self._cfx_to_treat_whitelist_ids)}")

        elif cfx_to_treat_ids:
            self.label: str = f"list {len(cfx_to_treat_ids)} white listed"  # type: ignore[no-redef]
            self._cfx_to_treat_whitelist_ids = cfx_to_treat_ids

    def match_cfx_entry_without_cache(self, cfx_entry: ChampFXEntry) -> bool:
        return cfx_entry.cfx_id in self._cfx_to_treat_whitelist_ids


class ChampFXFieldFilter(ChampFXtSaticCriteriaFilter):

    def __init__(self, field_name: str, field_accepted_values: Optional[List[Any]] = None, field_forbidden_values: Optional[List[Any]] = None) -> None:
        super().__init__()
        self.field_name = field_name
        self.field_accepted_values = field_accepted_values
        self.field_forbidden_values = field_forbidden_values

        label: str = f"{self.field_name}"

        if self.field_accepted_values:
            label = f"{label} among {self.field_accepted_values}"
        else:
            label = f"{label} without {self.field_forbidden_values}"
        self.label = label

    def match_cfx_entry_without_cache(self, cfx_entry: ChampFXEntry) -> bool:
        attribute_entry = getattr(cfx_entry, self.field_name)
        if self.field_accepted_values is not None:
            return attribute_entry in self.field_accepted_values
        else:
            return attribute_entry not in cast(List[Any], self.field_forbidden_values)


@dataclass
class ChampFXRoleAtSpecificDateFilter:
    timestamp: datetime
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

    def match_cfx_entry(self, cfx_entry: ChampFXEntry, timestamp: datetime) -> bool:
        return ChampFXRoleAtSpecificDateFilter(roles_at_date_allowed=self.roles_at_date_allowed, timestamp=timestamp).match_cfx_entry(cfx_entry=cfx_entry)


class ChampFxFilter:

    def __init__(
        self,
        role_depending_on_date_filter: Optional[ChampFXRoleDependingOnDateFilter] = None,
        field_filters: Optional[List[ChampFXFieldFilter]] = None,
        cfx_to_treat_whitelist_text_file_full_path: Optional[str] = None,
        label: Optional[str] = None,
    ):
        if field_filters is None:
            field_filters = []

        self.role_depending_on_date_filter: Optional[ChampFXRoleDependingOnDateFilter] = role_depending_on_date_filter
        self._field_filters: List[ChampFXFieldFilter] = field_filters
        self._cfx_to_treat_whitelist_text_file_full_path: Optional[str] = cfx_to_treat_whitelist_text_file_full_path
        self._cfx_to_treat_whitelist_ids: Optional[Set[str]] = None
        self.label: str = label if label is not None else ""

        self._white_list_filter: Optional[ChampFXWhitelistFilter] = (
            ChampFXWhitelistFilter(cfx_to_treat_whitelist_text_file_full_path) if cfx_to_treat_whitelist_text_file_full_path is not None else None
        )

        self._compute_label()

    def _compute_label(self) -> None:

        label = self.label

        if label is None:
            label = ""

        if self.role_depending_on_date_filter:
            label = f"{label} role {self.role_depending_on_date_filter.roles_at_date_allowed} per date"

        if len(self._field_filters) > 0:
            label = f"{label} fields {[field_filter.label for field_filter in self._field_filters]}"

        if self._white_list_filter:
            label = f"{label} {self._white_list_filter.label}"

        self.label = label

    def match_cfx_entry(self, cfx_entry: ChampFXEntry, timestamp: Optional[datetime] = None) -> bool:

        if self._white_list_filter is not None:
            if not self._white_list_filter.match_cfx_entry_with_cache(cfx_entry=cfx_entry):
                return False

        for field_filter in self._field_filters:
            if not field_filter.match_cfx_entry_with_cache(cfx_entry=cfx_entry):
                return False

        if self.role_depending_on_date_filter:
            if not self.role_depending_on_date_filter.match_cfx_entry(cfx_entry=cfx_entry, timestamp=cast(datetime, timestamp)):
                return False

        return True
