from logger import logger_config

from stsloganalyzis import (
    archive_analyzis,
    decode_archive,
    next_data,
    atc_logs,
    perturbo,
)
from dateutil import parser

OUTPUT_DIRECTORY = "output"


def main() -> None:
    with logger_config.application_logger():
        perturbo_test = (
            perturbo.PerturboTestResult.Builder()
            .add_file(file_full_path=r"C:\Users\fr232487\Downloads\260330_011108_prb cnx evc (2) - Copie.txt", equipment_name="PAE 48")
            .add_variables_filter(variables_filter=atc_logs.VariableFilter)
            .build()
        )


if __name__ == "__main__":
    main()
