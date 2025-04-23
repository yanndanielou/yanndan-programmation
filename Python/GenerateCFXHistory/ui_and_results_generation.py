import datetime
from collections import defaultdict
from datetime import datetime, timedelta
from enum import auto
from typing import Any, Dict, List, Optional, Set

import matplotlib.pyplot as plt
import mplcursors
import mpld3
import pandas as pd
from common import enums_utils, json_encoders, string_utils
from logger import logger_config
from mplcursors._mplcursors import HoverMode
from mpld3 import plugins
from dateutil import relativedelta


import cfx
import role

state_colors = {
    cfx.State.SUBMITTED: "red",
    cfx.State.ANALYSED: "orange",
    cfx.State.ASSIGNED: "blue",
    cfx.State.RESOLVED: "yellow",
    cfx.State.POSTPONED: "grey",
    cfx.State.REJECTED: "black",
    cfx.State.VERIFIED: "lightgreen",
    cfx.State.VALIDATED: "green",
    cfx.State.CLOSED: "darkgreen",
    # Add additional states and their respective colors
}


class RepresentationType(enums_utils.NameBasedEnum):
    VALUE = auto()
    CUMULATIVE_ERAS = auto()


class OneTimestampResult:
    def __init__(self, all_results_to_display: "AllResultsToDisplay", timestamp: datetime):
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


class AllResultsToDisplay:
    def __init__(self) -> None:
        self.timestamp_results: List[OneTimestampResult] = []
        self.present_states: Set[cfx.State] = set()

        self.cumulative_counts: Dict[cfx.State, List[int]] = dict()
        self.all_cfx_ids_that_have_matched: set[str] = set()
        self.at_least_one_cfx_matching_filter_has_been_found = False

    def get_all_timestamps(self) -> List[datetime]:
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


def gather_state_counts_for_each_date(cfx_library: cfx.ChampFXLibrary, time_delta: relativedelta, cfx_filters: Optional[List[cfx.ChampFxFilter]] = None) -> AllResultsToDisplay:

    all_results_to_display: AllResultsToDisplay = AllResultsToDisplay()
    timestamps_to_display_data: List[datetime] = cfx_library.get_dates_since_earliest_submit_date(time_delta)

    for timestamp_to_display_data in timestamps_to_display_data:
        timestamp_results = OneTimestampResult(timestamp=timestamp_to_display_data, all_results_to_display=all_results_to_display)
        count_by_state: dict[cfx.State, int] = defaultdict(int)
        for entry in cfx_library.get_all_cfx():
            state = entry.get_state_at_date(timestamp_to_display_data)

            match_all_filters = True if cfx_filters is None else all(cfx_filter.match_cfx_entry(entry, timestamp_to_display_data) for cfx_filter in cfx_filters)
            if match_all_filters:
                all_results_to_display.all_cfx_ids_that_have_matched.add(entry.cfx_id)

                if state != cfx.State.NOT_CREATED_YET:
                    count_by_state[state] += 1
                    timestamp_results.add_one_result_for_state(state=state)
                    all_results_to_display.at_least_one_cfx_matching_filter_has_been_found = True

        if all_results_to_display.at_least_one_cfx_matching_filter_has_been_found:
            all_results_to_display.timestamp_results.append(timestamp_results)

        with logger_config.stopwatch_alert_if_exceeds_duration("consolidate", duration_threshold_to_alert_info_in_s=0.1):
            timestamp_results.consolidate()

    return all_results_to_display


def produce_results_and_displays(
    cfx_library: cfx.ChampFXLibrary,
    output_directory_name: str,
    create_excel_file: bool,
    display_without_cumulative_eras: bool,
    display_with_cumulative_eras: bool,
    create_html_file: bool,
    time_delta: relativedelta,
    cfx_filters: Optional[List[cfx.ChampFxFilter]] = None,
    dump_all_cfx_ids_in_json: bool = False,
) -> None:

    if cfx_filters is None:
        cfx_filters = []

    generation_label = cfx_library.label
    if len(cfx_filters) > 0:
        generation_label += "".join([filter.label for filter in cfx_filters])
    else:
        generation_label += "All"

    with logger_config.stopwatch_with_label(f"{generation_label} Gather state counts for each date"):
        all_results_to_display: AllResultsToDisplay = gather_state_counts_for_each_date(cfx_library=cfx_library, time_delta=time_delta, cfx_filters=cfx_filters)

    with logger_config.stopwatch_alert_if_exceeds_duration("compute_cumulative_counts", duration_threshold_to_alert_info_in_s=0.1):
        all_results_to_display.compute_cumulative_counts()

    generation_label_for_valid_file_name = string_utils.format_filename(generation_label)
    generic_output_files_path_without_suffix_and_extension = f"{output_directory_name}/{generation_label_for_valid_file_name}"

    if dump_all_cfx_ids_in_json:
        json_encoders.JsonEncodersUtils.serialize_list_objects_in_json(
            list_objects=all_results_to_display.all_cfx_ids_that_have_matched, json_file_full_path=f"{generic_output_files_path_without_suffix_and_extension}.json"
        )

    if not all_results_to_display.at_least_one_cfx_matching_filter_has_been_found:
        logger_config.print_and_log_info(f"No data for {generation_label}")
        return

    if create_excel_file:

        with logger_config.stopwatch_with_label(f"produce_excel_output_file,  {generation_label}"):
            produce_excel_output_file(output_excel_file=f"{generic_output_files_path_without_suffix_and_extension}.xlsx", all_results_to_display=all_results_to_display)

    if display_with_cumulative_eras:
        with logger_config.stopwatch_with_label(f"produce_displays cumulative,  {generation_label}"):
            produce_displays_and_create_html(
                output_directory_name=output_directory_name,
                cfx_library=cfx_library,
                use_cumulative=True,
                all_results_to_display=all_results_to_display,
                create_html_file=create_html_file,
                window_title=f"Filter {generation_label}, CFX States Over Time (Cumulative)",
                generation_label=generation_label,
                generation_label_for_valid_file_name=generation_label_for_valid_file_name,
            )
    if display_without_cumulative_eras:
        with logger_config.stopwatch_with_label(f"produce_displays numbers, filter {generation_label} library {cfx_library.label}"):
            produce_displays_and_create_html(
                output_directory_name=output_directory_name,
                cfx_library=cfx_library,
                use_cumulative=False,
                all_results_to_display=all_results_to_display,
                create_html_file=create_html_file,
                window_title=f"Filter {generation_label}, CFX States Over Time (Values)",
                generation_label=generation_label,
                generation_label_for_valid_file_name=generation_label_for_valid_file_name,
            )


def produce_excel_output_file(output_excel_file: str, all_results_to_display: AllResultsToDisplay) -> None:
    # Convert data to DataFrame for Excel output

    data_for_excel = pd.DataFrame(all_results_to_display.get_state_counts_per_timestamp(), index=all_results_to_display.get_all_timestamps())
    data_for_excel.index.name = "Month"

    # Save DataFrame to Excel
    with pd.ExcelWriter(output_excel_file) as writer:
        data_for_excel.to_excel(writer, sheet_name="CFX State Counts")


def produce_displays_and_create_html(
    cfx_library: cfx.ChampFXLibrary,
    use_cumulative: bool,
    all_results_to_display: AllResultsToDisplay,
    create_html_file: bool,
    window_title: str,
    generation_label: str,
    generation_label_for_valid_file_name: str,
    output_directory_name: str,
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
    ax.set_title(f"{generation_label} CFX States Over Time")
    ax.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show(block=False)

    if create_html_file:
        # Save the plot to an HTML file
        html_content = mpld3.fig_to_html(fig)
        output_html_file = output_directory_name + "/" + generation_label_for_valid_file_name + ".html"

        with logger_config.stopwatch_with_label(f"html {output_html_file} creation"):
            with open(output_html_file, "w", encoding="utf8") as html_file:
                html_file.write(html_content)


def produce_results_and_displays_for_libary(
    cfx_library: cfx.ChampFXLibrary,
    output_directory_name: str,
    for_global: bool,
    for_each_subsystem: bool,
    for_each_current_owner_per_date: bool,
    time_delta: relativedelta = relativedelta.relativedelta(days=10),
    cfx_filters: Optional[List[cfx.ChampFxFilter]] = None,
    create_html_file: bool = True,
    create_excel_file: bool = True,
) -> None:

    if cfx_filters is None:
        cfx_filters = []

    if for_global:
        produce_results_and_displays(
            cfx_library=cfx_library,
            output_directory_name=output_directory_name,
            create_excel_file=create_excel_file,
            time_delta=time_delta,
            display_without_cumulative_eras=True,
            display_with_cumulative_eras=True,
            create_html_file=create_html_file,
            cfx_filters=cfx_filters,
        )

    if for_each_current_owner_per_date:
        for subsystem in role.SubSystem:
            with logger_config.stopwatch_with_label(f"{cfx_library.label} produce_results_and_displays for {subsystem.name}"):
                produce_results_and_displays(
                    cfx_library=cfx_library,
                    output_directory_name=output_directory_name,
                    # output_excel_file=f"{output_directory_name}/subsystem_{subsystem.name}.xlsx",
                    create_excel_file=create_excel_file,
                    time_delta=time_delta,
                    display_without_cumulative_eras=False,
                    display_with_cumulative_eras=True,
                    create_html_file=create_html_file,
                    cfx_filters=cfx_filters + [cfx.ChampFxFilter(role_depending_on_date_filter=cfx.ChampFXRoleDependingOnDateFilter(roles_at_date_allowed=[subsystem]))],
                )

    if for_each_subsystem:
        for subsystem in role.SubSystem:
            with logger_config.stopwatch_with_label(f"{cfx_library.label} produce_results_and_displays for {subsystem.name}"):

                produce_results_and_displays(
                    cfx_library=cfx_library,
                    output_directory_name=output_directory_name,
                    # output_excel_file=f"{output_directory_name}/subsystem_{subsystem.name}.xlsx",
                    create_excel_file=create_excel_file,
                    time_delta=time_delta,
                    display_without_cumulative_eras=False,
                    display_with_cumulative_eras=True,
                    create_html_file=create_html_file,
                    cfx_filters=cfx_filters + [cfx.ChampFxFilter(field_filters=[cfx.ChampFXFieldFilter(field_name="_subsystem", field_accepted_values=[subsystem])])],
                )


def block_execution_and_keep_all_windows_open() -> None:
    """Use plt.show() here to block execution and keep all windows open"""
    plt.show()
