import pytest

from datetime import datetime

from typing import List

import cfx


@pytest.fixture(scope="session")
def create_champfx_library() -> cfx.ChampFXLibrary:
    champfx_library = cfx.ChampFXLibrary()
    return champfx_library


@pytest.fixture(scope="session")
def get_cfx_closed_status_according_to_date_today(create_champfx_library: cfx.ChampFXLibrary) -> List[cfx.ChampFXEntry]:
    return create_champfx_library.get_cfx_by_state_at_date(reference_date=datetime.now().replace(hour=23, minute=59, second=59, microsecond=0, tzinfo=None))[cfx.State.Closed]


class TestConstruction:
    def test_no_error_at_init(self, create_champfx_library: cfx.ChampFXLibrary):
        champfx_library = create_champfx_library
        assert len(champfx_library.get_all_cfx()) > 0


class TestStatus:
    def test_library_is_not_empty(self, create_champfx_library: cfx.ChampFXLibrary):
        champfx_library = create_champfx_library
        assert len(champfx_library.get_all_cfx()) > 0

    def test_there_are_cfx_current_status_closed(self, create_champfx_library: cfx.ChampFXLibrary):
        champfx_library = create_champfx_library
        cfx_closed_status = list(filter(lambda champfx: champfx.raw_state == cfx.State.Closed, champfx_library.get_all_cfx()))
        assert len(cfx_closed_status) > 0

    def test_there_are_cfx_closed_by_date(self, get_cfx_closed_status_according_to_date_today: List[cfx.ChampFXEntry]):
        cfx_closed_status_according_to_date_today = get_cfx_closed_status_according_to_date_today
        assert len(cfx_closed_status_according_to_date_today) > 0

    def test_all_cfx_current_status_closed_are_also_closed_by_date(self, create_champfx_library: cfx.ChampFXLibrary, get_cfx_closed_status_according_to_date_today: List[cfx.ChampFXEntry]):
        champfx_library = create_champfx_library
        cfx_closed_status_according_to_date_today = get_cfx_closed_status_according_to_date_today

        cfx_closed_status = list(filter(lambda champfx: champfx.raw_state == cfx.State.Closed, champfx_library.get_all_cfx()))

        cfx_closed_by_status_but_not_by_date = list(set(cfx_closed_status) - set(cfx_closed_status_according_to_date_today))
        assert len(cfx_closed_by_status_but_not_by_date) == 0

    def test_errors_related_to_closed_status(self, create_champfx_library: cfx.ChampFXLibrary, get_cfx_closed_status_according_to_date_today: List[cfx.ChampFXEntry]):
        champfx_library = create_champfx_library

        cfx_closed_status_according_to_date_today = get_cfx_closed_status_according_to_date_today
        assert len(cfx_closed_status_according_to_date_today) > 0

        cfx_closed_status = list(filter(lambda champfx: champfx.raw_state == cfx.State.Closed, champfx_library.get_all_cfx()))

        cfx_closed_by_date_but_not_by_status = list(set(cfx_closed_status_according_to_date_today) - set(cfx_closed_status))
        assert len(cfx_closed_by_date_but_not_by_status) == 0, f"cfx_closed_by_date_but_not_by_status found: {cfx_closed_by_date_but_not_by_status}"
