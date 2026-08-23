from logger import logger_config

from stsloganalyzis.atc import atc_logs, simech_res
from stsloganalyzis.common import common_filters

from common import file_name_utils

OUTPUT_DIRECTORY = "output"


def main() -> None:
    with logger_config.application_logger():

        all_files = [
            r"D:\temp\Panne_VCC_US_CPA_A_Manu_RL3A01_20260625.res",
            r"C:\Users\fr232487\DOWNLO~1\PAD_61~1.TAR\PAD_61~1.1_O\PAD_61~1.RES",
        ]

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
                            "STAB_CPT",
                        ],
                    )
                )
                .build()
            )
            simech_res_test.create_report_all_variables()


if __name__ == "__main__":
    main()
