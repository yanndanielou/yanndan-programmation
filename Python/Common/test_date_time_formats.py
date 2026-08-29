import pytest

from common import date_time_formats


class TestFormatDurationTimedeltaToString:

    @pytest.mark.parametrize(
        "start_timestamp_str,end_timestamp_str,expected_result",
        [
            (
                "2026-06-23 12:11:22.427+02:00",
                "2026-06-23T12:11:22.430+02:00",
                "00:00:00.003",
            ),
            (
                "2026-06-23 12:11:22.427000+02:00",
                "2026-06-23T12:11:22.430+02:00",
                "00:00:00.003",
            ),
            (
                "2026-06-23 12:11:23.429000+02:00",
                "2026-06-23T12:11:23.430000+02:00",
                "00:00:00.001",
            ),
            (
                "2026-06-23 15:25:07.315000+02:00",
                "2026-06-23T15:25:08.223+02:00",
                "00:00:00.908",
            ),
            (
                "2026-06-24T11:27:31.715000+02:00",
                "2026-06-24T12:39:07.810+02:00",
                "01:11:36.095",
            ),
        ],
    )
    def test_format_duration_timedelta_to_string(self, start_timestamp_str: str, end_timestamp_str: str, expected_result: str) -> None:
        ret = date_time_formats.format_duration_between_timestamps_str_to_string(start_timestamp_str, end_timestamp_str)
        assert ret == expected_result
