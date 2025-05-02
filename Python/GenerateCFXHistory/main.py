import os

from dateutil import relativedelta
from logger import logger_config

import cfx
import role
import ui_and_results_generation

OUTPUT_DIRECTORY_NAME = "output"


def print_gathering_time(champfx_library: cfx.ChampFXLibrary, number_iterations: int) -> None:

    for _ in range(1, number_iterations):
        with logger_config.stopwatch_with_label("gather_state_counts_for_each_date no filter"):
            champfx_library.gather_state_counts_for_each_date(dates_generator=cfx.ConstantIntervalDatesGenerator(time_delta=relativedelta.relativedelta(days=10)))

    for _ in range(1, number_iterations):
        with logger_config.stopwatch_with_label("gather_state_counts_for_each_date filter nexteo"):
            champfx_library.gather_state_counts_for_each_date(
                dates_generator=cfx.ConstantIntervalDatesGenerator(time_delta=relativedelta.relativedelta(days=10)),
                cfx_filters=[cfx.ChampFxFilter(field_filters=[cfx.ChampFXFieldFilter(field_name="_cfx_project", field_accepted_values=[cfx.CfxProject.FR_NEXTEO])])],
            )

    for _ in range(1, number_iterations):
        with logger_config.stopwatch_with_label("gather_state_counts_for_each_date filter ats+"):
            champfx_library.gather_state_counts_for_each_date(
                dates_generator=cfx.ConstantIntervalDatesGenerator(time_delta=relativedelta.relativedelta(days=10)),
                cfx_filters=[cfx.ChampFxFilter(field_filters=[cfx.ChampFXFieldFilter(field_name="_cfx_project", field_accepted_values=[cfx.CfxProject.ATSP])])],
            )

    for _ in range(1, number_iterations):
        with logger_config.stopwatch_with_label("gather_state_counts_for_each_date security relevant"):
            champfx_library.gather_state_counts_for_each_date(
                dates_generator=cfx.ConstantIntervalDatesGenerator(time_delta=relativedelta.relativedelta(days=10)),
                cfx_filters=[
                    cfx.ChampFxFilter(field_filters=[cfx.ChampFXFieldFilter(field_name="_security_relevant", field_accepted_values=[cfx.SecurityRelevant.YES, cfx.SecurityRelevant.MITIGATED])])
                ],
            )

    for _ in range(1, number_iterations):
        with logger_config.stopwatch_with_label("gather_state_counts_for_each_date ChampFXRoleDependingOnDateFilter([role.SubSystem.ATS]"):
            champfx_library.gather_state_counts_for_each_date(
                dates_generator=cfx.ConstantIntervalDatesGenerator(time_delta=relativedelta.relativedelta(days=10)),
                cfx_filters=[cfx.ChampFxFilter(role_depending_on_date_filter=cfx.ChampFXRoleDependingOnDateFilter(roles_at_date_allowed=[role.SubSystem.ATS]))],
            )

    for _ in range(1, number_iterations):
        with logger_config.stopwatch_with_label("gather_state_counts_for_each_date ChampFXRoleDependingOnDateFilter([role.SubSystem.SW]"):
            champfx_library.gather_state_counts_for_each_date(
                dates_generator=cfx.ConstantIntervalDatesGenerator(time_delta=relativedelta.relativedelta(days=10)),
                cfx_filters=[cfx.ChampFxFilter(role_depending_on_date_filter=cfx.ChampFXRoleDependingOnDateFilter(roles_at_date_allowed=[role.SubSystem.SW]))],
            )

    for _ in range(1, number_iterations):
        with logger_config.stopwatch_with_label("gather_state_counts_for_each_date ChampFXRoleDependingOnDateFilter([role.SubSystem.QUALITE]"):
            champfx_library.gather_state_counts_for_each_date(
                dates_generator=cfx.ConstantIntervalDatesGenerator(time_delta=relativedelta.relativedelta(days=10)),
                cfx_filters=[cfx.ChampFxFilter(role_depending_on_date_filter=cfx.ChampFXRoleDependingOnDateFilter(roles_at_date_allowed=[role.SubSystem.QUALITE]))],
            )


def produce_results_and_displays_for_adonem_known_cstmr() -> None:

    adonem_library = cfx.ChampFXLibrary(champfx_filters=[cfx.ChampFXWhitelistFilter("Input/CFX_adonem_connus_client.txt")])

    ui_and_results_generation.produce_results_and_displays_for_libary(
        cfx_library=adonem_library,
        output_directory_name=OUTPUT_DIRECTORY_NAME,
        for_global=True,
        for_each_subsystem=False,
        for_each_current_owner_per_date=False,
        create_excel_file=True,
        create_html_file=True,
    )


def main() -> None:
    """Main function"""

    with logger_config.stopwatch_with_label("Application duration"):
        logger_config.configure_logger_with_random_log_file_suffix("GenerateCFXHistory")
        logger_config.print_and_log_info("Application start")

        if not os.path.exists(OUTPUT_DIRECTORY_NAME):
            os.mkdir(OUTPUT_DIRECTORY_NAME)

        # produce_results_and_displays_for_adonem_known_cstmr()
        # ui_and_results_generation.block_execution_and_keep_all_windows_open()

        all_champfx_library = cfx.ChampFXLibrary(champfx_filters=[cfx.ChampFXWhitelistFilter(cfx_to_treat_whitelist_text_file_full_path="Input_for_Tests/sample_cfx_ids.txt")])
        print_gathering_time(champfx_library=all_champfx_library, number_iterations=2)

        ui_and_results_generation.produce_results_and_displays_for_libary(
            cfx_library=all_champfx_library,
            output_directory_name=OUTPUT_DIRECTORY_NAME,
            for_global=True,
            for_each_subsystem=True,
            for_each_current_owner_per_date=True,
            create_excel_file=True,
            create_html_file=True,
        )
        ui_and_results_generation.produce_results_and_displays_for_libary(
            cfx_library=all_champfx_library,
            output_directory_name=OUTPUT_DIRECTORY_NAME,
            for_global=True,
            for_each_subsystem=True,
            for_each_current_owner_per_date=True,
            cfx_filters=[
                cfx.ChampFxFilter(cfx_to_treat_whitelist_text_file_full_path="Input/CFX_usine_site.txt"),
            ],
            create_excel_file=True,
            create_html_file=True,
        )

        ui_and_results_generation.produce_results_and_displays_for_libary(
            cfx_library=all_champfx_library,
            output_directory_name=OUTPUT_DIRECTORY_NAME,
            for_global=True,
            for_each_subsystem=False,
            for_each_current_owner_per_date=False,
            cfx_filters=[
                cfx.ChampFxFilter(field_filters=[cfx.ChampFXFieldFilter(field_name="_security_relevant", field_forbidden_values=[cfx.SecurityRelevant.YES, cfx.SecurityRelevant.MITIGATED])]),
            ],
            create_excel_file=True,
            create_html_file=True,
        )

        ui_and_results_generation.produce_results_and_displays_for_libary(
            cfx_library=all_champfx_library,
            output_directory_name=OUTPUT_DIRECTORY_NAME,
            for_global=True,
            for_each_subsystem=False,
            for_each_current_owner_per_date=False,
            cfx_filters=[
                cfx.ChampFxFilter(field_filters=[cfx.ChampFXFieldFilter(field_name="_security_relevant", field_accepted_values=[cfx.SecurityRelevant.YES, cfx.SecurityRelevant.MITIGATED])]),
            ],
            create_excel_file=True,
            create_html_file=True,
        )

        ui_and_results_generation.block_execution_and_keep_all_windows_open()


if __name__ == "__main__":
    # sys.argv[1:]
    main()
