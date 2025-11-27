import copy
import datetime
import os
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Optional, cast, Dict

import matplotlib.pyplot as plt
import mplcursors
import mpld3
import pandas as pd
import psutil
from common import enums_utils, json_encoders, string_utils
from logger import logger_config
from mplcursors._mplcursors import HoverMode

from generatecfxhistory.cfx import ChampFXLibrary
from generatecfxhistory.constants import State
from generatecfxhistory.dates_generators import (
    DatesGenerator,
    DecreasingIntervalDatesGenerator,
)
from generatecfxhistory.filters import ChampFxFilter, ChampFxFilterFieldProject, ChampFxFilterFieldSubsystem, ChampFXRoleDependingOnDateFilter, ChampFXtStaticCriteriaFilter
from generatecfxhistory.results import (
    AllResultsPerDates,
    AllResultsPerDatesWithDebugDetails,
)
from generatecfxhistory.role import SubSystem

state_colors = {
    State.SUBMITTED: "red",
    State.UNKNOWN: "purple",
    State.ANALYSED: "orange",
    State.ASSIGNED: "blue",
    State.RESOLVED: "yellow",
    State.POSTPONED: "grey",
    State.REJECTED: "black",
    State.VERIFIED: "lightgreen",
    State.VALIDATED: "green",
    State.CLOSED: "darkgreen",
    # Add additional states and their respective colors
}


class GenerateByProjectInstruction(Enum):
    GLOBAL_ALL_PROJECTS = auto()
    BY_PROJECT_AND_ALSO_GLOBAL_ALL_PROJECTS = auto()
    BY_PROJECT = auto()
    ONLY_ONE_PROJECT = auto()


class RepresentationType(enums_utils.NameBasedEnum):
    VALUE = auto()
    CUMULATIVE_ERAS = auto()


@dataclass
class GenerationInstructions:
    output_directory_name: str
    create_html_file: bool = True
    display_output_plots: bool = True
    create_screenshot: bool = True


@dataclass
class NumberOfCfxStatePerDateGenerationInstructions(GenerationInstructions):
    cfx_filters: List[ChampFxFilter] = field(default_factory=list)
    create_excel_file: bool = True
    dump_all_cfx_ids_in_json: bool = True
    dates_generator: DatesGenerator = DecreasingIntervalDatesGenerator()
    generate_by_project_instruction: GenerateByProjectInstruction = GenerateByProjectInstruction.GLOBAL_ALL_PROJECTS
    project_in_case_of_generate_by_project_instruction_one_project: Optional[str] = None


@dataclass
class NumberOfCfxStatePerDateGenerationInstructionsForLibrary(NumberOfCfxStatePerDateGenerationInstructions):
    for_global: bool = True
    for_each_subsystem: bool = False
    for_each_current_owner_per_date: bool = False


@dataclass
class NumberOfCfxByCriteriaGenerationInstructionsForLibrary(GenerationInstructions):
    static_criteria_filters: List[ChampFXtStaticCriteriaFilter] = field(default_factory=list)
    by_subsystem: bool = False
    by_current_owner_role: bool = False
    for_global: bool = False
    states_to_take_into_account_black_list: Optional[List[State]] = None
    states_to_take_into_account_white_list: Optional[List[State]] = None


def produce_line_graphs_number_of_cfx_by_state_per_date_line_graphs(
    cfx_library: ChampFXLibrary,
    generation_instructions: NumberOfCfxStatePerDateGenerationInstructions,
    display_without_cumulative_eras: bool,
    display_with_cumulative_eras: bool,
) -> None:

    generation_instructions.cfx_filters = generation_instructions.cfx_filters.copy()
    match generation_instructions.generate_by_project_instruction:
        case GenerateByProjectInstruction.ONLY_ONE_PROJECT:
            generation_instructions.cfx_filters.append(
                ChampFxFilter(field_filters=[ChampFxFilterFieldProject(field_accepted_values=[cast(str, generation_instructions.project_in_case_of_generate_by_project_instruction_one_project)])])
            )
        case GenerateByProjectInstruction.GLOBAL_ALL_PROJECTS:
            pass
        case GenerateByProjectInstruction.BY_PROJECT:
            for project in sorted(cfx_library._all_projects):
                generation_instructions_copy = copy.deepcopy(generation_instructions)
                generation_instructions_copy.generate_by_project_instruction = GenerateByProjectInstruction.ONLY_ONE_PROJECT
                generation_instructions_copy.project_in_case_of_generate_by_project_instruction_one_project = project

                produce_line_graphs_number_of_cfx_by_state_per_date_line_graphs(
                    cfx_library=cfx_library,
                    generation_instructions=generation_instructions_copy,
                    display_without_cumulative_eras=display_without_cumulative_eras,
                    display_with_cumulative_eras=display_with_cumulative_eras,
                )

            return
        case GenerateByProjectInstruction.BY_PROJECT_AND_ALSO_GLOBAL_ALL_PROJECTS:

            generation_instructions_copy = copy.deepcopy(generation_instructions)
            generation_instructions_copy.generate_by_project_instruction = GenerateByProjectInstruction.GLOBAL_ALL_PROJECTS
            produce_line_graphs_number_of_cfx_by_state_per_date_line_graphs(
                cfx_library=cfx_library,
                generation_instructions=generation_instructions_copy,
                display_without_cumulative_eras=display_without_cumulative_eras,
                display_with_cumulative_eras=display_with_cumulative_eras,
            )

            generation_instructions_copy = copy.deepcopy(generation_instructions)
            generation_instructions_copy.generate_by_project_instruction = GenerateByProjectInstruction.BY_PROJECT
            produce_line_graphs_number_of_cfx_by_state_per_date_line_graphs(
                cfx_library=cfx_library,
                generation_instructions=generation_instructions_copy,
                display_without_cumulative_eras=display_without_cumulative_eras,
                display_with_cumulative_eras=display_with_cumulative_eras,
            )

            return

    generation_label = cfx_library.label
    if len(generation_instructions.cfx_filters) > 0:
        generation_label += "".join([filt.label for filt in generation_instructions.cfx_filters])
    else:
        generation_label += "All"

    with logger_config.stopwatch_with_label(label=f"{generation_label} Gather state counts for each date", inform_beginning=True):
        all_results_to_display: AllResultsPerDatesWithDebugDetails = cfx_library.gather_state_counts_for_each_date(
            cfx_filters=generation_instructions.cfx_filters, dates_generator=generation_instructions.dates_generator
        )

    with logger_config.stopwatch_alert_if_exceeds_duration("compute_cumulative_counts", duration_threshold_to_alert_info_in_s=0.1):
        all_results_to_display.compute_cumulative_counts_number_of_state_per_date()

    generation_label_for_valid_file_name = string_utils.format_filename(generation_label).lstrip()
    generic_output_files_path_without_suffix_and_extension = f"{generation_instructions.output_directory_name}/{generation_label_for_valid_file_name}"

    if generation_instructions.dump_all_cfx_ids_in_json:
        all_cfx_that_have_match_id_and_state = [
            (
                champfx_entry.cfx_identifier,
                champfx_entry._state.name,
                champfx_entry._current_owner.full_name,
                champfx_entry._request_type.name if champfx_entry._request_type else "unknown request type",
                champfx_entry._category.name if champfx_entry._category else "unknown category",
                champfx_entry._cfx_project_name,
            )
            for champfx_entry in all_results_to_display.all_cfx_that_have_matched
        ]

        json_encoders.JsonEncodersUtils.serialize_list_objects_in_json(
            list_objects=list(all_cfx_that_have_match_id_and_state), json_file_full_path=f"{generic_output_files_path_without_suffix_and_extension}.json"
        )

    if not all_results_to_display.at_least_one_cfx_matching_filter_has_been_found:
        logger_config.print_and_log_info(f"No data for {generation_label}")
        return

    if generation_instructions.create_excel_file:
        with logger_config.stopwatch_with_label(label=f"produce_excel_output_file,  {generation_label}", inform_beginning=True):
            produce_excel_output_file_results_number_of_cfx_by_state_per_date(
                output_excel_file=f"{generic_output_files_path_without_suffix_and_extension}.xlsx", all_results_to_display=all_results_to_display
            )

    if display_with_cumulative_eras:
        with logger_config.stopwatch_with_label(label=f"produce_displays cumulative,  {generation_label}", inform_beginning=True, monitor_ram_usage=True):
            produce_displays_and_create_html_number_of_cfx_by_state_per_date(
                generation_instructions=generation_instructions,
                use_cumulative=True,
                all_results_to_display=all_results_to_display,
                window_title=f"Filter {generation_label}, CFX States Over Time (Cumulative)",
                generation_label=generation_label,
                generation_label_for_valid_file_name=generation_label_for_valid_file_name,
            )
    if display_without_cumulative_eras:
        with logger_config.stopwatch_with_label(label=f"produce_displays numbers, filter {generation_label} library {cfx_library.label}", inform_beginning=True, monitor_ram_usage=True):
            produce_displays_and_create_html_number_of_cfx_by_state_per_date(
                generation_instructions=generation_instructions,
                use_cumulative=False,
                all_results_to_display=all_results_to_display,
                window_title=f"Filter {generation_label}, CFX States Over Time (Values)",
                generation_label=generation_label,
                generation_label_for_valid_file_name=generation_label_for_valid_file_name,
            )


def produce_excel_output_file_results_number_of_cfx_by_state_per_date(output_excel_file: str, all_results_to_display: AllResultsPerDatesWithDebugDetails) -> None:
    # Convert data to DataFrame for Excel output

    state_counts_per_timestamp: List[Dict[State, int]] = all_results_to_display.get_state_counts_per_timestamp()
    all_timestamps: List[datetime.datetime] = all_results_to_display.get_all_timestamps()

    # Convert state enumerations to their names for DataFrame columns
    converted_data = [{state.name: count for state, count in state_dict.items()} for state_dict in state_counts_per_timestamp]
    data_for_excel = pd.DataFrame(converted_data, index=all_timestamps)
    data_for_excel.index.name = "Date"

    # Save DataFrame to Excel
    with pd.ExcelWriter(output_excel_file) as writer:
        data_for_excel.to_excel(writer, sheet_name="CFX State Counts")


def produce_displays_and_create_html_number_of_cfx_by_state_per_date(
    generation_instructions: NumberOfCfxStatePerDateGenerationInstructions,
    use_cumulative: bool,
    all_results_to_display: AllResultsPerDates,
    window_title: str,
    generation_label: str,
    generation_label_for_valid_file_name: str,
) -> None:
    before_plots_computation_ram_rss = cast(int, psutil.Process(os.getpid()).memory_info().rss)

    # Create a figure and axis
    fig, ax = plt.subplots(figsize=(10, 6))

    # Set the window title
    assert fig.canvas.manager
    fig.canvas.manager.set_window_title(window_title)

    # Retrieve all timestamps
    all_timestamps = all_results_to_display.get_all_timestamps()

    # Store cursor objects for cleanup
    cursors: List[mplcursors.Cursor] = []

    # Plot data
    if use_cumulative:
        bottom = [0] * len(all_timestamps)
        for state in all_results_to_display.present_states_ordered():
            color = state_colors.get(state, None)
            upper = [bottom[i] + all_results_to_display.cumulative_counts[state][i] for i in range(len(all_timestamps))]
            line = ax.fill_between(all_timestamps, bottom, upper, label=state.name, color=color)
            cursor = mplcursors.cursor(line, hover=True)
            cursors.append(cursor)
            bottom = upper
    else:
        for state in all_results_to_display.present_states_ordered():
            color = state_colors.get(state, None)
            counts = [state_counts[state] for state_counts in all_results_to_display.get_state_counts_per_timestamp()]
            (line,) = ax.plot(all_timestamps, counts, label=state.name, color=color)
            cursor = mplcursors.cursor(line, hover=HoverMode.Transient)
            cursors.append(cursor)

    # Set axis labels and title
    ax.set_xlabel("Month")
    ax.set_ylabel("Number of CFX Entries")
    ax.set_title(f"{generation_label} CFX States Over Time")
    ax.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Display plot if required
    if generation_instructions.display_output_plots:
        plt.show(block=False)

    # Generate and save HTML file if required
    if generation_instructions.create_html_file:
        output_html_file = generation_instructions.output_directory_name + "/" + generation_label_for_valid_file_name + " cumulative " + str(use_cumulative) + ".html"

        with logger_config.stopwatch_with_label(label=f"html {output_html_file} creation", inform_beginning=True):
            html_content = mpld3.fig_to_html(fig)
            with open(output_html_file, "w", encoding="utf8") as html_file:
                html_file.write(html_content)

    # Close the figure to free up memory resources
    # Cleanup to avoid memory leaks
    if generation_instructions.create_screenshot:
        screenshot_file_path_without_extension = generation_instructions.output_directory_name + "/" + generation_label_for_valid_file_name + " cumulative " + str(use_cumulative)
        fig.savefig(screenshot_file_path_without_extension + ".png")
        fig.savefig(screenshot_file_path_without_extension + ".svg")
        # fig.savefig(screenshot_file_path_without_extension + ".pdf")

    if not generation_instructions.display_output_plots:
        for cursor in cursors:
            try:
                cursor.remove()
            except Exception:
                pass
        plt.clf()
        plt.close(fig)

    logger_config.print_and_log_current_ram_usage(prefix="After UI computation", previous_reference_rss_value_and_label=[before_plots_computation_ram_rss, "Compared to before UI computation"])


def produce_baregraph_number_of_cfx(
    cfx_library: ChampFXLibrary,
    generation_instructions: NumberOfCfxByCriteriaGenerationInstructionsForLibrary,
) -> None:

    if generation_instructions.for_global:

        # Get cfx matching filter
        all_cfx_to_consider = cfx_library.get_all_cfx_matching_filters(static_criteria_filters=generation_instructions.static_criteria_filters)
        logger_config.print_and_log_info(f"produce_baregraph_number_of_cfx: {len(all_cfx_to_consider)} CFX to consider")

        all_cfx_to_consider_per_subsystem_per_state_dict: Dict[State, int] = {}
        all_cfx_to_consider_per_state_list: List[int] = []
        for state_it in State:
            all_cfx_to_consider_per_subsystem_per_state_dict[state_it] = 0
            all_cfx_to_consider_per_state_list.append(0)

        for cfx_entry in all_cfx_to_consider:
            all_cfx_to_consider_per_subsystem_per_state_dict[cfx_entry._state] += 1

        # Remove key of 0 values
        all_cfx_to_consider_per_subsystem_per_state_dict = {state: count for state, count in all_cfx_to_consider_per_subsystem_per_state_dict.items() if count != 0}

        logger_config.print_and_log_info(f"produce_baregraph_number_of_cfx. all_cfx_to_consider_per_state: {all_cfx_to_consider_per_subsystem_per_state_dict}")

        # Create figure and bar chart
        fig, ax = plt.subplots(figsize=(12, 6))
        plt.bar(range(len(all_cfx_to_consider_per_subsystem_per_state_dict)), list(all_cfx_to_consider_per_subsystem_per_state_dict.values()), align="center")
        plt.xticks(range(len(all_cfx_to_consider_per_subsystem_per_state_dict)), list(all_cfx_to_consider_per_subsystem_per_state_dict.keys()))
        plt.title("Number of CFX per state")
        plt.xlabel("State")
        plt.ylabel("Number of CFX")

        # Add tooltips
        tooltip_data = []
        for state, count in all_cfx_to_consider_per_subsystem_per_state_dict.items():
            tooltip_data.append(f"State: {state}\nCount: {count}")

        # Helper function to create a closure that captures the correct text
        def create_tooltip_handler(text):
            return lambda sel: sel.annotation.set_text(text)

        # Add cursor tooltips to all bar patches
        tooltip_idx = 0
        for container in ax.containers:
            for patch in container:
                if tooltip_idx < len(tooltip_data):
                    mplcursors.cursor(patch, hover=HoverMode.Transient).connect("add", create_tooltip_handler(tooltip_data[tooltip_idx]))
                    tooltip_idx += 1

        plt.show()

    if generation_instructions.by_current_owner_role:

        # Get cfx matching filter
        all_cfx_to_consider = cfx_library.get_all_cfx_matching_filters(static_criteria_filters=generation_instructions.static_criteria_filters)
        logger_config.print_and_log_info(f"produce_baregraph_number_of_cfx: {len(all_cfx_to_consider)} CFX to consider")

        all_cfx_to_consider_per_subsystem_per_state_dict: Dict[SubSystem, Dict[State, int]] = {}
        for subsystem_it in SubSystem:
            all_cfx_to_consider_per_subsystem_per_state_dict[subsystem_it] = {}
            for state_it in State:
                all_cfx_to_consider_per_subsystem_per_state_dict[subsystem_it][state_it] = 0

        logger_config.print_and_log_info(f"produce_baregraph_number_of_cfx. Empty all_cfx_to_consider_per_subsystem_per_state_dict: {all_cfx_to_consider_per_subsystem_per_state_dict}")

        for cfx_entry in all_cfx_to_consider:
            cfx_current_owner_role = cfx_entry._current_owner_role
            cfx_state = cfx_entry._state
            all_cfx_to_consider_per_subsystem_per_state_dict[cfx_current_owner_role][cfx_state] += 1

        logger_config.print_and_log_info(f"produce_baregraph_number_of_cfx. all_cfx_to_consider_per_subsystem_per_state_dict: {all_cfx_to_consider_per_subsystem_per_state_dict}")
        # Remove key of 0 values for states
        for subsystem_it in SubSystem:
            all_cfx_to_consider_per_subsystem_per_state_dict[subsystem_it] = {
                number_of_cfx_by_state: count for number_of_cfx_by_state, count in all_cfx_to_consider_per_subsystem_per_state_dict[subsystem_it].items() if count != 0
            }

        logger_config.print_and_log_info(
            f"produce_baregraph_number_of_cfx. after removing 0 States of each subsystem, all_cfx_to_consider_per_subsystem_per_state_dict: {all_cfx_to_consider_per_subsystem_per_state_dict}"
        )
        # Remove subsystem who don't have any state
        all_cfx_to_consider_per_subsystem_per_state_dict = {states: dict_by_state for states, dict_by_state in all_cfx_to_consider_per_subsystem_per_state_dict.items() if dict_by_state != {}}

        logger_config.print_and_log_info(
            f"produce_baregraph_number_of_cfx. after removing subsystem with no state, all_cfx_to_consider_per_subsystem_per_state_dict: {all_cfx_to_consider_per_subsystem_per_state_dict}"
        )

        # Convert nested dict to DataFrame
        data = []
        for subsystem_it, state_dict in all_cfx_to_consider_per_subsystem_per_state_dict.items():
            for state_it, count in state_dict.items():
                data.append({"SubSystem": str(subsystem_it), "State": str(state_it), "Count": count, "StateValue": state_it.value})

        df = pd.DataFrame(data)

        # Create grouped bar chart
        fig, ax = plt.subplots(figsize=(12, 6))
        df_pivot = df.pivot(index="SubSystem", columns="State", values="Count").fillna(0)
        # Sort columns (States) by their enum value
        state_order = sorted(df_pivot.columns, key=lambda x: df[df["State"] == x]["StateValue"].iloc[0])
        df_pivot = df_pivot[state_order]
        df_pivot.plot(kind="bar", ax=ax, width=0.8)

        # Add tooltips with mplcursors for each bar
        tooltip_data = []
        for idx, subsystem in enumerate(df_pivot.index):
            for state in df_pivot.columns:
                count = int(df_pivot.loc[subsystem, state])
                tooltip_data.append(f"SubSystem: {subsystem}\nState: {state}\nCount: {count}")

        # Helper function to create a closure that captures the correct text
        def create_tooltip_handler(text):
            return lambda sel: sel.annotation.set_text(text)

        # Add cursor tooltips to all bar patches
        tooltip_idx = 0
        for container in ax.containers:
            for patch in container:
                if tooltip_idx < len(tooltip_data):
                    mplcursors.cursor(patch, hover=HoverMode.Transient).connect("add", create_tooltip_handler(tooltip_data[tooltip_idx]))
                    tooltip_idx += 1

        # Customize the plot
        ax.set_xlabel("State", fontsize=12, fontweight="bold")
        ax.set_ylabel("Count", fontsize=12, fontweight="bold")
        ax.set_title("CFX Count by SubSystem and State", fontsize=14, fontweight="bold")
        ax.legend(title="States", bbox_to_anchor=(1.05, 1), loc="upper left")
        ax.grid(axis="y", alpha=0.3)
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.show()


def produce_number_of_cfx_by_state_per_date_line_graphs_for_library(
    cfx_library: ChampFXLibrary,
    generation_instructions: NumberOfCfxStatePerDateGenerationInstructionsForLibrary,
) -> None:

    if generation_instructions.for_global:

        produce_line_graphs_number_of_cfx_by_state_per_date_line_graphs(
            cfx_library=cfx_library,
            generation_instructions=generation_instructions,
            display_without_cumulative_eras=True,
            display_with_cumulative_eras=True,
        )

    if generation_instructions.for_each_current_owner_per_date:
        for subsystem in SubSystem:

            generation_instructions_copy = copy.deepcopy(generation_instructions)
            generation_instructions_copy.cfx_filters = generation_instructions_copy.cfx_filters + [
                ChampFxFilter(role_depending_on_date_filter=ChampFXRoleDependingOnDateFilter(roles_at_date_allowed=[subsystem]))
            ]
            with logger_config.stopwatch_with_label(label=f"{cfx_library.label} produce_results_and_displays for {subsystem.name}", inform_beginning=True, monitor_ram_usage=True):
                produce_line_graphs_number_of_cfx_by_state_per_date_line_graphs(
                    cfx_library=cfx_library,
                    generation_instructions=generation_instructions_copy,
                    display_without_cumulative_eras=False,
                    display_with_cumulative_eras=True,
                )

    if generation_instructions.for_each_subsystem:
        for subsystem in SubSystem:
            with logger_config.stopwatch_with_label(label=f"{cfx_library.label} produce_results_and_displays for {subsystem.name}", inform_beginning=True, monitor_ram_usage=True):
                generation_instructions_copy = copy.deepcopy(generation_instructions)
                generation_instructions_copy.cfx_filters = generation_instructions_copy.cfx_filters + [ChampFxFilter(field_filters=[ChampFxFilterFieldSubsystem(field_accepted_values=[subsystem])])]

                produce_line_graphs_number_of_cfx_by_state_per_date_line_graphs(
                    cfx_library=cfx_library,
                    generation_instructions=generation_instructions_copy,
                    display_without_cumulative_eras=False,
                    display_with_cumulative_eras=True,
                )


def block_execution_and_keep_all_windows_open() -> None:
    """Use plt.show() here to block execution and keep all windows open"""
    plt.show()
