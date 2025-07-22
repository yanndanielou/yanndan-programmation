import decode_archive
import decode_message
import decode_action_set_content

action_sets_messages_archives = [
    '{"SQLARCH":{"caller":"","catAla":0,"eqp":"TRAIN 9","eqpId":"EQ_CET_9","exeSt":"","id":"M_TRAIN_CC_9_ATS_CC_ACTION_SET","jdb":false,"label":"TRAIN : ATS_CC_ACTION_SET [192]","loc":"TB_CDV_z2466_04","locale":"2025-07-21T17:59:44.502+02:00","newSt":"08 08 20 48 60 00 00 00 40 00 00 00 00 00 00 00 01 25 14 51 24 92 C9 24 92 44 44 8B 60 91 11 21 12 12 21 10 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 29 5F EB FC 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ","oldSt":"","orders":"","sigT":"TCA","tstamp":"","utc_locale":"2025-07-21T15:59:44.502+01:00"},"date":"2025-07-21T17:59:44.502+02:00","tags":["SQLARCH"]}',
    '{"SQLARCH":{"caller":"","catAla":0,"eqp":"TRAIN 9","eqpId":"EQ_CET_9","exeSt":"","id":"M_TRAIN_CC_9_ATS_CC_ACTION_SET","jdb":false,"label":"TRAIN : ATS_CC_ACTION_SET [192]","loc":"TB_CDV_z2466_01","locale":"2025-07-21T18:03:10.518+02:00","newSt":"08 10 18 C8 60 00 00 00 40 00 00 00 00 00 00 00 01 25 14 51 24 92 C9 24 92 44 44 8B 60 91 11 21 12 12 21 10 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 29 5F EB FC 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ","oldSt":"","orders":"","sigT":"TCA","tstamp":"","utc_locale":"2025-07-21T16:03:10.518+01:00"},"date":"2025-07-21T18:03:10.518+02:00","tags":["SQLARCH"]}',
    '{"SQLARCH":{"caller":"","catAla":0,"eqp":"TRAIN 9","eqpId":"EQ_CET_9","exeSt":"","id":"M_TRAIN_CC_9_ATS_CC_ACTION_SET","jdb":false,"label":"TRAIN : ATS_CC_ACTION_SET [192]","loc":"TB_CDV_z8321_03","locale":"2025-07-21T13:06:13.489+02:00","newSt":"08 08 30 F8 30 00 00 00 70 00 00 00 00 00 00 00 01 44 A2 C9 24 94 49 24 92 44 44 4B 60 91 11 11 12 12 21 10 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 29 5F EB FC 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ","oldSt":"","orders":"","sigT":"TCA","tstamp":"","utc_locale":"2025-07-21T11:06:13.489+01:00"},"date":"2025-07-21T13:06:13.490+02:00","tags":["SQLARCH"]}',
    '{"SQLARCH":{"caller":"","catAla":0,"eqp":"TRAIN 9","eqpId":"EQ_CET_9","exeSt":"","id":"M_CC_9_CC_ATS_SOFT_VERSIONS","jdb":false,"label":"CC_ATS_SOFT_VERSIONS [113]","loc":"INDETERMINE","locale":"2025-07-09T12:55:53.616+02:00","newSt":"14 09 20 50 41 45 5F 5F 4E 45 58 54 5F 50 41 45 5F 43 55 43 50 5F 56 31 30 5F 30 20 20 20 20 20 20 20 20 20 20 20 20 50 41 45 5F 5F 4E 45 58 54 5F 50 41 45 5F 43 55 43 50 5F 56 31 30 5F 30 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 00 06 01 36 00 01 19 40 27 E0 ","oldSt":"","orders":"","sigT":"TSA","tstamp":"2025-07-09T12:55:52.600+02:00","utc_locale":"2025-07-09T10:55:53.616+01:00"},"date":"2025-07-09T12:55:53.616+02:00","tags":["SQLARCH"]}',
]

message_manager = decode_message.InvariantMessagesManager(messages_csv_file_full_path=r"D:\NEXT\Data\Csv\NEXT_message.csv")
message_decoder = decode_message.MessageDecoder(xml_directory_path=r"D:\NEXT\Data\Xml")

for action_set_message_archive in action_sets_messages_archives:
    archive_line = decode_archive.ArchiveLine(action_set_message_archive)
    archive_line_object_id = archive_line.get_id()

    invariant_message = message_manager.get_message_by_id(archive_line_object_id)
    if invariant_message:

        decoded_message = message_decoder.decode_message(message_number=invariant_message.message_number, hexadecimal_content=archive_line.get_new_state_str())
        print(decoded_message is not None)
        if decoded_message:
            print(decoded_message.decoded_fields)
