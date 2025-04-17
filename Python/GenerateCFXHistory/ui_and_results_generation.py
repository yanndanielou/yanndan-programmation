import pandas as pd
import matplotlib.pyplot as plt
from collections import defaultdict
import mpld3
from mpld3 import plugins

from typing import List, Optional, Any, Dict, Set

import mplcursors
from mplcursors._mplcursors import HoverMode

from common import json_encoders, string_utils

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


class AllResultsToDisplay:
    def __init__(self) -> None:
        self.timestamp_results: List[OneTimestampResult] = []
        self.present_states: Set[cfx.State] = set()

        self.cumulative_counts: Dict[cfx.State, List[int]] = dict()

    def get_all_timestamps(self) -> List[datetime.datetime]:
        all_timestamps = [results._timestamp for results in self.timestamp_results]
        return all_timestamps

    def present_states_ordered(self) -> List[cfx.State]:
        return sorted(self.present_states)

    def get_state_counts_per_timestamp(self) -> List[dict[cfx.State, int]]:
        return [results.count_by_state for results in self.timestamp_results]

    def compute_cumulative_counts(self) -> None:
        self.cumulative_counts = {state: [] for state in self.present_states_ordered()}
        for one_timestamp in self.timestamp_results:
            for state in self.present_states_ordered():
                self.cumulative_counts[state].append(one_timestamp.count_by_state[state])


def produce_results_and_displays(
    cfx_library: cfx.ChampFXLibrary,
    output_directory_name: str,
    create_excel_file: bool,
    display_without_cumulative_eras: bool,
    display_with_cumulative_eras: bool,
    create_html_file: bool,
    library_label: str,
    cfx_filters: Optional[List[cfx.ChampFxFilter]] = None,
    filter_enforced_label: Optional[str] = None,
) -> None:

    if cfx_filters is None:
        cfx_filters = []

    timestamps_to_display_data: List[datetime.datetime] = cfx_library.get_tenth_days_since_earliest_submit_date()

    all_results_to_display: AllResultsToDisplay = AllResultsToDisplay()

    at_least_one_cfx_matching_filter_has_been_found = False

    if filter_enforced_label is None:
        if len(cfx_filters) > 0:
            filter_enforced_label = "".join([filter.label for filter in cfx_filters])
        else:
            filter_enforced_label = "All"

    all_cfx_ids_that_have_matched: set[str] = set()

    # Gather state counts for each month
    for timestamp_to_display_data in timestamps_to_display_data:
        timestamp_results = OneTimestampResult(timestamp=timestamp_to_display_data, all_results_to_display=all_results_to_display)
        count_by_state: dict[cfx.State, int] = defaultdict(int)
        for entry in cfx_library.get_all_cfx():
            state = entry.get_state_at_date(timestamp_to_display_data)

            match_all_filters = True if cfx_filters is None else all(cfx_filter.match_cfx_entry(entry, timestamp_to_display_data) for cfx_filter in cfx_filters)
            if match_all_filters:
                all_cfx_ids_that_have_matched.add(entry.cfx_id)

                if state != cfx.State.NotCreatedYet:
                    count_by_state[state] += 1
                    timestamp_results.add_one_result_for_state(state=state)
                    at_least_one_cfx_matching_filter_has_been_found = True

        if at_least_one_cfx_matching_filter_has_been_found:
            all_results_to_display.timestamp_results.append(timestamp_results)

        timestamp_results.consolidate()

    all_results_to_display.compute_cumulative_counts()

    filter_enforced_label_for_valid_file_name = string_utils.format_filename(filter_enforced_label)
    generic_output_files_path_without_suffix_and_extension = f"{output_directory_name}/{library_label} {filter_enforced_label_for_valid_file_name}"
    json_encoders.JsonEncodersUtils.serialize_list_objects_in_json(list_objects=all_cfx_ids_that_have_matched, json_file_full_path=f"{generic_output_files_path_without_suffix_and_extension}.json")

    if not at_least_one_cfx_matching_filter_has_been_found:
        logger_config.print_and_log_info(f"No data for library {library_label} filters {filter_enforced_label}")
        return

    if create_excel_file:

        with logger_config.stopwatch_with_label(f"produce_excel_output_file, filter {filter_enforced_label} library {library_label}"):
            produce_excel_output_file(output_excel_file=f"{generic_output_files_path_without_suffix_and_extension}.xlsx", all_results_to_display=all_results_to_display)

    if display_with_cumulative_eras:
        with logger_config.stopwatch_with_label(f"produce_displays cumulative, filter {filter_enforced_label} library {library_label}"):
            produce_displays_and_create_html(
                use_cumulative=True,
                all_results_to_display=all_results_to_display,
                output_html_file_prefix=f"{generic_output_files_path_without_suffix_and_extension}_cumulative_eras_" if create_html_file else None,
                window_title=f"{library_label} Filter {filter_enforced_label}, CFX States Over Time (Cumulative)",
                library_label=library_label,
                filter_enforced_label=filter_enforced_label,
            )
    if display_without_cumulative_eras:
        with logger_config.stopwatch_with_label(f"produce_displays numbers, filter {filter_enforced_label} library {library_label}"):
            produce_displays_and_create_html(
                use_cumulative=False,
                all_results_to_display=all_results_to_display,
                output_html_file_prefix=f"{generic_output_files_path_without_suffix_and_extension}_values_" if create_html_file else None,
                window_title=f"{library_label} Filter {filter_enforced_label}, CFX States Over Time (Values)",
                library_label=library_label,
                filter_enforced_label=filter_enforced_label,
            )


def produce_excel_output_file(output_excel_file: str, all_results_to_display: AllResultsToDisplay) -> None:
    # Convert data to DataFrame for Excel output

    data_for_excel = pd.DataFrame(all_results_to_display.get_state_counts_per_timestamp(), index=all_results_to_display.get_all_timestamps())
    data_for_excel.index.name = "Month"

    # Save DataFrame to Excel
    with pd.ExcelWriter(output_excel_file) as writer:
        data_for_excel.to_excel(writer, sheet_name="CFX State Counts")


def produce_displays_and_create_html(
    use_cumulative: bool,
    all_results_to_display: AllResultsToDisplay,
    output_html_file_prefix: str,
    window_title: str,
    library_label: str,
    filter_enforced_label: str,
) -> None:
    fig, ax = plt.subplots(figsize=(10, 6))

    # Set the window title
    fig.canvas.manager.set_window_title(window_title)

    all_timestamps = all_results_to_display.get_all_timestamps()

    # Plot
    if use_cumulative:
        # Plot cumulative areas
        bottom = [0] * len(all_timestamps)
        for state in all_results_to_display.present_states_ordered():
            color = state_colors.get(state, None)
            upper = [bottom[i] + all_results_to_display.cumulative_counts[state][i] for i in range(len(all_timestamps))]
            line = ax.fill_between(all_timestamps, bottom, upper, label=state.name, color=color)
            mplcursors.cursor(line, hover=True)
            bottom = upper

    else:
        for state in all_results_to_display.present_states_ordered():
            color = state_colors.get(state, None)
            counts = [state_counts[state] for state_counts in all_results_to_display.get_state_counts_per_timestamp()]
            (line,) = ax.plot(all_timestamps, counts, label=state.name, color=color)
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


def produce_results_and_displays_for_libary(
    cfx_library: cfx.ChampFXLibrary,
    output_directory_name: str,
    library_label: str,
    for_global: bool,
    for_each_subsystem: bool,
    for_each_current_owner_per_date: bool,
    cfx_filters: Optional[List[cfx.ChampFxFilter]] = None,
) -> None:

    if cfx_filters is None:
        cfx_filters = []

    if for_global:
        produce_results_and_displays(
            cfx_library=cfx_library,
            output_directory_name=output_directory_name,
            create_excel_file=True,
            display_without_cumulative_eras=True,
            display_with_cumulative_eras=True,
            create_html_file=True,
            library_label=library_label,
            cfx_filters=cfx_filters,
            filter_enforced_label="All",
        )

    if for_each_current_owner_per_date:
        for subsystem in role.SubSystem:
            with logger_config.stopwatch_with_label(f"{library_label} produce_results_and_displays for {subsystem.name}"):
                produce_results_and_displays(
                    cfx_library=cfx_library,
                    output_directory_name=output_directory_name,
                    # output_excel_file=f"{output_directory_name}/subsystem_{subsystem.name}.xlsx",
                    create_excel_file=False,
                    display_without_cumulative_eras=False,
                    display_with_cumulative_eras=True,
                    create_html_file=True,
                    library_label=library_label,
                    cfx_filters=cfx_filters + [cfx.ChampFxFilter(role_depending_on_date_filter=cfx.ChampFXRoleDependingOnDateFilter(roles_at_date_allowed=[subsystem]))],
                )

    if for_each_subsystem:
        for subsystem in role.SubSystem:
            with logger_config.stopwatch_with_label(f"{library_label} produce_results_and_displays for {subsystem.name}"):

                produce_results_and_displays(
                    cfx_library=cfx_library,
                    output_directory_name=output_directory_name,
                    # output_excel_file=f"{output_directory_name}/subsystem_{subsystem.name}.xlsx",
                    create_excel_file=False,
                    display_without_cumulative_eras=False,
                    display_with_cumulative_eras=True,
                    create_html_file=True,
                    library_label=library_label,
                    cfx_filters=cfx_filters + [cfx.ChampFxFilter(field_filters=[cfx.ChampFXFieldFilter(field_name="_subsystem", field_accepted_values=[subsystem])])],
                )


def block_execution_and_keep_all_windows_open() -> None:
    """Use plt.show() here to block execution and keep all windows open"""
    plt.show()
