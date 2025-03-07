import pandas as pd
import matplotlib.pyplot as plt
from collections import defaultdict

from logger import logger_config

import cfx


def plot_cfx_states_over_time(cfx_library: cfx.ChampFXLibrary, output_excel_file: str, use_cumulative: bool) -> None:
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

    states = [state for state in cfx.State]

    # Prepare cumulative counts for stacked area plot and Excel output
    cumulative_counts = {state: [] for state in states}
    for state_counts in state_counts_per_month:
        for state in states:
            cumulative_counts[state].append(state_counts[state])

    # Convert data to DataFrame for Excel output
    data_for_excel = pd.DataFrame(cumulative_counts, index=months) if use_cumulative else pd.DataFrame(state_counts_per_month, index=months)
    data_for_excel.index.name = "Month"

    # Save DataFrame to Excel
    with pd.ExcelWriter(output_excel_file) as writer:
        data_for_excel.to_excel(writer, sheet_name="CFX State Counts")

    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot
    if use_cumulative:
        # Plot cumulative areas
        bottom = [0] * len(months)
        for state in states:
            ax.fill_between(months, bottom, [bottom[i] + cumulative_counts[state][i] for i in range(len(months))], label=state.name)
            bottom = [bottom[i] + cumulative_counts[state][i] for i in range(len(months))]

    else:
        for state in states:
            counts = [state_counts[state] for state_counts in state_counts_per_month]
            ax.plot(months, counts, label=state.name)

    ax.set_xlabel("Month")
    ax.set_ylabel("Number of CFX Entries")
    ax.set_title("CFX States Over Time")
    ax.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()


def old_plot_cfx_states_over_time(cfx_library: cfx.ChampFXLibrary, output_excel_file: str) -> None:
    # Retrieve months to process
    months = cfx_library.get_months_since_earliest_submit_date()

    # Gather state counts for each month
    state_counts_per_month = []
    for month in months:
        state_counts = defaultdict(int)
        for entry in cfx_library.get_all_cfx():
            state = entry.get_state_at_date(month)
            if state != cfx.State.NotCreatedYet:
                state_counts[state] += 1
        state_counts_per_month.append(state_counts)

    # Convert data to DataFrame for Excel output
    data_for_excel = pd.DataFrame(state_counts_per_month, index=months)
    data_for_excel.index.name = "Month"

    # Save DataFrame to Excel
    with pd.ExcelWriter(output_excel_file) as writer:
        data_for_excel.to_excel(writer, sheet_name="CFX State Counts")

    # Plot states per month
    fig, ax = plt.subplots(figsize=(10, 6))
    states = [state for state in cfx.State]
    for state in states:
        counts = [state_counts[state] for state_counts in state_counts_per_month]
        ax.plot(months, counts, label=state.name)

    ax.set_xlabel("Month")
    ax.set_ylabel("Number of CFX Entries")
    ax.set_title("CFX States Per Month")
    ax.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()


def old_plot_cfx_states_over_time_cumulated_eras(cfx_library: cfx.ChampFXLibrary, output_excel_file: str) -> None:
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

    # Prepare cumulative counts for stacked area plot and Excel output
    states = [state for state in cfx.State]
    cumulative_counts = {state: [] for state in states}
    for state_counts in state_counts_per_month:
        for state in states:
            cumulative_counts[state].append(state_counts[state])

    # Convert data to DataFrame for Excel output
    data_for_excel = pd.DataFrame(cumulative_counts, index=months)
    data_for_excel.index.name = "Month"

    # Save DataFrame to Excel
    with pd.ExcelWriter(output_excel_file) as writer:
        data_for_excel.to_excel(writer, sheet_name="CFX State Counts")

    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot cumulative areas
    bottom = [0] * len(months)
    for state in states:
        ax.fill_between(months, bottom, [bottom[i] + cumulative_counts[state][i] for i in range(len(months))], label=state.name)
        bottom = [bottom[i] + cumulative_counts[state][i] for i in range(len(months))]

    ax.set_xlabel("Month")
    ax.set_ylabel("Number of CFX Entries")
    ax.set_title("CFX States Over Time")
    ax.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()


def main() -> None:
    """Main function"""

    with logger_config.stopwatch_with_label("Application duration"):
        logger_config.print_and_log_info("Application start")

        champfx_library = cfx.ChampFXLibrary("extract_cfx_details.xlsx", "extract_cfx_change_state.xlsx")

        # Plot in the first window
        plot_cfx_states_over_time(cfx_library=champfx_library, output_excel_file="all_standard.xlsx", use_cumulative=False)
        # Plot in the second window
        plot_cfx_states_over_time(cfx_library=champfx_library, output_excel_file="all_cumulated_eras.xlsx", use_cumulative=True)

        # Use plt.show() here to block execution and keep all windows open
        plt.show()

        logger_config.print_and_log_info("Application end")


if __name__ == "__main__":
    # sys.argv[1:]
    main()
