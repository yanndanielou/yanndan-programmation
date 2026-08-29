import datetime
from collections import defaultdict, OrderedDict
from typing import Dict, List, Set


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from generatecfxhistory.cfx import ChampFXEntry

from generatecfxhistory.constants import State


class OneTimestampResult:
    def __init__(self, all_results_to_display: "AllResultsPerDates", timestamp: datetime.datetime):
        self._timestamp = timestamp
        self.count_by_state: dict[State, int] = defaultdict(int)
        self.total_count: int = 0
        self.all_results_to_display = all_results_to_display

    def add_one_result_for_state(self, state: State) -> None:
        self.count_by_state[state] += 1
        self.total_count += 1

    @property
    def total_count_all_states(self) -> int:
        return sum(self.count_by_state.values())

    @property
    def percentage_by_state(self) -> dict[State, float]:
        ret: dict[State, float] = defaultdict(float)
        total_count_all_states = self.total_count_all_states
        for state, count in self.count_by_state.items():
            ret[state] = count / total_count_all_states * 100

        return ret

    def is_empty(self) -> bool:
        return len(self.count_by_state) > 0

    def consolidate_present_states(self) -> None:
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
        self.at_least_one_cfx_matching_filter_has_been_found = False

    def get_all_timestamps(self) -> List[datetime.datetime]:
        all_timestamps = [results.timestamp for results in self.timestamp_results]
        return all_timestamps

    def present_states_ordered(self) -> List[State]:
        return sorted(self.present_states)

    def get_state_counts_per_timestamp(self) -> List[dict[State, int]]:
        return [results.count_by_state for results in self.timestamp_results]

    def get_state_counts_per_timestamp_plus_total(self) -> list[dict[str, int | float]]:
        ret: list[dict[str, int | float]] = []
        for results in self.timestamp_results:
            count_by_state: dict[str, int | float] = OrderedDict()
            for state, count in results.count_by_state.items():
                count_by_state[state.name] = count
            count_by_state["Total"] = results.total_count
            ret.append(count_by_state)
        return ret

    def get_state_percentage_per_timestamp(self) -> List[dict[str, int | float]]:
        ret: list[dict[str, int | float]] = []
        for results in self.timestamp_results:
            count_by_state: dict[str, int | float] = OrderedDict()
            for state, count in results.count_by_state.items():
                count_by_state[state.name + " %"] = round(count / results.total_count * 100, 1) if results.total_count else 0
            ret.append(count_by_state)
        return ret

    def compute_cumulative_counts_number_of_state_per_date(self) -> None:
        self.cumulative_counts = {state: [] for state in self.present_states_ordered()}
        for one_timestamp in self.timestamp_results:
            for state in self.present_states_ordered():
                self.cumulative_counts[state].append(one_timestamp.count_by_state[state])


class AllResultsPerDatesWithDebugDetails(AllResultsPerDates):
    def __init__(self) -> None:
        super().__init__()
        self.all_cfx_that_have_matched: set["ChampFXEntry"] = set()

    def is_empty(self) -> bool:
        return not self.all_cfx_ids_that_have_matched
