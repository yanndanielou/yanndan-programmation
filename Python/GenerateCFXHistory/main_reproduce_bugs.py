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
            .add_champfx_details_excel_files_by_directory_and_file_name_mask(directory_path="Input", filename_pattern="details_project_other_projects.xlsx")
            .add_champfx_states_changes_excel_files_by_directory_and_file_name_mask(directory_path="Input", filename_pattern="states_changes_other_projects.xlsx")
            .build()
        )

        all_raw_states: Set[str] = set()
        all_possible_values_by_column: Dict[str, Any] = {}

        "CFXID	State	SubmitDate	RequestType	Category	CurrentOwner.FullName	SystemStructure	Project	SafetyRelevant	SecurityRelevant	FixedImplementedIn	Severity	RejectionCause"

        "CFXID	history.old_state	history.new_state	history.action_timestamp	history.action_name	Project"

        combined_data_frames_list = cfx_inputs.champfx_details_excel_files_full_data_frames | cfx_inputs.champfx_states_changes_excel_files_data_frames
        for _, cfx_details_data_frame in combined_data_frames_list.items():
            for col in cfx_details_data_frame.columns:
                # Get the set of values for this column from the current DataFrame
                values = set(cfx_details_data_frame[col])
                if col in all_possible_values_by_column:
                    # Update the current set with the new values
                    all_possible_values_by_column[col].update(values)
                else:
                    # Initialize the set if the column is not present in the dictionary
                    all_possible_values_by_column[col] = values

        # logger_config.print_and_log_info("all_possible_values_by_column:" + str(all_possible_values_by_column))
        logger_config.print_and_log_info("All states:" + str(all_raw_states))
        logger_config.print_and_log_info("All states:" + str(all_possible_values_by_column["State"]))
        logger_config.print_and_log_info("All Category:" + str(all_possible_values_by_column["Category"]))
        logger_config.print_and_log_info("All RejectionCause:" + str(all_possible_values_by_column["RejectionCause"]))
        logger_config.print_and_log_info("All history.old_state:" + str(all_possible_values_by_column["history.old_state"]))
        logger_config.print_and_log_info("All history.new_state:" + str(all_possible_values_by_column["history.new_state"]))
        # logger_config.print_and_log_info("all_possible_values_by_column:" + str(all_possible_values_by_column))

        for _, cfx_details_data_frame in cfx_inputs.champfx_details_excel_files_full_data_frames.items():
            all_possible_values = {col: set(cfx_details_data_frame[col]) for col in cfx_details_data_frame.columns}
            columns = cfx_details_data_frame.columns
            for _, row in cfx_details_data_frame.iterrows():
                all_raw_states.add(row["State"])

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
