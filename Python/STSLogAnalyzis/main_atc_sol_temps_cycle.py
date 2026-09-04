from pathlib import Path
import os

from common import file_name_utils
from logger import logger_config

from stsloganalyzis.atc import atc_logs, simech_res, temps_cycle_report
from stsloganalyzis.common import common_filters

OUTPUT_DIRECTORY = "output"

ENABLE_PROFILING = False

# robocopy "C:\Users\fr232487\Siemens AG\ITV_ESSAIS_Usine_NEXTEO - Documents\General\Résultats Tests Plateforme Système 2\Suivi test système PTF2\RL3a.0.2\Campagne de test" "D:\temp\mesures_temps_cycle_usine\PLT_SYST_2_RL3a.0.2_Conf_30" *.res *.zip *.7z /S /R:1 /W:1
# robocopy "C:\Users\fr232487\Siemens AG\ITV_ESSAIS_Usine_NEXTEO - Documents\General\Résultats Tests Plateforme Système 1\RL3a.0.2\Campagne de test\Conf_30" "D:\temp\mesures_temps_cycle_usine\PLT_SYST_1_RL3a.0.2_Conf_30" *.res *.zip *.7z /S /R:1 /W:1


def main() -> None:

    # New-Item -Path Env:LINE_PROFILE -Value 1
    if ENABLE_PROFILING:
        os.environ["LINE_PROFILE"] = "1"
        assert os.environ["LINE_PROFILE"] == "1", f"You must set LINE_PROFILE to 1, it is {os.environ["LINE_PROFILE"]}"
    with logger_config.application_logger():

        files_paths_not_handled_because_errors: list[str] = []
        atc_test_results: list[atc_logs.ATCTestResult] = []

        for environment_type, root_result_files_folder_path in [
            (
                "PLT_SYST_1 RL3A02 Conf30",
                r"D:\temp\mesures_temps_cycle_usine\PLT_SYST_1_RL3a.0.2_Conf_30",
            ),
            (
                "PLT_SYST_2 RL3A02 Conf30",
                r"D:\temp\mesures_temps_cycle_usine\PLT_SYST_2_RL3a.0.2_Conf_30",
            ),
        ]:
            all_input_files = [full_path for full_path in Path(root_result_files_folder_path).rglob("*.res")]
            for input_file_it, input_file_path in enumerate(all_input_files):
                logger_config.print_and_log_info(f"Handle {input_file_it+1} th / {len(all_input_files)} ({round((input_file_it+1)/len(all_input_files)*100,1)}%) input file {input_file_path}")
                try:
                    atc_test_result = (
                        simech_res.SimechResTestResult.Builder(
                            label=f"{file_name_utils.get_file_name_without_extension_from_full_path(input_file_path)} temps cycle",
                            environment_name=environment_type,
                        )
                        .add_file(
                            file_full_path=input_file_path,
                        )
                        .add_variables_names_creation_filter(
                            variables_filter=atc_logs.VariableNameFilter(
                                white_or_black_list=common_filters.WhiteOrBlackListFilterType.WHITELIST,
                                filter_type=common_filters.StringFilterType.BEGIN_WITH_STRING,
                                variables_names=[
                                    "CHEURE",
                                    "CDECALAGE",
                                    "CJOUR",
                                    "CDECENIE",
                                    "TEMPS_AS",
                                    "STAB_CPT",
                                    "HLF",
                                ],
                            )
                        )
                        .add_equipments_names_creation_filter(
                            equipments_filter=atc_logs.EquipmentNameFilter(
                                white_or_black_list=common_filters.WhiteOrBlackListFilterType.BLACKLIST,
                                filter_type=common_filters.StringFilterType.CONTAINS,
                                variables_names=[
                                    ".KINEMATICS",
                                    ".TO.EUROBALISE",
                                    "MOTOR.IXL",
                                ],
                            )
                        )
                        .build()
                    )
                    atc_test_results.append(atc_test_result)
                except AssertionError as ass_err:
                    logger_config.print_and_log_exception(ass_err)
                    logger_config.print_and_log_error(f"Could not compute temps cycle for {input_file_path}")
                    files_paths_not_handled_because_errors.append(str(input_file_path))

        temps_cycle_report.build_temps_cycle_report_from_atc_log(atc_test_results)
        logger_config.print_and_log_error_if(len(files_paths_not_handled_because_errors), f"Files not handled because errors: \n{'\n'.join(files_paths_not_handled_because_errors)}")


if __name__ == "__main__":
    main()
