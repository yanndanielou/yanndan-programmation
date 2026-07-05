from dateutil import parser
from logger import logger_config

from stsloganalyzis.archive import archive_analyzis, decode_archive
from stsloganalyzis.next_data import (
    next_ats_data,
)

OUTPUT_DIRECTORY = "output"


def main() -> None:
    with logger_config.application_logger():

        railway_line, archive_decoder = next_ats_data.get_encoders(dc_log_folder_full_path=r"C:\D\temp\NEXT_INV_V6_16_P2_conf\conf\dc_log")

        for date_min, date_max, analysis_label in [
            ("2026-03-29T15:40:00.000", "2026-03-29T15:55:00.000", "CFX00924230"),
            # ("2026-06-18T02:00:00.000", "2026-06-18T02:40:00.000", "FU"),
            # ("2026-03-28T16:35:00.000", "2026-03-28T16:59:00.000", "CFX00921734"),
            # ("2026-03-28T16:10:00.000", "2026-03-28T16:28:00.000", "CFX00921756"),
            # ("2026-03-28T22:45:00.000", "2026-03-28T23:05:00.000", "CFX00921760"),
        ]:

            archive_library = (
                next_ats_data.get_classic_archive_library_base_builder(archive_decoder=archive_decoder)
                # .add_archive_file(
                #    file_full_path=r"C:\Users\fr232487\Downloads\2026-06-17&18 ITC\logs_ats\NEXTFileArchiveServer_439.json"
                # )
                .add_archive_files(directory_path=r"C:\Users\fr232487\Downloads\Archives_site_202-03- 27 au 29", filename_pattern="NEXTFileArchiveServer_*.json")
                # .add_archive_file(file_full_path=r"C:\Users\fr232487\Downloads\Archives_site_202-03- 27 au 29\CFX00921734_FU.json")
                # .add_archive_file(file_full_path=r"C:\Users\fr232487\Downloads\Archives_site_202-03- 27 au 29\NEXTFileArchiveServer_238.json")
                .add_sqlarch_archive_lines_filter(
                    decode_archive.DatesFilter.DateBetweenFilter(
                        date_min=parser.parse(date_min),
                        date_max=parser.parse(date_max),
                    )
                )
                # .add_sqlarch_archive_lines_filter(
                #    decode_archive.IdFilter(
                #        field_values="M_PAS_01_ZC_ATS_TRACKING_STATUS_VB_TE",
                #        filter_type=common_filters.StringFilterType.EQUALS_TO,
                #        white_or_black_list=common_filters.WhiteOrBlackListFilterType.WHITELIST,
                #    )
                # )
                .build()
            )

            analyzis = archive_analyzis.ArchiveAnalyzis(railway_line=railway_line, archive_library=archive_library, label=analysis_label)

            analyzis.create_reports_all_sqlarch_changes_since_previous()
            analyzis.create_output_with_all_fields_decoded()


if __name__ == "__main__":
    main()
