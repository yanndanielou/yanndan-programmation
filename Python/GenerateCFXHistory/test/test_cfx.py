import pytest

from datetime import datetime
from dateutil import relativedelta

from typing import List, Dict

from generatecfxhistory import cfx, role, inputs, filters, dates_generators, constants
from generatecfxhistory.constants import State

# from common import json_encoders


DEFAULT_CHAMPFX_EXTENDED_HISTORY_FILE_FULL_PATH: str = "Input_Downloaded/extended_history_nextats.txt"


@pytest.fixture(scope="session", name="default_cfx_inputs_for_tests_fixture")
def default_cfx_inputs_for_tests() -> inputs.ChampFxInputs:
    return (
        inputs.ChampFxInputsWithFilesBuilder()
        .add_champfx_details_excel_file_full_path("Input_Downloaded/details_project_FR_NEXTEO.xlsx")
        .add_champfx_details_excel_file_full_path("Input_Downloaded/details_project_ATSP.xlsx")
        .add_champfx_states_changes_excel_file_full_path("Input_Downloaded/states_changes_project_FR_NEXTEO.xlsx")
        .add_champfx_states_changes_excel_file_full_path("InInput_Downloadedput/states_changes_project_ATSP.xlsx")
        .add_cfx_extended_history_file_full_path(DEFAULT_CHAMPFX_EXTENDED_HISTORY_FILE_FULL_PATH)
        .set_user_and_role_data_text_file_full_path("Input/role_data_next_ats.txt")
        .build()
    )


@pytest.fixture(scope="session", name="create_champfx_library_only_cfx_closed_by_yda_in_whitelist_fixture")
def create_champfx_library_only_cfx_closed_by_yda_in_whitelist(default_cfx_inputs_for_tests_fixture: inputs.ChampFxInputs) -> cfx.ChampFXLibrary:
    champfx_library = cfx.ChampFXLibrary(
        cfx_inputs=default_cfx_inputs_for_tests_fixture,
        champfx_filters=[filters.ChampFXWhiteListBasedOnFileFilter("Input_for_Tests/CFX_list_ids_closed_yda.txt")],
    )
    return champfx_library


@pytest.fixture(scope="session", name="create_path_champfx_library_fixture")
def create_path_champfx_library() -> cfx.ChampFXLibrary:
    cfx_inputs = (
        inputs.ChampFxInputsWithFilesBuilder()
        .add_champfx_details_excel_file_full_path("Input_Downloaded/details_project_FR_PATH.xlsx")
        .add_champfx_states_changes_excel_file_full_path("Input_Downloaded/states_changes_project_FR_PATH.xlsx")
        .build()
    )

    champfx_library = cfx.ChampFXLibrary(cfx_inputs=cfx_inputs)
    return champfx_library


@pytest.fixture(scope="session", name="create_light_champfx_library_fixture")
def create_light_champfx_library(default_cfx_inputs_for_tests_fixture: inputs.ChampFxInputs) -> cfx.ChampFXLibrary:

    champfx_library = cfx.ChampFXLibrary(
        cfx_inputs=default_cfx_inputs_for_tests_fixture,
        champfx_filters=[filters.ChampFXWhiteListBasedOnFileFilter(cfx_to_treat_whitelist_text_file_full_path="Input_for_Tests/sample_cfx_ids.txt")],
    )
    return champfx_library


@pytest.fixture(scope="session", name="create_full_champfx_library_fixture")
def create_full_champfx_library(default_cfx_inputs_for_tests_fixture: inputs.ChampFxInputs) -> cfx.ChampFXLibrary:
    champfx_library = cfx.ChampFXLibrary(
        cfx_inputs=default_cfx_inputs_for_tests_fixture,
    )
    return champfx_library


@pytest.fixture(scope="session", name="create_other_projects_partial_champfx_library_fixture")
def create_other_projects_partial_champfx_library() -> cfx.ChampFXLibrary:
    cfx_inputs = (
        inputs.ChampFxInputsWithFilesBuilder()
        .add_champfx_details_excel_files_by_directory_and_file_name_mask(directory_path="Input_Downloaded", filename_pattern="details_project_other_projects.xlsx")
        .add_champfx_states_changes_excel_files_by_directory_and_file_name_mask(directory_path="Input_Downloaded", filename_pattern="states_changes_other_projects.xlsx")
        .build()
    )
    champfx_library = cfx.ChampFXLibrary(
        cfx_inputs=cfx_inputs,
        champfx_filters=[filters.ChampFXWhiteListBasedOnListFilter(cfx_to_treat_ids=["CFX00708313", "CFX00388493", "CFX00388494", "CFX00388495", "CFX00388496", "CFX00388497", "CFX00388498"])],
        allow_cfx_creation_errors=True,
    )
    return champfx_library


@pytest.fixture(scope="session", name="create_other_projects_full_champfx_library_fixture")
def create_other_projects_full_champfx_library() -> cfx.ChampFXLibrary:
    cfx_inputs = (
        inputs.ChampFxInputsWithFilesBuilder()
        .add_champfx_details_excel_files_by_directory_and_file_name_mask(directory_path="Input_Downloaded", filename_pattern="details_project_other_projects.xlsx")
        .add_champfx_states_changes_excel_files_by_directory_and_file_name_mask(directory_path="Input_Downloaded", filename_pattern="states_changes_other_projects.xlsx")
        .build()
    )
    champfx_library = cfx.ChampFXLibrary(cfx_inputs=cfx_inputs, allow_cfx_creation_errors=True)
    return champfx_library


@pytest.fixture(scope="session", name="get_cfx_closed_status_according_to_date_today_fixture")
def get_cfx_closed_status_according_to_date_today(create_light_champfx_library_fixture: cfx.ChampFXLibrary) -> List[cfx.ChampFXEntry]:
    return create_light_champfx_library_fixture.get_cfx_by_state_at_date(reference_date=datetime.now().replace(hour=23, minute=59, second=59, microsecond=0, tzinfo=None))[State.CLOSED]


class TestConstructLibraryWithChampFXWhiteListBasedOnListFilter:
    def test_only_expected_cfx_are_created(self) -> None:
        cfx_inputs = (
            inputs.ChampFxInputsWithFilesBuilder()
            .add_champfx_details_excel_files_by_directory_and_file_name_mask(directory_path="Input_Downloaded", filename_pattern="details_project_other_projects.xlsx")
            .build()
        )
        cfx_ids_to_keep = ["CFX00708313", "CFX00388493", "CFX00388494", "CFX00388495", "CFX00388496", "CFX00388497", "CFX00388498"]
        champfx_library = cfx.ChampFXLibrary(
            cfx_inputs=cfx_inputs,
            champfx_filters=[filters.ChampFXWhiteListBasedOnListFilter(cfx_to_treat_ids=cfx_ids_to_keep)],
            allow_cfx_creation_errors=True,
        )
        assert len(champfx_library.get_all_cfx_ids()) == len(cfx_ids_to_keep)
        for cfx_id_to_keep in cfx_ids_to_keep:
            assert cfx_id_to_keep in champfx_library.get_all_cfx_ids()
            assert champfx_library.get_cfx_by_id(cfx_id_to_keep)

    def test_other_cfx_that_produce_exception_are_not_even_treated_for_speed(self) -> None:
        cfx_inputs = (
            inputs.ChampFxInputsWithFilesBuilder()
            .add_champfx_details_excel_files_by_directory_and_file_name_mask(directory_path="Input_Downloaded", filename_pattern="details_project_other_projects.xlsx")
            .build()
        )
        cfx_ids_to_keep = ["CFX00708313"]
        champfx_library = cfx.ChampFXLibrary(
            cfx_inputs=cfx_inputs,
            champfx_filters=[filters.ChampFXWhiteListBasedOnListFilter(cfx_to_treat_ids=cfx_ids_to_keep)],
            allow_cfx_creation_errors=False,
        )
        assert not champfx_library.failed_to_create_cfx_ids


class TestConstructionLightLibrary:
    def test_no_error_at_init(self, create_light_champfx_library_fixture: cfx.ChampFXLibrary) -> None:
        champfx_library = create_light_champfx_library_fixture
        assert len(champfx_library.get_all_cfx()) > 0
        assert len(champfx_library.failed_to_create_cfx_ids) == 0


class TestConstructionFullLibrary:
    def test_no_error_at_init(self, create_full_champfx_library_fixture: cfx.ChampFXLibrary) -> None:
        champfx_library = create_full_champfx_library_fixture
        assert len(champfx_library.get_all_cfx()) > 0
        assert len(champfx_library.failed_to_create_cfx_ids) == 0

    def test_no_cfx_creation_has_failed(self, default_cfx_inputs_for_tests_fixture: inputs.ChampFxInputs) -> None:
        champfx_library = cfx.ChampFXLibrary(cfx_inputs=default_cfx_inputs_for_tests_fixture, allow_cfx_creation_errors=True)
        assert len(champfx_library.get_all_cfx()) > 0
        assert len(champfx_library.failed_to_create_cfx_ids) == 0


class TestStatus:
    def test_library_is_not_empty(self, create_light_champfx_library_fixture: cfx.ChampFXLibrary) -> None:
        champfx_library = create_light_champfx_library_fixture
        assert len(champfx_library.get_all_cfx()) > 0

    def test_cfx00333232_that_has_never_changed_state_by_date(self, create_path_champfx_library_fixture: cfx.ChampFXLibrary) -> None:
        """We use PATH and very old CFX so it won't change in the future"""
        champfx_library = create_path_champfx_library_fixture
        cfx00333232 = champfx_library.get_cfx_by_id("CFX00333232")
        # Submit date: 24/02/2017 16:16:59
        assert cfx00333232
        cfx00333232._all_change_state_actions_sorted_chronologically.clear()
        cfx00333232._all_change_state_actions_sorted_reversed_chronologically.clear()
        assert not cfx00333232.get_all_change_state_actions_sorted_chronologically()  # Test only makes sense if the cfx hasn't changed
        assert not cfx00333232.get_all_change_state_actions_sorted_reversed_chronologically()  # Test only makes sense if the cfx hasn't changed
        assert cfx00333232.get_state_at_date(datetime(2017, 2, 23)) == State.NOT_CREATED_YET
        assert cfx00333232.get_state_at_date(datetime(2017, 2, 26)) == State.SUBMITTED
        assert cfx00333232.get_state_at_date(datetime(2017, 2, 25)) == State.SUBMITTED
        assert cfx00333232.get_state_at_date(datetime.now()) == State.SUBMITTED  # Test only makes sense if the cfx hasn't changed

    def test_there_are_cfx_current_status_closed(self, create_light_champfx_library_fixture: cfx.ChampFXLibrary) -> None:
        champfx_library = create_light_champfx_library_fixture
        cfx_closed_status = list(filter(lambda champfx: champfx.raw_state == State.CLOSED, champfx_library.get_all_cfx()))
        assert len(cfx_closed_status) > 0

    def test_there_are_cfx_closed_by_date(self, get_cfx_closed_status_according_to_date_today_fixture: List[cfx.ChampFXEntry]) -> None:
        cfx_closed_status_according_to_date_today = get_cfx_closed_status_according_to_date_today_fixture
        assert len(cfx_closed_status_according_to_date_today) > 0

    def test_all_cfx_current_status_closed_are_also_closed_by_date(
        self, create_light_champfx_library_fixture: cfx.ChampFXLibrary, get_cfx_closed_status_according_to_date_today_fixture: List[cfx.ChampFXEntry]
    ) -> None:
        champfx_library = create_light_champfx_library_fixture
        cfx_closed_status_according_to_date_today = get_cfx_closed_status_according_to_date_today_fixture

        cfx_closed_status = list(filter(lambda champfx: champfx.raw_state == State.CLOSED, champfx_library.get_all_cfx()))

        cfx_closed_by_status_but_not_by_date = list(set(cfx_closed_status) - set(cfx_closed_status_according_to_date_today))
        assert len(cfx_closed_by_status_but_not_by_date) == 0

    def test_errors_related_to_closed_status(self, create_light_champfx_library_fixture: cfx.ChampFXLibrary, get_cfx_closed_status_according_to_date_today_fixture: List[cfx.ChampFXEntry]) -> None:
        champfx_library = create_light_champfx_library_fixture

        cfx_closed_status_according_to_date_today = get_cfx_closed_status_according_to_date_today_fixture
        assert len(cfx_closed_status_according_to_date_today) > 0

        cfx_closed_status = list(filter(lambda champfx: champfx.raw_state == State.CLOSED, champfx_library.get_all_cfx()))

        cfx_closed_by_date_but_not_by_status = list(set(cfx_closed_status_according_to_date_today) - set(cfx_closed_status))
        assert len(cfx_closed_by_date_but_not_by_status) == 0, f"cfx_closed_by_date_but_not_by_status found: {cfx_closed_by_date_but_not_by_status}"

    def test_cfx00708313_states_by_date(self, create_other_projects_partial_champfx_library_fixture: cfx.ChampFXLibrary) -> None:
        champfx_library = create_other_projects_partial_champfx_library_fixture
        cfx_entry = champfx_library.get_cfx_by_id("CFX00708313")
        # Submit date: 10/03/2023 18:20:12
        """
        CFXID	history.old_state	history.new_state	history.action_timestamp	history.action_name
        CFX00708313	Submitted	Analysed	13 mars 2023 à 08:18:43 UTC+1	Analyse
        CFX00708313	Analysed	Postponed	21 mars 2023 à 10:40:20 UTC+1	Postpone
        CFX00708313	no_value	Submitted	10 mars 2023 à 18:59:07 UTC+1	Submit        
        """

        assert cfx_entry.get_state_at_date(datetime(2023, 3, 9)) == State.NOT_CREATED_YET
        assert cfx_entry.get_state_at_date(datetime(2023, 3, 11)) == State.SUBMITTED
        assert cfx_entry.get_state_at_date(datetime(2023, 3, 11)) == State.SUBMITTED
        assert cfx_entry.get_state_at_date(datetime(2023, 3, 14)) == State.ANALYSED
        assert cfx_entry.get_state_at_date(datetime(2023, 3, 22)) == State.POSTPONED
        assert cfx_entry.get_state_at_date(datetime(2025, 8, 20)) == State.POSTPONED

    def test_cfx00427036_states_by_date(self, create_light_champfx_library_fixture: cfx.ChampFXLibrary) -> None:
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
        champfx_library = create_light_champfx_library_fixture

        # Opened 08/04/2019 09:23:09
        day_before_first_opening = datetime(2019, 4, 7)
        day_after_first_analyzis = datetime(2019, 4, 9)
        day_before_second_opening_first_resubmit = datetime(2020, 6, 25)
        day_after_second_opening_first_resubmit = datetime(2020, 6, 27)
        day_before_verification = datetime(year=2022, month=3, day=21)
        day_after_verification = datetime(year=2022, month=3, day=23)
        day_before_validation = datetime(year=2022, month=8, day=15)
        day_after_validation = datetime(year=2022, month=8, day=17)

        cfx_entry = champfx_library.get_cfx_by_id("CFX00427036")
        assert cfx_entry.get_state_at_date(day_before_first_opening) == State.NOT_CREATED_YET
        assert cfx_entry.get_state_at_date(day_after_first_analyzis) == State.ANALYSED
        assert cfx_entry.get_state_at_date(day_before_second_opening_first_resubmit) == State.RESOLVED
        assert cfx_entry.get_state_at_date(day_after_second_opening_first_resubmit) == State.SUBMITTED
        assert cfx_entry.get_state_at_date(day_before_verification) == State.RESOLVED
        assert cfx_entry.get_state_at_date(day_after_verification) == State.VERIFIED
        assert cfx_entry.get_state_at_date(day_before_validation) == State.VERIFIED
        assert cfx_entry.get_state_at_date(day_after_validation) == State.VALIDATED
        assert cfx_entry.get_state_at_date(datetime.now()) == State.CLOSED


class TestFirstCurrentOwner:

    def test_CFX00778656_first_current_owner(self, create_light_champfx_library_fixture: cfx.ChampFXLibrary) -> None:
        champfx_library = create_light_champfx_library_fixture
        cfx_entry = champfx_library.get_cfx_by_id("CFX00778656")
        assert cfx_entry
        first_current_owner = cfx_entry.get_current_owner_at_date(datetime(int(2024), int(1), int(6)))
        assert first_current_owner
        assert first_current_owner != role.UNKNOWN_USER
        assert "enaud" in first_current_owner.raw_full_name
        assert first_current_owner.subsystem == role.SubSystem.ATS


class TestSubsystem:
    def test_cfx00688257_that_has_been_rejected_and_closed(self, create_light_champfx_library_fixture: cfx.ChampFXLibrary) -> None:
        champfx_library = create_light_champfx_library_fixture
        cfx_entry = champfx_library.get_cfx_by_id("CFX00688257")
        assert cfx_entry._subsystem == role.SubSystem.ADONEM

    def test_cfx00822357_that_has_been_fixed_and_closed(self, create_light_champfx_library_fixture: cfx.ChampFXLibrary) -> None:
        champfx_library = create_light_champfx_library_fixture
        cfx_entry = champfx_library.get_cfx_by_id("CFX00822357")
        assert cfx_entry._subsystem == role.SubSystem.ADONEM

    def test_cfx00826404_that_has_not_changed(self, create_light_champfx_library_fixture: cfx.ChampFXLibrary) -> None:
        champfx_library = create_light_champfx_library_fixture
        cfx_entry = champfx_library.get_cfx_by_id("CFX00826404")
        assert cfx_entry._subsystem == role.SubSystem.RESEAU

    def test_reseau_19th_august_2025(self, create_full_champfx_library_fixture: cfx.ChampFXLibrary) -> None:

        all_cfx_to_check_ids = ["CFX00886383", "CFX00886386", "CFX00886390", "CFX00886391"]

        champfx_library = create_full_champfx_library_fixture
        cfx_filter = cfx.ChampFxFilter(field_filters=[filters.ChampFxFilterFieldSubsystem(field_accepted_values=[role.SubSystem.RESEAU])])
        cfx_filters = [cfx_filter]

        assert all_cfx_to_check_ids
        for cfx_to_check_id in all_cfx_to_check_ids:
            cfx_request = champfx_library.get_cfx_by_id(cfx_to_check_id)
            assert cfx_request._subsystem == role.SubSystem.RESEAU
            assert cfx_filter.match_cfx_entry(cfx_request)

        date_19th_august_2025 = datetime(year=int(2025), month=int(8), day=int(19))
        dates_generator = dates_generators.SpecificForTestsDatesGenerator([date_19th_august_2025])

        all_results_to_display = champfx_library.gather_state_counts_for_each_date(cfx_filters=cfx_filters, dates_generator=dates_generator)

        intersection = all_results_to_display.all_cfx_ids_that_have_matched.intersection(all_cfx_to_check_ids)
        assert len(intersection) == len(all_cfx_to_check_ids)

        result_19th_august_2025 = all_results_to_display.get_state_counts_per_timestamp()[0]
        assert bool(result_19th_august_2025)

        assert result_19th_august_2025[State.SUBMITTED] == 52, result_19th_august_2025
        assert result_19th_august_2025[State.ANALYSED] == 10, result_19th_august_2025
        assert result_19th_august_2025[State.ASSIGNED] == 5, result_19th_august_2025
        assert result_19th_august_2025[State.RESOLVED] == 8, result_19th_august_2025
        assert result_19th_august_2025[State.POSTPONED] == 0, result_19th_august_2025
        assert result_19th_august_2025[State.REJECTED] == 5, result_19th_august_2025
        assert result_19th_august_2025[State.VERIFIED] == 0, result_19th_august_2025
        assert result_19th_august_2025[State.VALIDATED] == 0, result_19th_august_2025
        assert result_19th_august_2025[State.CLOSED] == 49, result_19th_august_2025


class TestRoleOnDate:
    def test_role_ats_CFX00862371(self, default_cfx_inputs_for_tests_fixture: inputs.ChampFxInputs) -> None:
        champfx_library = cfx.ChampFXLibrary(
            cfx_inputs=default_cfx_inputs_for_tests_fixture,
            champfx_filters=[filters.ChampFXWhiteListBasedOnListFilter(cfx_to_treat_ids=["CFX00862371"])],
        )
        cfx_entry = champfx_library.get_cfx_by_id("CFX00862371")
        assert cfx_entry.get_current_role_at_date(datetime(int(2025), int(3), int(22))) == role.SubSystem.ATS
        assert cfx_entry.get_current_role_at_date(datetime(int(2025), int(3), int(25))) == role.SubSystem.ATS
        assert cfx_entry.get_current_role_at_date(datetime(int(2025), int(3), int(30))) == role.SubSystem.ATS
        assert cfx_entry.get_current_role_at_date(datetime.now()) == role.SubSystem.PROJET


class TestCurrentRoleAtDate:

    def test_all_std_cfx_7th_june_2025(self, create_full_champfx_library_fixture: cfx.ChampFXLibrary) -> None:
        champfx_library = create_full_champfx_library_fixture

        date_4th_june_2025 = datetime(year=int(2025), month=int(6), day=int(4))
        date_5th_june_2025 = datetime(year=int(2025), month=int(6), day=int(5))
        date_6th_june_2025 = datetime(year=int(2025), month=int(6), day=int(6))
        date_7th_june_2025 = datetime(year=int(2025), month=int(6), day=int(7))
        date_8th_june_2025 = datetime(year=int(2025), month=int(6), day=int(8))

        all_cfx_reseau_7th_june = []

        current_owner_by_cfx_id_at_7th_june_2025: Dict[str, role.CfxUser] = {}
        current_owner_full_name_by_cfx_id_at_7th_june_2025: Dict[str, str] = {}
        current_owner_subsystem_by_cfx_id_at_7th_june_2025: Dict[str, role.SubSystem] = {}
        cfx_id_by_current_owner_at_7th_june_2025: Dict[role.CfxUser, List[str]] = {}
        cfx_id_by_current_owner_full_name_at_7th_june_2025: Dict[str, List[str]] = {}
        cfx_id_by_current_owner_subsystem_at_7th_june_2025: Dict[role.SubSystem, List[str]] = {}

        all_cfx_that_were_not_created_at_that_time: List[cfx.ChampFXEntry] = []

        for cfx_entry in champfx_library.get_all_cfx():
            current_owner_7th_june_2025 = cfx_entry.get_current_owner_at_date(date_7th_june_2025)

            if current_owner_7th_june_2025:
                current_owner_by_cfx_id_at_7th_june_2025[cfx_entry.cfx_identifier] = current_owner_7th_june_2025
                current_owner_full_name_by_cfx_id_at_7th_june_2025[cfx_entry.cfx_identifier] = current_owner_7th_june_2025.full_name
                current_owner_subsystem_by_cfx_id_at_7th_june_2025[cfx_entry.cfx_identifier] = current_owner_7th_june_2025.subsystem.name

                if current_owner_7th_june_2025 not in cfx_id_by_current_owner_at_7th_june_2025:
                    cfx_id_by_current_owner_at_7th_june_2025[current_owner_7th_june_2025] = []
                cfx_id_by_current_owner_at_7th_june_2025[current_owner_7th_june_2025].append(cfx_entry.cfx_identifier)

                if current_owner_7th_june_2025.subsystem.name not in cfx_id_by_current_owner_subsystem_at_7th_june_2025:
                    cfx_id_by_current_owner_subsystem_at_7th_june_2025[current_owner_7th_june_2025.subsystem.name] = []
                cfx_id_by_current_owner_subsystem_at_7th_june_2025[current_owner_7th_june_2025.subsystem.name].append(cfx_entry.cfx_identifier)

                if current_owner_7th_june_2025.full_name not in cfx_id_by_current_owner_full_name_at_7th_june_2025:
                    cfx_id_by_current_owner_full_name_at_7th_june_2025[current_owner_7th_june_2025.full_name] = []
                cfx_id_by_current_owner_full_name_at_7th_june_2025[current_owner_7th_june_2025.full_name].append(cfx_entry.cfx_identifier)

            else:
                print(f"{cfx_entry.cfx_identifier} was not created at that time, it was submitted {cfx_entry.submit_date}")
                assert cfx_entry.submit_date > date_7th_june_2025
                all_cfx_that_were_not_created_at_that_time.append(cfx_entry)

            print(f"{len(all_cfx_that_were_not_created_at_that_time)} were not created at that time")

        # json_encoders.JsonEncodersUtils.serialize_list_objects_in_json(current_owner_full_name_by_cfx_id_at_7th_june_2025, "output/current_owner_full_name_by_cfx_id_at_7th_june_2025.json")
        # json_encoders.JsonEncodersUtils.serialize_list_objects_in_json(current_owner_subsystem_by_cfx_id_at_7th_june_2025, "output/current_owner_subsystem_by_cfx_id_at_7th_june_2025.json")
        # json_encoders.JsonEncodersUtils.serialize_list_objects_in_json(cfx_id_by_current_owner_full_name_at_7th_june_2025, "output/cfx_id_by_current_owner_full_name_at_7th_june_2025.json")
        # json_encoders.JsonEncodersUtils.serialize_list_objects_in_json(cfx_id_by_current_owner_subsystem_at_7th_june_2025, "output/cfx_id_by_current_owner_subsystem_at_7th_june_2025.json")

        role_depending_on_date_filter = filters.ChampFXRoleDependingOnDateFilter(roles_at_date_allowed=([role.SubSystem.RESEAU]))
        for cfx_entry in champfx_library.get_all_cfx():
            if role_depending_on_date_filter.match_cfx_entry(cfx_entry=cfx_entry, timestamp=date_7th_june_2025):
                all_cfx_reseau_7th_june.append(cfx_entry)

        assert len(all_cfx_reseau_7th_june) == 90

        all_results = champfx_library.gather_state_counts_for_each_date(
            cfx_filters=[cfx.ChampFxFilter(role_depending_on_date_filter)],
            dates_generator=dates_generators.SpecificForTestsDatesGenerator([date_4th_june_2025, date_5th_june_2025, date_6th_june_2025, date_7th_june_2025, date_8th_june_2025]),
        )

        assert not all_results.is_empty()

        assert all_results.get_state_counts_per_timestamp()

        result_4th_june_2025: cfx.AllResultsPerDatesWithDebugDetails = champfx_library.gather_state_counts_for_each_date(
            cfx_filters=[cfx.ChampFxFilter(role_depending_on_date_filter)],
            dates_generator=dates_generators.SpecificForTestsDatesGenerator([date_4th_june_2025]),
        )
        result_4th_june_2025_cfx_ids = result_4th_june_2025.all_cfx_ids_that_have_matched

        result_5th_june_2025: cfx.AllResultsPerDatesWithDebugDetails = champfx_library.gather_state_counts_for_each_date(
            cfx_filters=[cfx.ChampFxFilter(role_depending_on_date_filter)],
            dates_generator=dates_generators.SpecificForTestsDatesGenerator([date_5th_june_2025]),
        )
        result_5th_june_2025_cfx_ids = result_5th_june_2025.all_cfx_ids_that_have_matched

        result_6th_june_2025: cfx.AllResultsPerDatesWithDebugDetails = champfx_library.gather_state_counts_for_each_date(
            cfx_filters=[cfx.ChampFxFilter(role_depending_on_date_filter)],
            dates_generator=dates_generators.SpecificForTestsDatesGenerator([date_6th_june_2025]),
        )
        result_6th_june_2025_cfx_ids = result_6th_june_2025.all_cfx_ids_that_have_matched

        result_7th_june_2025: cfx.AllResultsPerDatesWithDebugDetails = champfx_library.gather_state_counts_for_each_date(
            cfx_filters=[cfx.ChampFxFilter(role_depending_on_date_filter)],
            dates_generator=dates_generators.SpecificForTestsDatesGenerator([date_7th_june_2025]),
        )
        result_7th_june_2025_cfx_ids = result_7th_june_2025.all_cfx_ids_that_have_matched

        result_8th_june_2025: cfx.AllResultsPerDatesWithDebugDetails = champfx_library.gather_state_counts_for_each_date(
            cfx_filters=[cfx.ChampFxFilter(role_depending_on_date_filter)],
            dates_generator=dates_generators.SpecificForTestsDatesGenerator([date_8th_june_2025]),
        )
        result_8th_june_2025_cfx_ids = result_8th_june_2025.all_cfx_ids_that_have_matched

        all_cfx_ids_of_concerned_days = result_4th_june_2025_cfx_ids.union(result_5th_june_2025_cfx_ids, result_6th_june_2025_cfx_ids, result_7th_june_2025_cfx_ids, result_8th_june_2025_cfx_ids)

        print("all_cfx_ids_of_concerned_days:")
        print(all_cfx_ids_of_concerned_days)

        assert bool(result_4th_june_2025)
        assert bool(result_5th_june_2025)
        assert bool(result_6th_june_2025)
        assert bool(result_7th_june_2025)

        assert len(all_cfx_reseau_7th_june) == sum(result_7th_june_2025.get_state_counts_per_timestamp()[0].values())

        assert result_4th_june_2025.get_state_counts_per_timestamp()[0][State.SUBMITTED] == 26
        assert result_5th_june_2025.get_state_counts_per_timestamp()[0][State.SUBMITTED] == 26
        assert result_6th_june_2025.get_state_counts_per_timestamp()[0][State.SUBMITTED] == 57
        assert result_7th_june_2025.get_state_counts_per_timestamp()[0][State.SUBMITTED] == 61
        assert result_8th_june_2025.get_state_counts_per_timestamp()[0][State.SUBMITTED] == 61

    def test_all_std_cfx_19th_august_2025(self, create_full_champfx_library_fixture: cfx.ChampFXLibrary) -> None:
        champfx_library = create_full_champfx_library_fixture

        date_19th_august_2025 = datetime(year=int(2025), month=int(8), day=int(19))

        role_depending_on_date_filter = filters.ChampFXRoleDependingOnDateFilter(roles_at_date_allowed=([role.SubSystem.RESEAU]))

        all_results = champfx_library.gather_state_counts_for_each_date(
            cfx_filters=[cfx.ChampFxFilter(role_depending_on_date_filter)],
            dates_generator=dates_generators.SpecificForTestsDatesGenerator([date_19th_august_2025]),
        )
        assert not all_results.is_empty()

        assert all_results.get_state_counts_per_timestamp()

        result_19th_august_2025 = all_results.get_state_counts_per_timestamp()[0]

        assert bool(result_19th_august_2025)

        assert result_19th_august_2025[State.SUBMITTED] == 54
        assert result_19th_august_2025[State.ANALYSED] == 10
        assert result_19th_august_2025[State.ASSIGNED] == 5
        assert result_19th_august_2025[State.VERIFIED] == 0
        assert result_19th_august_2025[State.RESOLVED] == 0
        assert result_19th_august_2025[State.REJECTED] == 5
        assert result_19th_august_2025[State.POSTPONED] == 1
        assert result_19th_august_2025[State.CLOSED] == 4


class TestAllCfxAreCreated:
    def test_all_cfx_creation(self, create_full_champfx_library_fixture: cfx.ChampFXLibrary) -> None:
        champfx_library = create_full_champfx_library_fixture
        assert "CFX00785515" in champfx_library.get_all_cfx_ids()


class TestCurrentOwner:

    def test_cfx00875545_current_owner_at_creation(self, create_light_champfx_library_fixture: cfx.ChampFXLibrary) -> None:
        champfx_library = create_light_champfx_library_fixture
        cfx_entry = champfx_library.get_cfx_by_id("CFX00875545")
        assert cfx_entry
        date_6th_june_2025 = datetime(year=int(2025), month=int(6), day=int(6))
        current_owner_just_after_creation = cfx_entry.get_current_owner_at_date(date_6th_june_2025)
        assert current_owner_just_after_creation
        assert "livia" in current_owner_just_after_creation.full_name
        assert current_owner_just_after_creation.subsystem == role.SubSystem.RESEAU

    def test_cfx00427036_current_owner_by_date(self, create_light_champfx_library_fixture: cfx.ChampFXLibrary) -> None:
        champfx_library = create_light_champfx_library_fixture
        cfx_entry = champfx_library.get_cfx_by_id("CFX00427036")
        assert cfx_entry.get_current_owner_at_date(datetime.now())
        assert cfx_entry.get_current_owner_at_date(datetime.now()) == cfx_entry._current_owner
        assert "herve" in cfx_entry.get_current_owner_at_date(datetime.now())._raw_full_name.lower()

    def test_all_cfx_have_none_current_owner_before_creation(self, create_light_champfx_library_fixture: cfx.ChampFXLibrary) -> None:
        champfx_library = create_light_champfx_library_fixture
        for cfx_entry in champfx_library.get_all_cfx():

            day_before_first_opening = datetime(int(2000), int(1), int(4))
            assert cfx_entry.get_current_owner_at_date(day_before_first_opening) is None

    def test_all_cfx_have_current_owner_which_is_same_as_history(self, create_light_champfx_library_fixture: cfx.ChampFXLibrary) -> None:
        champfx_library = create_light_champfx_library_fixture
        for cfx_entry in champfx_library.get_all_cfx():
            assert cfx_entry._current_owner == cfx_entry.get_current_owner_at_date(datetime.now())

    def test_before_cfx_creation(self, create_light_champfx_library_fixture: cfx.ChampFXLibrary) -> None:
        champfx_library = create_light_champfx_library_fixture
        cfx_entry = champfx_library.get_cfx_by_id("CFX00778656")
        first_current_owner = cfx_entry.get_current_owner_at_date(datetime(int(2000), int(1), int(6)))
        assert first_current_owner is None

    class TestCFX00778656:

        def test_CFX00778656_that_has_never_changed(self, create_light_champfx_library_fixture: cfx.ChampFXLibrary) -> None:
            """05/01/2024 18:05:35"""
            champfx_library = create_light_champfx_library_fixture
            cfx_entry = champfx_library.get_cfx_by_id("CFX00778656")
            assert cfx_entry.get_current_owner_at_date(datetime.now()) == cfx_entry._current_owner
            assert "Renaud".lower() in cfx_entry.get_current_owner_at_date(datetime.now())._raw_full_name.lower()

            day_before_first_opening = datetime(int(2024), int(1), int(4))
            day_after_first_analyzis = datetime(int(2024), int(1), int(6))
            assert cfx_entry.get_current_owner_at_date(day_before_first_opening) is None
            assert "Renaud".lower() in cfx_entry.get_current_owner_at_date(day_after_first_analyzis)._raw_full_name.lower()

    class TestChampFxFilter:
        def test_next_project_field_filter(self, default_cfx_inputs_for_tests_fixture: inputs.ChampFxInputs) -> None:
            nexteo_only_champfx_library = cfx.ChampFXLibrary(
                cfx_inputs=default_cfx_inputs_for_tests_fixture,
                champfx_filters=[filters.ChampFxFilterFieldProject(field_accepted_values=[constants.CfxProject.FR_NEXTEO])],
            )

            assert len(nexteo_only_champfx_library.get_all_cfx()) > 0
            for cfx_entry in nexteo_only_champfx_library.get_all_cfx():
                assert cfx_entry._cfx_project_name == constants.CfxProject.FR_NEXTEO

        def test_two_field_filters(self, create_light_champfx_library_fixture: cfx.ChampFXLibrary) -> None:
            security_and_ats = cfx.ChampFxFilter
            champfx_library = create_light_champfx_library_fixture

            ats_non_security_filter = cfx.ChampFxFilter(
                field_filters=[
                    filters.ChampFxFilterFieldSecurityRelevant(field_forbidden_values=[constants.SecurityRelevant.YES, constants.SecurityRelevant.MITIGATED]),
                    filters.ChampFxFilterFieldSubsystem(field_accepted_values=[role.SubSystem.ATS]),
                ],
            )
            ats_security_filter = cfx.ChampFxFilter(
                field_filters=[
                    filters.ChampFxFilterFieldSecurityRelevant(field_accepted_values=[constants.SecurityRelevant.YES, constants.SecurityRelevant.MITIGATED]),
                    filters.ChampFxFilterFieldSubsystem(field_accepted_values=[role.SubSystem.ATS]),
                ],
            )

            assert ats_non_security_filter.match_cfx_entry(champfx_library.get_cfx_by_id("CFX00427369"))
            assert not ats_non_security_filter.match_cfx_entry(champfx_library.get_cfx_by_id("CFX00831682"))

            assert not ats_security_filter.match_cfx_entry(champfx_library.get_cfx_by_id("CFX00427369"))
            assert ats_security_filter.match_cfx_entry(champfx_library.get_cfx_by_id("CFX00831682"))

        def test_get_sub_system_method_for_filter(self) -> None:
            pass

        def test_security_relevant_only_field_filter(self, default_cfx_inputs_for_tests_fixture: inputs.ChampFxInputs) -> None:
            security_relevant_only_champfx_library = cfx.ChampFXLibrary(
                cfx_inputs=default_cfx_inputs_for_tests_fixture,
                champfx_filters=[filters.ChampFxFilterFieldSecurityRelevant(field_accepted_values=[constants.SecurityRelevant.YES, constants.SecurityRelevant.MITIGATED])],
            )

            assert len(security_relevant_only_champfx_library.get_all_cfx()) > 0
            for cfx_entry in security_relevant_only_champfx_library.get_all_cfx():
                assert cfx_entry._security_relevant


class TestIncompleteCFXAreNotCreated:
    def test_cfx_with_no_type(self) -> None:
        "details_project_CHAMP"
        expected_incomplete_cfx_ids = [
            "CFX00651637",
            "CFX00421683",
            "CFX00569313",
            "CFX00625909",
            "CFX00786926",
            "CFX00873434",
            "CFX00886160",
            "CFX00864282",
        ]
        cfx_inputs = (
            inputs.ChampFxInputsWithFilesBuilder()
            .add_champfx_details_excel_file_full_path("Input_Downloaded/details_project_CHAMP.xlsx")
            .add_champfx_details_excel_file_full_path("Input_Downloaded/details_project_TrashCan.xlsx")
            .add_champfx_details_excel_file_full_path("Input_Downloaded/details_project_UK_Freight.xlsx")
            .add_champfx_details_excel_file_full_path("Input_Downloaded/details_project_Op_LT_D_Proj.xlsx")
            .build()
        )

        champfx_library = cfx.ChampFXLibrary(cfx_inputs=cfx_inputs, allow_cfx_creation_errors=True)
        assert champfx_library.get_all_cfx()
        assert champfx_library.failed_to_create_cfx_ids
        for expected_incomplete_cfx_id in expected_incomplete_cfx_ids:
            assert expected_incomplete_cfx_id in champfx_library.failed_to_create_cfx_ids

    def test_cfx_with_no_submit_date_fpts(self) -> None:
        "details_project_CHAMP"
        expected_incomplete_cfx_ids = [
            "CFX00630301",
            "CFX00630298",
        ]
        cfx_inputs = inputs.ChampFxInputsWithFilesBuilder().add_champfx_details_excel_file_full_path("Input_Downloaded/details_project_DE_FPTS.xlsx").build()

        champfx_library = cfx.ChampFXLibrary(cfx_inputs=cfx_inputs, allow_cfx_creation_errors=True)
        assert champfx_library.get_all_cfx()
        assert champfx_library.failed_to_create_cfx_ids
        for expected_incomplete_cfx_id in expected_incomplete_cfx_ids:
            assert expected_incomplete_cfx_id in champfx_library.failed_to_create_cfx_ids


class TestFullDatabase:
    def test_all_system_structure(self, create_full_champfx_library_fixture: cfx.ChampFXLibrary) -> None:
        champfx_library = create_full_champfx_library_fixture
        for cfx_entry in champfx_library.get_all_cfx():
            assert cfx_entry._system_structure_subsystem

    def test_all_cfx_have_submit_state_change(self, create_full_champfx_library_fixture: cfx.ChampFXLibrary) -> None:
        champfx_library = create_full_champfx_library_fixture
        for cfx_entry in champfx_library.get_all_cfx():
            assert cfx_entry.get_oldest_change_state_action_by_new_state(State.SUBMITTED, allow_identical_states=False), cfx_entry.cfx_identifier

    def test_all_cfx_have_submit_date(self, create_full_champfx_library_fixture: cfx.ChampFXLibrary) -> None:
        champfx_library = create_full_champfx_library_fixture
        for cfx_entry in champfx_library.get_all_cfx():
            assert cfx_entry.get_oldest_submit_date(allow_identical_states=False), cfx_entry.cfx_identifier


class TestConstantIntervalDatesGenerator:

    def test_with_one_day_interval(self) -> None:
        dates_generator = dates_generators.ConstantIntervalDatesGenerator(time_delta=relativedelta.relativedelta(days=1))
        all_dates = dates_generator._compute_dates_since_until_today(datetime(year=2025, month=7, day=1))
        assert all_dates

    def test_with_no_interval(self) -> None:
        dates_generator = dates_generators.ConstantIntervalDatesGenerator(time_delta=relativedelta.relativedelta(day=1))
        with pytest.raises(AssertionError):
            dates_generator._compute_dates_since_until_today(datetime(year=2025, month=7, day=1))


class TestStatisticsPreparation:

    @pytest.mark.timeout(120)
    def test_gather_state_counts_for_each_date_whithout_filter(self, create_light_champfx_library_fixture: cfx.ChampFXLibrary) -> None:
        champfx_library = create_light_champfx_library_fixture
        champfx_library.gather_state_counts_for_each_date(dates_generators.ConstantIntervalDatesGenerator(time_delta=relativedelta.relativedelta(days=10)))

    @pytest.mark.timeout(120)
    def test_gather_state_counts_for_each_date_whith_filter(self, create_light_champfx_library_fixture: cfx.ChampFXLibrary) -> None:
        champfx_library = create_light_champfx_library_fixture
        champfx_library.gather_state_counts_for_each_date(dates_generators.ConstantIntervalDatesGenerator(time_delta=relativedelta.relativedelta(days=10)))
        champfx_library.gather_state_counts_for_each_date(
            dates_generators.ConstantIntervalDatesGenerator(time_delta=relativedelta.relativedelta(days=10)),
            cfx_filters=[cfx.ChampFxFilter(role_depending_on_date_filter=filters.ChampFXRoleDependingOnDateFilter(roles_at_date_allowed=[role.SubSystem.ATS]))],
        )


class TestStatisticsPreparationRoleDependingOnDate:
    """['CFX00398968', 'CFX00401911', 'CFX00466137', 'CFX00494052', 'CFX00551164', 'CFX00551910', 'CFX00584295', 'CFX00587132', 'CFX00618804', 'CFX00623862', 'CFX00623864', 'CFX00623870', 'CFX00623879', 'CFX00623898', 'CFX00623899', 'CFX00624544', 'CFX00639805', 'CFX00674321', 'CFX00687787', 'CFX00690605', 'CFX00690624', 'CFX00695357', 'CFX00695358', 'CFX00701981', 'CFX00716682', 'CFX00716724', 'CFX00720447', 'CFX00723144', 'CFX00723481', 'CFX00734937', 'CFX00742602', 'CFX00749341', 'CFX00786363', 'CFX00786374', 'CFX00789495', 'CFX00806369', 'CFX00812751', 'CFX00817953', 'CFX00831083', 'CFX00842156', 'CFX00842390', 'CFX00848518', 'CFX00849529', 'CFX00849547', 'CFX00849556', 'CFX00849571', 'CFX00849576']"""

    def test_role_sw_constant_interval(self, create_champfx_library_only_cfx_closed_by_yda_in_whitelist_fixture: cfx.ChampFXLibrary) -> None:
        champfx_library = create_champfx_library_only_cfx_closed_by_yda_in_whitelist_fixture
        all_results_per_date = champfx_library.gather_state_counts_for_each_date(
            dates_generators.ConstantIntervalDatesGenerator(time_delta=relativedelta.relativedelta(days=10)),
            cfx_filters=[
                cfx.ChampFxFilter(
                    role_depending_on_date_filter=filters.ChampFXRoleDependingOnDateFilter(roles_at_date_allowed=[role.SubSystem.SW]),
                    whitelist_filter=filters.ChampFXWhiteListBasedOnListFilter(cfx_to_treat_ids=set(["CFX00398968"])),
                )
            ],
        )
        assert not all_results_per_date.is_empty()

    def test_role_sw_decreasing_interval(self, create_champfx_library_only_cfx_closed_by_yda_in_whitelist_fixture: cfx.ChampFXLibrary) -> None:
        champfx_library = create_champfx_library_only_cfx_closed_by_yda_in_whitelist_fixture
        all_results_per_date = champfx_library.gather_state_counts_for_each_date(
            dates_generators.DecreasingIntervalDatesGenerator(),
            cfx_filters=[cfx.ChampFxFilter(role_depending_on_date_filter=filters.ChampFXRoleDependingOnDateFilter(roles_at_date_allowed=[role.SubSystem.SW]))],
        )
        assert not all_results_per_date.is_empty()

    def test_role_ats_CFX00862371(self, default_cfx_inputs_for_tests_fixture: inputs.ChampFxInputs) -> None:
        champfx_library = cfx.ChampFXLibrary(
            cfx_inputs=default_cfx_inputs_for_tests_fixture,
            champfx_filters=[filters.ChampFXWhiteListBasedOnListFilter(cfx_to_treat_ids=["CFX00862371"])],
        )
        all_results_per_date = champfx_library.gather_state_counts_for_each_date(
            dates_generators.ConstantIntervalDatesGenerator(time_delta=relativedelta.relativedelta(days=2)),
            cfx_filters=[cfx.ChampFxFilter(role_depending_on_date_filter=filters.ChampFXRoleDependingOnDateFilter(roles_at_date_allowed=[role.SubSystem.ATS]))],
        )
        assert not all_results_per_date.is_empty()


class TestBugCFX00882153CoreshieldObSeenUnknownState:
    def test_has_not_unknown_state(self) -> None:
        cfx_inputs = (
            inputs.ChampFxInputsWithFilesBuilder()
            .add_champfx_details_excel_files_by_directory_and_file_name_mask(directory_path="Input_Downloaded", filename_pattern="details_project_other_projects.xlsx")
            .add_champfx_states_changes_excel_files_by_directory_and_file_name_mask(directory_path="Input_Downloaded", filename_pattern="states_changes_other_projects.xlsx")
            .build()
        )
        champfx_library = cfx.ChampFXLibrary(
            cfx_inputs=cfx_inputs,
            champfx_filters=[filters.ChampFXWhiteListBasedOnListFilter(cfx_to_treat_ids=["CFX00882153"])],
        )
        cfx_entry = champfx_library.get_cfx_by_id("CFX00882153")
        # Submit 18/07/2025 14:54:32
        assert cfx_entry.get_state_at_date(datetime(2011, 5, 1, 0, 0)) == State.NOT_CREATED_YET
        assert cfx_entry.get_state_at_date(datetime(2025, 7, 19)) != State.UNKNOWN
        assert cfx_entry.get_state_at_date(datetime(2025, 8, 19)) != State.UNKNOWN


class TestDecreasingIntervalDatesGenerator:

    def test_now(self) -> None:

        list_dates: List[datetime] = dates_generators.DecreasingIntervalDatesGenerator().get_dates_since(datetime.now())
        assert len(list_dates) > 1

    def test_few_values(self) -> None:
        assert len(dates_generators.DecreasingIntervalDatesGenerator().get_dates_since(datetime(int(2000), int(1), int(4)))) > 100


class TestCrashObservedOtherProjects:

    def test_CFX00608002(self, create_other_projects_full_champfx_library_fixture: cfx.ChampFXLibrary) -> None:
        champfx_library = create_other_projects_full_champfx_library_fixture
        earliest_submit_date = cfx.get_earliest_submit_date(champfx_library.get_all_cfx())
        assert earliest_submit_date

    def test_get_earliest_submit_date(self, create_other_projects_partial_champfx_library_fixture: cfx.ChampFXLibrary) -> None:
        champfx_library = create_other_projects_partial_champfx_library_fixture
        assert champfx_library.get_all_cfx()
        earliest_submit_date = cfx.get_earliest_submit_date(champfx_library.get_all_cfx())
        assert earliest_submit_date

    def test_cfx_have_oldest_submit_date(self, create_other_projects_partial_champfx_library_fixture: cfx.ChampFXLibrary) -> None:
        champfx_library = create_other_projects_partial_champfx_library_fixture
        assert champfx_library.get_all_cfx()
        for cfx_entry in champfx_library.get_all_cfx():
            assert cfx_entry.get_oldest_submit_date(allow_identical_states=False), cfx_entry.cfx_identifier


class TestOldClearquestThatWereBeforeChampFx:

    def test_alternative_name(self, create_path_champfx_library_fixture: cfx.ChampFXLibrary) -> None:
        champfx_library = create_path_champfx_library_fixture
        cfx_entry = champfx_library.get_cfx_by_id("CFX00266625")
        assert cfx_entry.alternative_cfx_identifier == "USTS00017567"

    def test_get_earliest_submit_date(self, create_path_champfx_library_fixture: cfx.ChampFXLibrary) -> None:
        champfx_library = create_path_champfx_library_fixture
        earliest_submit_date = cfx.get_earliest_submit_date(champfx_library.get_all_cfx())
        assert earliest_submit_date
        assert earliest_submit_date.year == 2011

    def test_usts00017567_states(self, create_path_champfx_library_fixture: cfx.ChampFXLibrary) -> None:
        champfx_library = create_path_champfx_library_fixture
        cfx_entry = champfx_library.get_cfx_by_id("CFX00266625")
        # Submit date: 30/05/2012 00:00:00
        after_submit_date = datetime(2012, 5, 31)
        assert cfx_entry.get_state_at_date(after_submit_date)
        assert cfx_entry.get_state_at_date(after_submit_date) == State.UNKNOWN

    def test_usts00007543_state_after_submition(self, create_path_champfx_library_fixture: cfx.ChampFXLibrary) -> None:
        champfx_library = create_path_champfx_library_fixture
        cfx_entry = champfx_library.get_cfx_by_id("CFX00267049")
        # Submit date: 11/02/2011 00:00:00
        assert cfx_entry.get_state_at_date(datetime(2011, 5, 1, 0, 0))
        assert cfx_entry.get_state_at_date(datetime(2011, 5, 1, 0, 0)) != State.NOT_CREATED_YET


class TestOldUsts00007543ClearquestThatWereBeforeChampFx:

    # Submit date: 11/02/2011 00:00:00
    """13 juillet 2015 à 22:54:57 UTC+2
    15 juillet 2015 à 16:01:20 UTC+2
    15 juillet 2015 à 16:01:23 UTC+2
    5 août 2015 à 18:36:04 UTC+2
    17 août 2015 à 13:52:53 UTC+2
    20 août 2015 à 17:59:02 UTC+2
    4 septembre 2015 à 18:55:16 UTC+2"""

    def test_state_before_creation(self, create_path_champfx_library_fixture: cfx.ChampFXLibrary) -> None:
        champfx_library = create_path_champfx_library_fixture
        cfx_entry = champfx_library.get_cfx_by_id("CFX00267049")
        assert cfx_entry.get_state_at_date(datetime(2011, 2, 10, 0, 0)) == State.NOT_CREATED_YET

    def test_state_after_creation_before_closing(self, create_path_champfx_library_fixture: cfx.ChampFXLibrary) -> None:
        champfx_library = create_path_champfx_library_fixture
        cfx_entry = champfx_library.get_cfx_by_id("CFX00267049")
        assert cfx_entry.get_state_at_date(datetime(2012, 2, 10, 0, 0)) == State.UNKNOWN

    def test_state_after_closing(self, create_path_champfx_library_fixture: cfx.ChampFXLibrary) -> None:
        champfx_library = create_path_champfx_library_fixture
        cfx_entry = champfx_library.get_cfx_by_id("CFX00267049")
        assert cfx_entry.get_state_at_date(datetime(2016, 2, 10, 0, 0)) == State.CLOSED
