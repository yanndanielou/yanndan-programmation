import os


from logger import logger_config

import ui_and_results_generation

import cfx
import role


def main() -> None:
    """Main function"""

    with logger_config.stopwatch_with_label("Application duration"):
        logger_config.configure_logger_with_random_log_file_suffix("GenerateCFXHistory")
        logger_config.print_and_log_info("Application start")

        output_directory_name = "output"
        if not os.path.exists(output_directory_name):
            os.mkdir(output_directory_name)

        all_champfx_library = cfx.ChampFXLibrary(
            champfx_filters=[
                cfx.ChampFXWhitelistFilter(cfx_to_treat_whitelist_text_file_full_path="Input/CFX_usine_site.txt"),
                cfx.ChampFXFieldFilter(field_name="_security_relevant", field_forbidden_values=[cfx.SecurityRelevant.YES, cfx.SecurityRelevant.MITIGATED]),
            ],
        )

        ui_and_results_generation.produce_results_and_displays_for_libary(
            cfx_library=all_champfx_library,
            output_directory_name=output_directory_name,
            for_global=True,
            for_each_subsystem=True,
            for_each_current_owner_per_date=False,
            create_excel_file=False,
            create_html_file=False,
            cfx_filters=[
                cfx.ChampFxFilter(
                    field_filters=[
                        cfx.ChampFXFieldFilter(
                            field_name="_subsystem", field_accepted_values=[role.SubSystem.ADONEM, role.SubSystem.ATC_MANAGER, role.SubSystem.SW, role.SubSystem.COC_DE, role.SubSystem.ATS]
                        )
                    ],
                ),
            ],
        )
        """
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
        )"""

        ui_and_results_generation.block_execution_and_keep_all_windows_open()


if __name__ == "__main__":
    # sys.argv[1:]
    main()
