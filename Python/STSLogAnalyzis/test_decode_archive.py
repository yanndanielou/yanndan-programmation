import datetime

import pytest

import decode_archive
import decode_archive
import decode_message

archive_line_str_message_zc_ats_tracking_status = '{"SQLARCH":{"caller":"","catAla":0,"eqp":"PAS 05","eqpId":"EQ_PAS_05_PAS_05","exeSt":"","id":"M_PAS_05_ZC_ATS_TRACKING_STATUS_TRAINS_ID","jdb":false,"label":"PAS_05 : ZC ATS TRACKING STATUS TRAINS ID [161]","loc":"PAS 05","locale":"2025-07-21T10:54:18.439+02:00","newSt":"14 09 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 04 E4 44 00 01 19 40 27 EC ","oldSt":"","orders":"","sigT":"TSA","tstamp":"2025-07-21T10:54:18.000+02:00","utc_locale":"2025-07-21T08:54:18.439+01:00"},"date":"2025-07-21T10:54:18.440+02:00","tags":["SQLARCH"]}'

archive_line_str_message_lc_ats_sso_versions = '{"SQLARCH":{"caller":"","catAla":0,"eqp":"PAL","eqpId":"EQ_PAL_01_PAL_01","exeSt":"","id":"M_PAL_01_LC_ATS_SSO_VERSIONS","jdb":false,"label":"PAL_01 : ATS_LC_SSO_VERSIONS [175]","loc":"PAL","locale":"2025-07-09T12:41:00.208+02:00","newSt":"80 00 00 00 04 10 41 84 20 42 84 30 43 84 40 44 84 50 45 84 60 46 84 70 47 84 B8 4C 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 08 00 00 00 00 00 00 ","oldSt":"","orders":"","sigT":"TSA","tstamp":"2000-01-01T01:00:00.800+01:00","utc_locale":"2025-07-09T10:41:00.208+01:00"},"date":"2025-07-09T12:41:00.208+02:00","tags":["SQLARCH"]}'

archive_line_str_message_pae_ats_soft_versions = '{"SQLARCH":{"caller":"","catAla":0,"eqp":"TRAIN 9","eqpId":"EQ_CET_9","exeSt":"","id":"M_CC_9_CC_ATS_SOFT_VERSIONS","jdb":false,"label":"CC_ATS_SOFT_VERSIONS [113]","loc":"INDETERMINE","locale":"2025-07-09T12:55:53.616+02:00","newSt":"14 09 20 50 41 45 5F 5F 4E 45 58 54 5F 50 41 45 5F 43 55 43 50 5F 56 31 30 5F 30 20 20 20 20 20 20 20 20 20 20 20 20 50 41 45 5F 5F 4E 45 58 54 5F 50 41 45 5F 43 55 43 50 5F 56 31 30 5F 30 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 00 06 01 36 00 01 19 40 27 E0 ","oldSt":"","orders":"","sigT":"TSA","tstamp":"2025-07-09T12:55:52.600+02:00","utc_locale":"2025-07-09T10:55:53.616+01:00"},"date":"2025-07-09T12:55:53.616+02:00","tags":["SQLARCH"]}'
message_manager = decode_message.InvariantMessagesManager(messages_csv_file_full_path=r"D:\NEXT\Data\Csv\NEXT_message.csv")
message_decoder = decode_message.MessageDecoder(xml_directory_path=r"D:\NEXT\Data\Xml")


class TestDecodeOneLine:
    def test_decode_basic_fields_zc_ats_tracking_status(self) -> None:
        archive_line = decode_archive.ArchiveLine(full_raw_archive_line=archive_line_str_message_zc_ats_tracking_status)
        assert archive_line.get_date_raw_str() == "2025-07-21T10:54:18.440+02:00"
        assert archive_line.get_id() == "M_PAS_05_ZC_ATS_TRACKING_STATUS_TRAINS_ID"
        assert (
            archive_line.get_new_state_str()
            == "14 09 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 04 E4 44 00 01 19 40 27 EC "
        )

    def test_decode_basic_fields_lc_ats_sso_versions(self) -> None:
        archive_line = decode_archive.ArchiveLine(full_raw_archive_line=archive_line_str_message_lc_ats_sso_versions)
        assert archive_line.get_id() == "M_PAL_01_LC_ATS_SSO_VERSIONS"

        invariant_message = message_manager.get_message_by_id(archive_line.get_id())
        if invariant_message:
            decoded_message = message_decoder.decode_message(message_number=invariant_message.message_number, hexadecimal_content=archive_line.get_new_state_str())
            pass

    def test_decode_string_version_field_in_message(self) -> None:
        archive_line = decode_archive.ArchiveLine(full_raw_archive_line=archive_line_str_message_pae_ats_soft_versions)

        invariant_message = message_manager.get_message_by_id(archive_line.get_id())
        if invariant_message:
            decoded_message = message_decoder.decode_message(message_number=invariant_message.message_number, hexadecimal_content=archive_line.get_new_state_str())
            pass
