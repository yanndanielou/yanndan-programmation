import datetime

import pytest

from stsloganalyzis.atc import atc_logs


class TestDecodeTimestamp:

    @pytest.mark.parametrize(
        "c_heure, c_decalage, c_decenie, c_jour, expected_timetamp",
        [
            (
                476950,
                3600000,
                2,
                2279,
                datetime.datetime(day=29, month=3, year=2026, hour=1, minute=7, second=56, microsecond=950 * 1000),
            )
        ],
    )
    def test_decode_pert_timestamp(self, c_heure: int, c_decalage: int, c_decenie: int, c_jour: int, expected_timetamp: datetime.datetime) -> None:
        decoded_timestamp = atc_logs.pert_variable_to_timestamp(c_heure=c_heure, c_decalage=c_decalage, c_decenie=c_decenie, c_jour=c_jour)
        assert decoded_timestamp == expected_timetamp
