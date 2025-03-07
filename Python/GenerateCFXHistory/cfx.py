from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Optional, List

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


@dataclass
class ChampFXLibrary:
    _champ_fx: list["ChampFXEntry"]

    def get_earliest_submit_date(self) -> datetime:
        earliest_date = min(entry._submit_date for entry in self._champ_fx)
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
        self.state: State = State[(row["State"])]
        self._submit_date: datetime = utils.convert_champfx_extract_date(row["SubmitDate"])
        self._analysis_date: datetime = utils.convert_champfx_extract_date(row["HistoryOfLastAction.AnalysisDate"])
        self._solution_date: datetime = utils.convert_champfx_extract_date(row["HistoryOfLastAction.SolutionDate"])
        self._verification_date: datetime = utils.convert_champfx_extract_date(row["HistoryOfLastAction.VerificationDate"])
        self._validation_date: datetime = utils.convert_champfx_extract_date(row["HistoryOfLastAction.ValidationDate"])
        self._closing_date: datetime = utils.convert_champfx_extract_date(row["HistoryOfLastAction.ClosingDate"])
        self.fixed_implemented_in: str = row["FixedImplementedIn"]
        self._current_owner: str = row["CurrentOwner.FullName"]
        self._current_owner_role: role.SubSystem = role.get_subsystem_from_cfx_current_owner(self._current_owner)
        # self._submit_year: datetime = self._submit_date.year
        # self._submit_month: datetime = self._submit_date.month

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
