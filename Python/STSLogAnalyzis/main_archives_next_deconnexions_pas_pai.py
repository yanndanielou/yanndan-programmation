from datetime import timedelta

from logger import logger_config

from stsloganalyzis.archive import archive_analyzis, decode_archive
from stsloganalyzis.common import common_filters
from stsloganalyzis.next_data import (
    next_ats_data,
)

OUTPUT_DIRECTORY = "output"


def main() -> None:
    with logger_config.application_logger():

        # railway_line, archive_decoder = next_ats_data.get_encoders()
        archive_library = (
            next_ats_data.get_classic_archive_library_base_builder(archive_decoder=None)
            .add_archive_files(directory_path=r"D:\temp\TemporaryArchiving 2026-11-02 PLT_1\TemporaryArchiving", filename_pattern="NEXTFileArchiveServer_*.json")
            .add_sqlarch_archive_lines_filter(
                decode_archive.IdFilter(
                    field_values=[
                        "S_PAI_.*._PAS_0._LINK_LOSS",
                        "S_PAS_.*_ZAUM.*_RAZ_RESTRICTED",
                    ],
                    filter_type=common_filters.StringFilterType.MATCHES_REGEX,
                    white_or_black_list=common_filters.WhiteOrBlackListFilterType.WHITELIST,
                )
            )
            .build()
        )

        analyzis = archive_analyzis.ArchiveAnalyzis(railway_line=None, archive_library=archive_library, label="déconnexions PAS PAI ITV 1 2026-09-11")

        # analyzis.create_reports_all_sqlarch_changes_since_previous()
        # analyzis.create_output_with_all_fields_decoded()
        analyzis.create_output_with_frequencies_of_terms(
            groups_definitions_to_create=[
                archive_analyzis.ArchiveAnalyzis.GroupToCreateForFrequencyReportDefinition(
                    split_by_id=True,
                    archive_id_filters=[
                        common_filters.StringFieldValueBasedFilter(
                            field_values="S_PAI_.*_PAS_0._LINK_LOSS",
                            filter_type=common_filters.StringFilterType.MATCHES_REGEX,
                            white_or_black_list=common_filters.WhiteOrBlackListFilterType.WHITELIST,
                        ),
                    ],
                    label="PAI PAS LINK",
                ),
                archive_analyzis.ArchiveAnalyzis.GroupToCreateForFrequencyReportDefinition(
                    split_by_id=False,
                    archive_id_filters=[
                        common_filters.StringFieldValueBasedFilter(
                            field_values="S_PAS_.*_ZAUM.*_RAZ_RESTRICTED",
                            filter_type=common_filters.StringFilterType.MATCHES_REGEX,
                            white_or_black_list=common_filters.WhiteOrBlackListFilterType.WHITELIST,
                        ),
                    ],
                    label="RAZ restricted",
                ),
            ],
            frequency_between_measures=timedelta(minutes=30),
            file_base_name="ZAUM vs PAI PAS link",
        )


if __name__ == "__main__":
    main()
