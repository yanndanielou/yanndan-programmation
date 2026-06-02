from logger import logger_config

from stsloganalyzis import (
    next_data,
)
from stsloganalyzis.atc import simech_res

OUTPUT_DIRECTORY = "output"


def main() -> None:
    with logger_config.application_logger():
        perturbo_test = (
            simech_res.SimechResTestResult.Builder(label="DMI DECO").add_file(
                file_full_path=r"C:\Users\fr232487\Downloads\2026-05-28 12h3 déconnexion DMI majeure\11.4.1_LR_CPA_A-Quai_ZMS-OP-F-URG-Aval-OT_alarm_incendie_20260528 (1).res",
            )
            # .add_variables_names_creation_filter(variables_filter=atc_logs.VariableFilter)
            .build()
        )
        perturbo_test.create_report_all_variables()


if __name__ == "__main__":
    main()
