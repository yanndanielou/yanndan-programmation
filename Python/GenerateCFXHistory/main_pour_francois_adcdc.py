import os

from typing import List

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


atc_bord_filter = cfx.ChampFxFilterFieldConfigUnit(
    field_forbidden_contained_texts=[
        "Component MES",
        "Component PAS",
        "Applicatif PAS",
        "Module Application PAS",
        "S004_Module PAI",
        "S003_Component PAL",
        "Module Application PAL",
    ],
    forced_label="ATC Bord",
)

atc_sol_filter = cfx.ChampFxFilterFieldConfigUnit(
    field_accepted_contained_texts=[
        "Component MES",
        "Component PAS",
        "Applicatif PAS",
        "Module Application PAS",
        "S004_Module PAI",
        "S003_Component PAL",
        "Module Application PAL",
    ],
    forced_label="ATC Sol",
)


def main() -> None:
    """Main function"""

    with logger_config.stopwatch_with_label("Application duration"):
        logger_config.configure_logger_with_random_log_file_suffix("main_pour_francois_adcdc.py")
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
            .build()
        )

        all_champfx_library = cfx.ChampFXLibrary(cfx_inputs=cfx_inputs)

        def generate_with_filters(field_filters: List[cfx.ChampFXFieldFilter]) -> None:

            adc_dc_subsystem_filter = cfx.ChampFxFilterFieldSubsystem(
                field_accepted_values=[role.SubSystem.SW, role.SubSystem.SW_ANALYSES_SECU, role.SubSystem.SW_TESTS_SECU, role.SubSystem.SW_VAL], forced_label="ADC DC"
            )
            ui_and_results_generation.produce_results_and_displays(
                cfx_library=all_champfx_library,
                output_directory_name=OUTPUT_DIRECTORY_NAME,
                create_excel_file=CREATE_EXCEL_FILE,
                display_without_cumulative_eras=False,
                display_with_cumulative_eras=True,
                create_html_file=CREATE_HTML_FILE,
                display_output_plots=DISPLAY_OUTPUT,
                cfx_filters=[cfx.ChampFxFilter(field_filters=field_filters + [adc_dc_subsystem_filter])],
                dump_all_cfx_ids_in_json=CREATE_JSON_DUMP,
                generate_by_project_instruction=ui_and_results_generation.GenerateByProjectInstruction.GLOBAL_ALL_PROJECTS,
            )

        def generate_for_bord_et_sol_filter(field_filters: List[cfx.ChampFXFieldFilter]) -> None:
            generate_with_filters(field_filters + [atc_bord_filter])
            generate_with_filters(field_filters + [atc_sol_filter])

        request_type_defect_filter = cfx.ChampFxFilterFieldType(field_accepted_values=[cfx.RequestType.DEFECT])
        request_type_not_defect_filter = cfx.ChampFxFilterFieldType(field_forbidden_values=[cfx.RequestType.DEFECT])

        safety_cfx_filter = cfx.ChampFxFilterFieldSafetyRelevant(field_accepted_value=True)
        not_safety_cfx_filter = cfx.ChampFxFilterFieldSafetyRelevant(field_accepted_value=False)

        generate_for_bord_et_sol_filter(
            field_filters=[
                request_type_defect_filter,
            ],
        )
        generate_for_bord_et_sol_filter(
            field_filters=[
                request_type_not_defect_filter,
            ]
        )

        generate_for_bord_et_sol_filter(
            field_filters=[
                not_safety_cfx_filter,
            ]
        )
        generate_for_bord_et_sol_filter(
            field_filters=[
                safety_cfx_filter,
            ]
        )
        generate_for_bord_et_sol_filter(
            field_filters=[],
        )

        generate_with_filters(
            field_filters=[],
        )

        if DISPLAY_OUTPUT:
            ui_and_results_generation.block_execution_and_keep_all_windows_open()


if __name__ == "__main__":
    # sys.argv[1:]
    main()
