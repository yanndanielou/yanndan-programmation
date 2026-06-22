from logger import logger_config

from stsloganalyzis.next_data import (
    next_ats_data,
)
from stsloganalyzis.atc import atc_logs, perturbo
from stsloganalyzis.common import common_filters

from common import file_utils

import cProfile, pstats, io
from pstats import SortKey

OUTPUT_DIRECTORY = "output"


def main() -> None:
    with logger_config.application_logger():

        all_files = file_utils.get_files_by_directory_and_file_name_mask(
            directory_path=r"C:\Users\fr232487\Downloads\2026-06-20&21 ITC\Perturbo sol\2026-06-20&21 perturbos duree total",
        )

        for perturbo_file in all_files:

            perturbo_test = (
                perturbo.PerturboTestResult.Builder(label=f"{perturbo_file} temps cycle")
                .add_file(
                    file_full_path=perturbo_file,
                    equipment_name=perturbo_file,
                    forced_cjour_at_beginning_value=2291,
                    forced_cdecenie_value=2,
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
                            "HLF",
                        ],
                    )
                )
                .build()
            )
            # perturbo_test.create_report_all_variables()


if __name__ == "__main__":
    main()
