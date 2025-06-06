import pytest

from generatecfxhistory import utils

# fmt: off
champfx_raw_dates_data = ["19 juillet 2022 à 16:00:58 UTC+2",
"30 janvier 2024 à 09:54:41 UTC+1",
"7 février 2023 à 13:39:01 UTC+1",
"7 février 2023 à 13:43:58 UTC+1",
"20 octobre 2022 à 14:36:58 UTC+2",
"29 octobre 2024 à 16:03:31 UTC+1",
"29 octobre 2024 à 16:02:53 UTC+1",
"4 novembre 2022 à 11:09:17 UTC+1",
"13 octobre 2022 à 17:02:21 UTC+2",
"13 octobre 2022 à 17:02:21 UTC+2",
"2 février 2023 à 15:37:02 UTC+1",
"2 février 2023 à 15:37:02 UTC+1"]
# fmt: on


class TestDateConversion:
    @pytest.mark.parametrize("champfx_raw_date", champfx_raw_dates_data)
    def test_date_can_be_converted(self, champfx_raw_date: str) -> None:
        converted_date = utils.convert_champfx_extract_date(champfx_raw_date)
        assert converted_date is not None

    def test_nan_str(self) -> None:
        converted_date = utils.convert_champfx_extract_date("nan")
        assert converted_date is None

    def test_nan_float(self) -> None:
        converted_date = utils.convert_champfx_extract_date(float("NaN"))
        assert converted_date is None
