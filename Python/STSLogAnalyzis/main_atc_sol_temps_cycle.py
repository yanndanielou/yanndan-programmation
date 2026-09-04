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

        root_result_files_folder_path = r"D:\temp\mesures_temps_cycle_usine"

        input_files_full_path = [
            r"C:\Users\fr232487\Siemens AG\ITV_ESSAIS_Usine_NEXTEO - Documents\General\Résultats Tests Plateforme Système 1\RL3a.0.2\Campagne de test\Conf_30\3.1.LR_RTV_par_OT\log_3.1.LR_RTV_par_OT\3.1.LR_RTV_par_OT_Manu.res",
            r"D:\temp\mesures_temps_cycle_usine\rl3a02\YDA_4.1_LR_TrDyn_KVB-CMC_V1EO_PLDE7523__CMC_UM_A_ - partial.res",
            r"D:\temp\mesures_temps_cycle_usine\rl3a02\4.1_LR_TrDyn_KVB-CMC_V1EO_PLDE7523__CMC_UM_A_.res",
        ]
        atc_test_results: list[atc_logs.ATCTestResult] = []
        for perturbo_file_path in Path(root_result_files_folder_path).rglob("*.res"):
            atc_test_result = (
                simech_res.SimechResTestResult.Builder(label=f"{file_name_utils.get_file_name_without_extension_from_full_path(perturbo_file_path)} temps cycle")
                .add_file(
                    file_full_path=perturbo_file_path,
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
                .build()
            )
            atc_test_results.append(atc_test_result)
        temps_cycle_report.build_temps_cycle_report_from_atc_log(atc_test_results)


if __name__ == "__main__":
    main()
