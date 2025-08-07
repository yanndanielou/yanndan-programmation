import os

from typing import Set, Dict, Any

from dateutil import relativedelta
from logger import logger_config

from generatecfxhistory import cfx
from generatecfxhistory import ui_and_results_generation, release_role_mapping, role

OUTPUT_DIRECTORY_NAME = "output_all_projects"

DISPLAY_OUTPUT = False


def main() -> None:
    """Main function"""

    with logger_config.application_logger("GenerateCFXHistory_otherprojects"):

        if not os.path.exists(OUTPUT_DIRECTORY_NAME):
            os.mkdir(OUTPUT_DIRECTORY_NAME)

        cfx_inputs = (
            cfx.ChampFxInputsBuilder()
            .add_champfx_details_excel_files_by_directory_and_file_name_mask(directory_path="Input", filename_pattern="details_project_*.xlsx")
            .add_champfx_states_changes_excel_files_by_directory_and_file_name_mask(directory_path="Input", filename_pattern="states_changes_project_*.xlsx")
            .build()
        )

        with logger_config.stopwatch_with_label(label="Print possible values", inform_beginning=True):
            cfx_inputs.print_all_possible_values_by_column()

        all_champfx_library = cfx.ChampFXLibrary(
            cfx_inputs=cfx_inputs, 
            label="Other projects",
        )

        ui_and_results_generation.produce_results_and_displays_for_libary(
            cfx_library=all_champfx_library,
            output_directory_name=OUTPUT_DIRECTORY_NAME,
            for_global=True,
            for_each_subsystem=False,
            for_each_current_owner_per_date=False,
            create_excel_file=True,
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
            create_excel_file=True,
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
            create_excel_file=True,
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
            create_excel_file=True,
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

        logger_config.print_and_log_info("End of application")


if __name__ == "__main__":
    # sys.argv[1:]
    main()
