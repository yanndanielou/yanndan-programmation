import pandas as pd
import matplotlib.pyplot as plt
from collections import defaultdict
import mpld3
from mpld3 import plugins

import mplcursors
from mplcursors._mplcursors import HoverMode

import os


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


def produce_results_and_displays(
    cfx_library: cfx.ChampFXLibrary,
    output_excel_file: str,
    display_without_cumulative_eras: bool,
    display_with_cumulative_eras: bool,
    output_html_file_prefix: str,
    filter_only_subsystem=None,
    filter_only_known_by_cstr=False,
) -> None:
    # Retrieve months to process
    months = cfx_library.get_months_since_earliest_submit_date()
    state_counts_per_month = []

    # Gather state counts for each month
    for month in months:
        state_counts = defaultdict(int)
        for entry in cfx_library.get_all_cfx():
            state = entry.get_state_at_date(month)

            if filter_only_subsystem is None or filter_only_subsystem == entry.get_sub_system():

                entry_cfx_id = entry.cfx_id
                cfx_id_known = entry.cfx_id in cfx_library._cfx_known_by_cstmr_ids

                if not filter_only_known_by_cstr or entry.cfx_id in cfx_library._cfx_known_by_cstmr_ids:

                    if state != cfx.State.NotCreatedYet:
                        state_counts[state] += 1
        state_counts_per_month.append(state_counts)

    # Determine the states that are present in the data
    present_states_set = set()
    for state_counts in state_counts_per_month:
        present_states_set.update(state_counts.keys())

    present_states_list = list(present_states_set)
    present_states_ordered_list = sorted(list(present_states_set))

    # Prepare cumulative counts for stacked area plot and Excel output
    cumulative_counts = {state: [] for state in present_states_ordered_list}
    for state_counts in state_counts_per_month:
        for state in present_states_ordered_list:
            cumulative_counts[state].append(state_counts[state])

    if output_excel_file:
        with logger_config.stopwatch_with_label(f"produce_excel_output_file, filter {filter_only_subsystem}"):
            produce_excel_output_file(output_excel_file=output_excel_file, state_counts_per_month=state_counts_per_month, months=months)

    if display_with_cumulative_eras:
        with logger_config.stopwatch_with_label(f"produce_displays cumulative, filter {filter_only_subsystem}"):
            produce_displays(
                use_cumulative=True,
                months=months,
                present_states_ordered_list=present_states_ordered_list,
                cumulative_counts=cumulative_counts,
                state_counts_per_month=state_counts_per_month,
                output_html_file_prefix=output_html_file_prefix + "_cumulative_eras_",
                filter_only_subsystem=filter_only_subsystem,
                window_title=f"Filter {filter_only_subsystem}, CFX States Over Time (Cumulative)",
            )
    if display_without_cumulative_eras:
        with logger_config.stopwatch_with_label(f"produce_displays numbers, filter {filter_only_subsystem}"):
            produce_displays(
                use_cumulative=False,
                months=months,
                present_states_ordered_list=present_states_ordered_list,
                cumulative_counts=cumulative_counts,
                state_counts_per_month=state_counts_per_month,
                output_html_file_prefix=output_html_file_prefix + "_values_",
                filter_only_subsystem=filter_only_subsystem,
                window_title=f"Filter {filter_only_subsystem}, CFX States Over Time (Values)",
            )


def produce_excel_output_file(output_excel_file: str, state_counts_per_month, months) -> None:
    # Convert data to DataFrame for Excel output
    data_for_excel = pd.DataFrame(state_counts_per_month, index=months)
    data_for_excel.index.name = "Month"

    # Save DataFrame to Excel
    with pd.ExcelWriter(output_excel_file) as writer:
        data_for_excel.to_excel(writer, sheet_name="CFX State Counts")


def produce_displays(use_cumulative, months, present_states_ordered_list, cumulative_counts, state_counts_per_month, output_html_file_prefix, filter_only_subsystem, window_title) -> None:
    fig, ax = plt.subplots(figsize=(10, 6))

    # Set the window title
    fig.canvas.manager.set_window_title(window_title)

    tooltips = []

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
            # tooltip = plugins.LineLabelTooltip(line, label=state.name)
            # tooltips.append(tooltip)

    else:
        for state in present_states_ordered_list:
            color = state_colors.get(state, None)
            counts = [state_counts[state] for state_counts in state_counts_per_month]
            (line,) = ax.plot(months, counts, label=state.name, color=color)
            mplcursors.cursor(line, hover=HoverMode.Transient)
            # tooltip = plugins.LineLabelTooltip(line, label=state.name)
            # tooltips.append(tooltip)

    ax.set_xlabel("Month")
    ax.set_ylabel("Number of CFX Entries")
    ax.set_title("All CFX States Over Time" if filter_only_subsystem is None else f"Subsytem {filter_only_subsystem} CFX States Over Time")
    ax.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Add tooltips
    # plugins.connect(fig, *tooltips)
    # Add mplcursors for tooltip functionality
    # mplcursors.cursor(ax, hover=True).connect("add", lambda sel: sel.annotation.set_text(f"State: {present_states_ordered_list[sel.index].name}"))
    # Add mplcursors for tooltip functionality
    # mplcursors.cursor(ax, hover=True).connect("add", lambda sel: sel.annotation.set_text(f"State: {present_states_ordered_list[int(sel.index)].name}"))

    # cursor = mplcursors.cursor(line, hover=True)
    # cursor.connect("add", lambda sel: sel.annotation.set_text(f"State: {present_states_ordered_list[int(sel.index)].name}"))

    # mplcursors.cursor(ax, hover=True)  # .connect("add", lambda sel: print(f"State: {sel.index}"))

    # Save the plot to an HTML file
    html_content = mpld3.fig_to_html(fig)
    output_html_file = output_html_file_prefix + ".html"

    with logger_config.stopwatch_with_label(f"html {output_html_file} creation"):
        with open(output_html_file, "w", encoding="utf8") as html_file:
            html_file.write(html_content)


def main() -> None:
    """Main function"""

    with logger_config.stopwatch_with_label("Application duration"):
        logger_config.configure_logger_with_random_log_file_suffix("GenerateCFXHistory")
        logger_config.print_and_log_info("Application start")

        output_directory_name = "output"
        if not os.path.exists(output_directory_name):
            os.mkdir(output_directory_name)

        champfx_library = cfx.ChampFXLibrary(
            champfx_details_excel_file_full_path="Input/extract_cfx_details.xlsx",
            champfx_states_changes_excel_file_full_path="Input/extract_cfx_change_state.xlsx",
            all_current_owner_modifications_per_cfx_pickle_file_full_path="Input/all_current_owner_modifications_per_cfx.pkl",
            all_current_owner_modifications_pickle_file_full_path="Input/all_current_owner_modifications.pkl",
        )

        produce_results_and_displays(
            cfx_library=champfx_library,
            output_excel_file=f"{output_directory_name}/all_cfx.xlsx",
            display_without_cumulative_eras=True,
            display_with_cumulative_eras=True,
            output_html_file_prefix=f"{output_directory_name}/all_cfx_",
            filter_only_subsystem=None,
            filter_only_known_by_cstr=True,
        )

        plt.show()
        exit()

        for subsystem in role.SubSystem:
            with logger_config.stopwatch_with_label(f"produce_results_and_displays for {subsystem.name}"):
                produce_results_and_displays(
                    cfx_library=champfx_library,
                    # output_excel_file=f"{output_directory_name}/subsystem_{subsystem.name}.xlsx",
                    output_excel_file=None,
                    display_without_cumulative_eras=False,
                    display_with_cumulative_eras=True,
                    output_html_file_prefix=f"{output_directory_name}/subsystem_{subsystem.name}",
                    filter_only_subsystem=subsystem,
                    filter_only_known_by_cstr=False,
                )

        # Use plt.show() here to block execution and keep all windows open
        plt.show()

        logger_config.print_and_log_info("Application end")


if __name__ == "__main__":
    # sys.argv[1:]
    main()
