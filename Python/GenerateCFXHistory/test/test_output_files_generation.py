import inspect
import os

import glob

import pytest
from logger import logger_config

import shutil

from generatecfxhistory import (
    cfx,
    constants,
    filters,
    inputs,
    role,
    ui_and_results_generation,
)

CREATE_JSON_DUMP = True
CREATE_EXCEL_FILE = True
CREATE_HTML_FILE = True

DISPLAY_OUTPUT = False

OUTPUT_TESTS_PARENT_DIRECTORY = "output_for_tests"


class TestGenerateByProjectInstruction:

    def test_by_project_and_also_global_all_projects_nextlib(self) -> None:

        output_directory_name = f"{OUTPUT_TESTS_PARENT_DIRECTORY}/{inspect.stack(0)[0].function}"
        # output_directory_path = os.path.(output_directory_name)

        if not os.path.exists(OUTPUT_TESTS_PARENT_DIRECTORY):
            os.mkdir(OUTPUT_TESTS_PARENT_DIRECTORY)
        if os.path.exists(output_directory_name):
            shutil.rmtree(output_directory_name)
        if not os.path.exists(output_directory_name):
            os.mkdir(output_directory_name)

        cfx_inputs = (
            inputs.ChampFxInputsWithFilesBuilder()
            .add_champfx_details_excel_file_full_path("Input_Downloaded/details_project_FR_NEXTEO.xlsx")
            .add_champfx_states_changes_excel_file_full_path("Input_Downloaded/states_changes_project_FR_NEXTEO.xlsx")
            .build()
        )

        nextatsp_champfx_library = cfx.ChampFXLibrary(cfx_inputs=cfx_inputs)
        ui_and_results_generation.produce_results_and_displays_for_libary(
            cfx_library=nextatsp_champfx_library,
            generation_instructions=ui_and_results_generation.GenerationInstructionsForLibary(
                output_directory_name=output_directory_name,
                for_global=True,
                for_each_subsystem=False,
                for_each_current_owner_per_date=False,
                create_excel_file=True,
                create_html_file=True,
                generate_by_project_instruction=ui_and_results_generation.GenerateByProjectInstruction.BY_PROJECT_AND_ALSO_GLOBAL_ALL_PROJECTS,
                display_output_plots=DISPLAY_OUTPUT,
                dump_all_cfx_ids_in_json=CREATE_JSON_DUMP,
            ),
        )

        assert glob.glob(f"{output_directory_name}/All cumulative*.html")
        assert glob.glob(f"{output_directory_name}/All cumulative*.png")
        assert glob.glob(f"{output_directory_name}/All*.json")

        assert glob.glob(f"{output_directory_name}/*FR_NEXTEO*cumulative*.html")
        assert glob.glob(f"{output_directory_name}/*FR_NEXTEO*cumulative*.png")
        assert glob.glob(f"{output_directory_name}/*FR_NEXTEO*.json")

    def test_by_project_only_projects_nextlib(self) -> None:

        output_directory_name = f"{OUTPUT_TESTS_PARENT_DIRECTORY}/{inspect.stack(0)[0].function}"
        # output_directory_path = os.path.(output_directory_name)

        if not os.path.exists(OUTPUT_TESTS_PARENT_DIRECTORY):
            os.mkdir(OUTPUT_TESTS_PARENT_DIRECTORY)
        if os.path.exists(output_directory_name):
            shutil.rmtree(output_directory_name)
        if not os.path.exists(output_directory_name):
            os.mkdir(output_directory_name)

        cfx_inputs = (
            inputs.ChampFxInputsWithFilesBuilder()
            .add_champfx_details_excel_file_full_path("Input_Downloaded/details_project_FR_NEXTEO.xlsx")
            .add_champfx_states_changes_excel_file_full_path("Input_Downloaded/states_changes_project_FR_NEXTEO.xlsx")
            .build()
        )

        nextatsp_champfx_library = cfx.ChampFXLibrary(cfx_inputs=cfx_inputs)
        ui_and_results_generation.produce_results_and_displays_for_libary(
            cfx_library=nextatsp_champfx_library,
            generation_instructions=ui_and_results_generation.GenerationInstructionsForLibary(
                output_directory_name=output_directory_name,
                for_global=True,
                for_each_subsystem=False,
                for_each_current_owner_per_date=False,
                create_excel_file=True,
                create_html_file=True,
                generate_by_project_instruction=ui_and_results_generation.GenerateByProjectInstruction.BY_PROJECT,
                display_output_plots=DISPLAY_OUTPUT,
                dump_all_cfx_ids_in_json=CREATE_JSON_DUMP,
            ),
        )

        assert not glob.glob(f"{output_directory_name}/All cumulative*.html")
        assert not glob.glob(f"{output_directory_name}/All cumulative*.png")
        assert not glob.glob(f"{output_directory_name}/All*.json")

        assert glob.glob(f"{output_directory_name}/*FR_NEXTEO*cumulative*.html")
        assert glob.glob(f"{output_directory_name}/*FR_NEXTEO*cumulative*.png")
        assert glob.glob(f"{output_directory_name}/*FR_NEXTEO*.json")
