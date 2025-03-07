import pandas as pd
import matplotlib.pyplot as plt
import datetime
from collections import defaultdict


import cfx


def plot_cfx_states_over_time(cfx_library: cfx.ChampFXLibrary) -> None:
    months = cfx_library.get_months_since_earliest_submit_date()
    state_counts_per_month = []

    for month in months:
        state_counts = defaultdict(int)

        for entry in cfx_library._champ_fx:
            state = entry.get_state_at_date(month)
            state_counts[state] += 1

        state_counts_per_month.append(state_counts)

    fig, ax = plt.subplots(figsize=(10, 6))

    states = [state for state in cfx.State]
    # Prepare lists for plotting
    for state in states:
        counts = [state_counts[state] for state_counts in state_counts_per_month]
        ax.plot(months, counts, label=state.name)

    ax.set_xlabel("Month")
    ax.set_ylabel("Number of CFX Entries")
    ax.set_title("CFX States Over Time")
    ax.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


champfx_library = cfx.ChampFXLibrary("extract_cfx.xlsx")
plot_cfx_states_over_time(cfx_library=champfx_library)
