from logger import logger_config

from stsloganalyzis import (
    archive_analyzis,
    decode_action_set_content,
    decode_archive,
    decode_message,
    decode_xml_message,
    line_topology,
)

OUTPUT_DIRECTORY = "output"

messages_205 = [
    '{"SQLARCH":{"caller":"","catAla":0,"eqp":"PAS 05","eqpId":"EQ_PAS_05_PAS_05","exeSt":"","id":"M_PAS_05_ZC_ATS_OP_AWS","jdb":false,"label":"PAS_05 : ZC_ATS_OP_AWS [205]","loc":"PAS 05","locale":"2026-03-30T19:08:25.921+02:00","newSt":"00 00 00 00 00 00 00 00 00 00 00 40 42 00 00 00 00 00 01 01 01 01 01 01 00 00 00 00 01 01 01 01 01 01 01 01 01 01 00 00 01 01 01 01 01 00 01 00 01 00 00 01 00 01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 40 00 09 6A 61 00 01 19 40 28 E8 ","oldSt":"","orders":"","sigT":"TSA","tstamp":"2026-03-30T19:08:25.700+02:00","utc_locale":"2026-03-30T17:08:25.921+01:00"},"date":"2026-03-30T19:08:25.921+02:00","tags":["SQLARCH"]}',
]

messages_113 = [
    '{"SQLARCH":{"caller":"","catAla":0,"eqp":"TRAIN 6","eqpId":"EQ_CET_6","exeSt":"","id":"M_CC_6_CC_ATS_SOFT_VERSIONS","jdb":false,"label":"CC_ATS_SOFT_VERSIONS [113]","loc":"INDETERMINE","locale":"2026-03-27T18:34:12.097+01:00","newSt":"14 06 20 50 41 45 5F 5F 4E 45 58 54 5F 50 41 45 5F 43 55 43 50 5F 56 31 30 5F 34 5F 50 33 20 20 20 20 20 20 20 20 20 50 41 45 5F 5F 4E 45 58 54 5F 50 41 45 5F 43 55 43 50 5F 56 31 30 5F 34 5F 50 33 20 20 20 20 20 20 20 20 20 50 41 45 5F 5F 4E 45 58 54 5F 50 41 45 5F 43 55 43 50 5F 56 31 30 5F 34 5F 50 32 20 20 20 20 20 20 20 20 20 00 09 A6 BF 00 00 8C A0 28 E5 ","oldSt":"","orders":"","sigT":"TSA","tstamp":"2026-03-27T18:34:11.100+01:00","utc_locale":"2026-03-27T17:34:12.097+01:00"},"date":"2026-03-27T18:34:12.098+01:00","tags":["SQLARCH"]}',
    '{"SQLARCH":{"caller":"","catAla":0,"eqp":"TRAIN 6","eqpId":"EQ_CET_6","exeSt":"","id":"M_CC_6_CC_ATS_SOFT_VERSIONS","jdb":false,"label":"CC_ATS_SOFT_VERSIONS [113]","loc":"INDETERMINE","locale":"2026-03-27T18:34:12.098+01:00","newSt":"14 06 40 50 41 45 5F 5F 4E 45 58 54 5F 49 4E 56 5F 56 36 5F 31 36 5F 50 32 20 20 20 20 20 20 20 20 20 20 20 20 20 20 50 41 45 5F 5F 4E 45 58 54 5F 49 4E 56 5F 56 36 5F 31 36 5F 50 32 20 20 20 20 20 20 20 20 20 20 20 20 20 20 50 41 45 5F 5F 4E 45 58 54 5F 49 4E 56 5F 56 36 5F 31 36 5F 50 31 20 20 20 20 20 20 20 20 20 20 20 20 20 20 00 09 A6 BF 00 00 8C A0 28 E5 ","oldSt":"","orders":"","sigT":"TSA","tstamp":"2026-03-27T18:34:11.100+01:00","utc_locale":"2026-03-27T17:34:12.098+01:00"},"date":"2026-03-27T18:34:12.098+01:00","tags":["SQLARCH"]}',
    '{"SQLARCH":{"caller":"","catAla":0,"eqp":"TRAIN 6","eqpId":"EQ_CET_6","exeSt":"","id":"M_CC_6_CC_ATS_SOFT_VERSIONS","jdb":false,"label":"CC_ATS_SOFT_VERSIONS [113]","loc":"INDETERMINE","locale":"2026-03-27T18:34:12.098+01:00","newSt":"14 06 00 50 41 45 5F 5F 4E 45 58 54 5F 50 41 45 5F 50 41 52 41 4D 5F 4C 52 5F 56 38 5F 30 37 5F 50 31 20 20 20 20 20 50 41 45 5F 5F 4E 45 58 54 5F 50 41 45 5F 50 41 52 41 4D 5F 4C 52 5F 56 38 5F 30 37 5F 50 31 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 00 09 A6 BF 00 00 8C A0 28 E5 ","oldSt":"","orders":"","sigT":"TSA","tstamp":"2026-03-27T18:34:11.100+01:00","utc_locale":"2026-03-27T17:34:12.098+01:00"},"date":"2026-03-27T18:34:12.099+01:00","tags":["SQLARCH"]}',
    '{"SQLARCH":{"caller":"","catAla":0,"eqp":"TRAIN 9","eqpId":"EQ_CET_9","exeSt":"","id":"M_CC_9_CC_ATS_SOFT_VERSIONS","jdb":false,"label":"CC_ATS_SOFT_VERSIONS [113]","loc":"TB_CDV_z8728_01","locale":"2026-03-27T18:34:12.100+01:00","newSt":"14 09 20 50 41 45 5F 5F 4E 45 58 54 5F 50 41 45 5F 43 55 43 50 5F 56 31 30 5F 34 5F 50 33 20 20 20 20 20 20 20 20 20 50 41 45 5F 5F 4E 45 58 54 5F 50 41 45 5F 43 55 43 50 5F 56 31 30 5F 34 5F 50 33 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 00 09 A6 BF 00 00 8C A0 28 E5 ","oldSt":"","orders":"","sigT":"TSA","tstamp":"2026-03-27T18:34:11.100+01:00","utc_locale":"2026-03-27T17:34:12.100+01:00"},"date":"2026-03-27T18:34:12.101+01:00","tags":["SQLARCH"]}',
    '{"SQLARCH":{"caller":"","catAla":0,"eqp":"TRAIN 9","eqpId":"EQ_CET_9","exeSt":"","id":"M_CC_9_CC_ATS_SOFT_VERSIONS","jdb":false,"label":"CC_ATS_SOFT_VERSIONS [113]","loc":"TB_CDV_z8728_01","locale":"2026-03-27T18:34:12.101+01:00","newSt":"14 09 40 50 41 45 5F 5F 4E 45 58 54 5F 49 4E 56 5F 56 36 5F 31 36 5F 50 32 20 20 20 20 20 20 20 20 20 20 20 20 20 20 50 41 45 5F 5F 4E 45 58 54 5F 49 4E 56 5F 56 36 5F 31 36 5F 50 32 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 00 09 A6 BF 00 00 8C A0 28 E5 ","oldSt":"","orders":"","sigT":"TSA","tstamp":"2026-03-27T18:34:11.100+01:00","utc_locale":"2026-03-27T17:34:12.101+01:00"},"date":"2026-03-27T18:34:12.101+01:00","tags":["SQLARCH"]}',
    '{"SQLARCH":{"caller":"","catAla":0,"eqp":"TRAIN 9","eqpId":"EQ_CET_9","exeSt":"","id":"M_CC_9_CC_ATS_SOFT_VERSIONS","jdb":false,"label":"CC_ATS_SOFT_VERSIONS [113]","loc":"TB_CDV_z8728_01","locale":"2026-03-27T18:34:12.101+01:00","newSt":"14 09 00 50 41 45 5F 5F 4E 45 58 54 5F 50 41 45 5F 50 41 52 41 4D 5F 4C 52 5F 56 38 5F 30 37 5F 50 31 20 20 20 20 20 50 41 45 5F 5F 4E 45 58 54 5F 50 41 45 5F 50 41 52 41 4D 5F 4C 52 5F 56 38 5F 30 37 5F 50 31 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 00 09 A6 BF 00 00 8C A0 28 E5 ","oldSt":"","orders":"","sigT":"TSA","tstamp":"2026-03-27T18:34:11.100+01:00","utc_locale":"2026-03-27T17:34:12.101+01:00"},"date":"2026-03-27T18:34:12.101+01:00","tags":["SQLARCH"]}',
]

messages_101_archives = [
    #'{"SQLARCH":{"caller":"","catAla":0,"eqp":"TRAIN 9","eqpId":"EQ_CET_9","exeSt":"","id":"M_TRAIN_CC_9_ATS_CC_REMOTE_CONTROL_SPE","jdb":false,"label":"TRAIN : ATS_CC_REMOTE_CONTROL_SPE [101]","loc":"TB_CDV_z8514_03","locale":"2026-03-25T18:46:52.896+01:00","newSt":"04 90 85 48 1D 24 00 2C 02 14 80 10 E4 00 C1 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ","oldSt":"","orders":"","sigT":"TCA","tstamp":"","utc_locale":"2026-03-25T17:46:52.896+01:00"},"date":"2026-03-25T18:46:52.896+01:00","tags":["SQLARCH"]}',
    '{"SQLARCH":{"caller":"","catAla":0,"eqp":"TRAIN 9","eqpId":"EQ_CET_9","exeSt":"","id":"M_TRAIN_CC_9_ATS_CC_REMOTE_CONTROL_SPE","jdb":false,"label":"TRAIN : ATS_CC_REMOTE_CONTROL_SPE [101]","loc":"INDETERMINE","locale":"2026-03-26T06:23:49.572+01:00","newSt":"04 FF FF FF FF FF FF FF FF FF FF FF FF FF FF E0 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ","oldSt":"","orders":"","sigT":"TCA","tstamp":"","utc_locale":"2026-03-26T05:23:49.572+01:00"},"date":"2026-03-26T06:23:49.573+01:00","tags":["SQLARCH"]}',
    '{"SQLARCH":{"caller":"","catAla":0,"eqp":"TRAIN 9","eqpId":"EQ_CET_9","exeSt":"","id":"M_TRAIN_CC_9_ATS_CC_REMOTE_CONTROL_SPE","jdb":false,"label":"TRAIN : ATS_CC_REMOTE_CONTROL_SPE [101]","loc":"INDETERMINE","locale":"2026-03-26T06:30:00.165+01:00","newSt":"04 EF FF F7 FF 9C FF D4 BF FF FF FF FF FF FF E0 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ","oldSt":"","orders":"","sigT":"TCA","tstamp":"","utc_locale":"2026-03-26T05:30:00.165+01:00"},"date":"2026-03-26T06:30:00.166+01:00","tags":["SQLARCH"]}',
]

action_sets_messages_archives = [
    '{"SQLARCH":{"caller":"","catAla":0,"eqp":"TRAIN 9","eqpId":"EQ_CET_9","exeSt":"","id":"M_TRAIN_CC_9_ATS_CC_ACTION_SET","jdb":false,"label":"TRAIN : ATS_CC_ACTION_SET [192]","loc":"TB_CDV_z2466_04","locale":"2025-07-21T17:59:44.502+02:00","newSt":"08 08 20 48 60 00 00 00 40 00 00 00 00 00 00 00 01 25 14 51 24 92 C9 24 92 44 44 8B 60 91 11 21 12 12 21 10 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 29 5F EB FC 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ","oldSt":"","orders":"","sigT":"TCA","tstamp":"","utc_locale":"2025-07-21T15:59:44.502+01:00"},"date":"2025-07-21T17:59:44.502+02:00","tags":["SQLARCH"]}',
    '{"SQLARCH":{"caller":"","catAla":0,"eqp":"TRAIN 9","eqpId":"EQ_CET_9","exeSt":"","id":"M_TRAIN_CC_9_ATS_CC_ACTION_SET","jdb":false,"label":"TRAIN : ATS_CC_ACTION_SET [192]","loc":"TB_CDV_z2466_01","locale":"2025-07-21T18:03:10.518+02:00","newSt":"08 10 18 C8 60 00 00 00 40 00 00 00 00 00 00 00 01 25 14 51 24 92 C9 24 92 44 44 8B 60 91 11 21 12 12 21 10 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 29 5F EB FC 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ","oldSt":"","orders":"","sigT":"TCA","tstamp":"","utc_locale":"2025-07-21T16:03:10.518+01:00"},"date":"2025-07-21T18:03:10.518+02:00","tags":["SQLARCH"]}',
    '{"SQLARCH":{"caller":"","catAla":0,"eqp":"TRAIN 9","eqpId":"EQ_CET_9","exeSt":"","id":"M_TRAIN_CC_9_ATS_CC_ACTION_SET","jdb":false,"label":"TRAIN : ATS_CC_ACTION_SET [192]","loc":"TB_CDV_z8321_03","locale":"2025-07-21T13:06:13.489+02:00","newSt":"08 08 30 F8 30 00 00 00 70 00 00 00 00 00 00 00 01 44 A2 C9 24 94 49 24 92 44 44 4B 60 91 11 11 12 12 21 10 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 29 5F EB FC 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ","oldSt":"","orders":"","sigT":"TCA","tstamp":"","utc_locale":"2025-07-21T11:06:13.489+01:00"},"date":"2025-07-21T13:06:13.490+02:00","tags":["SQLARCH"]}',
    '{"SQLARCH":{"caller":"","catAla":0,"eqp":"TRAIN 9","eqpId":"EQ_CET_9","exeSt":"","id":"M_CC_9_CC_ATS_SOFT_VERSIONS","jdb":false,"label":"CC_ATS_SOFT_VERSIONS [113]","loc":"INDETERMINE","locale":"2025-07-09T12:55:53.616+02:00","newSt":"14 09 20 50 41 45 5F 5F 4E 45 58 54 5F 50 41 45 5F 43 55 43 50 5F 56 31 30 5F 30 20 20 20 20 20 20 20 20 20 20 20 20 50 41 45 5F 5F 4E 45 58 54 5F 50 41 45 5F 43 55 43 50 5F 56 31 30 5F 30 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 00 06 01 36 00 01 19 40 27 E0 ","oldSt":"","orders":"","sigT":"TSA","tstamp":"2025-07-09T12:55:52.600+02:00","utc_locale":"2025-07-09T10:55:53.616+01:00"},"date":"2025-07-09T12:55:53.616+02:00","tags":["SQLARCH"]}',
]

messages_205_archives = [
    '{"SQLARCH":{"caller":"","catAla":0,"eqp":"PAS 03","eqpId":"EQ_PAS_03_PAS_03","exeSt":"","id":"M_PAS_03_ZC_ATS_OP_AWS","jdb":false,"label":"PAS_03 : ZC_ATS_OP_AWS [205]","loc":"PAS 03","locale":"2025-08-06T14:38:09.535+02:00","newSt":"00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 01 42 01 42 01 01 01 01 01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 40 00 06 F0 E9 00 01 19 40 27 FC ","oldSt":"","orders":"","sigT":"TSA","tstamp":"2025-08-06T14:38:08.900+02:00","utc_locale":"2025-08-06T12:38:09.535+01:00"},"date":"2025-08-06T14:38:09.535+02:00","tags":["SQLARCH"]}',
    '{"SQLARCH":{"caller":"","catAla":0,"eqp":"PAS 03","eqpId":"EQ_PAS_03_PAS_03","exeSt":"","id":"M_PAS_03_ZC_ATS_OP_AWS","jdb":false,"label":"PAS_03 : ZC_ATS_OP_AWS [205]","loc":"PAS 03","locale":"2025-08-06T14:38:09.572+02:00","newSt":"00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 01 42 01 42 01 01 01 01 01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 40 00 06 F0 E9 00 01 19 40 27 FC ","oldSt":"","orders":"","sigT":"TSA","tstamp":"2025-08-06T14:38:08.900+02:00","utc_locale":"2025-08-06T12:38:09.572+01:00"},"date":"2025-08-06T14:38:09.572+02:00","tags":["SQLARCH"]}',
]


def main() -> None:
    with logger_config.application_logger():

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

        """
          (101, "RestrEnd1Stationning"),
                (101, "RestrEnd2Stationning"),
                (94, "Stopping_Accuracy"),
                """
        message_manager = decode_message.InvariantMessagesManager(messages_list_csv_file_full_path=messages_list_csv_file_full_path)
        action_set_content_decoder = decode_action_set_content.ActionSetContentDecoder(csv_file_file_path=r"D:\NEXT\Data\Csv\ACTION_SET.csv")
        xml_message_decoder = decode_xml_message.XmlMessageDecoder(
            xml_directory_path=xml_directory_path,
            signed_or_unsigned_type_for_integer_fields_manager=[,
        )

        archive_decoder = decode_archive.ArchiveDecoder(
            action_set_content_decoder=action_set_content_decoder,
            message_manager=message_manager,
            xml_message_decoder=xml_message_decoder,
            railway_line=railway_line,
        )

        archive_library = (
            decode_archive.ArchiveLibrary.Builder()
            # .add_archive_files(directory_path=r"C:\Users\fr232487\Downloads\Archives_site_202-03- 27 au 29", filename_pattern="NEXTFileArchiveServer_*.json")
            .add_archive_file(file_full_path=r"C:\Users\fr232487\Downloads\Archives_site_202-03- 27 au 29\CFX00921734_FU.json")
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

        analyzis = archive_analyzis.ArchiveAnalyzis(railway_line=railway_line, archive_library=archive_library, label="CFX")
        analyzis.create_reports_all_sqlarch_changes_since_previous(
            output_directory_path=OUTPUT_DIRECTORY,
            also_print_and_log=False,
        )


if __name__ == "__main__":
    main()
