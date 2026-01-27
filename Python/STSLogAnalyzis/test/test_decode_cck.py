import datetime

import pytest

from typing import List

from stsloganalyzis import decode_cck


decode_mpro_trace_date_data = [
    (
        "[2026/01/27 15/34/41/32] 8055 11 Main [tem@6182]Liaison 25A - La liaison n'a pas pu être démarré, on va reessayer plus tard",
        datetime.datetime(year=2026, month=1, day=27, hour=15, minute=34, second=41, microsecond=320000),
    )
]


class TestCckMproTraceLine:
    @pytest.mark.parametrize("full_raw_line_str, expected_timestamp", decode_mpro_trace_date_data)
    def test_line_timestamp(self, full_raw_line_str: str, expected_timestamp: datetime.datetime) -> None:

        cck_mpro_trace_line = decode_cck.CckMproTraceLine(full_line=full_raw_line_str)
        assert cck_mpro_trace_line.decoded_timestamp == expected_timestamp
