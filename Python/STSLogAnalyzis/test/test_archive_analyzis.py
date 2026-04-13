import pytest

from stsloganalyzis import archive_analyzis, decode_archive, line_topology


@pytest.fixture(scope="session", name="archive_analyzis_zc_ats_mal_fixture")
def archive_analyzis_zc_ats_mal() -> archive_analyzis.ArchiveAnalyzis:

    messages_list_csv_file_full_path = r"D:\NEXT\Data\Csv\NEXT_message.csv"
    xml_directory_path = r"D:\NEXT\Data\Xml"

    railway_line = line_topology.Line.load_from_csv(
        segments_csv_full_path=r"D:\NEXT\Data\Csv\NEXT_segment.csv",
        track_circuits_csv_full_path=r"D:\NEXT\Data\Csv\NEXT_track_circuit.csv",
        tracking_blocks_csv_full_path=r"D:\NEXT\Data\Csv\NEXT_tracking_block.csv",
        switches_csv_full_path=r"D:\NEXT\Data\Csv\NEXT_switch.csv",
        segments_relations_csv_full_path=r"D:\NEXTTS\Data\Csv\NEXT_tsSegmentRelation.csv",
        tracking_block_on_segments_csv_full_path=r"D:\NEXTTS\Data\Csv\NEXT_tsLocUnitTopo.csv",
        ignore_tracking_blocks_without_circuits=True,
    )
    assert railway_line

    archive_decoder = decode_archive.ArchiveDecoder(
        action_set_content_csv_file_path=r"D:\NEXT\Data\Csv\ACTION_SET.csv",
        messages_list_csv_file_full_path=messages_list_csv_file_full_path,
        xml_directory_path=xml_directory_path,
        railway_line=railway_line,
    )

    archive_library = (
        decode_archive.ArchiveLibrary.Builder()
        .add_archive_file(file_full_path=r"Input_for_tests\archives\M_PAS_01_ZC_ATS_MAL.json")
        .add_archive_decoder(archive_decoder=archive_decoder)
        .add_sqlarch_archive_lines_blacklist_filter_based_on_id_term("NB_ACTIVE_SCRUTATION", decode_archive.ArchiveLineFilterOnIdType.CONTAINS)
        .add_sqlarch_archive_lines_blacklist_filter_based_on_id_term("NB_PASSIVE_SCRUTATION", decode_archive.ArchiveLineFilterOnIdType.CONTAINS)
        .add_sqlarch_archive_lines_blacklist_filter_based_on_id_term("QUESTION_NUMBER_ISSUED", decode_archive.ArchiveLineFilterOnIdType.CONTAINS)
        .add_sqlarch_archive_lines_blacklist_filter_based_on_id_term("NB_RESPONSE_ACTIVE_SCRUTATION", decode_archive.ArchiveLineFilterOnIdType.CONTAINS)
        .add_sqlarch_archive_lines_blacklist_filter_based_on_id_term("NB_RESPONSE_PASSIVE_SCRUTATION", decode_archive.ArchiveLineFilterOnIdType.CONTAINS)
        .add_sqlarch_archive_lines_blacklist_filter_based_on_id_term("ACTIVE_QUESTION_NUMBER_RECEIVED", decode_archive.ArchiveLineFilterOnIdType.CONTAINS)
        .add_sqlarch_archive_lines_blacklist_filter_based_on_id_term("PASSIVE_QUESTION_NUMBER_RECEIVED", decode_archive.ArchiveLineFilterOnIdType.CONTAINS)
        .build()
    )

    analyzis = archive_analyzis.ArchiveAnalyzis(railway_line=railway_line, archive_library=archive_library, label="tests")
    return analyzis


class TestArchiveAnalysis:

    def test_create_report(self, archive_analyzis_zc_ats_mal: archive_analyzis.ArchiveAnalyzis) -> None:
        analyzis.create_reports_all_sqlarch_changes_since_previous(
            output_directory_path=OUTPUT_DIRECTORY,
            also_print_and_log=False,
        )
