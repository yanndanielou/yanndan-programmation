import pytest

from datetime import datetime
from dateutil import relativedelta

from typing import List, Dict

from generatecfxhistory import cfx, role, ui_and_results_generation
from generatecfxhistory.constants import State

from common import json_encoders


class TestNoMemoryLeakWhenNoDisplay:
    def test_use_cumulative_only_and_no_html(self):
        all_results_to_display = cfx.AllResultsPerDates()
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
