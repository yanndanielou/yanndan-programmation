import os


from logger import logger_config

from generatecfxhistory import cfx, inputs, filters, constants
from generatecfxhistory import ui_and_results_generation

OUTPUT_DIRECTORY_NAME = "output_all_projects"

DISPLAY_OUTPUT = False


def main() -> None:
    """Main function"""

    with logger_config.application_logger("GenerateCFXHistory_otherprojects"):

        if not os.path.exists(OUTPUT_DIRECTORY_NAME):
            os.mkdir(OUTPUT_DIRECTORY_NAME)

        cfx_inputs = (
            inputs.ChampFxInputsWithFilesBuilder()
            .add_champfx_details_excel_files_by_directory_and_file_name_mask(directory_path="Input_Downloaded", filename_pattern="details_project_*.xlsx")
            .add_champfx_states_changes_excel_files_by_directory_and_file_name_mask(directory_path="Input_Downloaded", filename_pattern="states_changes_project_*.xlsx")
            .build()
        )

        with logger_config.stopwatch_with_label(label="Print possible values", inform_beginning=True):
            cfx_inputs.print_all_possible_values_by_column()

        all_champfx_library = cfx.ChampFXLibrary(
            cfx_inputs=cfx_inputs,
            label="Other projects",
            allow_cfx_creation_errors=True,
        )

        ui_and_results_generation.produce_number_of_cfx_by_state_per_date_results_and_displays_for_library(
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

        ui_and_results_generation.produce_number_of_cfx_by_state_per_date_results_and_displays_for_library(
            cfx_library=all_champfx_library,
            output_directory_name=OUTPUT_DIRECTORY_NAME,
            for_global=True,
            for_each_subsystem=False,
            for_each_current_owner_per_date=False,
            cfx_filters=[
                cfx.ChampFxFilter(field_filters=[filters.ChampFxFilterFieldSecurityRelevant(field_accepted_values=[constants.SecurityRelevant.YES, constants.SecurityRelevant.MITIGATED])]),
            ],
            create_excel_file=True,
            create_html_file=True,
            display_output_plots=DISPLAY_OUTPUT,
            generate_by_project_instruction=ui_and_results_generation.GenerateByProjectInstruction.BY_PROJECT_AND_ALSO_GLOBAL_ALL_PROJECTS,
        )

        ui_and_results_generation.produce_number_of_cfx_by_state_per_date_results_and_displays_for_library(
            cfx_library=all_champfx_library,
            output_directory_name=OUTPUT_DIRECTORY_NAME,
            for_global=True,
            for_each_subsystem=False,
            for_each_current_owner_per_date=False,
            cfx_filters=[
                cfx.ChampFxFilter(field_filters=[filters.ChampFxFilterFieldSafetyRelevant(field_accepted_value=True)]),
            ],
            create_excel_file=True,
            create_html_file=True,
            display_output_plots=DISPLAY_OUTPUT,
            generate_by_project_instruction=ui_and_results_generation.GenerateByProjectInstruction.BY_PROJECT_AND_ALSO_GLOBAL_ALL_PROJECTS,
        )

        ui_and_results_generation.produce_line_graphs_number_of_cfx_by_state_per_date_results_and_displays(
            cfx_library=all_champfx_library,
            output_directory_name=OUTPUT_DIRECTORY_NAME,
            display_without_cumulative_eras=False,
            display_with_cumulative_eras=True,
            cfx_filters=[
                cfx.ChampFxFilter(
                    field_filters=[
                        filters.ChampFxFilterFieldCategory(field_accepted_values=[constants.Category.SOFTWARE]),
                        filters.ChampFxFilterFieldType(field_accepted_values=[constants.RequestType.DEFECT]),
                    ]
                ),
            ],
            create_excel_file=True,
            create_html_file=True,
            display_output_plots=DISPLAY_OUTPUT,
            generate_by_project_instruction=ui_and_results_generation.GenerateByProjectInstruction.BY_PROJECT_AND_ALSO_GLOBAL_ALL_PROJECTS,
        )

        ui_and_results_generation.produce_line_graphs_number_of_cfx_by_state_per_date_results_and_displays(
            cfx_library=all_champfx_library,
            output_directory_name=OUTPUT_DIRECTORY_NAME,
            display_without_cumulative_eras=False,
            display_with_cumulative_eras=True,
            cfx_filters=[
                cfx.ChampFxFilter(
                    field_filters=[
                        filters.ChampFxFilterFieldCategory(field_accepted_values=[constants.Category.CONFIGURATION_DATA]),
                        filters.ChampFxFilterFieldType(field_accepted_values=[constants.RequestType.DEFECT]),
                    ]
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
