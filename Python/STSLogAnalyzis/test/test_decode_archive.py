import datetime

import pytest

from typing import cast

from stsloganalyzis import decode_archive, decode_archive, decode_message

archive_line_str_message_zc_ats_tracking_status = '{"SQLARCH":{"caller":"","catAla":0,"eqp":"PAS 05","eqpId":"EQ_PAS_05_PAS_05","exeSt":"","id":"M_PAS_05_ZC_ATS_TRACKING_STATUS_TRAINS_ID","jdb":false,"label":"PAS_05 : ZC ATS TRACKING STATUS TRAINS ID [161]","loc":"PAS 05","locale":"2025-07-21T10:54:18.439+02:00","newSt":"14 09 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 04 E4 44 00 01 19 40 27 EC ","oldSt":"","orders":"","sigT":"TSA","tstamp":"2025-07-21T10:54:18.000+02:00","utc_locale":"2025-07-21T08:54:18.439+01:00"},"date":"2025-07-21T10:54:18.440+02:00","tags":["SQLARCH"]}'
archive_line_str_message_lc_ats_sso_versions = '{"SQLARCH":{"caller":"","catAla":0,"eqp":"PAL","eqpId":"EQ_PAL_01_PAL_01","exeSt":"","id":"M_PAL_01_LC_ATS_SSO_VERSIONS","jdb":false,"label":"PAL_01 : ATS_LC_SSO_VERSIONS [175]","loc":"PAL","locale":"2025-07-09T12:41:00.208+02:00","newSt":"80 00 00 00 04 10 41 84 20 42 84 30 43 84 40 44 84 50 45 84 60 46 84 70 47 84 B8 4C 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 08 00 00 00 00 00 00 ","oldSt":"","orders":"","sigT":"TSA","tstamp":"2000-01-01T01:00:00.800+01:00","utc_locale":"2025-07-09T10:41:00.208+01:00"},"date":"2025-07-09T12:41:00.208+02:00","tags":["SQLARCH"]}'
archive_line_str_message_pae_ats_soft_versions = '{"SQLARCH":{"caller":"","catAla":0,"eqp":"TRAIN 9","eqpId":"EQ_CET_9","exeSt":"","id":"M_CC_9_CC_ATS_SOFT_VERSIONS","jdb":false,"label":"CC_ATS_SOFT_VERSIONS [113]","loc":"INDETERMINE","locale":"2025-07-09T12:55:53.616+02:00","newSt":"14 09 20 50 41 45 5F 5F 4E 45 58 54 5F 50 41 45 5F 43 55 43 50 5F 56 31 30 5F 30 20 20 20 20 20 20 20 20 20 20 20 20 50 41 45 5F 5F 4E 45 58 54 5F 50 41 45 5F 43 55 43 50 5F 56 31 30 5F 30 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 00 06 01 36 00 01 19 40 27 E0 ","oldSt":"","orders":"","sigT":"TSA","tstamp":"2025-07-09T12:55:52.600+02:00","utc_locale":"2025-07-09T10:55:53.616+01:00"},"date":"2025-07-09T12:55:53.616+02:00","tags":["SQLARCH"]}'
archive_line_str_message_ats_pae_action_set = '{"SQLARCH":{"caller":"","catAla":0,"eqp":"TRAIN 9","eqpId":"EQ_CET_9","exeSt":"","id":"M_TRAIN_CC_9_ATS_CC_ACTION_SET","jdb":false,"label":"TRAIN : ATS_CC_ACTION_SET [192]","loc":"TB_CDV_z8321_03","locale":"2025-07-21T13:06:13.489+02:00","newSt":"08 08 30 F8 30 00 00 00 70 00 00 00 00 00 00 00 01 44 A2 C9 24 94 49 24 92 44 44 4B 60 91 11 11 12 12 21 10 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 29 5F EB FC 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ","oldSt":"","orders":"","sigT":"TCA","tstamp":"","utc_locale":"2025-07-21T11:06:13.489+01:00"},"date":"2025-07-21T13:06:13.490+02:00","tags":["SQLARCH"]}'
archive_line_str_message_ats_pae_spe_remote_ctrl = '{"SQLARCH":{"caller":"","catAla":0,"eqp":"TRAIN 9","eqpId":"EQ_CET_9","exeSt":"","id":"M_TRAIN_CC_9_ATS_CC_REMOTE_CONTROL_SPE","jdb":false,"label":"TRAIN : ATS_CC_REMOTE_CONTROL_SPE [101]","loc":"TB_CDV_z2466_01","locale":"2025-07-21T18:03:50.661+02:00","newSt":"04 A0 83 18 EA C7 00 71 82 0C 20 00 00 00 F8 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ","oldSt":"","orders":"","sigT":"TCA","tstamp":"","utc_locale":"2025-07-21T16:03:50.661+01:00"},"date":"2025-07-21T18:03:50.662+02:00","tags":["SQLARCH"]}'
archive_line_str_message_pae_ats_spe_oper = '{"SQLARCH":{"caller":"","catAla":0,"eqp":"TRAIN 9","eqpId":"EQ_CET_9","exeSt":"","id":"M_TRAIN_CC_9_CC_ATS_OPERATION_SPE","jdb":false,"label":"TRAIN : CC_ATS_OPERATION_SPE [36]","loc":"INDETERMINE","locale":"2025-07-21T17:57:14.924+02:00","newSt":"00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 40 40 40 40 40 40 40 40 01 C5 23 FF FF FF FF FF FE 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 10 40 00 00 00 00 02 84 00 00 00 00 00 00 00 00 00 00 00 00 ","oldSt":"","orders":"","sigT":"TSA","tstamp":"2000-01-01T01:00:01.200+01:00","utc_locale":"2025-07-21T15:57:14.924+01:00"},"date":"2025-07-21T17:57:14.924+02:00","tags":["SQLARCH"]}'

message_manager = decode_message.InvariantMessagesManager(messages_list_csv_file_full_path=r"D:\NEXT\Data\Csv\NEXT_message.csv")
message_decoder = decode_message.XmlMessageDecoder(xml_directory_path=r"D:\NEXT\Data\Xml")


class TestDecodeOneArchiveFile:
    def test_process_one_file(self) -> None:
        archive_decoder = decode_archive.ArchiveDecoder(
            messages_list_csv_file_full_path=r"D:\NEXT\Data\Csv\NEXT_message.csv", xml_directory_path=r"D:\NEXT\Data\Xml", action_set_content_csv_file_path=r"D:\NEXT\Data\Csv\ACTION_SET.csv"
        )

        archive_file = decode_archive.ArchiveFile(r"Input\archive_2025_07_22\NEXTFileArchiveServer_365.json")
        archive_file.open_and_read_archive_file_lines()
        archive_file.decode_all_lines(archive_decoder=archive_decoder)
        assert len(archive_file.all_version_lines) == 1
        assert len(archive_file.all_sqlarch_lines) > 100
        pass


class TestDecodeOneLineWithoutXml:
    def test_decode_basic_fields_zc_ats_tracking_status(self) -> None:
        archive_line = decode_archive.SqlArchArchiveLine(full_raw_archive_line=archive_line_str_message_zc_ats_tracking_status)
        assert archive_line.get_date_raw_str() == "2025-07-21T10:54:18.440+02:00"
        assert archive_line.get_id() == "M_PAS_05_ZC_ATS_TRACKING_STATUS_TRAINS_ID"
        assert (
            archive_line.get_new_state_str()
            == "14 09 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 04 E4 44 00 01 19 40 27 EC "
        )


class TestDecodeOneLineWithXml:
    def test_decode_basic_fields_lc_ats_sso_versions(self) -> None:
        archive_line = decode_archive.SqlArchArchiveLine(full_raw_archive_line=archive_line_str_message_lc_ats_sso_versions)
        assert archive_line.get_id() == "M_PAL_01_LC_ATS_SSO_VERSIONS"

        invariant_message = message_manager.get_message_by_id(archive_line.get_id())
        assert invariant_message
        decoded_message = message_decoder.decode_xml_fields_in_message_hexadecimal(message_number=invariant_message.message_number, hexadecimal_content=archive_line.get_new_state_str())
        assert decoded_message
        assert decoded_message.decoded_fields_flat_directory["InitLCStatus"] == 1
        assert decoded_message.decoded_fields_flat_directory["SSOLineVersion"] == 0
        assert decoded_message.decoded_fields_flat_directory["Time"] == 8

    def test_get_archive_line_fields_message_ats_pae_action_set(self) -> None:
        archive_line = decode_archive.SqlArchArchiveLine(full_raw_archive_line=archive_line_str_message_ats_pae_action_set)
        assert archive_line.get_id() == "M_TRAIN_CC_9_ATS_CC_ACTION_SET"

    def test_decode_message_fields_with_xml_ats_pae_action_set(self) -> None:
        archive_line = decode_archive.SqlArchArchiveLine(full_raw_archive_line=archive_line_str_message_ats_pae_action_set)

        invariant_message = message_manager.get_message_by_id(archive_line.get_id())
        assert invariant_message
        decoded_message = message_decoder.decode_xml_fields_in_message_hexadecimal(message_number=invariant_message.message_number, hexadecimal_content=archive_line.get_new_state_str())
        assert decoded_message
        assert decoded_message.decoded_fields_flat_directory["LineId"] == 1
        assert decoded_message.decoded_fields_flat_directory["ActionSetId"] == 1
        assert decoded_message.decoded_fields_flat_directory["AllStationsSkip"] == 0
        assert decoded_message.decoded_fields_flat_directory["RunDirectionRefSegId"] == 391
        assert decoded_message.decoded_fields_flat_directory["RunDirection"] == 1
        assert decoded_message.decoded_fields_flat_directory["PartStopDestination"] == 1
        assert decoded_message.decoded_fields_flat_directory["FinalStopPlatform"] == 3
        assert decoded_message.decoded_fields_flat_directory["FinalStopStaIdPis"] == 7
        assert decoded_message.decoded_fields_flat_directory["ExchZoneTypeTdI"] == "0000000000000000000000000000000000000000000000000000000000000000"
        assert (
            decoded_message.decoded_fields_flat_directory["Actions"]
            == "010100010010100010110010010010010010010100010010010010010010010010010001000100010001001011011000001001000100010001000100010001001000010010001000010001000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000010100101011111111010111111110000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
        )

    def test_decode_string_version_field_in_message(self) -> None:
        archive_line = decode_archive.SqlArchArchiveLine(full_raw_archive_line=archive_line_str_message_pae_ats_soft_versions)

        invariant_message = message_manager.get_message_by_id(archive_line.get_id())
        assert invariant_message
        decoded_message = message_decoder.decode_xml_fields_in_message_hexadecimal(message_number=invariant_message.message_number, hexadecimal_content=archive_line.get_new_state_str())
        assert decoded_message
        assert cast(str, decoded_message.decoded_fields_flat_directory["SoftVersionPart1"]).startswith("PAE__NEXT_PAE_CUCP_V10_0")
        assert cast(str, decoded_message.decoded_fields_flat_directory["SoftVersionPart1"]) == "PAE__NEXT_PAE_CUCP_V10_0"
        assert cast(str, decoded_message.decoded_fields_flat_directory["SoftVersionPart1_0"]) == "P"
        assert cast(str, decoded_message.decoded_fields_flat_directory["SoftVersionPart1_1"]) == "A"
        assert cast(str, decoded_message.decoded_fields_flat_directory["SoftVersionPart1_2"]) == "E"

    def test_incomplete_hexadecimal_message(self) -> None:
        archive_line = decode_archive.SqlArchArchiveLine(full_raw_archive_line=archive_line_str_message_pae_ats_spe_oper)

        invariant_message = message_manager.get_message_by_id(archive_line.get_id())
        assert invariant_message
        decoded_message = message_decoder.decode_xml_fields_in_message_hexadecimal(message_number=invariant_message.message_number, hexadecimal_content=archive_line.get_new_state_str())
        assert decoded_message
        assert decoded_message.decoded_fields_flat_directory["CriticalSectStop"] == 0
        assert decoded_message.decoded_fields_flat_directory["UnexpectedTransponderId"] == 0
        assert "Time" in decoded_message.not_decoded_because_error_fields_names
        assert "Time" not in decoded_message.decoded_fields_flat_directory

    def test_decode_when_selector_rc_type(self) -> None:
        archive_line = decode_archive.SqlArchArchiveLine(full_raw_archive_line=archive_line_str_message_ats_pae_spe_remote_ctrl)
        invariant_message = message_manager.get_message_by_id(archive_line.get_id())
        assert invariant_message
        decoded_message = message_decoder.decode_xml_fields_in_message_hexadecimal(message_number=invariant_message.message_number, hexadecimal_content=archive_line.get_new_state_str())
        assert decoded_message
        assert "TrainNumber" not in decoded_message.decoded_fields_flat_directory
        assert cast(str, decoded_message.decoded_fields_flat_directory["RestrEnd1SegId"]) == 8390
        assert cast(str, decoded_message.decoded_fields_flat_directory["RestrEnd1SegId"]) == 8390
        assert cast(str, decoded_message.decoded_fields_flat_directory["RestrEnd1Offset"]) == 60103
        assert cast(str, decoded_message.decoded_fields_flat_directory["RestrEnd1Stationning"]) == 454
        assert cast(str, decoded_message.decoded_fields_flat_directory["DownRestrReason"]) == 0
