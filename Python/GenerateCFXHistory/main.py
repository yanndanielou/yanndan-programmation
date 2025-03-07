import pandas as pd
import matplotlib.pyplot as plt
from collections import defaultdict
import mpld3
from mpld3 import plugins


from logger import logger_config

import cfx

state_colors = {
    cfx.State.Submitted: "red",
    cfx.State.Analysed: "orange",
    cfx.State.Assigned: "blue",
    cfx.State.Resolved: "brown",
    cfx.State.Postponed: "grey",
    cfx.State.Rejected: "black",
    cfx.State.Verified: "yellow",
    cfx.State.Validated: "darkgreen",
    cfx.State.Closed: "green",
    # Add additional states and their respective colors
}


def plot_cfx_states_over_time(cfx_library: cfx.ChampFXLibrary, output_excel_file: str, use_cumulative: bool, output_html_file: str) -> None:
    # Retrieve months to process
    months = cfx_library.get_months_since_earliest_submit_date()
    state_counts_per_month = []

    # Gather state counts for each month
    for month in months:
        state_counts = defaultdict(int)
        for entry in cfx_library.get_all_cfx():
            state = entry.get_state_at_date(month)
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

    # Convert data to DataFrame for Excel output
    data_for_excel = pd.DataFrame(cumulative_counts, index=months) if use_cumulative else pd.DataFrame(state_counts_per_month, index=months)
    data_for_excel.index.name = "Month"

    # Save DataFrame to Excel
    with pd.ExcelWriter(output_excel_file) as writer:
        data_for_excel.to_excel(writer, sheet_name="CFX State Counts")

    fig, ax = plt.subplots(figsize=(10, 6))

    tooltips = []

    # Plot
    if use_cumulative:
        # Plot cumulative areas
        bottom = [0] * len(months)
        for state in present_states_ordered_list:
            color = state_colors.get(state, None)
            upper = [bottom[i] + cumulative_counts[state][i] for i in range(len(months))]
            line = ax.fill_between(months, bottom, upper, label=state.name, color=color)
            bottom = upper
            tooltip = plugins.LineLabelTooltip(line, label=state.name)
            tooltips.append(tooltip)

    else:
        for state in present_states_ordered_list:
            color = state_colors.get(state, None)
            counts = [state_counts[state] for state_counts in state_counts_per_month]
            (line,) = ax.plot(months, counts, label=state.name, color=color)
            tooltip = plugins.LineLabelTooltip(line, label=state.name)
            tooltips.append(tooltip)

    ax.set_xlabel("Month")
    ax.set_ylabel("Number of CFX Entries")
    ax.set_title("CFX States Over Time")
    ax.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Add tooltips
    plugins.connect(fig, *tooltips)

    # Save the plot to an HTML file
    html_content = mpld3.fig_to_html(fig)

    with open(output_html_file, "w") as html_file:
        html_file.write(html_content)


def main() -> None:
    """Main function"""

    with logger_config.stopwatch_with_label("Application duration"):
        logger_config.print_and_log_info("Application start")

        champfx_library = cfx.ChampFXLibrary("extract_cfx_details.xlsx", "extract_cfx_change_state.xlsx")

        # Plot in the first window
        plot_cfx_states_over_time(cfx_library=champfx_library, output_excel_file="all_standard.xlsx", use_cumulative=False, output_html_file="all_standard.html")
        # Plot in the second window
        plot_cfx_states_over_time(cfx_library=champfx_library, output_excel_file="all_cumulated_eras.xlsx", use_cumulative=True, output_html_file="all_cumulated_eras.html")

        # plot_cfx_states_over_time(cfx_library=champfx_library, output_excel_file="all_cumulated_eras.xlsx", use_cumulative=True, output_html_file="all_cumulated_eras.html")

        # Use plt.show() here to block execution and keep all windows open
        plt.show()

        logger_config.print_and_log_info("Application end")


if __name__ == "__main__":
    # sys.argv[1:]
    main()
