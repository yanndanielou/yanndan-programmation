import os

from logger import logger_config

from stsloganalyzis.atc import temps_cycle_report

OUTPUT_DIRECTORY = "output"

ENABLE_PROFILING = False

# robocopy "C:\Users\fr232487\Siemens AG\ITV_ESSAIS_Usine_NEXTEO - Documents\General\Résultats Tests Plateforme Système 2\Suivi test système PTF2\RL3a.0.2\Campagne de test" "D:\temp\mesures_temps_cycle_usine\PLT_SYST_2_RL3a.0.2_Conf_30" *.res *.zip *.7z *.tar *.gz /S /R:1 /W:1
# robocopy "C:\Users\fr232487\Siemens AG\ITV_ESSAIS_Usine_NEXTEO - Documents\General\Résultats Tests Plateforme Système 1\RL3a.0.2\Campagne de test\Conf_30" "D:\temp\mesures_temps_cycle_usine\PLT_SYST_1_RL3a.0.2_Conf_30" *.res *.zip *.7z *.tar *.gz /S /R:1 /W:1


def main() -> None:

    # New-Item -Path Env:LINE_PROFILE -Value 1
    if ENABLE_PROFILING:
        os.environ["LINE_PROFILE"] = "1"
        assert os.environ["LINE_PROFILE"] == "1", f"You must set LINE_PROFILE to 1, it is {os.environ["LINE_PROFILE"]}"
    with logger_config.application_logger():

        # temps_cycle_report.process_root_folders_and_environments_build_results_then_reports(
        temps_cycle_report.process_root_folders_and_environments(
            [
                (
                    "PLT_SYST_1 RL3A02 Conf30",
                    r"D:\temp\mesures_temps_cycle_usine\PLT_SYST_1_RL3a.0.2_Conf_30____",
                ),
                (
                    "PLT_SYST_2 RL3A02 Conf30",
                    r"D:\temp\mesures_temps_cycle_usine\PLT_SYST_2_RL3a.0.2_Conf_30___",
                ),
                (
                    "4.1_LR_TrDyn_KVB",
                    r"D:\temp\mesures_temps_cycle_usine\PLT_SYST_2_RL3a.0.2_Conf_30\4.1_LR_TrDyn_KVB-CMC_V2EO_PLDE2480__CMC_US_AC_V2EO_PLDE2480__CMC_US_A",
                ),
            ],
        )


if __name__ == "__main__":
    main()
