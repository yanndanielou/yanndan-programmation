from logger import logger_config

from stsloganalyzis import (
    archive_analyzis,
    decode_action_set_content,
    decode_archive,
    decode_message,
    decode_xml_message,
    line_topology,
    next_data,
)

OUTPUT_DIRECTORY = "output"


def main() -> None:
    with logger_config.application_logger():

        railway_line, archive_decoder = next_data.get_encoders()

        archive_library = (
            decode_archive.ArchiveLibrary.Builder()
            .add_archive_file(file_full_path=r"Input_for_tests\archives\M_PAS_01_ZC_ATS_MAL_several.json")
            # .add_archive_file(file_full_path=r"Input_for_tests\archives\M_PAS_01_ZC_ATS_MAL_one.json")
            .add_archive_decoder(archive_decoder=archive_decoder)
            .add_sqlarch_archive_lines_filter(
                decode_archive.SignalTypeFilter(
                    white_or_black_list=decode_archive.WhiteOrBlackListFilterType.BLACKLIST,
                    field_values=["TRAIN", "ARS_AD", "TB"],
                    filter_type=decode_archive.SqlArchLineStringFieldValueBasedFilter.ArchiveLineStringFilterType.EQUALS_TO,
                )
            )
            .add_sqlarch_archive_lines_filter(
                decode_archive.IdFilter(
                    white_or_black_list=decode_archive.WhiteOrBlackListFilterType.BLACKLIST,
                    field_values=["NB_ACTIVE_SCRUTATION"],
                    filter_type=decode_archive.SqlArchLineStringFieldValueBasedFilter.ArchiveLineStringFilterType.CONTAINS,
                )
            )
            .add_sqlarch_archive_lines_filter(
                decode_archive.IdFilter(
                    white_or_black_list=decode_archive.WhiteOrBlackListFilterType.BLACKLIST,
                    field_values=["NB_RESPONSE_PASSIVE_SCRUTATION"],
                    filter_type=decode_archive.SqlArchLineStringFieldValueBasedFilter.ArchiveLineStringFilterType.CONTAINS,
                )
            )
            .add_sqlarch_archive_lines_filter(
                decode_archive.IdFilter(
                    white_or_black_list=decode_archive.WhiteOrBlackListFilterType.BLACKLIST,
                    field_values=["NB_RESPONSE_ACTIVE_SCRUTATION"],
                    filter_type=decode_archive.SqlArchLineStringFieldValueBasedFilter.ArchiveLineStringFilterType.CONTAINS,
                )
            )
            .add_sqlarch_archive_lines_filter(
                decode_archive.IdFilter(
                    white_or_black_list=decode_archive.WhiteOrBlackListFilterType.BLACKLIST,
                    field_values=["QUESTION_NUMBER_ISSUED"],
                    filter_type=decode_archive.SqlArchLineStringFieldValueBasedFilter.ArchiveLineStringFilterType.CONTAINS,
                )
            )
            .add_sqlarch_archive_lines_filter(
                decode_archive.IdFilter(
                    white_or_black_list=decode_archive.WhiteOrBlackListFilterType.BLACKLIST,
                    field_values=["NB_PASSIVE_SCRUTATION"],
                    filter_type=decode_archive.SqlArchLineStringFieldValueBasedFilter.ArchiveLineStringFilterType.CONTAINS,
                )
            )
            .add_sqlarch_archive_lines_filter(
                decode_archive.IdFilter(
                    white_or_black_list=decode_archive.WhiteOrBlackListFilterType.BLACKLIST,
                    field_values=["ACTIVE_QUESTION_NUMBER_RECEIVED"],
                    filter_type=decode_archive.SqlArchLineStringFieldValueBasedFilter.ArchiveLineStringFilterType.CONTAINS,
                )
            )
            .add_sqlarch_archive_lines_filter(
                decode_archive.IdFilter(
                    white_or_black_list=decode_archive.WhiteOrBlackListFilterType.BLACKLIST,
                    field_values=["PASSIVE_QUESTION_NUMBER_RECEIVED"],
                    filter_type=decode_archive.SqlArchLineStringFieldValueBasedFilter.ArchiveLineStringFilterType.CONTAINS,
                )
            )
            .build()
        )

        analyzis = archive_analyzis.ArchiveAnalyzis(railway_line=railway_line, archive_library=archive_library, label="CFX")
        analyzis.create_reports_all_sqlarch_changes_since_previous(
            output_directory_path=OUTPUT_DIRECTORY,
        )


if __name__ == "__main__":
    main()
