import pytest

from datetime import datetime

from typing import List

import cfx


@pytest.fixture(scope="session")
def create_light_champfx_library() -> cfx.ChampFXLibrary:
    champfx_library = cfx.ChampFXLibrary(
        champfx_details_excel_file_full_path="Input_for_Tests/extract_cfx_details.xlsx",
        champfx_states_changes_excel_file_full_path="Input_for_Tests/extract_cfx_change_state.xlsx",
        all_current_owner_modifications_pickle_file_full_path="Input_for_Tests/all_current_owner_modifications.pkl",
        all_current_owner_modifications_per_cfx_pickle_file_full_path="Input_for_Tests/all_current_owner_modifications_per_cfx.pkl",
    )
    return champfx_library


@pytest.fixture(scope="session")
def get_cfx_closed_status_according_to_date_today(create_light_champfx_library: cfx.ChampFXLibrary) -> List[cfx.ChampFXEntry]:
    return create_light_champfx_library.get_cfx_by_state_at_date(reference_date=datetime.now().replace(hour=23, minute=59, second=59, microsecond=0, tzinfo=None))[cfx.State.Closed]


class TestConstruction:
    def test_no_error_at_init(self, create_light_champfx_library: cfx.ChampFXLibrary):
        champfx_library = create_light_champfx_library
        assert len(champfx_library.get_all_cfx()) > 0


class TestStatus:
    def test_library_is_not_empty(self, create_light_champfx_library: cfx.ChampFXLibrary):
        champfx_library = create_light_champfx_library
        assert len(champfx_library.get_all_cfx()) > 0

    def test_there_are_cfx_current_status_closed(self, create_light_champfx_library: cfx.ChampFXLibrary):
        champfx_library = create_light_champfx_library
        cfx_closed_status = list(filter(lambda champfx: champfx.raw_state == cfx.State.Closed, champfx_library.get_all_cfx()))
        assert len(cfx_closed_status) > 0

    def test_there_are_cfx_closed_by_date(self, get_cfx_closed_status_according_to_date_today: List[cfx.ChampFXEntry]):
        cfx_closed_status_according_to_date_today = get_cfx_closed_status_according_to_date_today
        assert len(cfx_closed_status_according_to_date_today) > 0

    def test_all_cfx_current_status_closed_are_also_closed_by_date(self, create_light_champfx_library: cfx.ChampFXLibrary, get_cfx_closed_status_according_to_date_today: List[cfx.ChampFXEntry]):
        champfx_library = create_light_champfx_library
        cfx_closed_status_according_to_date_today = get_cfx_closed_status_according_to_date_today

        cfx_closed_status = list(filter(lambda champfx: champfx.raw_state == cfx.State.Closed, champfx_library.get_all_cfx()))

        cfx_closed_by_status_but_not_by_date = list(set(cfx_closed_status) - set(cfx_closed_status_according_to_date_today))
        assert len(cfx_closed_by_status_but_not_by_date) == 0

    def test_errors_related_to_closed_status(self, create_light_champfx_library: cfx.ChampFXLibrary, get_cfx_closed_status_according_to_date_today: List[cfx.ChampFXEntry]):
        champfx_library = create_light_champfx_library

        cfx_closed_status_according_to_date_today = get_cfx_closed_status_according_to_date_today
        assert len(cfx_closed_status_according_to_date_today) > 0

        cfx_closed_status = list(filter(lambda champfx: champfx.raw_state == cfx.State.Closed, champfx_library.get_all_cfx()))

        cfx_closed_by_date_but_not_by_status = list(set(cfx_closed_status_according_to_date_today) - set(cfx_closed_status))
        assert len(cfx_closed_by_date_but_not_by_status) == 0, f"cfx_closed_by_date_but_not_by_status found: {cfx_closed_by_date_but_not_by_status}"

    def test_CFX00427036_states_by_date(self, create_light_champfx_library: cfx.ChampFXLibrary):
        """
        CFX00427036	no_value	Submitted	8 avril 2019 à 09:23:12 UTC+2	Submit
        CFX00427036	Submitted	Analysed	8 avril 2019 à 09:38:13 UTC+2	Analyse
        CFX00427036	Analysed	Resolved	24 octobre 2019 à 14:04:32 UTC+2	Resolve
        CFX00427036	Resolved	Submitted	11 juin 2020 à 15:17:03 UTC+2	ReSubmit
        CFX00427036	Submitted	Analysed	17 juin 2020 à 16:28:33 UTC+2	Analyse
        CFX00427036	Analysed	Resolved	17 juin 2020 à 16:29:18 UTC+2	Resolve
        CFX00427036	Resolved	Submitted	26 juin 2020 à 14:11:12 UTC+2	ReSubmit
        CFX00427036	Submitted	Analysed	1 juillet 2020 à 12:24:13 UTC+2	Analyse
        CFX00427036	Analysed	Resolved	1 juillet 2020 à 12:27:06 UTC+2	Resolve
        CFX00427036	Resolved	Submitted	12 août 2020 à 09:44:44 UTC+2	ReSubmit
        CFX00427036	Submitted	Analysed	13 août 2020 à 15:46:09 UTC+2	Analyse
        CFX00427036	Analysed	Submitted	2 décembre 2020 à 14:07:57 UTC+1	ReSubmit
        CFX00427036	Submitted	Analysed	10 mars 2021 à 14:27:56 UTC+1	Analyse
        CFX00427036	Analysed	Resolved	10 mars 2021 à 14:28:17 UTC+1	Resolve
        CFX00427036	Resolved	Verified	22 mars 2022 à 16:43:52 UTC+1	Verify
        CFX00427036	Verified	Validated	16 août 2022 à 14:59:51 UTC+2	Validate
        CFX00427036	Validated	Closed	17 août 2022 à 16:06:16 UTC+2	Close
        """
        champfx_library = create_light_champfx_library

        # Opened 08/04/2019 09:23:09
        day_before_first_opening = datetime(int(2019), int(4), int(7))
        day_after_first_analyzis = datetime(int(2019), int(4), int(9))
        day_before_second_opening_first_resubmit = datetime(int(2020), int(6), int(25))
        day_after_second_opening_first_resubmit = datetime(int(2020), int(6), int(27))
        day_before_verification = datetime(year=int(2022), month=int(3), day=int(21))
        day_after_verification = datetime(year=int(2022), month=int(3), day=int(23))
        day_before_validation = datetime(year=int(2022), month=int(8), day=int(15))
        day_after_validation = datetime(year=int(2022), month=int(8), day=int(17))

        cfx_entry = champfx_library.get_cfx_by_id("CFX00427036")
        assert cfx_entry.get_state_at_date(day_before_first_opening) == cfx.State.NotCreatedYet
        assert cfx_entry.get_state_at_date(day_after_first_analyzis) == cfx.State.Analysed
        assert cfx_entry.get_state_at_date(day_before_second_opening_first_resubmit) == cfx.State.Resolved
        assert cfx_entry.get_state_at_date(day_after_second_opening_first_resubmit) == cfx.State.Submitted
        assert cfx_entry.get_state_at_date(day_before_verification) == cfx.State.Resolved
        assert cfx_entry.get_state_at_date(day_after_verification) == cfx.State.Verified
        assert cfx_entry.get_state_at_date(day_before_validation) == cfx.State.Verified
        assert cfx_entry.get_state_at_date(day_after_validation) == cfx.State.Validated
        assert cfx_entry.get_state_at_date(datetime.now()) == cfx.State.Closed


class TestCurrentOwner:

    def test_CFX00427036_currenet_owner_by_date(self, create_light_champfx_library: cfx.ChampFXLibrary):
        champfx_library = create_light_champfx_library
        cfx_entry = champfx_library.get_cfx_by_id("CFX00427036")
        assert cfx_entry.get_current_owner_at_date(datetime.now()) == cfx_entry._current_owner
        assert "herve" in cfx_entry.get_current_owner_at_date(datetime.now())._raw_full_name.lower()

    class TestCFX00778656:

        def test_CFX00778656_that_has_never_changed(self, create_light_champfx_library: cfx.ChampFXLibrary):
            """05/01/2024 18:05:35"""
            champfx_library = create_light_champfx_library
            cfx_entry = champfx_library.get_cfx_by_id("CFX00778656")
            assert cfx_entry.get_current_owner_at_date(datetime.now()) == cfx_entry._current_owner
            assert "Renaud".lower() in cfx_entry.get_current_owner_at_date(datetime.now())._raw_full_name.lower()

            day_before_first_opening = datetime(int(2024), int(1), int(4))
            day_after_first_analyzis = datetime(int(2024), int(1), int(6))
            assert cfx_entry.get_current_owner_at_date(day_before_first_opening) is None
            assert "Renaud".lower() in cfx_entry.get_current_owner_at_date(day_after_first_analyzis)._raw_full_name.lower()
