from logger import logger_config

from stsloganalyzis import (
    next_data,
)
from stsloganalyzis.atc import atc_logs, perturbo

OUTPUT_DIRECTORY = "output"


def main() -> None:
    with logger_config.application_logger():
        perturbo_test = (
            perturbo.PerturboTestResult.Builder(label="atc temps cycle").add_file(
                file_full_path=r"C:\Users\fr232487\Downloads\260330_011108_prb cnx evc_few_lines.txt",
                equipment_name="PAE 48",
            )
            # .add_variables_names_creation_filter(variables_filter=atc_logs.VariableFilter)
            .build()
        )
        perturbo_test.create_report_all_variables()


if __name__ == "__main__":
    main()
