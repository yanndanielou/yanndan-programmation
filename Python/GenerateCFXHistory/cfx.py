import pickle

import pandas as pd
from datetime import datetime, timedelta
from dateutil import relativedelta

from dataclasses import dataclass
from typing import Optional, List, Dict

from enum import Enum, auto, IntEnum

from logger import logger_config

import utils
import role
import cfx_extended_history


class ActionType(Enum):
    Import = auto()
    ReSubmit = auto()
    Submit = auto()
    Assign = auto()
    Analyse = auto()
    Postpone = auto()
    Reject = auto()
    Resolve = auto()
    Verify = auto()
    Validate = auto()
    Close = auto()


class State(IntEnum):
    NotCreatedYet = auto()
    no_value = auto()
    Submitted = auto()
    Analysed = auto()
    Assigned = auto()
    Resolved = auto()
    Rejected = auto()
    Postponed = auto()
    Verified = auto()
    Validated = auto()
    Closed = auto()


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
        champfx_details_excel_file_full_path: str = "Input/extract_cfx_details.xlsx",
        champfx_states_changes_excel_file_full_path: str = "Input/extract_cfx_change_state.xlsx",
        all_current_owner_modifications_pickle_file_full_path: str = "Input/all_current_owner_modifications.pkl",
        all_current_owner_modifications_per_cfx_pickle_file_full_path: str = "Input/all_current_owner_modifications_per_cfx.pkl",
    ):

        self._all_current_owner_modifications_pickle_file_full_path = all_current_owner_modifications_pickle_file_full_path
        self._all_current_owner_modifications_per_cfx_pickle_file_full_path = all_current_owner_modifications_per_cfx_pickle_file_full_path
        self._champfx_entry_by_id: Dict[str, ChampFXEntry] = dict()

        cfx_known_by_cstmr_text_file_path = "Input/CFX_kown_by_customer.txt"
        self._cfx_known_by_cstmr_ids: set[str] = set()
        with logger_config.stopwatch_with_label(f"Load CfxUserLibrary {cfx_known_by_cstmr_text_file_path}"):
            with open(cfx_known_by_cstmr_text_file_path, "r", encoding="utf-8") as cfx_known_by_cstmr_text_file:
                self._cfx_known_by_cstmr_ids = [line.strip() for line in cfx_known_by_cstmr_text_file.readlines()]
        logger_config.print_and_log_info(f"Number of cfx_known_by_cstmr_ids:{len(self._cfx_known_by_cstmr_ids)}")

        all_cfx_complete_extended_histories_text_file_path = "Input/cfx_extended_history.txt"
        with logger_config.stopwatch_with_label(f"Load cfx_extended_history {all_cfx_complete_extended_histories_text_file_path}"):
            self._all_cfx_complete_extended_histories: List[cfx_extended_history.CFXEntryCompleteHistory] = (
                cfx_extended_history.AllCFXCompleteHistoryExport.parse_full_complete_extended_histories_text_file(all_cfx_complete_extended_histories_text_file_path)
            )

        with logger_config.stopwatch_with_label("Load CfxUserLibrary"):
            self._cfx_users_library: role.CfxUserLibrary = role.CfxUserLibrary()

        with logger_config.stopwatch_with_label("ChampFXLibrary creation and initialisation"):

            with logger_config.stopwatch_with_label(f"Open cfx details excel file {champfx_details_excel_file_full_path}"):
                cfx_details_data_frame = pd.read_excel(champfx_details_excel_file_full_path)

            with logger_config.stopwatch_with_label(f"Open cfx state changes excel file {champfx_states_changes_excel_file_full_path}"):
                cfx_states_changes_data_frame = pd.read_excel(champfx_states_changes_excel_file_full_path)

            with logger_config.stopwatch_with_label(f"Create ChampFXEntry objects"):
                self.create_or_fill_champfx_entry_with_dataframe(cfx_details_data_frame)
                logger_config.print_and_log_info(f"{len(self.get_all_cfx())} ChampFXEntry objects created")

            with logger_config.stopwatch_with_label(f"Create state changes objects"):
                change_state_actions_created = self.create_states_changes_with_dataframe(cfx_states_changes_data_frame)
                logger_config.print_and_log_info(f"{len(change_state_actions_created)} ChangeStateAction objects created")

            with logger_config.stopwatch_with_label("ChampFXLibrary process_current_owner_role"):
                list(map(lambda champ_fx: champ_fx.process_current_owner_role(self), self.get_all_cfx()))

            # with logger_config.stopwatch_with_label(f"create current owner modifications"):
            #    self.create_current_owner_modifications()

            with logger_config.stopwatch_with_label(f"ChampFXLibrary process_subsystem_from_fixed_implemented_in"):
                list(map(lambda champ_fx: champ_fx.process_subsystem_from_fixed_implemented_in(), self.get_all_cfx()))

    def create_or_fill_champfx_entry_with_dataframe(self, cfx_details_data_frame: pd.DataFrame) -> None:
        for _, row in cfx_details_data_frame.iterrows():
            cfx_id = row["CFXID"]
            if cfx_id in self._champfx_entry_by_id:
                cfx = self._champfx_entry_by_id[cfx_id]
                cfx._current_owner
            else:
                cfx = ChampFXEntryBuilder.build_with_row(row, self._cfx_known_by_cstmr_ids)
                self._champfx_entry_by_id[cfx_id] = cfx

    def create_states_changes_with_dataframe(self, cfx_states_changes_data_frame: pd.DataFrame) -> List[ChangeStateAction]:
        change_state_actions_created: List[ChangeStateAction] = []

        for _, row in cfx_states_changes_data_frame.iterrows():
            cfx_id = row["CFXID"]

            cfx_request = self.get_cfx_by_id(cfx_id)
            history_raw_old_state = row["history.old_state"]
            old_state: State = State[history_raw_old_state]
            history_raw_new_state = row["history.new_state"]
            new_state: State = State[history_raw_new_state]
            history_raw_action_timestamp_str = row["history.action_timestamp"]
            action_timestamp = utils.convert_champfx_extract_date(history_raw_action_timestamp_str)
            history_raw_action_name = row["history.action_name"]
            history_action = ActionType[history_raw_action_name]
            change_state_actions_created.append(history_action)

            change_state_action = ChangeStateAction(_cfx_request=cfx_request, _old_state=old_state, _new_state=new_state, _timestamp=action_timestamp, _action=history_action)

            cfx_request.add_change_state_action(change_state_action)

        return change_state_actions_created

    def convert_cfx_history_element_to_valid_full_name(self, cfx_history_element_state: str) -> str:
        return cfx_history_element_state.split("(")[0].strip()

    def create_current_owner_modifications(self):

        change_current_owner_actions_created: List[ChangeCurrentOwnerAction] = []

        with open(self._all_current_owner_modifications_per_cfx_pickle_file_full_path, "rb") as file:
            all_current_owner_modifications_per_cfx: Dict[str, List[cfx_extended_history.CFXHistoryField]] = pickle.load(file)

            for cfx_id, cfx_history_elements in all_current_owner_modifications_per_cfx.items():
                cfx_entry = self.get_cfx_by_id(cfx_id)
                for cfx_history_element in cfx_history_elements:
                    # cfx_history_element.

                    # Ignore invalid entries

                    previous_current_owner_name = self.convert_cfx_history_element_to_valid_full_name(cfx_history_element.old_state)
                    new_current_owner_name = self.convert_cfx_history_element_to_valid_full_name(cfx_history_element.new_state)

                    if not previous_current_owner_name or not new_current_owner_name:
                        logger_config.print_and_log_error(f"Invalid current owner change history for {cfx_id}, from {previous_current_owner_name} to {new_current_owner_name}. {cfx_history_element}")

                    previous_owner = self._cfx_users_library.get_cfx_user_by_full_name(previous_current_owner_name) if previous_current_owner_name else self._cfx_users_library.unknown_user
                    new_owner: role.CfxUser = self._cfx_users_library.get_cfx_user_by_full_name(new_current_owner_name) if new_current_owner_name else self._cfx_users_library.unknown_user

                    change_current_owner_action: ChangeCurrentOwnerAction = ChangeCurrentOwnerAction(
                        _cfx_request=cfx_entry, _previous_owner=previous_owner, _new_owner=new_owner, _timestamp=cfx_history_element.change_timestamp.replace(tzinfo=None)
                    )
                    change_current_owner_actions_created.append(change_current_owner_action)
                    cfx_entry.add_change_current_owner_action(change_current_owner_action)

        return change_current_owner_actions_created

    def get_all_cfx(self) -> List["ChampFXEntry"]:
        return self._champfx_entry_by_id.values()

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
        earliest_date = min(entry.get_oldest_change_action_by_new_state(State.Submitted).timestamp for entry in self.get_all_cfx())
        return earliest_date

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
    def build_with_row(row, cfx_known_by_cstmr_ids: set[str]) -> "ChampFXEntry":
        cfx_id = row["CFXID"]
        _raw_state: State = State[(row["State"])]
        _fixed_implemented_in: str = row["FixedImplementedIn"]
        _current_owner_raw: str = row["CurrentOwner.FullName"]
        known_by_cstmr = cfx_id in cfx_known_by_cstmr_ids
        champfx_entry = ChampFXEntry(cfx_id=cfx_id, raw_state=_raw_state, fixed_implemented_in=_fixed_implemented_in, current_owner_raw=_current_owner_raw, known_by_cstmr=known_by_cstmr)
        return champfx_entry


class ChampFXEntry:
    def __init__(self, cfx_id: str, raw_state: State, fixed_implemented_in: str, current_owner_raw: str, known_by_cstmr: bool):
        self._change_state_actions: list[ChangeStateAction] = []
        self._change_state_actions_by_date: Dict[datetime, ChangeStateAction] = dict()

        self._change_current_owner_actions: list[ChangeCurrentOwnerAction] = []
        self._change_current_owner_actions_by_date: Dict[datetime, ChangeCurrentOwnerAction] = dict()

        self.cfx_id = cfx_id
        self._raw_state: State = raw_state
        self._fixed_implemented_in: str = fixed_implemented_in
        self._current_owner_raw: str = current_owner_raw
        self._known_by_cstmr = known_by_cstmr
        self._current_owner: role.CfxUser = None
        self._current_owner_role: role.SubSystem = None
        self._subsystem_from_fixed_implemented_in: role.SubSystem = None

    def __repr__(self) -> str:
        return f"<ChampFXEntry cfx_id={self.cfx_id} _raw_state={self._raw_state} _current_owner_raw={self._current_owner_raw}>"

    def get_all_actions_sorted_chronologically(self) -> list[ChangeStateAction]:
        # return sorted(self._change_state_actions_by_date.items())
        return [action for _, action in sorted(self._change_state_actions_by_date.items())]

    def get_all_current_owner_modifications_sorted_chronologically(self) -> list[ChangeCurrentOwnerAction]:
        # return sorted(self._change_state_actions_by_date.items())
        return [action for _, action in sorted(self._change_current_owner_actions_by_date.items())]

    def get_oldest_change_action_by_new_state(self, new_state: State) -> ChangeStateAction:
        return next((action for action in self.get_all_actions_sorted_chronologically() if action.new_state == new_state), None)

    def get_newest_change_action_that_is_before_date(self, reference_date: datetime) -> ChangeStateAction:
        return next((action for action in reversed(self.get_all_actions_sorted_chronologically()) if action.timestamp < reference_date), None)

    def get_newest_current_owner_modification_that_is_before_date(self, reference_date: datetime) -> ChangeCurrentOwnerAction:
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

    def process_subsystem_from_fixed_implemented_in(self) -> Optional[role.SubSystem]:
        if self._fixed_implemented_in:
            self._subsystem_from_fixed_implemented_in = role.get_subsystem_from_champfx_fixed_implemented_in(self._fixed_implemented_in)
            return self._subsystem_from_fixed_implemented_in
        return None

    def get_sub_system(self) -> role.SubSystem:
        return self._subsystem_from_fixed_implemented_in if self._subsystem_from_fixed_implemented_in else self._current_owner_role

    def get_current_owner_at_date(self, reference_date: datetime) -> role.CfxUser:
        newest_current_owner_modification_action_that_is_before_date = self.get_newest_current_owner_modification_that_is_before_date(reference_date)
        if newest_current_owner_modification_action_that_is_before_date is not None:
            return newest_current_owner_modification_action_that_is_before_date.new_owner
        return self._current_owner

    def get_state_at_date(self, reference_date: datetime) -> State:

        newest_change_action_that_is_before_date = self.get_newest_change_action_that_is_before_date(reference_date)
        if newest_change_action_that_is_before_date is None:
            return State.NotCreatedYet
        else:
            return newest_change_action_that_is_before_date.new_state
