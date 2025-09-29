import pytest

from datetime import datetime
from dateutil import relativedelta

from typing import List, Dict

from generatecfxhistory import cfx, role, inputs, filters, dates_generators, constants
from generatecfxhistory.constants import State

# from common import json_encoders


DEFAULT_CHAMPFX_EXTENDED_HISTORY_FILE_FULL_PATH: str = "Input_Downloaded/extended_history_nextats.txt"


class TestChampFxFilterWithOnlyWhitelistFilterLabel:
    def test_label_contains_whitelist_file_name_once(self) -> None:
        cfx_usine_site_filter = cfx.ChampFxFilter(cfx_to_treat_whitelist_text_file_full_path="Input/CFX_usine_site.txt")
        assert "CFX_usine_site" in cfx_usine_site_filter.label
        assert cfx_usine_site_filter.label.count("CFX_usine_site") == 1
