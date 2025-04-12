import pandas as pd
import matplotlib.pyplot as plt
from collections import defaultdict
import mpld3
from mpld3 import plugins

from typing import List, Optional, Any, Dict, Set

import mplcursors
from mplcursors._mplcursors import HoverMode

import datetime


from logger import logger_config

import cfx
import role

state_colors = {
    cfx.State.Submitted: "red",
    cfx.State.Analysed: "orange",
    cfx.State.Assigned: "blue",
    cfx.State.Resolved: "yellow",
    cfx.State.Postponed: "grey",
    cfx.State.Rejected: "black",
    cfx.State.Verified: "lightgreen",
    cfx.State.Validated: "green",
    cfx.State.Closed: "darkgreen",
    # Add additional states and their respective colors
}


class OneTimestampResult:
    def __init__(self, all_results_to_display: "AllResultsToDisplay", timestamp: datetime.datetime):
        self._timestamp = timestamp
        self.count_by_state: dict[cfx.State, int] = defaultdict(int)
        self.all_results_to_display = all_results_to_display

    def add_one_result_for_state(self, state: cfx.State) -> None:
        self.count_by_state[state] += 1

    def is_empty(self) -> bool:
        return len(self.count_by_state) > 0

    def consolidate(self) -> None:
        all_states_found = list(self.count_by_state.keys())
        self.all_results_to_display.present_states.update(all_states_found)
        all_states_found_sorted = sorted(all_states_found)
        # self.compute_cumulated_count()

    def get_cumulated_count(self) -> dict[cfx.State, int]:
        pass


class AllResultsToDisplay:
    def __init__(self) -> None:
        self.timestamp_results: List[OneTimestampResult] = []
        self.present_states: Set[cfx.State] = set()


def produce_results_and_displays(
    cfx_library: cfx.ChampFXLibrary,
    output_excel_file: Optional[str],
    display_without_cumulative_eras: bool,
    display_with_cumulative_eras: bool,
    output_html_file_prefix: str,
    library_label: str,
    cfx_filter: Optional[cfx.ChampFxFilter] = None,
    filter_enforced_label: Optional[str] = None,
) -> None:
    # Retrieve months to process
    # months = cfx_library.get_months_since_earliest_submit_date()
    timestamps_to_display_data: List[datetime.datetime] = cfx_library.get_tenth_days_since_earliest_submit_date()
    timestamps_to_display_data_containing_data_with_filter: List[datetime.datetime] = []
    counts_by_state_per_month: List[dict[cfx.State, int]] = []

    all_results_to_display: AllResultsToDisplay = AllResultsToDisplay()

    at_least_one_cfx_matching_filter_has_been_found = False

    if filter_enforced_label is None:
        if cfx_filter:
            filter_enforced_label = cfx_filter.label
        else:
            filter_enforced_label = "All"

    # Gather state counts for each month
    for timestamp_to_display_data in timestamps_to_display_data:
        timestamp_results = OneTimestampResult(timestamp=timestamp_to_display_data, all_results_to_display=all_results_to_display)
        count_by_state: dict[cfx.State, int] = defaultdict(int)
        for entry in cfx_library.get_all_cfx():
            state = entry.get_state_at_date(timestamp_to_display_data)

            if cfx_filter is None or cfx_filter.match_cfx_entry(entry):

                if state != cfx.State.NotCreatedYet:
                    count_by_state[state] += 1
                    timestamp_results.add_one_result_for_state(state=state)
                    at_least_one_cfx_matching_filter_has_been_found = True

        if at_least_one_cfx_matching_filter_has_been_found:
            counts_by_state_per_month.append(count_by_state)
            timestamps_to_display_data_containing_data_with_filter.append(timestamp_to_display_data)

        timestamp_results.consolidate()

        if not timestamp_results.is_empty():
            all_results_to_display.timestamp_results.append(timestamp_results)

    # Determine the states that are present in the data
    present_states_set: Set[cfx.State] = set()
    for count_by_state in counts_by_state_per_month:
        present_states_set.update(count_by_state.keys())

    if len(present_states_set) == 0:
        logger_config.print_and_log_info(f"No data for library {library_label} filters {filter_enforced_label}")
        return

    present_states_ordered_list: List[cfx.State] = sorted(list(present_states_set))

    # Prepare cumulative counts for stacked area plot and Excel output
    cumulative_counts: Dict[cfx.State, List[int]] = {state: [] for state in present_states_ordered_list}
    for count_by_state in counts_by_state_per_month:
        for state in present_states_ordered_list:
            cumulative_counts[state].append(count_by_state[state])

    if output_excel_file:
        with logger_config.stopwatch_with_label(f"produce_excel_output_file, filter {filter_enforced_label} library {library_label}"):
            produce_excel_output_file(output_excel_file=output_excel_file, state_counts_per_month=counts_by_state_per_month, months=timestamps_to_display_data_containing_data_with_filter)

    if display_with_cumulative_eras:
        with logger_config.stopwatch_with_label(f"produce_displays cumulative, filter {filter_enforced_label} library {library_label}"):
            produce_displays(
                use_cumulative=True,
                months=timestamps_to_display_data_containing_data_with_filter,
                present_states_ordered_list=present_states_ordered_list,
                cumulative_counts=cumulative_counts,
                state_counts_per_month=counts_by_state_per_month,
                output_html_file_prefix=output_html_file_prefix + "_cumulative_eras_",
                window_title=f"{library_label} Filter {filter_enforced_label}, CFX States Over Time (Cumulative)",
                library_label=library_label,
                filter_enforced_label=filter_enforced_label,
            )
    if display_without_cumulative_eras:
        with logger_config.stopwatch_with_label(f"produce_displays numbers, filter {filter_enforced_label} library {library_label}"):
            produce_displays(
                use_cumulative=False,
                months=timestamps_to_display_data_containing_data_with_filter,
                present_states_ordered_list=present_states_ordered_list,
                cumulative_counts=cumulative_counts,
                state_counts_per_month=counts_by_state_per_month,
                output_html_file_prefix=output_html_file_prefix + "_values_",
                window_title=f"{library_label} Filter {filter_enforced_label}, CFX States Over Time (Values)",
                library_label=library_label,
                filter_enforced_label=filter_enforced_label,
            )


def produce_excel_output_file(output_excel_file: str, state_counts_per_month, months) -> None:
    # Convert data to DataFrame for Excel output
    data_for_excel = pd.DataFrame(state_counts_per_month, index=months)
    data_for_excel.index.name = "Month"

    # Save DataFrame to Excel
    with pd.ExcelWriter(output_excel_file) as writer:
        data_for_excel.to_excel(writer, sheet_name="CFX State Counts")


def produce_displays(
    use_cumulative: bool,
    months: list[datetime.datetime],
    present_states_ordered_list: set[cfx.State],
    cumulative_counts: Dict[cfx.State, List[int]],
    state_counts_per_month: List[dict[cfx.State, int]],
    output_html_file_prefix: str,
    window_title: str,
    library_label: str,
    filter_enforced_label: str,
) -> None:
    fig, ax = plt.subplots(figsize=(10, 6))

    # Set the window title
    fig.canvas.manager.set_window_title(window_title)

    # Plot
    if use_cumulative:
        # Plot cumulative areas
        bottom = [0] * len(months)
        for state in present_states_ordered_list:
            color = state_colors.get(state, None)
            upper = [bottom[i] + cumulative_counts[state][i] for i in range(len(months))]
            line = ax.fill_between(months, bottom, upper, label=state.name, color=color)
            mplcursors.cursor(line, hover=True)
            bottom = upper

    else:
        for state in present_states_ordered_list:
            color = state_colors.get(state, None)
            counts = [state_counts[state] for state_counts in state_counts_per_month]
            (line,) = ax.plot(months, counts, label=state.name, color=color)
            mplcursors.cursor(line, hover=HoverMode.Transient)

    ax.set_xlabel("Month")
    ax.set_ylabel("Number of CFX Entries")
    ax.set_title(f"{library_label} All CFX States Over Time" if filter_enforced_label is None else f"{library_label} {filter_enforced_label} CFX States Over Time")
    ax.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Save the plot to an HTML file
    html_content = mpld3.fig_to_html(fig)
    output_html_file = output_html_file_prefix + ".html"

    with logger_config.stopwatch_with_label(f"html {output_html_file} creation"):
        with open(output_html_file, "w", encoding="utf8") as html_file:
            html_file.write(html_content)


def produce_results_and_displays_for_libary(cfx_library: cfx.ChampFXLibrary, output_directory_name: str, library_label: str, for_global: bool, for_each_subsystem: bool) -> None:

    if for_global:
        produce_results_and_displays(
            cfx_library=cfx_library,
            output_excel_file=f"{output_directory_name}/{library_label}_global.xlsx",
            display_without_cumulative_eras=True,
            display_with_cumulative_eras=True,
            output_html_file_prefix=f"{output_directory_name}/{library_label}_global",
            library_label=library_label,
        )

    if for_each_subsystem:
        for subsystem in role.SubSystem:
            with logger_config.stopwatch_with_label(f"{library_label} produce_results_and_displays for {subsystem.name}"):
                produce_results_and_displays(
                    cfx_library=cfx_library,
                    # output_excel_file=f"{output_directory_name}/subsystem_{subsystem.name}.xlsx",
                    output_excel_file=None,
                    display_without_cumulative_eras=False,
                    display_with_cumulative_eras=True,
                    output_html_file_prefix=f"{output_directory_name}/{library_label}_subsystem_{subsystem.name}",
                    library_label=library_label,
                    cfx_filter=cfx.ChampFxFilter(field_filters=cfx.ChampFXFieldFilter(field_name="_subsystem", field_accepted_values=[subsystem])),
                )


def block_execution_and_keep_all_windows_open() -> None:
    """Use plt.show() here to block execution and keep all windows open"""
    plt.show()
