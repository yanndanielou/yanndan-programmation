import pytest

from datetime import datetime
import cfx


class TestStatus:
    def test_errors_related_to_closed_status(self):
        champfx_library = cfx.ChampFXLibrary("extract_cfx.xlsx")

        assert len(champfx_library.all_cfx) > 0

        cfx_closed_status_according_to_date_today = champfx_library.get_cfx_by_state_at_date(reference_date=datetime.now().replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=None))[
            cfx.State.Closed
        ]
        cfx_closed_status = list(filter(lambda champfx: champfx.raw_state == cfx.State.Closed, champfx_library.all_cfx))

        cfx_closed_by_status_but_not_by_date = list(set(cfx_closed_status) - set(cfx_closed_status_according_to_date_today))
        cfx_closed_by_date_but_not_by_status = list(set(cfx_closed_status_according_to_date_today) - set(cfx_closed_status))

        print(cfx_closed_by_date_but_not_by_status)

        print(len(cfx_closed_status_according_to_date_today))
        print(len(cfx_closed_status))

        assert cfx_closed_by_status_but_not_by_date is None
        assert cfx_closed_by_date_but_not_by_status is None
        assert len(cfx_closed_status_according_to_date_today) == len(cfx_closed_status)
