import os

from dateutil import relativedelta
from logger import logger_config

from generatecfxhistory import cfx
from generatecfxhistory import constants, role
from generatecfxhistory import ui_and_results_generation

OUTPUT_DIRECTORY_NAME = "output_pour_francois_adcdc"
CREATE_JSON_DUMP = True
CREATE_EXCEL_FILE = True
CREATE_HTML_FILE = True

DISPLAY_OUTPUT = False


def main() -> None:
    """Main function"""

    with logger_config.stopwatch_with_label("Application duration"):
        logger_config.configure_logger_with_random_log_file_suffix("main_pour_francois_adcdc.py")
        logger_config.print_and_log_info("Application start")

        if not os.path.exists(OUTPUT_DIRECTORY_NAME):
            os.mkdir(OUTPUT_DIRECTORY_NAME)

        all_champfx_library = cfx.ChampFXLibrary(
            champfx_details_excel_file_full_path="Input/extract_cfx_details.xlsx",
            champfx_states_changes_excel_file_full_path="Input/extract_cfx_change_state.xlsx",
            cfx_extended_history_file_full_path="Input/cfx_extended_history.txt",
            user_and_role_data_text_file_full_path="Input/role_data_next_ats.txt",
        )

        # Bord

        ui_and_results_generation.produce_results_and_displays(
            cfx_library=all_champfx_library,
            output_directory_name=OUTPUT_DIRECTORY_NAME,
            create_excel_file=CREATE_EXCEL_FILE,
            display_without_cumulative_eras=False,
            display_with_cumulative_eras=True,
            create_html_file=CREATE_HTML_FILE,
            display_output_plots=DISPLAY_OUTPUT,
            cfx_filters=[
                cfx.ChampFxFilter(
                    field_filters=[
                        cfx.ChampFxFilterFieldSubsystem(
                            field_accepted_values=[role.SubSystem.SW, role.SubSystem.SW_ANALYSES_SECU, role.SubSystem.SW_TESTS_SECU, role.SubSystem.SW_VAL], forced_label="ADC DC"
                        ),
                        cfx.ChampFxFilterFieldType(field_accepted_values=[cfx.RequestType.DEFECT]),
                        cfx.ChampFxFilterFieldConfigUnit(
                            field_forbidden_contained_texts=[
                                "Component MES",
                                "Component PAS",
                                "Applicatif PAS",
                                "Module Application PAS",
                                "S004_Module PAI",
                                "S003_Component PAL",
                                "Module Application PAL",
                            ],
                            forced_label="ADC DC Bord",
                        ),
                    ]
                ),
            ],
            dump_all_cfx_ids_in_json=CREATE_JSON_DUMP,
            generate_by_project_instruction=ui_and_results_generation.GenerateByProjectInstruction.GLOBAL_ALL_PROJECTS,
        )

        ui_and_results_generation.produce_results_and_displays_for_libary(
            cfx_library=all_champfx_library,
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
                        cfx.ChampFxFilterFieldConfigUnit(
                            field_forbidden_contained_texts=[
                                "Component MES",
                                "Component PAS",
                                "Applicatif PAS",
                                "Module Application PAS",
                                "S004_Module PAI",
                                "S003_Component PAL",
                                "Module Application PAL",
                            ],
                            forced_label="ADC DC Bord",
                        ),
                    ]
                ),
            ],
            create_excel_file=True,
            create_html_file=True,
            display_output_plots=DISPLAY_OUTPUT,
            dump_all_cfx_ids_in_json=CREATE_JSON_DUMP,
        )

        # Sol
        ui_and_results_generation.produce_results_and_displays_for_libary(
            cfx_library=all_champfx_library,
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
                        cfx.ChampFxFilterFieldType(
                            field_accepted_values=[cfx.RequestType.DEFECT],
                            forced_label="Defect",
                        ),
                        cfx.ChampFxFilterFieldConfigUnit(
                            field_accepted_contained_texts=[
                                "Component MES",
                                "Component PAS",
                                "Applicatif PAS",
                                "Module Application PAS",
                                "S004_Module PAI",
                                "S003_Component PAL",
                                "Module Application PAL",
                            ],
                            forced_label="ADC DC Sol",
                        ),
                    ]
                ),
            ],
            create_excel_file=True,
            create_html_file=True,
            display_output_plots=DISPLAY_OUTPUT,
            dump_all_cfx_ids_in_json=CREATE_JSON_DUMP,
        )

        # Bord
        ui_and_results_generation.produce_results_and_displays_for_libary(
            cfx_library=all_champfx_library,
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
                        cfx.ChampFxFilterFieldConfigUnit(
                            field_forbidden_contained_texts=[
                                "Component MES",
                                "Component PAS",
                                "Applicatif PAS",
                                "Module Application PAS",
                                "S004_Module PAI",
                                "S003_Component PAL",
                                "Module Application PAL",
                            ],
                            forced_label="ADC DC Bord",
                        ),
                    ]
                ),
            ],
            create_excel_file=True,
            create_html_file=True,
            display_output_plots=DISPLAY_OUTPUT,
            dump_all_cfx_ids_in_json=CREATE_JSON_DUMP,
        )
        # Sol
        ui_and_results_generation.produce_results_and_displays_for_libary(
            cfx_library=all_champfx_library,
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
                        cfx.ChampFxFilterFieldConfigUnit(
                            field_accepted_contained_texts=[
                                "Component MES",
                                "Component PAS",
                                "Applicatif PAS",
                                "Module Application PAS",
                                "S004_Module PAI",
                                "S003_Component PAL",
                                "Module Application PAL",
                            ],
                            forced_label="ADC DC Sol",
                        ),
                    ]
                ),
            ],
            create_excel_file=True,
            create_html_file=True,
            display_output_plots=DISPLAY_OUTPUT,
        )
        # Bord
        ui_and_results_generation.produce_results_and_displays_for_libary(
            cfx_library=all_champfx_library,
            output_directory_name=OUTPUT_DIRECTORY_NAME,
            for_global=True,
            for_each_subsystem=False,
            for_each_current_owner_per_date=False,
            cfx_filters=[
                cfx.ChampFxFilter(
                    field_filters=[
                        cfx.ChampFxFilterFieldConfigUnit(
                            field_forbidden_contained_texts=[
                                "Component MES",
                                "Component PAS",
                                "Applicatif PAS",
                                "Module Application PAS",
                                "S004_Module PAI",
                                "S003_Component PAL",
                                "Module Application PAL",
                            ],
                            forced_label="ADC DC Bord",
                        ),
                    ]
                ),
            ],
            create_excel_file=True,
            create_html_file=True,
            display_output_plots=DISPLAY_OUTPUT,
            dump_all_cfx_ids_in_json=CREATE_JSON_DUMP,
        )
        # Sol
        ui_and_results_generation.produce_results_and_displays_for_libary(
            cfx_library=all_champfx_library,
            output_directory_name=OUTPUT_DIRECTORY_NAME,
            for_global=True,
            for_each_subsystem=False,
            for_each_current_owner_per_date=False,
            cfx_filters=[
                cfx.ChampFxFilter(
                    field_filters=[
                        cfx.ChampFxFilterFieldConfigUnit(
                            field_accepted_contained_texts=[
                                "Component MES",
                                "Component PAS",
                                "Applicatif PAS",
                                "Module Application PAS",
                                "S004_Module PAI",
                                "S003_Component PAL",
                                "Module Application PAL",
                            ],
                            forced_label="ADC DC Sol",
                        ),
                    ]
                ),
            ],
            create_excel_file=True,
            create_html_file=True,
            display_output_plots=DISPLAY_OUTPUT,
        )

        ui_and_results_generation.produce_results_and_displays_for_libary(
            cfx_library=all_champfx_library,
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
            cfx_library=all_champfx_library,
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
            cfx_library=all_champfx_library,
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
            cfx_library=all_champfx_library,
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
            cfx_library=all_champfx_library,
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

        if DISPLAY_OUTPUT:
            ui_and_results_generation.block_execution_and_keep_all_windows_open()


if __name__ == "__main__":
    # sys.argv[1:]
    main()
