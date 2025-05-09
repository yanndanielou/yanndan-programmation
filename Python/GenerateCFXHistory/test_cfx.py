import pytest

from datetime import datetime
from dateutil import relativedelta

from typing import List

import cfx
import role


@pytest.fixture(scope="session")
def create_champfx_library_only_cfx_closed_by_yda_in_whitelist() -> cfx.ChampFXLibrary:
    champfx_library = cfx.ChampFXLibrary(champfx_filters=[cfx.ChampFXWhitelistFilter("Input/CFX_list_ids_closed_yda.txt")])
    return champfx_library


@pytest.fixture(scope="session")
def create_light_champfx_library() -> cfx.ChampFXLibrary:
    champfx_library = cfx.ChampFXLibrary(
        champfx_filters=[cfx.ChampFXWhitelistFilter(cfx_to_treat_whitelist_text_file_full_path="Input_for_Tests/sample_cfx_ids.txt")],
    )
    return champfx_library


@pytest.fixture(scope="session")
def create_full_champfx_library() -> cfx.ChampFXLibrary:
    champfx_library = cfx.ChampFXLibrary()
    return champfx_library


@pytest.fixture(scope="session")
def get_cfx_closed_status_according_to_date_today(create_light_champfx_library: cfx.ChampFXLibrary) -> List[cfx.ChampFXEntry]:
    return create_light_champfx_library.get_cfx_by_state_at_date(reference_date=datetime.now().replace(hour=23, minute=59, second=59, microsecond=0, tzinfo=None))[cfx.State.CLOSED]


class TestConstruction:
    def test_no_error_at_init(self, create_light_champfx_library: cfx.ChampFXLibrary) -> None:
        champfx_library = create_light_champfx_library
        assert len(champfx_library.get_all_cfx()) > 0


class TestStatus:
    def test_library_is_not_empty(self, create_light_champfx_library: cfx.ChampFXLibrary) -> None:
        champfx_library = create_light_champfx_library
        assert len(champfx_library.get_all_cfx()) > 0

    def test_there_are_cfx_current_status_closed(self, create_light_champfx_library: cfx.ChampFXLibrary) -> None:
        champfx_library = create_light_champfx_library
        cfx_closed_status = list(filter(lambda champfx: champfx.raw_state == cfx.State.CLOSED, champfx_library.get_all_cfx()))
        assert len(cfx_closed_status) > 0

    def test_there_are_cfx_closed_by_date(self, get_cfx_closed_status_according_to_date_today: List[cfx.ChampFXEntry]) -> None:
        cfx_closed_status_according_to_date_today = get_cfx_closed_status_according_to_date_today
        assert len(cfx_closed_status_according_to_date_today) > 0

    def test_all_cfx_current_status_closed_are_also_closed_by_date(
        self, create_light_champfx_library: cfx.ChampFXLibrary, get_cfx_closed_status_according_to_date_today: List[cfx.ChampFXEntry]
    ) -> None:
        champfx_library = create_light_champfx_library
        cfx_closed_status_according_to_date_today = get_cfx_closed_status_according_to_date_today

        cfx_closed_status = list(filter(lambda champfx: champfx.raw_state == cfx.State.CLOSED, champfx_library.get_all_cfx()))

        cfx_closed_by_status_but_not_by_date = list(set(cfx_closed_status) - set(cfx_closed_status_according_to_date_today))
        assert len(cfx_closed_by_status_but_not_by_date) == 0

    def test_errors_related_to_closed_status(self, create_light_champfx_library: cfx.ChampFXLibrary, get_cfx_closed_status_according_to_date_today: List[cfx.ChampFXEntry]) -> None:
        champfx_library = create_light_champfx_library

        cfx_closed_status_according_to_date_today = get_cfx_closed_status_according_to_date_today
        assert len(cfx_closed_status_according_to_date_today) > 0

        cfx_closed_status = list(filter(lambda champfx: champfx.raw_state == cfx.State.CLOSED, champfx_library.get_all_cfx()))

        cfx_closed_by_date_but_not_by_status = list(set(cfx_closed_status_according_to_date_today) - set(cfx_closed_status))
        assert len(cfx_closed_by_date_but_not_by_status) == 0, f"cfx_closed_by_date_but_not_by_status found: {cfx_closed_by_date_but_not_by_status}"

    def test_CFX00427036_states_by_date(self, create_light_champfx_library: cfx.ChampFXLibrary) -> None:
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
        assert cfx_entry.get_state_at_date(day_before_first_opening) == cfx.State.NOT_CREATED_YET
        assert cfx_entry.get_state_at_date(day_after_first_analyzis) == cfx.State.ANALYSED
        assert cfx_entry.get_state_at_date(day_before_second_opening_first_resubmit) == cfx.State.RESOLVED
        assert cfx_entry.get_state_at_date(day_after_second_opening_first_resubmit) == cfx.State.SUBMITTED
        assert cfx_entry.get_state_at_date(day_before_verification) == cfx.State.RESOLVED
        assert cfx_entry.get_state_at_date(day_after_verification) == cfx.State.VERIFIED
        assert cfx_entry.get_state_at_date(day_before_validation) == cfx.State.VERIFIED
        assert cfx_entry.get_state_at_date(day_after_validation) == cfx.State.VALIDATED
        assert cfx_entry.get_state_at_date(datetime.now()) == cfx.State.CLOSED


class TestFirstCurrentOwner:

    def test_CFX00778656_first_current_owner(self, create_light_champfx_library: cfx.ChampFXLibrary) -> None:
        champfx_library = create_light_champfx_library
        cfx_entry = champfx_library.get_cfx_by_id("CFX00778656")
        first_current_owner = cfx_entry.get_current_owner_at_date(datetime(int(2024), int(1), int(6)))
        assert "enaud" in first_current_owner.raw_full_name
        assert first_current_owner.subsystem == role.SubSystem.ATS


class TestSubsystem:
    def test_CFX00688257_that_has_been_rejected_and_closed(self, create_light_champfx_library: cfx.ChampFXLibrary) -> None:
        champfx_library = create_light_champfx_library
        cfx_entry = champfx_library.get_cfx_by_id("CFX00688257")
        assert cfx_entry._subsystem == role.SubSystem.ADONEM

    def test_CFX00822357_that_has_been_fixed_and_closed(self, create_light_champfx_library: cfx.ChampFXLibrary) -> None:
        champfx_library = create_light_champfx_library
        cfx_entry = champfx_library.get_cfx_by_id("CFX00822357")
        assert cfx_entry._subsystem == role.SubSystem.ADONEM


class TestRoleOnDate:
    def test_role_ats_CFX00862371(self) -> None:
        champfx_library = cfx.ChampFXLibrary(champfx_filters=[cfx.ChampFXWhitelistFilter(cfx_to_treat_ids=["CFX00862371"])])
        cfx_entry = champfx_library.get_cfx_by_id("CFX00862371")
        assert cfx_entry.get_current_role_at_date(datetime(int(2025), int(3), int(22))) == role.SubSystem.ATS
        assert cfx_entry.get_current_role_at_date(datetime(int(2025), int(3), int(25))) == role.SubSystem.ATS
        assert cfx_entry.get_current_role_at_date(datetime(int(2025), int(3), int(30))) == role.SubSystem.ATS
        assert cfx_entry.get_current_role_at_date(datetime.now()) == role.SubSystem.PROJET


class TestCurrentOwner:

    def test_CFX00427036_currenet_owner_by_date(self, create_light_champfx_library: cfx.ChampFXLibrary) -> None:
        champfx_library = create_light_champfx_library
        cfx_entry = champfx_library.get_cfx_by_id("CFX00427036")
        assert cfx_entry.get_current_owner_at_date(datetime.now()) == cfx_entry._current_owner
        assert "herve" in cfx_entry.get_current_owner_at_date(datetime.now())._raw_full_name.lower()

    def test_all_cfx_have_none_current_owner_before_creation(self, create_light_champfx_library: cfx.ChampFXLibrary) -> None:
        champfx_library = create_light_champfx_library
        for cfx_entry in champfx_library.get_all_cfx():

            day_before_first_opening = datetime(int(2000), int(1), int(4))
            assert cfx_entry.get_current_owner_at_date(day_before_first_opening) is None

    def test_all_cfx_have_current_owner_which_is_same_as_history(self, create_light_champfx_library: cfx.ChampFXLibrary) -> None:
        champfx_library = create_light_champfx_library
        for cfx_entry in champfx_library.get_all_cfx():
            assert cfx_entry._current_owner == cfx_entry.get_current_owner_at_date(datetime.now())

    def test_before_cfx_creation(self, create_light_champfx_library: cfx.ChampFXLibrary) -> None:
        champfx_library = create_light_champfx_library
        cfx_entry = champfx_library.get_cfx_by_id("CFX00778656")
        first_current_owner = cfx_entry.get_current_owner_at_date(datetime(int(2000), int(1), int(6)))
        assert first_current_owner is None

    class TestCFX00778656:

        def test_CFX00778656_that_has_never_changed(self, create_light_champfx_library: cfx.ChampFXLibrary) -> None:
            """05/01/2024 18:05:35"""
            champfx_library = create_light_champfx_library
            cfx_entry = champfx_library.get_cfx_by_id("CFX00778656")
            assert cfx_entry.get_current_owner_at_date(datetime.now()) == cfx_entry._current_owner
            assert "Renaud".lower() in cfx_entry.get_current_owner_at_date(datetime.now())._raw_full_name.lower()

            day_before_first_opening = datetime(int(2024), int(1), int(4))
            day_after_first_analyzis = datetime(int(2024), int(1), int(6))
            assert cfx_entry.get_current_owner_at_date(day_before_first_opening) is None
            assert "Renaud".lower() in cfx_entry.get_current_owner_at_date(day_after_first_analyzis)._raw_full_name.lower()

    class TestChampFxFilter:
        def test_next_project_field_filter(self) -> None:
            nexteo_only_champfx_library = cfx.ChampFXLibrary(champfx_filters=[cfx.ChampFxFilterFieldProject(field_accepted_values=[cfx.CfxProject.FR_NEXTEO])])

            assert len(nexteo_only_champfx_library.get_all_cfx()) > 0
            for cfx_entry in nexteo_only_champfx_library.get_all_cfx():
                assert cfx_entry._cfx_project == cfx.CfxProject.FR_NEXTEO

        def test_two_field_filters(self, create_light_champfx_library: cfx.ChampFXLibrary) -> None:
            security_and_ats = cfx.ChampFxFilter
            champfx_library = create_light_champfx_library

            ats_non_security_filter = cfx.ChampFxFilter(
                field_filters=[
                    cfx.ChampFxFilterFieldSecurityRelevant(field_forbidden_values=[cfx.SecurityRelevant.YES, cfx.SecurityRelevant.MITIGATED]),
                    cfx.ChampFxFilterFieldSubsystem(field_accepted_values=[role.SubSystem.ATS]),
                ],
            )
            ats_security_filter = cfx.ChampFxFilter(
                field_filters=[
                    cfx.ChampFxFilterFieldSecurityRelevant(field_accepted_values=[cfx.SecurityRelevant.YES, cfx.SecurityRelevant.MITIGATED]),
                    cfx.ChampFxFilterFieldSubsystem(field_accepted_values=[role.SubSystem.ATS]),
                ],
            )

            assert ats_non_security_filter.match_cfx_entry(champfx_library.get_cfx_by_id("CFX00427369"))
            assert not ats_non_security_filter.match_cfx_entry(champfx_library.get_cfx_by_id("CFX00831682"))

            assert not ats_security_filter.match_cfx_entry(champfx_library.get_cfx_by_id("CFX00427369"))
            assert ats_security_filter.match_cfx_entry(champfx_library.get_cfx_by_id("CFX00831682"))

        def test_get_sub_system_method_for_filter(self) -> None:
            pass

        def test_security_relevant_only_field_filter(self) -> None:
            security_relevant_only_champfx_library = cfx.ChampFXLibrary(
                champfx_filters=[cfx.ChampFxFilterFieldSecurityRelevant(field_accepted_values=[cfx.SecurityRelevant.YES, cfx.SecurityRelevant.MITIGATED])]
            )

            assert len(security_relevant_only_champfx_library.get_all_cfx()) > 0
            for cfx_entry in security_relevant_only_champfx_library.get_all_cfx():
                assert cfx_entry._security_relevant


class TestFullDatabase:
    def test_all_system_structure(self, create_full_champfx_library: cfx.ChampFXLibrary) -> None:
        champfx_library = create_full_champfx_library
        for cfx_entry in champfx_library.get_all_cfx():
            assert cfx_entry._system_structure


class TestStatisticsPreparation:
    @pytest.mark.timeout(120)
    def test_gather_state_counts_for_each_date_whithout_filter(self, create_full_champfx_library: cfx.ChampFXLibrary) -> None:
        champfx_library = create_full_champfx_library
        champfx_library.gather_state_counts_for_each_date(cfx.ConstantIntervalDatesGenerator(time_delta=relativedelta.relativedelta(days=10)))

    @pytest.mark.timeout(120)
    def test_gather_state_counts_for_each_date_whith_filter(self, create_full_champfx_library: cfx.ChampFXLibrary) -> None:
        champfx_library = create_full_champfx_library
        champfx_library.gather_state_counts_for_each_date(cfx.ConstantIntervalDatesGenerator(time_delta=relativedelta.relativedelta(days=10)))
        champfx_library.gather_state_counts_for_each_date(
            cfx.ConstantIntervalDatesGenerator(time_delta=relativedelta.relativedelta(days=10)),
            cfx_filters=[cfx.ChampFxFilter(role_depending_on_date_filter=cfx.ChampFXRoleDependingOnDateFilter(roles_at_date_allowed=[role.SubSystem.ATS]))],
        )


class TestStatisticsPreparationRoleDependingOnDate:
    """['CFX00398968', 'CFX00401911', 'CFX00466137', 'CFX00494052', 'CFX00551164', 'CFX00551910', 'CFX00584295', 'CFX00587132', 'CFX00618804', 'CFX00623862', 'CFX00623864', 'CFX00623870', 'CFX00623879', 'CFX00623898', 'CFX00623899', 'CFX00624544', 'CFX00639805', 'CFX00674321', 'CFX00687787', 'CFX00690605', 'CFX00690624', 'CFX00695357', 'CFX00695358', 'CFX00701981', 'CFX00716682', 'CFX00716724', 'CFX00720447', 'CFX00723144', 'CFX00723481', 'CFX00734937', 'CFX00742602', 'CFX00749341', 'CFX00786363', 'CFX00786374', 'CFX00789495', 'CFX00806369', 'CFX00812751', 'CFX00817953', 'CFX00831083', 'CFX00842156', 'CFX00842390', 'CFX00848518', 'CFX00849529', 'CFX00849547', 'CFX00849556', 'CFX00849571', 'CFX00849576']"""

    def test_role_sw_constant_interval(self, create_champfx_library_only_cfx_closed_by_yda_in_whitelist: cfx.ChampFXLibrary) -> None:
        champfx_library = create_champfx_library_only_cfx_closed_by_yda_in_whitelist
        all_results_per_date = champfx_library.gather_state_counts_for_each_date(
            cfx.ConstantIntervalDatesGenerator(time_delta=relativedelta.relativedelta(days=10)),
            cfx_filters=[
                cfx.ChampFxFilter(
                    role_depending_on_date_filter=cfx.ChampFXRoleDependingOnDateFilter(roles_at_date_allowed=[role.SubSystem.SW]),
                    whitelist_filter=cfx.ChampFXWhitelistFilter(cfx_to_treat_ids=set(["CFX00398968"])),
                )
            ],
        )
        assert not all_results_per_date.is_empty()

    def test_role_sw_decreasing_interval(self, create_champfx_library_only_cfx_closed_by_yda_in_whitelist: cfx.ChampFXLibrary) -> None:
        champfx_library = create_champfx_library_only_cfx_closed_by_yda_in_whitelist
        all_results_per_date = champfx_library.gather_state_counts_for_each_date(
            cfx.DecreasingIntervalDatesGenerator(),
            cfx_filters=[cfx.ChampFxFilter(role_depending_on_date_filter=cfx.ChampFXRoleDependingOnDateFilter(roles_at_date_allowed=[role.SubSystem.SW]))],
        )
        assert not all_results_per_date.is_empty()

    def test_role_ats_CFX00862371(self) -> None:
        champfx_library = cfx.ChampFXLibrary(champfx_filters=[cfx.ChampFXWhitelistFilter(cfx_to_treat_ids=["CFX00862371"])])
        all_results_per_date = champfx_library.gather_state_counts_for_each_date(
            cfx.ConstantIntervalDatesGenerator(time_delta=relativedelta.relativedelta(days=2)),
            cfx_filters=[cfx.ChampFxFilter(role_depending_on_date_filter=cfx.ChampFXRoleDependingOnDateFilter(roles_at_date_allowed=[role.SubSystem.ATS]))],
        )
        assert not all_results_per_date.is_empty()


class TestDecreasingIntervalDatesGenerator:

    def test_now(self) -> None:

        list_dates: List[datetime] = cfx.DecreasingIntervalDatesGenerator().get_dates_since(datetime.now())
        assert len(list_dates) > 1

    def test_few_values(self) -> None:
        assert len(cfx.DecreasingIntervalDatesGenerator().get_dates_since(datetime(int(2000), int(1), int(4)))) > 100
