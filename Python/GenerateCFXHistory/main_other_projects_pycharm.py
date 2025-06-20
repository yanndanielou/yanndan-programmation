import os

from dateutil import relativedelta
from logger import logger_config

from generatecfxhistory import cfx
from generatecfxhistory import ui_and_results_generation, release_role_mapping

OUTPUT_DIRECTORY_NAME = "output"

DISPLAY_OUTPUT = False


def main() -> None:
    """Main function"""

    with logger_config.stopwatch_with_label("Application duration"):
        logger_config.configure_logger_with_random_log_file_suffix("GenerateCFXHistory")
        logger_config.print_and_log_info("Application start")

        if not os.path.exists(OUTPUT_DIRECTORY_NAME):
            os.mkdir(OUTPUT_DIRECTORY_NAME)

        all_champfx_library = cfx.ChampFXLibrary(
            champfx_details_excel_file_full_path="Input/autres_projets___details.xlsx",
            champfx_states_changes_excel_file_full_path="Input/autres_projets___changements_etats.xlsx",
            cfx_extended_history_file_full_path=None,
            user_and_role_data_text_file_full_path="Input/role_data_next_other_projects.txt",
            release_subsystem_mapping=release_role_mapping.other_projects_release_subsystem_mapping,
            label="Other projects",
        )

        ui_and_results_generation.produce_results_and_displays_for_libary(
            cfx_library=all_champfx_library,
            output_directory_name=OUTPUT_DIRECTORY_NAME,
            for_global=True,
            for_each_subsystem=False,
            for_each_current_owner_per_date=False,
            create_excel_file=False,
            create_html_file=True,
            display_output_plots=DISPLAY_OUTPUT,
            generate_by_project_instruction=ui_and_results_generation.GenerateByProjectInstruction.BY_PROJECT_AND_ALSO_GLOBAL_ALL_PROJECTS,
        )

        ui_and_results_generation.produce_results_and_displays_for_libary(
            cfx_library=all_champfx_library,
            output_directory_name=OUTPUT_DIRECTORY_NAME,
            for_global=True,
            for_each_subsystem=False,
            for_each_current_owner_per_date=False,
            cfx_filters=[
                cfx.ChampFxFilter(field_filters=[cfx.ChampFxFilterFieldSecurityRelevant(field_accepted_values=[cfx.SecurityRelevant.YES, cfx.SecurityRelevant.MITIGATED])]),
            ],
            create_excel_file=False,
            create_html_file=True,
            display_output_plots=DISPLAY_OUTPUT,
            generate_by_project_instruction=ui_and_results_generation.GenerateByProjectInstruction.BY_PROJECT_AND_ALSO_GLOBAL_ALL_PROJECTS,
        )

        ui_and_results_generation.produce_results_and_displays_for_libary(
            cfx_library=all_champfx_library,
            output_directory_name=OUTPUT_DIRECTORY_NAME,
            for_global=True,
            for_each_subsystem=False,
            for_each_current_owner_per_date=False,
            cfx_filters=[
                cfx.ChampFxFilter(field_filters=[cfx.ChampFxFilterFieldSafetyRelevant(field_accepted_value=True)]),
            ],
            create_excel_file=False,
            create_html_file=True,
            display_output_plots=DISPLAY_OUTPUT,
            generate_by_project_instruction=ui_and_results_generation.GenerateByProjectInstruction.BY_PROJECT_AND_ALSO_GLOBAL_ALL_PROJECTS,
        )


        ui_and_results_generation.produce_results_and_displays(
            cfx_library=all_champfx_library,
            output_directory_name=OUTPUT_DIRECTORY_NAME,
            display_without_cumulative_eras=False,
            display_with_cumulative_eras=True,
            cfx_filters=[
                cfx.ChampFxFilter(
                    field_filters=[cfx.ChampFxFilterFieldCategory(field_accepted_values=[cfx.Category.SOFTWARE]), cfx.ChampFxFilterFieldType(field_accepted_values=[cfx.RequestType.DEFECT])]
                ),
            ],
            create_excel_file=False,
            create_html_file=True,
            display_output_plots=DISPLAY_OUTPUT,
            generate_by_project_instruction=ui_and_results_generation.GenerateByProjectInstruction.BY_PROJECT_AND_ALSO_GLOBAL_ALL_PROJECTS,
        )

        ui_and_results_generation.produce_results_and_displays(
            cfx_library=all_champfx_library,
            output_directory_name=OUTPUT_DIRECTORY_NAME,
            display_without_cumulative_eras=False,
            display_with_cumulative_eras=True,
            cfx_filters=[
                cfx.ChampFxFilter(
                    field_filters=[cfx.ChampFxFilterFieldCategory(field_accepted_values=[cfx.Category.CONFIGURATION_DATA]), cfx.ChampFxFilterFieldType(field_accepted_values=[cfx.RequestType.DEFECT])]
                ),
            ],
            create_excel_file=True,
            create_html_file=False,
            display_output_plots=DISPLAY_OUTPUT,
            generate_by_project_instruction=ui_and_results_generation.GenerateByProjectInstruction.BY_PROJECT_AND_ALSO_GLOBAL_ALL_PROJECTS,
        )

        if DISPLAY_OUTPUT:
            ui_and_results_generation.block_execution_and_keep_all_windows_open()


if __name__ == "__main__":
    # sys.argv[1:]
    main()
