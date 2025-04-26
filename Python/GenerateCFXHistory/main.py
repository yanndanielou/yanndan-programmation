import os

from dateutil import relativedelta
from logger import logger_config

import cfx
import role
import ui_and_results_generation


def main() -> None:
    """Main function"""

    with logger_config.stopwatch_with_label("Application duration"):
        logger_config.configure_logger_with_random_log_file_suffix("GenerateCFXHistory")
        logger_config.print_and_log_info("Application start")

        output_directory_name = "output"
        if not os.path.exists(output_directory_name):
            os.mkdir(output_directory_name)

        all_champfx_library = cfx.ChampFXLibrary()

        for i in range(1, 10):
            with logger_config.stopwatch_with_label("gather_state_counts_for_each_date no filter"):
                all_champfx_library.gather_state_counts_for_each_date(relativedelta.relativedelta(days=10))

        for i in range(1, 10):
            with logger_config.stopwatch_with_label("gather_state_counts_for_each_date filter nexteo"):
                all_champfx_library.gather_state_counts_for_each_date(
                    relativedelta.relativedelta(days=10),
                    cfx_filters=[cfx.ChampFxFilter(field_filters=[cfx.ChampFXFieldFilter(field_name="_cfx_project", field_accepted_values=[cfx.CfxProject.FR_NEXTEO])])],
                )

        for i in range(1, 10):
            with logger_config.stopwatch_with_label("gather_state_counts_for_each_date filter ats+"):
                all_champfx_library.gather_state_counts_for_each_date(
                    relativedelta.relativedelta(days=10),
                    cfx_filters=[cfx.ChampFxFilter(field_filters=[cfx.ChampFXFieldFilter(field_name="_cfx_project", field_accepted_values=[cfx.CfxProject.ATSP])])],
                )

        for i in range(1, 10):
            with logger_config.stopwatch_with_label("gather_state_counts_for_each_date security relevant"):
                all_champfx_library.gather_state_counts_for_each_date(
                    relativedelta.relativedelta(days=10),
                    cfx_filters=[
                        cfx.ChampFxFilter(field_filters=[cfx.ChampFXFieldFilter(field_name="_security_relevant", field_accepted_values=[cfx.SecurityRelevant.YES, cfx.SecurityRelevant.MITIGATED])])
                    ],
                )

        for i in range(1, 10):
            with logger_config.stopwatch_with_label("gather_state_counts_for_each_date ChampFXRoleDependingOnDateFilter([role.SubSystem.ATS]"):
                all_champfx_library.gather_state_counts_for_each_date(
                    relativedelta.relativedelta(days=10),
                    cfx_filters=[cfx.ChampFxFilter(role_depending_on_date_filter=cfx.ChampFXRoleDependingOnDateFilter(roles_at_date_allowed=[role.SubSystem.ATS]))],
                )

        for i in range(1, 10):
            with logger_config.stopwatch_with_label("gather_state_counts_for_each_date ChampFXRoleDependingOnDateFilter([role.SubSystem.SW]"):
                all_champfx_library.gather_state_counts_for_each_date(
                    relativedelta.relativedelta(days=10),
                    cfx_filters=[cfx.ChampFxFilter(role_depending_on_date_filter=cfx.ChampFXRoleDependingOnDateFilter(roles_at_date_allowed=[role.SubSystem.SW]))],
                )
        for i in range(1, 10):
            with logger_config.stopwatch_with_label("gather_state_counts_for_each_date ChampFXRoleDependingOnDateFilter([role.SubSystem.QUALITE]"):
                all_champfx_library.gather_state_counts_for_each_date(
                    relativedelta.relativedelta(days=10),
                    cfx_filters=[cfx.ChampFxFilter(role_depending_on_date_filter=cfx.ChampFXRoleDependingOnDateFilter(roles_at_date_allowed=[role.SubSystem.QUALITE]))],
                )

        ui_and_results_generation.produce_results_and_displays_for_libary(
            cfx_library=all_champfx_library,
            output_directory_name=output_directory_name,
            for_global=True,
            for_each_subsystem=True,
            for_each_current_owner_per_date=True,
            create_excel_file=True,
            create_html_file=True,
        )
        ui_and_results_generation.produce_results_and_displays_for_libary(
            cfx_library=all_champfx_library,
            output_directory_name=output_directory_name,
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
            output_directory_name=output_directory_name,
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
            output_directory_name=output_directory_name,
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
