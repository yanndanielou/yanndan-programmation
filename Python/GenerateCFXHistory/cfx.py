import pandas as pd
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Optional, List, Dict

from logger import logger_config

import utils
import role

from enum import Enum, auto


class State(Enum):
    NotCreatedYet = auto()
    Submitted = auto()
    Analysed = auto()
    Assigned = auto()
    Resolved = auto()
    Rejected = auto()
    Postponed = auto()
    Verified = auto()
    Validated = auto()
    Closed = auto()


class ChampFXLibrary:

    def __init__(self, champfx_extract_excel_file_full_path: str):

        with logger_config.stopwatch_with_label(f"ChampFXLibrary creation and initialisation"):

            with logger_config.stopwatch_with_label(f"Open excel file {champfx_extract_excel_file_full_path}"):
                df = pd.read_excel(champfx_extract_excel_file_full_path)

            with logger_config.stopwatch_with_label(f"Create ChampFXEntry objects"):
                self._all_cfx: list["ChampFXEntry"] = [ChampFXEntry(row) for _, row in df.iterrows()]
                logger_config.print_and_log_info(f"{len(self._all_cfx)} ChampFXEntry objects created")

            with logger_config.stopwatch_with_label("ChampFXLibrary process_current_owner_role"):
                list(map(lambda champ_fx: champ_fx.process_current_owner_role(), self._all_cfx))

            with logger_config.stopwatch_with_label(f"ChampFXLibrary process_subsystem_from_fixed_implemented_in"):
                list(map(lambda champ_fx: champ_fx.process_subsystem_from_fixed_implemented_in(), self._all_cfx))

    @property
    def all_cfx(self) -> List["ChampFXEntry"]:
        return self._all_cfx

    def get_cfx_by_state_at_date(self, reference_date: datetime) -> Dict[State, list["ChampFXEntry"]]:
        result: Dict[State, List[ChampFXEntry]] = {}
        for cfx_entry in self._all_cfx:
            state = cfx_entry.get_state_at_date(reference_date)
            if state not in result:
                result[state] = []
            result[state].append(cfx_entry)

        return result

    def get_earliest_submit_date(self) -> datetime:
        earliest_date = min(entry._submit_date for entry in self._all_cfx)
        return earliest_date

    def get_months_since_earliest_submit_date(self) -> List[datetime]:
        earliest_date = self.get_earliest_submit_date()
        if earliest_date is None:
            return []  # Return an empty list if no entries are present

        # Ensure 'today' is naive datetime
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=None)
        months = []

        # Ensure 'current_date' is naive datetime
        current_date = earliest_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0, tzinfo=None)
        while current_date <= today:
            months.append(current_date)
            # Move to the first day of the next month
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)

        return months


class ChampFXEntry:
    def __init__(self, row):
        self.cfx_id = row["CFXID"]
        self._raw_state: State = State[(row["State"])]
        self._submit_date: datetime = utils.convert_champfx_extract_date(row["SubmitDate"])
        self._analysis_date: datetime = utils.convert_champfx_extract_date(row["HistoryOfLastAction.AnalysisDate"])
        self._solution_date: datetime = utils.convert_champfx_extract_date(row["HistoryOfLastAction.SolutionDate"])
        self._verification_date: datetime = utils.convert_champfx_extract_date(row["HistoryOfLastAction.VerificationDate"])
        self._validation_date: datetime = utils.convert_champfx_extract_date(row["HistoryOfLastAction.ValidationDate"])
        self._closing_date: datetime = utils.convert_champfx_extract_date(row["HistoryOfLastAction.ClosingDate"])
        self._fixed_implemented_in: str = row["FixedImplementedIn"]
        self._current_owner: str = row["CurrentOwner.FullName"]
        self._current_owner_role: role.SubSystem = None
        self._subsystem_from_fixed_implemented_in: role.SubSystem = None
        # self._submit_year: datetime = self._submit_date.year
        # self._submit_month: datetime = self._submit_date.month

    @property
    def raw_state(self) -> State:
        return self._raw_state

    def process_current_owner_role(self) -> role.SubSystem:
        self._current_owner_role: role.SubSystem = role.get_subsystem_from_cfx_current_owner(self._current_owner)
        return self._current_owner_role

    def process_subsystem_from_fixed_implemented_in(self) -> Optional[role.SubSystem]:
        if self._fixed_implemented_in:
            self._subsystem_from_fixed_implemented_in = role.get_subsystem_from_champfx_fixed_implemented_in(self._fixed_implemented_in)
            return self._subsystem_from_fixed_implemented_in
        return None

    def get_sub_system(self) -> role.SubSystem:
        return self._subsystem_from_fixed_implemented_in if self._subsystem_from_fixed_implemented_in else self._current_owner_role

    def get_state_at_date(self, reference_date: datetime) -> State:

        if reference_date < self._submit_date:
            return State.NotCreatedYet

        elif self._closing_date and reference_date > self._closing_date:
            return State.Closed

        elif self._validation_date and reference_date > self._validation_date:
            return State.Validated

        elif self._verification_date and reference_date > self._verification_date:
            return State.Verified

        elif self._solution_date and reference_date > self._solution_date:
            return State.Resolved

        elif self._analysis_date and reference_date > self._analysis_date:
            return State.Analysed

        elif reference_date > self._submit_date:
            return State.Submitted
