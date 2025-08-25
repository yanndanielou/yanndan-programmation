import os
import psutil
import pytest

from datetime import datetime
from dateutil import relativedelta

from typing import List, Dict

import humanize

from generatecfxhistory import cfx, role, ui_and_results_generation
from generatecfxhistory.constants import State

from common import json_encoders


def prepare_data(year: int, all_results_to_display: cfx.AllResultsPerDates) -> List[datetime]:

    dates_generator = cfx.ConstantIntervalDatesGenerator(time_delta=relativedelta.relativedelta(days=1))

    all_dates = dates_generator.get_dates_since(datetime(year=year, month=1, day=1))
    print(f"{len(all_dates)} dates for tests generated since {year}")

    for index, one_date in enumerate(all_dates):
        one_result_timestamp = cfx.OneTimestampResult(all_results_to_display=all_results_to_display, timestamp=one_date)
        one_result_timestamp.count_by_state[State.SUBMITTED] = index * 5
        one_result_timestamp.count_by_state[State.ANALYSED] = index * 3
        one_result_timestamp.count_by_state[State.ASSIGNED] = index * 2
        one_result_timestamp.count_by_state[State.RESOLVED] = index
        one_result_timestamp.count_by_state[State.VERIFIED] = index // 2
        one_result_timestamp.count_by_state[State.VALIDATED] = index // 3
        one_result_timestamp.count_by_state[State.CLOSED] = index // 4
        one_result_timestamp.consolidate_present_states()
        all_results_to_display.timestamp_results.append(one_result_timestamp)

    all_results_to_display.compute_cumulative_counts()
    return all_dates


class TestNoMemoryLeakWhenDisplay:
    def ignore_test_use_cumulative_only_and_no_html(self) -> None:
        all_results_to_display = cfx.AllResultsPerDates()

        all_dates = prepare_data(2024, all_results_to_display)
        initial_ram_rss = psutil.Process(os.getpid()).memory_info().rss
        previous_ram_rss = initial_ram_rss
        for iter in range(1, 1):
            ui_and_results_generation.produce_displays_and_create_html(
                use_cumulative=True,
                all_results_to_display=all_results_to_display,
                create_html_file=False,
                window_title="test_use_cumulative_only_and_no_html",
                generation_label="test_use_cumulative_only_and_no_html",
                generation_label_for_valid_file_name="test_use_cumulative_only_and_no_html",
                output_directory_name="output_for_tests",
                display_output_plots=True,
            )
            current_ram_rss = psutil.Process(os.getpid()).memory_info().rss
            ram_increase_since_beginning = current_ram_rss - initial_ram_rss
            ram_increase_since_last_ui_display = current_ram_rss - previous_ram_rss
            print(
                f"{len(all_dates)} dates, iter {iter} process {os.getpid()} memory rss:{humanize.naturalsize(current_ram_rss)}. Ram increase since beginning:{humanize.naturalsize(ram_increase_since_beginning)}. Ram increase since last ui computation:{humanize.naturalsize(ram_increase_since_last_ui_display)}"
            )
            previous_ram_rss = current_ram_rss
            assert current_ram_rss < (2 * initial_ram_rss)

        # ui_and_results_generation.block_execution_and_keep_all_windows_open()


class TestNoMemoryLeakWhenNoDisplay:
    @pytest.mark.parametrize("initial_year", [(2000), (2010), (2020)])
    def test_use_cumulative_only_and_no_html(self, initial_year: int) -> None:
        all_results_to_display = cfx.AllResultsPerDates()

        all_dates = prepare_data(initial_year, all_results_to_display)
        initial_ram_rss = psutil.Process(os.getpid()).memory_info().rss
        previous_ram_rss = initial_ram_rss
        for iter in range(1, 20):
            ui_and_results_generation.produce_displays_and_create_html(
                use_cumulative=True,
                all_results_to_display=all_results_to_display,
                create_html_file=False,
                window_title="test_use_cumulative_only_and_no_html",
                generation_label="test_use_cumulative_only_and_no_html",
                generation_label_for_valid_file_name="test_use_cumulative_only_and_no_html",
                output_directory_name="output_for_tests",
                display_output_plots=False,
            )
            current_ram_rss = psutil.Process(os.getpid()).memory_info().rss
            ram_increase_since_beginning = current_ram_rss - initial_ram_rss
            ram_increase_since_last_ui_display = current_ram_rss - previous_ram_rss
            print(
                f"{len(all_dates)} dates, iter {iter} process {os.getpid()} memory rss:{humanize.naturalsize(current_ram_rss)}. Ram increase since beginning:{humanize.naturalsize(ram_increase_since_beginning)}. Ram increase since last ui computation:{humanize.naturalsize(ram_increase_since_last_ui_display)}"
            )
            previous_ram_rss = current_ram_rss
            assert current_ram_rss < (2 * initial_ram_rss)
