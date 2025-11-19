import os

from logger import logger_config

from generatecfxhistory import cfx, filters
from generatecfxhistory import constants, role, inputs
from generatecfxhistory import ui_and_results_generation

OUTPUT_DIRECTORY_NAME = "output"
CREATE_JSON_DUMP = True
CREATE_EXCEL_FILE = True
CREATE_HTML_FILE = True

DISPLAY_OUTPUT = False


def main() -> None:
    """Main function"""

    with logger_config.application_logger("GenerateCFXHistory_nextatsp"):

        if not os.path.exists(OUTPUT_DIRECTORY_NAME):
            os.mkdir(OUTPUT_DIRECTORY_NAME)

        cfx_inputs = (
            inputs.ChampFxInputsWithFilesBuilder()
            .add_champfx_details_excel_file_full_path("Input_Downloaded/details_project_FR_NEXTEO.xlsx")
            .add_champfx_details_excel_file_full_path("Input_Downloaded/details_project_ATSP.xlsx")
            .add_champfx_states_changes_excel_file_full_path("Input_Downloaded/states_changes_project_FR_NEXTEO.xlsx")
            .add_champfx_states_changes_excel_file_full_path("Input_Downloaded/states_changes_project_ATSP.xlsx")
            .add_cfx_extended_history_file_full_path("Input_Downloaded/extended_history_nextats.txt")
            .set_user_and_role_data_text_file_full_path("Input/role_data_next_ats.txt")
            .build()
        )

        nextatsp_champfx_library = cfx.ChampFXLibrary(cfx_inputs=cfx_inputs)

        ui_and_results_generation.produce_results_and_displays_for_library(
            cfx_library=nextatsp_champfx_library,
            generation_instructions=ui_and_results_generation.GenerationInstructionsForLibary(
                output_directory_name=OUTPUT_DIRECTORY_NAME,
                for_global=True,
                for_each_subsystem=False,
                for_each_current_owner_per_date=False,
                cfx_filters=[
                    filters.ChampFxFilter(
                        field_filters=[
                            filters.ChampFxFilterFieldSubsystem(
                                field_accepted_values=[role.SubSystem.SW, role.SubSystem.SW_ANALYSES_SECU, role.SubSystem.SW_TESTS_SECU, role.SubSystem.SW_VAL], forced_label="ADC DC"
                            ),
                            filters.ChampFxFilterFieldType(field_accepted_values=[constants.RequestType.DEFECT]),
                        ]
                    ),
                ],
                create_excel_file=True,
                create_html_file=True,
                display_output_plots=DISPLAY_OUTPUT,
                dump_all_cfx_ids_in_json=CREATE_JSON_DUMP,
            ),
        )

        ui_and_results_generation.produce_results_and_displays_for_library(
            cfx_library=nextatsp_champfx_library,
            generation_instructions=ui_and_results_generation.GenerationInstructionsForLibary(
                output_directory_name=OUTPUT_DIRECTORY_NAME,
                for_global=True,
                for_each_subsystem=False,
                for_each_current_owner_per_date=False,
                cfx_filters=[
                    cfx.ChampFxFilter(
                        field_filters=[
                            filters.ChampFxFilterFieldSubsystem(
                                field_accepted_values=[role.SubSystem.SW, role.SubSystem.SW_ANALYSES_SECU, role.SubSystem.SW_TESTS_SECU, role.SubSystem.SW_VAL], forced_label="ADC DC"
                            ),
                            filters.ChampFxFilterFieldType(field_forbidden_values=[constants.RequestType.DEFECT]),
                        ]
                    ),
                ],
                create_excel_file=True,
                create_html_file=True,
                display_output_plots=DISPLAY_OUTPUT,
                dump_all_cfx_ids_in_json=CREATE_JSON_DUMP,
            ),
        )

        ui_and_results_generation.produce_results_and_displays_for_library(
            cfx_library=nextatsp_champfx_library,
            generation_instructions=ui_and_results_generation.GenerationInstructionsForLibary(
                output_directory_name=OUTPUT_DIRECTORY_NAME,
                for_global=True,
                for_each_subsystem=False,
                for_each_current_owner_per_date=False,
                cfx_filters=[
                    cfx.ChampFxFilter(
                        field_filters=[
                            filters.ChampFxFilterFieldSubsystem(
                                field_accepted_values=[role.SubSystem.SW, role.SubSystem.SW_ANALYSES_SECU, role.SubSystem.SW_TESTS_SECU, role.SubSystem.SW_VAL], forced_label="ADC DC"
                            ),
                        ]
                    ),
                ],
                create_excel_file=True,
                create_html_file=True,
                display_output_plots=DISPLAY_OUTPUT,
                dump_all_cfx_ids_in_json=CREATE_JSON_DUMP,
            ),
        )

        ui_and_results_generation.produce_results_and_displays_for_library(
            cfx_library=nextatsp_champfx_library,
            generation_instructions=ui_and_results_generation.GenerationInstructionsForLibary(
                output_directory_name=OUTPUT_DIRECTORY_NAME,
                for_global=True,
                for_each_subsystem=False,
                for_each_current_owner_per_date=False,
                cfx_filters=[
                    cfx.ChampFxFilter(
                        field_filters=[
                            filters.ChampFxFilterFieldSafetyRelevant(field_accepted_value=True),
                            filters.ChampFxFilterFieldSubsystem(
                                field_accepted_values=[role.SubSystem.SW, role.SubSystem.SW_ANALYSES_SECU, role.SubSystem.SW_TESTS_SECU, role.SubSystem.SW_VAL], forced_label="ADC DC"
                            ),
                        ]
                    ),
                ],
                create_excel_file=True,
                create_html_file=True,
                display_output_plots=DISPLAY_OUTPUT,
                dump_all_cfx_ids_in_json=CREATE_JSON_DUMP,
            ),
        )

        ui_and_results_generation.produce_results_and_displays_for_library(
            cfx_library=nextatsp_champfx_library,
            generation_instructions=ui_and_results_generation.GenerationInstructionsForLibary(
                output_directory_name=OUTPUT_DIRECTORY_NAME,
                for_global=True,
                for_each_subsystem=False,
                for_each_current_owner_per_date=False,
                cfx_filters=[
                    cfx.ChampFxFilter(
                        field_filters=[
                            filters.ChampFxFilterFieldSafetyRelevant(field_accepted_value=False),
                            filters.ChampFxFilterFieldSubsystem(
                                field_accepted_values=[role.SubSystem.SW, role.SubSystem.SW_ANALYSES_SECU, role.SubSystem.SW_TESTS_SECU, role.SubSystem.SW_VAL], forced_label="ADC DC"
                            ),
                        ]
                    ),
                ],
                create_excel_file=True,
                create_html_file=True,
                display_output_plots=DISPLAY_OUTPUT,
                dump_all_cfx_ids_in_json=CREATE_JSON_DUMP,
            ),
        )

        ui_and_results_generation.produce_results_and_displays_for_library(
            cfx_library=nextatsp_champfx_library,
            generation_instructions=ui_and_results_generation.GenerationInstructionsForLibary(
                output_directory_name=OUTPUT_DIRECTORY_NAME,
                for_global=True,
                for_each_subsystem=False,
                for_each_current_owner_per_date=False,
                cfx_filters=[
                    cfx.ChampFxFilter(cfx_to_treat_whitelist_text_file_full_path="Input/CFX_list_cyber_aio.txt"),
                ],
                create_excel_file=True,
                create_html_file=True,
                display_output_plots=DISPLAY_OUTPUT,
                dump_all_cfx_ids_in_json=CREATE_JSON_DUMP,
            ),
        )

        ui_and_results_generation.produce_results_and_displays_for_library(
            cfx_library=nextatsp_champfx_library,
            generation_instructions=ui_and_results_generation.GenerationInstructionsForLibary(
                output_directory_name=OUTPUT_DIRECTORY_NAME,
                for_global=True,
                for_each_subsystem=True,
                for_each_current_owner_per_date=True,
                cfx_filters=[
                    cfx.ChampFxFilter(cfx_to_treat_whitelist_text_file_full_path="Input/CFX_usine_site.txt"),
                ],
                create_excel_file=True,
                create_html_file=True,
                display_output_plots=DISPLAY_OUTPUT,
                dump_all_cfx_ids_in_json=CREATE_JSON_DUMP,
            ),
        )

        ui_and_results_generation.produce_results_and_displays_for_library(
            cfx_library=nextatsp_champfx_library,
            generation_instructions=ui_and_results_generation.GenerationInstructionsForLibary(
                output_directory_name=OUTPUT_DIRECTORY_NAME,
                for_global=True,
                for_each_subsystem=False,
                for_each_current_owner_per_date=True,
                cfx_filters=[
                    cfx.ChampFxFilter(
                        field_filters=[
                            filters.ChampFxFilterFieldSecurityRelevant(field_accepted_values=[constants.SecurityRelevant.YES, constants.SecurityRelevant.MITIGATED], forced_label="Security relevant")
                        ]
                    ),
                ],
                create_excel_file=True,
                create_html_file=True,
                display_output_plots=DISPLAY_OUTPUT,
                dump_all_cfx_ids_in_json=CREATE_JSON_DUMP,
            ),
        )

        ui_and_results_generation.produce_results_and_displays_for_library(
            cfx_library=nextatsp_champfx_library,
            generation_instructions=ui_and_results_generation.GenerationInstructionsForLibary(
                output_directory_name=OUTPUT_DIRECTORY_NAME,
                for_global=True,
                for_each_subsystem=True,
                for_each_current_owner_per_date=True,
                cfx_filters=[
                    cfx.ChampFxFilter(field_filters=[filters.ChampFxFilterFieldSafetyRelevant(field_accepted_value=True)]),
                ],
                create_excel_file=False,
                create_html_file=True,
                display_output_plots=DISPLAY_OUTPUT,
                dump_all_cfx_ids_in_json=CREATE_JSON_DUMP,
                generate_by_project_instruction=ui_and_results_generation.GenerateByProjectInstruction.BY_PROJECT_AND_ALSO_GLOBAL_ALL_PROJECTS,
            ),
        )

        ui_and_results_generation.produce_results_and_displays(
            cfx_library=nextatsp_champfx_library,
            display_without_cumulative_eras=False,
            display_with_cumulative_eras=True,
            generation_instructions=ui_and_results_generation.GenerationInstructionsForLibary(
                output_directory_name=OUTPUT_DIRECTORY_NAME,
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
                dump_all_cfx_ids_in_json=CREATE_JSON_DUMP,
                generate_by_project_instruction=ui_and_results_generation.GenerateByProjectInstruction.ONLY_ONE_PROJECT,
                project_in_case_of_generate_by_project_instruction_one_project=constants.CfxProject.ATSP,
            ),
        )

        ui_and_results_generation.produce_results_and_displays(
            cfx_library=nextatsp_champfx_library,
            display_without_cumulative_eras=False,
            display_with_cumulative_eras=True,
            generation_instructions=ui_and_results_generation.GenerationInstructions(
                output_directory_name=OUTPUT_DIRECTORY_NAME,
                cfx_filters=[
                    cfx.ChampFxFilter(
                        field_filters=[
                            filters.ChampFxFilterFieldCategory(field_accepted_values=[constants.Category.CONFIGURATION_DATA]),
                            filters.ChampFxFilterFieldType(field_accepted_values=[constants.RequestType.DEFECT]),
                        ]
                    ),
                ],
                create_excel_file=True,
                create_html_file=True,
                display_output_plots=DISPLAY_OUTPUT,
                dump_all_cfx_ids_in_json=CREATE_JSON_DUMP,
                generate_by_project_instruction=ui_and_results_generation.GenerateByProjectInstruction.ONLY_ONE_PROJECT,
                project_in_case_of_generate_by_project_instruction_one_project=constants.CfxProject.ATSP,
            ),
        )

        ui_and_results_generation.produce_results_and_displays_for_library(
            cfx_library=nextatsp_champfx_library,
            generation_instructions=ui_and_results_generation.GenerationInstructionsForLibary(
                output_directory_name=OUTPUT_DIRECTORY_NAME,
                for_global=True,
                for_each_subsystem=True,
                for_each_current_owner_per_date=True,
                create_excel_file=True,
                create_html_file=True,
                generate_by_project_instruction=ui_and_results_generation.GenerateByProjectInstruction.BY_PROJECT_AND_ALSO_GLOBAL_ALL_PROJECTS,
                display_output_plots=DISPLAY_OUTPUT,
                dump_all_cfx_ids_in_json=CREATE_JSON_DUMP,
            ),
        )

        if DISPLAY_OUTPUT:
            ui_and_results_generation.block_execution_and_keep_all_windows_open()


if __name__ == "__main__":
    # sys.argv[1:]
    main()
