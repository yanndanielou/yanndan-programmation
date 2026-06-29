from logger import logger_config

from stsloganalyzis.next_data import (
    next_ats_data,
)
from stsloganalyzis.atc import atc_logs, simech_res
from stsloganalyzis.common import common_filters

from common import file_utils, file_name_utils

import cProfile, pstats, io
from pstats import SortKey

OUTPUT_DIRECTORY = "output"


def main() -> None:
    with logger_config.application_logger():

        all_files = [r"C:\Users\fr232487\DOWNLO~1\PAD_61~1.TAR\PAD_61~1.1_O\PAD_61~1.RES"]

        for simech_res_file in all_files:

            simech_res_test = (
                simech_res.SimechResTestResult.Builder(label=f"{file_name_utils.get_file_name_without_extension_from_full_path(simech_res_file)} temps cycle")
                .add_file(
                    file_full_path=simech_res_file,
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
                            "STAB_CPT1",
                        ],
                    )
                )
                .build()
            )
            simech_res_test.create_report_all_variables()


if __name__ == "__main__":
    main()
