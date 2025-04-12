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

        usine_site_champfx_library = cfx.ChampFXLibrary(
            champfx_filter=cfx.ChampFxFilter(cfx_to_treat_whitelist_text_file_full_path="Input/CFX_usine_site.txt"),
        )
        ui_and_results_generation.produce_results_and_displays_for_libary(
            cfx_library=usine_site_champfx_library, output_directory_name=output_directory_name, library_label="Usine&site", for_global=True, for_each_subsystem=True
        )

        ui_and_results_generation.block_execution_and_keep_all_windows_open()
        """
        security_relevant_only_champfx_library = cfx.ChampFXLibrary(
            champfx_filter=cfx.ChampFxFilter(field_filter=cfx.ChampFXFieldFilter(field_name="_security_relevant", field_accepted_values=[cfx.SecurityRelevant.Yes])),
        )
        ui_and_results_generation.produce_results_and_displays_for_libary(
            cfx_library=security_relevant_only_champfx_library, output_directory_name=output_directory_name, library_label="security(cyber)", for_global=True, for_each_subsystem=True
        )

        nexteo_only_champfx_library = cfx.ChampFXLibrary(
            champfx_filter=cfx.ChampFxFilter(field_filter=cfx.ChampFXFieldFilter(field_name="_cfx_project", field_accepted_values=[cfx.CfxProject.FR_NEXTEO])),
        )"""

        """all_champfx_library = cfx.ChampFXLibrary(
            # champfx_filter=cfx.ChampFxFilter(field_filters=[cfx.ChampFXFieldFilter(field_name="_security_relevant", field_accepted_values=[cfx.SecurityRelevant.Yes, cfx.SecurityRelevant.Mitigated])]),
        )
        """
        """ui_and_results_generation.produce_results_and_displays_for_libary(
            cfx_library=all_champfx_library, output_directory_name=output_directory_name, library_label="all", for_global=True, for_each_subsystem=True
        )
        """

        """,
            cfx_filter=cfx.ChampFxFilter(
                field_filters=[
                    cfx.ChampFXFieldFilter(field_name="_security_relevant", field_forbidden_values=[cfx.SecurityRelevant.Yes]),
                    cfx.ChampFXFieldFilter(field_name="_subsystem", field_accepted_values=[subsystem]),
                ],
            ),"""


if __name__ == "__main__":
    # sys.argv[1:]
    main()
