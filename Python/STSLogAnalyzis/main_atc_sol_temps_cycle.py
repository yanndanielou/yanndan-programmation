import cProfile
import io
import os
import pstats
from pstats import SortKey

from common import file_name_utils
from logger import logger_config

from stsloganalyzis.atc import atc_logs, simech_res, temps_cycle_report
from stsloganalyzis.common import common_filters
from stsloganalyzis.next_data import next_ats_data

OUTPUT_DIRECTORY = "output"

ENABLE_PROFILING = False


def main() -> None:

    # New-Item -Path Env:LINE_PROFILE -Value 1
    if ENABLE_PROFILING:
        os.environ["LINE_PROFILE"] = "1"
        assert os.environ["LINE_PROFILE"] == "1", f"You must set LINE_PROFILE to 1, it is {os.environ["LINE_PROFILE"]}"
    with logger_config.application_logger():

        perturbo_file_full_path = r"D:\temp\mesures_temps_cycle_usine\rl3a02\YDA_4.1_LR_TrDyn_KVB-CMC_V1EO_PLDE7523__CMC_UM_A_ - partial.res"
        perturbo_file_full_path = r"D:\temp\mesures_temps_cycle_usine\rl3a02\4.1_LR_TrDyn_KVB-CMC_V1EO_PLDE7523__CMC_UM_A_.res"
        perturbo_test = (
            simech_res.SimechResTestResult.Builder(label=f"{file_name_utils.get_file_name_without_extension_from_full_path(perturbo_file_full_path)} temps cycle")
            .add_file(
                file_full_path=perturbo_file_full_path,
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
        temps_cycle_report.build_temps_cycle_report_from_atc_log(perturbo_test)


if __name__ == "__main__":
    main()
