import os
from collections import OrderedDict
from itertools import chain

from common import reports_utils
from logger import logger_config

from datetime import timedelta

from stsloganalyzis.pai import pai_archives_mccs
from stsloganalyzis.common import common_filters


def main() -> None:

    with logger_config.application_logger():

        root_path = r"D:\temp\YannDanielouASupprimer\TT-026397\c_travail_archives"
        all_sub_directories = [f for f in os.listdir(root_path) if os.path.isdir(os.path.join(root_path, f))]

        logger_config.print_and_log_info(f"{len(all_sub_directories)} child directories")
        for child_directory in all_sub_directories:

            logger_config.print_and_log_info(f"Handling directory {child_directory}")
            library = pai_archives_mccs.PaiMccsArchivesLibrary(
                directory_path=root_path + "\\" + child_directory,
                label=child_directory,
                # lines_creation_filters=[
                #    common_filters.StringFieldValueBasedFilter(
                #        white_or_black_list=common_filters.WhiteOrBlackListFilterType.WHITELIST,
                #        field_values="Expiration timeout message UGS",
                #        filter_type=common_filters.StringFilterType.CONTAINS,
                #    )
                # ],
            )

            all_timeout_pas_pai_lines = [log_line for log_line in library.decoded_lines if "Expiration timeout message UGS" in log_line.raw_log_line]

            reports_utils.save_rows_to_output_files(
                rows_as_list_dict=[
                    OrderedDict(
                        {
                            "timestamp": log_line.timestamp.timestamp,
                            "timestamp (iso format)": log_line.timestamp.timestamp.isoformat(),
                            "Number of lines since timestamp": (
                                log_line.line_number - log_line.timestamp.line_number_in_file if log_line.file.file_full_path == log_line.timestamp.file_path else "NA, files different"
                            ),
                            "File name": log_line.file.file_name,
                            "Line number": log_line.line_number,
                            "full line": log_line.raw_log_line,
                        }
                    )
                    for log_line in all_timeout_pas_pai_lines
                ],
                file_base_name=child_directory,
                create_csv_file=False,
                create_txt_file=False,
                split_big_files=False,
                chunk_size=200000,
            )

            library.create_output_with_frequencies_of_terms(
                lines_to_use=all_timeout_pas_pai_lines,
                frequency_between_measures=timedelta(minutes=30),
                label="UGS timeout",
            )
            pass
        pass


# Exemple d'utilisation
if __name__ == "__main__":
    main()
