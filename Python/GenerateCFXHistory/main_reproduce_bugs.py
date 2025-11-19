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
            .add_champfx_details_excel_files_by_directory_and_file_name_mask(directory_path="Input_Downloaded", filename_pattern="details_project_other_projects.xlsx")
            .add_champfx_states_changes_excel_files_by_directory_and_file_name_mask(directory_path="Input_Downloaded", filename_pattern="states_changes_other_projects.xlsx")
            .build()
        )

        champfx_library = cfx.ChampFXLibrary(
            cfx_inputs=cfx_inputs, champfx_filters=[cfx.ChampFXWhiteListBasedOnListFilter(cfx_to_treat_ids=["CFX00388493", "CFX00388494", "CFX00388495", "CFX00388496", "CFX00388497", "CFX00388498"])]
        )

        assert champfx_library.get_all_cfx()
        for cfx_entry in champfx_library.get_all_cfx():
            assert cfx_entry.get_oldest_change_action_by_new_state(cfx.State.SUBMITTED), cfx_entry.cfx_id

        ui_and_results_generation.produce_number_of_cfx_by_state_per_date_line_graphs_for_library(
            cfx_library=champfx_library,
            output_directory_name=OUTPUT_DIRECTORY_NAME,
            for_global=True,
            for_each_subsystem=False,
            for_each_current_owner_per_date=False,
            create_excel_file=False,
            create_html_file=True,
            display_output_plots=DISPLAY_OUTPUT,
            generate_by_project_instruction=ui_and_results_generation.GenerateByProjectInstruction.BY_PROJECT_AND_ALSO_GLOBAL_ALL_PROJECTS,
        )

        ui_and_results_generation.produce_number_of_cfx_by_state_per_date_line_graphs_for_library(
            cfx_library=champfx_library,
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

        ui_and_results_generation.produce_number_of_cfx_by_state_per_date_line_graphs_for_library(
            cfx_library=champfx_library,
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

        ui_and_results_generation.produce_line_graphs_number_of_cfx_by_state_per_date_line_graphs(
            cfx_library=champfx_library,
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

        ui_and_results_generation.produce_line_graphs_number_of_cfx_by_state_per_date_line_graphs(
            cfx_library=champfx_library,
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
