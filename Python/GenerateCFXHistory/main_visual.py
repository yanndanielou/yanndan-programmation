import os

from dateutil import relativedelta
from logger import logger_config

from generatecfxhistory import cfx
from generatecfxhistory import role
from generatecfxhistory import ui_and_results_generation

OUTPUT_DIRECTORY_NAME = "output"


def main() -> None:
    """Main function"""

    with logger_config.stopwatch_with_label("Application duration"):
        logger_config.configure_logger_with_random_log_file_suffix("GenerateCFXHistory")
        logger_config.print_and_log_info("Application start")

        if not os.path.exists(OUTPUT_DIRECTORY_NAME):
            os.mkdir(OUTPUT_DIRECTORY_NAME)

        all_champfx_library = cfx.ChampFXLibrary(
            champfx_details_excel_file_full_path="Input/extract_cfx_details.xlsx",
            champfx_states_changes_excel_file_full_path="Input/extract_cfx_change_state.xlsx",
            cfx_extended_history_file_full_path="Input/cfx_extended_history.txt",
        )

        ui_and_results_generation.produce_results_and_displays_for_libary(
            cfx_library=all_champfx_library,
            output_directory_name=OUTPUT_DIRECTORY_NAME,
            for_global=True,
            for_each_subsystem=False,
            for_each_current_owner_per_date=False,
            cfx_filters=[
                cfx.ChampFxFilter(cfx_to_treat_whitelist_text_file_full_path="Input/CFX_list_cyber_aio.txt"),
            ],
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
            for_each_subsystem=True,
            for_each_current_owner_per_date=True,
            create_excel_file=True,
            create_html_file=True,
            generate_by_project_instruction=ui_and_results_generation.GenerateByProjectInstruction.BY_PROJECT_AND_ALSO_GLOBAL_ALL_PROJECTS,
        )

        ui_and_results_generation.block_execution_and_keep_all_windows_open()


if __name__ == "__main__":
    # sys.argv[1:]
    main()
