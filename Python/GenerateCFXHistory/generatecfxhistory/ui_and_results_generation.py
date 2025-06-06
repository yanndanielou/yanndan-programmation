import datetime
from enum import auto, Enum
from typing import List, Optional

import matplotlib.pyplot as plt
import mplcursors
import mpld3
import pandas as pd
from common import enums_utils, json_encoders, string_utils
from logger import logger_config
from mplcursors._mplcursors import HoverMode

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


class GenerateByProjectInstruction(Enum):
    ONLY_ATP = auto()
    ONLY_NEXTEO = auto()
    GLOBAL_ALL_PROJECTS = auto()
    BY_PROJECT_AND_ALSO_GLOBAL_ALL_PROJECTS = auto()


class RepresentationType(enums_utils.NameBasedEnum):
    VALUE = auto()
    CUMULATIVE_ERAS = auto()


def produce_results_and_displays(
    cfx_library: cfx.ChampFXLibrary,
    output_directory_name: str,
    create_excel_file: bool,
    display_without_cumulative_eras: bool,
    display_with_cumulative_eras: bool,
    create_html_file: bool,
    cfx_filters: Optional[List[cfx.ChampFxFilter]] = None,
    dump_all_cfx_ids_in_json: bool = True,
    generate_by_project_instruction: GenerateByProjectInstruction = GenerateByProjectInstruction.GLOBAL_ALL_PROJECTS,
) -> None:

    if cfx_filters is None:
        cfx_filters = []
    else:
        cfx_filters = cfx_filters.copy()

    match generate_by_project_instruction:
        case GenerateByProjectInstruction.ONLY_ATP:
            cfx_filters.append(cfx.ChampFxFilter(field_filters=[cfx.ChampFxFilterFieldProject(field_accepted_values=[cfx.CfxProject.ATSP])]))
        case GenerateByProjectInstruction.ONLY_NEXTEO:
            cfx_filters.append(cfx.ChampFxFilter(field_filters=[cfx.ChampFxFilterFieldProject(field_accepted_values=[cfx.CfxProject.FR_NEXTEO])]))
        case GenerateByProjectInstruction.GLOBAL_ALL_PROJECTS:
            pass
        case GenerateByProjectInstruction.BY_PROJECT_AND_ALSO_GLOBAL_ALL_PROJECTS:
            produce_results_and_displays(
                cfx_library=cfx_library,
                output_directory_name=output_directory_name,
                create_excel_file=create_excel_file,
                display_without_cumulative_eras=display_without_cumulative_eras,
                display_with_cumulative_eras=display_with_cumulative_eras,
                create_html_file=create_html_file,
                cfx_filters=cfx_filters,
                dump_all_cfx_ids_in_json=dump_all_cfx_ids_in_json,
                generate_by_project_instruction=GenerateByProjectInstruction.ONLY_ATP,
            )

            produce_results_and_displays(
                cfx_library=cfx_library,
                output_directory_name=output_directory_name,
                create_excel_file=create_excel_file,
                display_without_cumulative_eras=display_without_cumulative_eras,
                display_with_cumulative_eras=display_with_cumulative_eras,
                create_html_file=create_html_file,
                cfx_filters=cfx_filters,
                dump_all_cfx_ids_in_json=dump_all_cfx_ids_in_json,
                generate_by_project_instruction=GenerateByProjectInstruction.ONLY_NEXTEO,
            )

            produce_results_and_displays(
                cfx_library=cfx_library,
                output_directory_name=output_directory_name,
                create_excel_file=create_excel_file,
                display_without_cumulative_eras=display_without_cumulative_eras,
                display_with_cumulative_eras=display_with_cumulative_eras,
                create_html_file=create_html_file,
                cfx_filters=cfx_filters,
                dump_all_cfx_ids_in_json=dump_all_cfx_ids_in_json,
                generate_by_project_instruction=GenerateByProjectInstruction.GLOBAL_ALL_PROJECTS,
            )
            return

    generation_label = cfx_library.label
    if len(cfx_filters) > 0:
        generation_label += "".join([filt.label for filt in cfx_filters])
    else:
        generation_label += "All"

    with logger_config.stopwatch_with_label(f"{generation_label} Gather state counts for each date"):
        all_results_to_display: cfx.AllResultsPerDates = cfx_library.gather_state_counts_for_each_date(cfx_filters=cfx_filters, dates_generator=cfx.DecreasingIntervalDatesGenerator())

    with logger_config.stopwatch_alert_if_exceeds_duration("compute_cumulative_counts", duration_threshold_to_alert_info_in_s=0.1):
        all_results_to_display.compute_cumulative_counts()

    generation_label_for_valid_file_name = string_utils.format_filename(generation_label)
    generic_output_files_path_without_suffix_and_extension = f"{output_directory_name}/{generation_label_for_valid_file_name}"

    if dump_all_cfx_ids_in_json:
        all_cfx_that_have_match_id_and_state = [
            (champfx_entry.cfx_id, champfx_entry._state.name, champfx_entry._current_owner.full_name, champfx_entry._request_type.name, champfx_entry._category.name, champfx_entry._cfx_project.name)
            for champfx_entry in all_results_to_display.all_cfx_that_have_matched
        ]

        json_encoders.JsonEncodersUtils.serialize_list_objects_in_json(
            list_objects=list(all_cfx_that_have_match_id_and_state), json_file_full_path=f"{generic_output_files_path_without_suffix_and_extension}.json"
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
                use_cumulative=False,
                all_results_to_display=all_results_to_display,
                create_html_file=create_html_file,
                window_title=f"Filter {generation_label}, CFX States Over Time (Values)",
                generation_label=generation_label,
                generation_label_for_valid_file_name=generation_label_for_valid_file_name,
            )


def produce_excel_output_file(output_excel_file: str, all_results_to_display: cfx.AllResultsPerDates) -> None:
    # Convert data to DataFrame for Excel output

    state_counts_per_timestamp: List[dict[cfx.State, int]] = all_results_to_display.get_state_counts_per_timestamp()
    all_timestamps: List[datetime.datetime] = all_results_to_display.get_all_timestamps()

    # Convert state enumerations to their names for DataFrame columns
    converted_data = [{state.name: count for state, count in state_dict.items()} for state_dict in state_counts_per_timestamp]
    data_for_excel = pd.DataFrame(converted_data, index=all_timestamps)
    data_for_excel.index.name = "Date"

    # Save DataFrame to Excel
    with pd.ExcelWriter(output_excel_file) as writer:
        data_for_excel.to_excel(writer, sheet_name="CFX State Counts")


def produce_displays_and_create_html(
    use_cumulative: bool,
    all_results_to_display: cfx.AllResultsPerDates,
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
        output_html_file = output_directory_name + "/" + generation_label_for_valid_file_name + " cumulative " + str(use_cumulative) + ".html"

        with logger_config.stopwatch_with_label(f"html {output_html_file} creation"):
            html_content = mpld3.fig_to_html(fig)
            with open(output_html_file, "w", encoding="utf8") as html_file:
                html_file.write(html_content)


def produce_results_and_displays_for_libary(
    cfx_library: cfx.ChampFXLibrary,
    output_directory_name: str,
    for_global: bool,
    for_each_subsystem: bool,
    for_each_current_owner_per_date: bool,
    generate_by_project_instruction: GenerateByProjectInstruction = GenerateByProjectInstruction.GLOBAL_ALL_PROJECTS,
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
            display_without_cumulative_eras=True,
            display_with_cumulative_eras=True,
            create_html_file=create_html_file,
            cfx_filters=cfx_filters,
            generate_by_project_instruction=generate_by_project_instruction,
        )

    if for_each_current_owner_per_date:
        for subsystem in role.SubSystem:
            with logger_config.stopwatch_with_label(f"{cfx_library.label} produce_results_and_displays for {subsystem.name}"):
                produce_results_and_displays(
                    cfx_library=cfx_library,
                    output_directory_name=output_directory_name,
                    # output_excel_file=f"{output_directory_name}/subsystem_{subsystem.name}.xlsx",
                    create_excel_file=create_excel_file,
                    display_without_cumulative_eras=False,
                    display_with_cumulative_eras=True,
                    create_html_file=create_html_file,
                    cfx_filters=cfx_filters + [cfx.ChampFxFilter(role_depending_on_date_filter=cfx.ChampFXRoleDependingOnDateFilter(roles_at_date_allowed=[subsystem]))],
                    generate_by_project_instruction=generate_by_project_instruction,
                )

    if for_each_subsystem:
        for subsystem in role.SubSystem:
            with logger_config.stopwatch_with_label(f"{cfx_library.label} produce_results_and_displays for {subsystem.name}"):

                produce_results_and_displays(
                    cfx_library=cfx_library,
                    output_directory_name=output_directory_name,
                    # output_excel_file=f"{output_directory_name}/subsystem_{subsystem.name}.xlsx",
                    create_excel_file=create_excel_file,
                    display_without_cumulative_eras=False,
                    display_with_cumulative_eras=True,
                    create_html_file=create_html_file,
                    cfx_filters=cfx_filters + [cfx.ChampFxFilter(field_filters=[cfx.ChampFxFilterFieldSubsystem(field_accepted_values=[subsystem])])],
                    generate_by_project_instruction=generate_by_project_instruction,
                )


def block_execution_and_keep_all_windows_open() -> None:
    """Use plt.show() here to block execution and keep all windows open"""
    plt.show()
