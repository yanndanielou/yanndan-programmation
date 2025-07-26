import os

from dateutil import relativedelta
from logger import logger_config

from generatecfxhistory import cfx
from generatecfxhistory import constants, role
from generatecfxhistory import ui_and_results_generation

OUTPUT_DIRECTORY_NAME = "output"
CREATE_JSON_DUMP = True
CREATE_EXCEL_FILE = True
CREATE_HTML_FILE = True

DISPLAY_OUTPUT = False


def main() -> None:
    """Main function"""

    with logger_config.stopwatch_with_label("Application duration"):
        logger_config.configure_logger_with_random_log_file_suffix("GenerateCFXHistory")
        logger_config.print_and_log_info("Application start")

        if not os.path.exists(OUTPUT_DIRECTORY_NAME):
            os.mkdir(OUTPUT_DIRECTORY_NAME)

        cfx_inputs = (
            cfx.ChampFxInputsBuilder()
            .add_champfx_details_excel_file_full_path("Input/details_project_FR_NEXTEO.xlsx")
            .add_champfx_details_excel_file_full_path("Input/details_project_ATSP.xlsx")
            .add_champfx_states_changes_excel_file_full_path("Input/states_changes_project_FR_NEXTEO.xlsx")
            .add_champfx_states_changes_excel_file_full_path("Input/states_changes_project_ATSP.xlsx")
            .add_cfx_extended_history_file_full_path("Input/extended_history_nextats.txt")
            .set_user_and_role_data_text_file_full_path("Input/role_data_next_ats.txt")
            .build()
        )

        nextatsp_champfx_library = cfx.ChampFXLibrary(cfx_inputs=cfx_inputs)

        ui_and_results_generation.produce_results_and_displays_for_libary(
            cfx_library=nextatsp_champfx_library,
            output_directory_name=OUTPUT_DIRECTORY_NAME,
            for_global=True,
            for_each_subsystem=False,
            for_each_current_owner_per_date=False,
            cfx_filters=[
                cfx.ChampFxFilter(
                    field_filters=[
                        cfx.ChampFxFilterFieldSubsystem(
                            field_accepted_values=[role.SubSystem.SW, role.SubSystem.SW_ANALYSES_SECU, role.SubSystem.SW_TESTS_SECU, role.SubSystem.SW_VAL], forced_label="ADC DC"
                        ),
                        cfx.ChampFxFilterFieldType(field_accepted_values=[cfx.RequestType.DEFECT]),
                    ]
                ),
            ],
            create_excel_file=True,
            create_html_file=True,
            display_output_plots=DISPLAY_OUTPUT,
            dump_all_cfx_ids_in_json=CREATE_JSON_DUMP,
        )

        ui_and_results_generation.produce_results_and_displays_for_libary(
            cfx_library=nextatsp_champfx_library,
            output_directory_name=OUTPUT_DIRECTORY_NAME,
            for_global=True,
            for_each_subsystem=False,
            for_each_current_owner_per_date=False,
            cfx_filters=[
                cfx.ChampFxFilter(
                    field_filters=[
                        cfx.ChampFxFilterFieldSubsystem(
                            field_accepted_values=[role.SubSystem.SW, role.SubSystem.SW_ANALYSES_SECU, role.SubSystem.SW_TESTS_SECU, role.SubSystem.SW_VAL], forced_label="ADC DC"
                        ),
                        cfx.ChampFxFilterFieldType(field_forbidden_values=[cfx.RequestType.DEFECT]),
                    ]
                ),
            ],
            create_excel_file=True,
            create_html_file=True,
            display_output_plots=DISPLAY_OUTPUT,
            dump_all_cfx_ids_in_json=CREATE_JSON_DUMP,
        )

        ui_and_results_generation.produce_results_and_displays_for_libary(
            cfx_library=nextatsp_champfx_library,
            output_directory_name=OUTPUT_DIRECTORY_NAME,
            for_global=True,
            for_each_subsystem=False,
            for_each_current_owner_per_date=False,
            cfx_filters=[
                cfx.ChampFxFilter(
                    field_filters=[
                        cfx.ChampFxFilterFieldSubsystem(
                            field_accepted_values=[role.SubSystem.SW, role.SubSystem.SW_ANALYSES_SECU, role.SubSystem.SW_TESTS_SECU, role.SubSystem.SW_VAL], forced_label="ADC DC"
                        ),
                    ]
                ),
            ],
            create_excel_file=True,
            create_html_file=True,
            display_output_plots=DISPLAY_OUTPUT,
            dump_all_cfx_ids_in_json=CREATE_JSON_DUMP,
        )

        ui_and_results_generation.produce_results_and_displays_for_libary(
            cfx_library=nextatsp_champfx_library,
            output_directory_name=OUTPUT_DIRECTORY_NAME,
            for_global=True,
            for_each_subsystem=False,
            for_each_current_owner_per_date=False,
            cfx_filters=[
                cfx.ChampFxFilter(
                    field_filters=[
                        cfx.ChampFxFilterFieldSafetyRelevant(field_accepted_value=True),
                        cfx.ChampFxFilterFieldSubsystem(
                            field_accepted_values=[role.SubSystem.SW, role.SubSystem.SW_ANALYSES_SECU, role.SubSystem.SW_TESTS_SECU, role.SubSystem.SW_VAL], forced_label="ADC DC"
                        ),
                    ]
                ),
            ],
            create_excel_file=True,
            create_html_file=True,
            display_output_plots=DISPLAY_OUTPUT,
            dump_all_cfx_ids_in_json=CREATE_JSON_DUMP,
        )

        ui_and_results_generation.produce_results_and_displays_for_libary(
            cfx_library=nextatsp_champfx_library,
            output_directory_name=OUTPUT_DIRECTORY_NAME,
            for_global=True,
            for_each_subsystem=False,
            for_each_current_owner_per_date=False,
            cfx_filters=[
                cfx.ChampFxFilter(
                    field_filters=[
                        cfx.ChampFxFilterFieldSafetyRelevant(field_accepted_value=False),
                        cfx.ChampFxFilterFieldSubsystem(
                            field_accepted_values=[role.SubSystem.SW, role.SubSystem.SW_ANALYSES_SECU, role.SubSystem.SW_TESTS_SECU, role.SubSystem.SW_VAL], forced_label="ADC DC"
                        ),
                    ]
                ),
            ],
            create_excel_file=True,
            create_html_file=True,
            display_output_plots=DISPLAY_OUTPUT,
            dump_all_cfx_ids_in_json=CREATE_JSON_DUMP,
        )

        ui_and_results_generation.produce_results_and_displays_for_libary(
            cfx_library=nextatsp_champfx_library,
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
        )

        ui_and_results_generation.produce_results_and_displays_for_libary(
            cfx_library=nextatsp_champfx_library,
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
        )

        ui_and_results_generation.produce_results_and_displays_for_libary(
            cfx_library=nextatsp_champfx_library,
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
        )

        ui_and_results_generation.produce_results_and_displays_for_libary(
            cfx_library=nextatsp_champfx_library,
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
            dump_all_cfx_ids_in_json=CREATE_JSON_DUMP,
        )

        ui_and_results_generation.produce_results_and_displays_for_libary(
            cfx_library=nextatsp_champfx_library,
            output_directory_name=OUTPUT_DIRECTORY_NAME,
            for_global=True,
            for_each_subsystem=True,
            for_each_current_owner_per_date=False,
            cfx_filters=[
                cfx.ChampFxFilter(field_filters=[cfx.ChampFxFilterFieldSafetyRelevant(field_accepted_value=True)]),
            ],
            create_excel_file=False,
            create_html_file=True,
            display_output_plots=DISPLAY_OUTPUT,
            dump_all_cfx_ids_in_json=CREATE_JSON_DUMP,
            generate_by_project_instruction=ui_and_results_generation.GenerateByProjectInstruction.BY_PROJECT_AND_ALSO_GLOBAL_ALL_PROJECTS,
        )

        ui_and_results_generation.produce_results_and_displays(
            cfx_library=nextatsp_champfx_library,
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
            dump_all_cfx_ids_in_json=CREATE_JSON_DUMP,
            generate_by_project_instruction=ui_and_results_generation.GenerateByProjectInstruction.ONLY_ONE_PROJECT,
            project_in_case_of_generate_by_project_instruction_one_project=cfx.CfxProject.ATSP,
        )

        ui_and_results_generation.produce_results_and_displays(
            cfx_library=nextatsp_champfx_library,
            output_directory_name=OUTPUT_DIRECTORY_NAME,
            display_without_cumulative_eras=False,
            display_with_cumulative_eras=True,
            cfx_filters=[
                cfx.ChampFxFilter(
                    field_filters=[cfx.ChampFxFilterFieldCategory(field_accepted_values=[cfx.Category.CONFIGURATION_DATA]), cfx.ChampFxFilterFieldType(field_accepted_values=[cfx.RequestType.DEFECT])]
                ),
            ],
            create_excel_file=True,
            create_html_file=True,
            display_output_plots=DISPLAY_OUTPUT,
            dump_all_cfx_ids_in_json=CREATE_JSON_DUMP,
            generate_by_project_instruction=ui_and_results_generation.GenerateByProjectInstruction.ONLY_ONE_PROJECT,
            project_in_case_of_generate_by_project_instruction_one_project=cfx.CfxProject.ATSP,
        )

        ui_and_results_generation.produce_results_and_displays_for_libary(
            cfx_library=nextatsp_champfx_library,
            output_directory_name=OUTPUT_DIRECTORY_NAME,
            for_global=True,
            for_each_subsystem=True,
            for_each_current_owner_per_date=True,
            create_excel_file=True,
            create_html_file=True,
            generate_by_project_instruction=ui_and_results_generation.GenerateByProjectInstruction.BY_PROJECT_AND_ALSO_GLOBAL_ALL_PROJECTS,
            display_output_plots=DISPLAY_OUTPUT,
            dump_all_cfx_ids_in_json=CREATE_JSON_DUMP,
        )

        if DISPLAY_OUTPUT:
            ui_and_results_generation.block_execution_and_keep_all_windows_open()


if __name__ == "__main__":
    # sys.argv[1:]
    main()
