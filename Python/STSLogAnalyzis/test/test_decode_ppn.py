import pytest

from stsloganalyzis.ppn import ppn_profibus_log
from stsloganalyzis.unisig import decode_unisig, upper_layer_libraries


@pytest.fixture(scope="session", name="next_unisig_58_library_fixture")
def next_unisig_58_library() -> upper_layer_libraries.UpperLayerDecodingLibrary:
    ret = upper_layer_libraries.UpperLayerDecodingLibrary.from_next_json_file_full_path(json_file_full_path=r"D:\temp\GenTel\0.1-0-Original_Edition\GenTel\rom\unisig_s58.json")
    assert isinstance(ret, upper_layer_libraries.UpperLayerDecodingLibrary)
    return ret


class TestDecodeOnePpnLogLine:

    class TestSda:

        class TestConnectConfirmTelegram:
            def test_decode_one_sl0(self) -> None:

                ppn_log_line = ppn_profibus_log.ProfibusLogLine.decode_raw_log_line(
                    line="2026-03-29 22:46:05:305 kppn 1.3.3: [99:4 <= 5:4] Received PROFIBUS message [num:1459][mode:SDA][len:23] a0 c2 a0 0a d5 e7 88 13 03 00 00 01 03 00 00 e8 03 00 00 00 00 00 00",
                    upper_layer_decoding_library=None,
                )
                assert ppn_log_line
                ppn_log_line.decode_sdn_or_sda()
                unisig_message = ppn_log_line.unisig_message
                assert unisig_message
                assert isinstance(unisig_message, decode_unisig.SdaConnectRequestOrConfirmTelegram)
                assert not unisig_message.creational_and_decoding_errors
                assert unisig_message.byte_message_decoded.is_correctly_and_completely_decoded
                assert unisig_message.crc is None

            def test_decode_one_sl4(self) -> None:

                ppn_log_line = ppn_profibus_log.ProfibusLogLine.decode_raw_log_line(
                    line="2026-03-29 22:46:05:609 kppn 1.3.3: [99:37 <= 2:37] Received PROFIBUS message [num:1469][mode:SDA][len:29] 93 82 93 3c 80 d0 b8 0b 03 00 00 01 03 00 00 e8 03 00 00 05 00 00 00 e3 cd 44 5a 18 49",
                    upper_layer_decoding_library=None,
                )
                assert ppn_log_line
                ppn_log_line.decode_sdn_or_sda()
                unisig_message = ppn_log_line.unisig_message
                assert unisig_message
                assert isinstance(unisig_message, decode_unisig.SdaConnectRequestOrConfirmTelegram)
                assert unisig_message.byte_message_decoded.is_correctly_and_completely_decoded
                assert not unisig_message.creational_and_decoding_errors
                # assert unisig_message.stl_time_stamp_ms is not None
                assert unisig_message.crc is not None

        class TestConnectRequestTelegram:
            def test_decode_one_sl0(self) -> None:

                ppn_log_line = ppn_profibus_log.ProfibusLogLine.decode_raw_log_line(
                    line="2026-03-29 22:46:05:192 kppn 1.3.3: [99:4 => 5:4] Sending PROFIBUS message  [num:5][rt:2063][mode:SDA][len:23] 91 c0 91 84 76 00 88 13 03 00 00 00 03 00 00 aa 00 00 00 00 00 00 00",
                    upper_layer_decoding_library=None,
                )
                assert ppn_log_line
                ppn_log_line.decode_sdn_or_sda()
                unisig_message = ppn_log_line.unisig_message
                assert unisig_message
                assert isinstance(unisig_message, decode_unisig.SdaConnectRequestOrConfirmTelegram)
                assert not unisig_message.creational_and_decoding_errors
                assert unisig_message.byte_message_decoded.is_correctly_and_completely_decoded
                assert unisig_message.crc is None

            def test_decode_one_sl4(self) -> None:

                ppn_log_line = ppn_profibus_log.ProfibusLogLine.decode_raw_log_line(
                    line="2026-03-29 22:46:16:615 kppn 1.3.3: [99:33 => 2:33] Sending PROFIBUS message  [num:1][rt:1970][mode:SDA][len:29] 6e 80 6e d5 2e 7b a0 0f 03 00 00 00 03 00 00 dc 05 00 00 ee 00 00 00 1a 08 67 0c 13 23",
                    upper_layer_decoding_library=None,
                )
                assert ppn_log_line
                ppn_log_line.decode_sdn_or_sda()
                unisig_message = ppn_log_line.unisig_message
                assert unisig_message
                assert isinstance(unisig_message, decode_unisig.SdaConnectRequestOrConfirmTelegram)
                assert unisig_message.byte_message_decoded.is_correctly_and_completely_decoded
                assert not unisig_message.creational_and_decoding_errors
                # assert unisig_message.stl_time_stamp_ms is not None
                assert unisig_message.crc is not None

        class TestReadyToRunTelegram:
            def test_decode_one_sl0(self) -> None:

                ppn_log_line = ppn_profibus_log.ProfibusLogLine.decode_raw_log_line(
                    line="2026-03-30 00:42:05:615 kppn 1.3.3: [99:4 <= 5:4] Received PROFIBUS message [num:1453][mode:SDA][len:6] ec e2 78 02 58 00",
                    upper_layer_decoding_library=None,
                )
                assert ppn_log_line
                ppn_log_line.decode_sdn_or_sda()
                unisig_message = ppn_log_line.unisig_message
                assert unisig_message
                assert isinstance(unisig_message, decode_unisig.OnboardSdaUnisigMessage)
                assert not unisig_message.creational_and_decoding_errors
                assert unisig_message.stl_time_stamp is not None
                assert unisig_message.byte_message_decoded.is_correctly_and_completely_decoded

            def test_decode_one_sl4(self) -> None:

                ppn_log_line = ppn_profibus_log.ProfibusLogLine.decode_raw_log_line(
                    line="2026-03-29 22:46:17:905 kppn 1.3.3: [99:33 <= 2:33] Received PROFIBUS message [num:1437][mode:SDA][len:12] dd a2 54 bf 07 00 0e df e7 12 ca 37",
                    upper_layer_decoding_library=None,
                )
                assert ppn_log_line
                ppn_log_line.decode_sdn_or_sda()
                unisig_message = ppn_log_line.unisig_message
                assert unisig_message
                assert isinstance(unisig_message, decode_unisig.OnboardSdaUnisigMessage)
                assert not unisig_message.creational_and_decoding_errors
                assert unisig_message.stl_time_stamp is not None
                assert unisig_message.byte_message_decoded.is_correctly_and_completely_decoded

        class TestRunTelegram:
            def test_decode_one_sl0(self) -> None:

                ppn_log_line = ppn_profibus_log.ProfibusLogLine.decode_raw_log_line(
                    line="2026-03-29 22:46:05:289 kppn 1.3.3: [99:2 => 3:2] Sending PROFIBUS message  [num:9][rt:1223][mode:SDA][len:6] 27 e3 b3 c5 07 00",
                    upper_layer_decoding_library=None,
                )
                assert ppn_log_line
                ppn_log_line.decode_sdn_or_sda()
                unisig_message = ppn_log_line.unisig_message
                assert unisig_message
                assert isinstance(unisig_message, decode_unisig.OnboardSdaUnisigMessage)
                assert not unisig_message.creational_and_decoding_errors
                assert unisig_message.stl_time_stamp is not None
                assert unisig_message.byte_message_decoded.is_correctly_and_completely_decoded

            def test_decode_one_sl4(self) -> None:

                ppn_log_line = ppn_profibus_log.ProfibusLogLine.decode_raw_log_line(
                    line="2026-03-29 22:46:06:608 kppn 1.3.3: [99:37 => 2:37] Sending PROFIBUS message  [num:23][rt:1187][mode:SDA][len:12] d9 a3 7d c9 07 00 9a fb ee d4 35 4f",
                    upper_layer_decoding_library=None,
                )
                assert ppn_log_line
                ppn_log_line.decode_sdn_or_sda()
                unisig_message = ppn_log_line.unisig_message
                assert unisig_message
                assert isinstance(unisig_message, decode_unisig.OnboardSdaUnisigMessage)
                assert not unisig_message.creational_and_decoding_errors
                assert unisig_message.stl_time_stamp is not None
                assert unisig_message.byte_message_decoded.is_correctly_and_completely_decoded

        class TestIdleTelegram:
            def test_decode_one_sl0(self) -> None:
                ppn_log_line = ppn_profibus_log.ProfibusLogLine.decode_raw_log_line(
                    line="2026-03-29 22:17:05:682 kppn 1.3.3: [99:2 <= 3:2] Received PROFIBUS message [num:169521][mode:SDA][len:2] db c6",
                    upper_layer_decoding_library=None,
                )
                assert ppn_log_line
                ppn_log_line.decode_sdn_or_sda()
                unisig_message = ppn_log_line.unisig_message
                assert unisig_message
                assert isinstance(unisig_message, decode_unisig.OnboardSdaUnisigMessage)
                assert not unisig_message.creational_and_decoding_errors
                assert unisig_message.byte_message_decoded.is_correctly_and_completely_decoded

            def test_decode_one_sl4(self) -> None:
                ppn_log_line = ppn_profibus_log.ProfibusLogLine.decode_raw_log_line(
                    line="2026-03-29 22:17:05:687 kppn 1.3.3: [99:33 <= 2:33] Received PROFIBUS message [num:169524][mode:SDA][len:8] b4 86 cc ff 38 ff ce be",
                    upper_layer_decoding_library=None,
                )
                assert ppn_log_line
                ppn_log_line.decode_sdn_or_sda()
                unisig_message = ppn_log_line.unisig_message
                assert unisig_message
                assert isinstance(unisig_message, decode_unisig.OnboardSdaUnisigMessage)
                assert not unisig_message.creational_and_decoding_errors
                assert unisig_message.byte_message_decoded.is_correctly_and_completely_decoded

        class TestAuthenticationTelegram:
            def test_decode_one_sl4(self) -> None:
                ppn_log_line = ppn_profibus_log.ProfibusLogLine.decode_raw_log_line(
                    line="2026-03-29 22:46:17:410 kppn 1.3.3: [99:33 => 2:33] Sending PROFIBUS message  [num:2][rt:1791][mode:SDA][len:12] 6f 83 dc b9 a8 50 8d 00 a7 42 59 80",
                    upper_layer_decoding_library=None,
                )
                assert ppn_log_line
                ppn_log_line.decode_sdn_or_sda()
                unisig_message = ppn_log_line.unisig_message
                assert unisig_message
                assert isinstance(unisig_message, decode_unisig.SdaAuthenticationOrAuthenticationAcknowledgementTelegram)
                assert not unisig_message.creational_and_decoding_errors
                assert unisig_message.byte_message_decoded.is_correctly_and_completely_decoded

        class TestDisconnect:
            def test_decode_one_disconnect_sl0(self, next_unisig_58_library_fixture: upper_layer_libraries.UpperLayerDecodingLibrary) -> None:

                ppn_log_line = ppn_profibus_log.ProfibusLogLine.decode_raw_log_line(
                    line="2026-05-28 12:37:05:492 kppn 1.3.3: [99:44 => 5:44] Sending PROFIBUS message [num:4138][rt:2363][mode:SDA][len:23] 76 c5 01 05 69 64 6c 65 20 63 79 63 6c 65 20 74 69 6d 65 2d 6f 75 74",
                    upper_layer_decoding_library=next_unisig_58_library_fixture,
                )
                assert ppn_log_line
                ppn_log_line.decode_sdn_or_sda()
                unisig_message = ppn_log_line.unisig_message
                assert unisig_message
                assert isinstance(unisig_message, decode_unisig.SdaDisconnectTelegram)
                assert not unisig_message.creational_and_decoding_errors
                assert unisig_message.byte_message_decoded.is_correctly_and_completely_decoded
                print(unisig_message.disconnect_reason_text)

            def test_decode_one_disconnect_sl4(self, next_unisig_58_library_fixture: upper_layer_libraries.UpperLayerDecodingLibrary) -> None:
                ppn_log_line = ppn_profibus_log.ProfibusLogLine.decode_raw_log_line(
                    line="2026-05-28 12:37:06:666 kppn 1.3.3: [99:33 => 2:33] Sending PROFIBUS message [num:4143][rt:2397][mode:SDA][len:50] 7f 85 01 05 69 64 6c 65 20 63 79 63 6c 65 20 74 69 6d 65 2d 6f 75 74 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 d9 5c c9 44 a2 45",
                    upper_layer_decoding_library=next_unisig_58_library_fixture,
                )
                assert ppn_log_line
                ppn_log_line.decode_sdn_or_sda()
                unisig_message = ppn_log_line.unisig_message
                assert unisig_message
                assert isinstance(unisig_message, decode_unisig.SdaDisconnectTelegram)
                assert not unisig_message.creational_and_decoding_errors
                assert unisig_message.byte_message_decoded.is_correctly_and_completely_decoded
                print(unisig_message.disconnect_reason_text)

        class TestStmMessagesInUpperLayer:

            class TestNIter:

                def test_decode_line_stm_183(self, next_unisig_58_library_fixture: upper_layer_libraries.UpperLayerDecodingLibrary) -> None:
                    ppn_log_line = ppn_profibus_log.ProfibusLogLine.decode_raw_log_line(
                        line="2026-03-28 20:01:07:329 kppn 1.3.3: [99:33 => 2:33] Sending PROFIBUS message  [num:5790][rt:2455][mode:SDA][len:146] 63 89 1d 86 b7 20 38 80 cb 22 61 d4 b1 e1 d4 b6 17 10 2d 98 9a 96 98 9a 18 10 35 b6 97 b4 2e a4 c0 b0 e0 d4 81 b4 bd cc c8 1c b5 66 97 46 57 37 36 52 06 d6 17 84 18 9a 18 10 35 b6 97 b4 04 18 ac ca e4 e6 d2 de dc 40 c4 de e4 c9 15 04 14 55 f4 35 54 35 05 f5 63 13 05 f3 45 f5 03 20 94 d5 99 5c 9c da 5b db 88 1c 18 5c 98 5b 4b 88 18 9b dc 99 24 a0 82 8a be a0 82 a4 82 9a be 98 a4 be ac 70 be 60 6e 1e 01 94 64 1d 2a 00 5e d0 4d 95 17 ea",
                        upper_layer_decoding_library=next_unisig_58_library_fixture,
                    )
                    assert ppn_log_line
                    ppn_log_line.decode_sdn_or_sda()
                    assert ppn_log_line.unisig_message
                    assert not ppn_log_line.unisig_message.creational_and_decoding_errors
                    assert isinstance(ppn_log_line.unisig_message, decode_unisig.SdaForUpperLayerTelegram)
                    assert ppn_log_line.unisig_message.upper_layer_decoded_stms
                    assert len(ppn_log_line.unisig_message.upper_layer_decoded_stms) == 2
                    stm_message_183 = ppn_log_line.unisig_message.upper_layer_decoded_stms[0]
                    assert stm_message_183.nid_stm == 183
                    for upper_layer_decoded_stm in ppn_log_line.unisig_message.upper_layer_decoded_stms:
                        assert not upper_layer_decoded_stm.creational_and_decoding_errors

                def test_decode_line_stm_34(self, next_unisig_58_library_fixture: upper_layer_libraries.UpperLayerDecodingLibrary) -> None:
                    ppn_log_line = ppn_profibus_log.ProfibusLogLine.decode_raw_log_line(
                        line="2026-03-28 06:29:08:022 kppn 1.3.3: [99:4 <= 5:4] Received PROFIBUS message [num:228122][mode:SDA][len:17] 96 c9 1d 0b 22 02 18 41 c0 34 96 65 9f d2 b2 a4 01",
                        upper_layer_decoding_library=next_unisig_58_library_fixture,
                    )
                    assert ppn_log_line
                    ppn_log_line.decode_sdn_or_sda()
                    assert ppn_log_line.unisig_message
                    assert not ppn_log_line.unisig_message.creational_and_decoding_errors
                    assert isinstance(ppn_log_line.unisig_message, decode_unisig.SdaForUpperLayerTelegram)
                    assert ppn_log_line.unisig_message.upper_layer_decoded_stms
                    assert len(ppn_log_line.unisig_message.upper_layer_decoded_stms) == 1
                    stm_message_34 = ppn_log_line.unisig_message.upper_layer_decoded_stms[0]
                    assert stm_message_34.nid_stm == 34
                    for upper_layer_decoded_stm in ppn_log_line.unisig_message.upper_layer_decoded_stms:
                        assert not upper_layer_decoded_stm.creational_and_decoding_errors

                def test_decode_line_stm_35_to_handle_l_caption_inside_n_iter(self, next_unisig_58_library_fixture: upper_layer_libraries.UpperLayerDecodingLibrary) -> None:
                    ppn_log_line = ppn_profibus_log.ProfibusLogLine.decode_raw_log_line(
                        line="2026-03-29 01:21:10:704 kppn 1.3.3: [99:4 => 5:4] Sending PROFIBUS message  [num:589][rt:1292][mode:SDA][len:28] 6a c9 1d 16 23 04 20 84 16 2f 00 02 62 22 c1 88 00 33 53 43 70 f0 0c b8 a9 23 4f 01",
                        upper_layer_decoding_library=next_unisig_58_library_fixture,
                    )
                    assert ppn_log_line
                    ppn_log_line.decode_sdn_or_sda()
                    assert ppn_log_line.unisig_message
                    assert not ppn_log_line.unisig_message.creational_and_decoding_errors
                    assert isinstance(ppn_log_line.unisig_message, decode_unisig.SdaForUpperLayerTelegram)
                    assert ppn_log_line.unisig_message.upper_layer_decoded_stms
                    assert len(ppn_log_line.unisig_message.upper_layer_decoded_stms) == 2
                    stm_message_35 = ppn_log_line.unisig_message.upper_layer_decoded_stms[0]
                    assert stm_message_35.nid_stm == 35
                    assert len(stm_message_35.fields_names_and_values) == 13
                    stm_message_15 = ppn_log_line.unisig_message.upper_layer_decoded_stms[1]
                    assert stm_message_15.nid_stm == 15
                    for upper_layer_decoded_stm in ppn_log_line.unisig_message.upper_layer_decoded_stms:
                        assert not upper_layer_decoded_stm.creational_and_decoding_errors

            class TestTextWithLength:

                def test_decode_line_stms_38_to_handle_l_text(self, next_unisig_58_library_fixture: upper_layer_libraries.UpperLayerDecodingLibrary) -> None:
                    ppn_log_line = ppn_profibus_log.ProfibusLogLine.decode_raw_log_line(
                        line="2026-03-28 07:28:11:532 kppn 1.3.3: [99:44 => 5:44] Sending PROFIBUS message  [num:296866][rt:3095][mode:SDA][len:64] 24 c9 1d 3a 26 0d 05 c8 02 2e 4e 45 78 54 20 3a 20 4d 61 69 6e 74 65 6e 69 72 20 6c 27 69 6d 6d 6f 62 69 6c 69 73 61 74 69 6f 6e 20 65 74 20 70 61 74 69 65 6e 74 65 72 0f 00 ca 00 91 c4 da 01",
                        upper_layer_decoding_library=next_unisig_58_library_fixture,
                    )
                    assert ppn_log_line
                    ppn_log_line.decode_sdn_or_sda()
                    assert ppn_log_line.unisig_message
                    assert not ppn_log_line.unisig_message.creational_and_decoding_errors
                    assert isinstance(ppn_log_line.unisig_message, decode_unisig.SdaForUpperLayerTelegram)
                    assert ppn_log_line.unisig_message.upper_layer_decoded_stms
                    assert len(ppn_log_line.unisig_message.upper_layer_decoded_stms) == 2
                    stm_message_38 = ppn_log_line.unisig_message.upper_layer_decoded_stms[0]
                    assert stm_message_38.nid_stm == 38
                    stm_message_15 = ppn_log_line.unisig_message.upper_layer_decoded_stms[1]
                    assert stm_message_15.nid_stm == 15
                    for upper_layer_decoded_stm in ppn_log_line.unisig_message.upper_layer_decoded_stms:
                        assert not upper_layer_decoded_stm.creational_and_decoding_errors

            class TestStm161ForJru:

                def test_decode_161_fields_are_correct(self, next_unisig_58_library_fixture: upper_layer_libraries.UpperLayerDecodingLibrary) -> None:
                    ppn_log_line = ppn_profibus_log.ProfibusLogLine.decode_raw_log_line(
                        line="2026-03-28 18:17:17:722 kppn 1.3.3: [99:2 => 3:2] Sending PROFIBUS message  [num:25130][rt:1763][mode:SDA][len:102] 7a c9 1d 5e a1 16 28 21 20 dd da 88 70 51 34 7c 92 45 01 08 61 83 00 7d 40 00 00 02 00 a0 00 00 00 00 00 06 c7 06 26 06 a6 26 e9 80 00 00 00 00 68 0e 8e d4 21 45 04 24 1b bb 21 14 30 40 00 00 00 11 53 d3 11 40 02 3e e0 18 f0 1a 88 17 92 02 18 2f 51 55 b0 00 00 f8 00 09 21 80 00 78 06 50 9a 12 bb 1b 24 04",
                        upper_layer_decoding_library=next_unisig_58_library_fixture,
                    )
                    assert ppn_log_line
                    ppn_log_line.decode_sdn_or_sda()
                    assert ppn_log_line.unisig_message
                    assert isinstance(ppn_log_line.unisig_message, decode_unisig.SdaForUpperLayerTelegram)
                    assert ppn_log_line.unisig_message.upper_layer_decoded_stms
                    assert len(ppn_log_line.unisig_message.upper_layer_decoded_stms) == 2
                    stm_161 = ppn_log_line.unisig_message.upper_layer_decoded_stms[0]
                    assert stm_161.fields_names_and_values
                    assert stm_161.fields_names_and_values["SECONDS"] == 10
                    assert stm_161.fields_names_and_values["Variant NID_EVENT name"] == "Nexteo-12"
                    assert stm_161.fields_names_and_values["STM-161 Nexteo specific datas entry point Nexteo-12 Message radio applicatif BIM_TARGET"] == 9264
                    assert stm_161.fields_names_and_values["STM-161 Nexteo specific datas entry point NID_LIGNE"] == "EOLE"
                    assert stm_161.fields_names_and_values["T_JD human format"] == "19:17:55.259"

                def test_decode_161_no_error(self, next_unisig_58_library_fixture: upper_layer_libraries.UpperLayerDecodingLibrary) -> None:
                    ppn_log_line = ppn_profibus_log.ProfibusLogLine.decode_raw_log_line(
                        line="2026-03-28 18:17:17:722 kppn 1.3.3: [99:2 => 3:2] Sending PROFIBUS message  [num:25130][rt:1763][mode:SDA][len:102] 7a c9 1d 5e a1 16 28 21 20 dd da 88 70 51 34 7c 92 45 01 08 61 83 00 7d 40 00 00 02 00 a0 00 00 00 00 00 06 c7 06 26 06 a6 26 e9 80 00 00 00 00 68 0e 8e d4 21 45 04 24 1b bb 21 14 30 40 00 00 00 11 53 d3 11 40 02 3e e0 18 f0 1a 88 17 92 02 18 2f 51 55 b0 00 00 f8 00 09 21 80 00 78 06 50 9a 12 bb 1b 24 04",
                        upper_layer_decoding_library=next_unisig_58_library_fixture,
                    )
                    assert ppn_log_line
                    ppn_log_line.decode_sdn_or_sda()
                    assert ppn_log_line.unisig_message
                    assert not ppn_log_line.unisig_message.creational_and_decoding_errors
                    assert isinstance(ppn_log_line.unisig_message, decode_unisig.SdaForUpperLayerTelegram)
                    assert ppn_log_line.unisig_message.upper_layer_decoded_stms
                    assert len(ppn_log_line.unisig_message.upper_layer_decoded_stms) == 2
                    for upper_layer_decoded_stm in ppn_log_line.unisig_message.upper_layer_decoded_stms:
                        assert not upper_layer_decoded_stm.creational_and_decoding_errors

            class TestBasicStmMessages:

                @pytest.mark.parametrize(
                    "raw_ppn_log_line",
                    [
                        "2026-03-29 22:17:12:004 kppn 1.3.3: [99:44 => 5:44] Sending PROFIBUS message  [num:69066][rt:2469][mode:SDA][len:12] 54 c9 1d 06 0f 00 ca 00 17 86 b3 00",
                    ],
                )
                def test_decode_line_with_stm15_sl0(
                    self,
                    raw_ppn_log_line: str,
                    next_unisig_58_library_fixture: upper_layer_libraries.UpperLayerDecodingLibrary,
                ) -> None:
                    ppn_log_line = ppn_profibus_log.ProfibusLogLine.decode_raw_log_line(raw_ppn_log_line, upper_layer_decoding_library=next_unisig_58_library_fixture)
                    assert ppn_log_line
                    ppn_log_line.decode_sdn_or_sda()
                    assert ppn_log_line.unisig_message
                    assert not ppn_log_line.unisig_message.creational_and_decoding_errors
                    assert isinstance(ppn_log_line.unisig_message, decode_unisig.SdaForUpperLayerTelegram)
                    assert ppn_log_line.unisig_message.upper_layer_decoded_stms
                    assert len(ppn_log_line.unisig_message.upper_layer_decoded_stms) == 1
                    for upper_layer_decoded_stm in ppn_log_line.unisig_message.upper_layer_decoded_stms:
                        assert not upper_layer_decoded_stm.creational_and_decoding_errors

                @pytest.mark.parametrize(
                    "raw_ppn_log_line",
                    [
                        "2026-05-22 15:17:08:758 kppn 1.3.3: [99:33 => 2:33] Sending PROFIBUS message [num:197704][rt:3903][mode:SDA][len:18] e0 89 1d 06 0f 00 ca 00 95 d1 b2 04 c0 fd 4f 34 44 a1",
                        "2026-05-22 15:26:13:149 kppn 1.3.3: [99:37 => 2:37] Sending PROFIBUS message [num:199067][rt:1679][mode:SDA][len:18] f4 89 1d 06 0f 00 ca 00 23 20 bb 04 75 e8 c4 a2 d6 ad",
                    ],
                )
                def test_decode_line_with_stm15_sl4(
                    self,
                    raw_ppn_log_line: str,
                    next_unisig_58_library_fixture: upper_layer_libraries.UpperLayerDecodingLibrary,
                ) -> None:
                    ppn_log_line = ppn_profibus_log.ProfibusLogLine.decode_raw_log_line(raw_ppn_log_line, upper_layer_decoding_library=next_unisig_58_library_fixture)
                    assert ppn_log_line
                    ppn_log_line.decode_sdn_or_sda()
                    assert ppn_log_line.unisig_message
                    assert not ppn_log_line.unisig_message.creational_and_decoding_errors
                    assert isinstance(ppn_log_line.unisig_message, decode_unisig.SdaForUpperLayerTelegram)
                    assert ppn_log_line.unisig_message.upper_layer_decoded_stms
                    assert len(ppn_log_line.unisig_message.upper_layer_decoded_stms) == 1
                    for upper_layer_decoded_stm in ppn_log_line.unisig_message.upper_layer_decoded_stms:
                        assert not upper_layer_decoded_stm.creational_and_decoding_errors

                @pytest.mark.parametrize(
                    "raw_ppn_log_line",
                    [
                        "2026-03-28 18:21:04:919 kppn 1.3.3: [99:2 => 3:2] Sending PROFIBUS message  [num:25736][rt:1273][mode:SDA][len:102] 06 c9 1d 5e a1 16 28 21 3a e4 72 88 70 51 34 7c 92 b5 89 08 62 07 00 01 40 00 40 00 80 00 00 00 00 00 00 06 c7 06 26 06 a6 26 e9 80 00 00 00 00 68 0b 0e d4 21 45 04 27 5c 8e 21 14 30 40 00 00 00 11 53 d3 11 40 01 ff e0 00 00 00 f0 00 02 02 18 2f 55 7b 40 00 02 a8 03 c8 1f 50 00 78 06 50 cb 85 8e 5c 27 04",
                        "2026-03-29 12:11:15:745 kppn 1.3.3: [99:2 => 3:2] Sending PROFIBUS message  [num:28][rt:1146][mode:SDA][len:77] 2c c9 1d 45 a1 0f e8 00 1a ac 21 c0 70 38 34 7d 61 6f 01 ff ff ff ff ff 5f ff ff ff ff c0 00 00 00 00 00 06 e6 c6 06 c6 06 86 49 a0 00 00 00 00 68 0b 0e d6 20 74 00 00 00 07 ff e0 ff ff fc ff ff ff fc 00 78 06 48 49 97 84 55 03 00",
                    ],
                )
                def test_decode_line_with_stm_to_ensure_crashs_are_resolved(
                    self,
                    raw_ppn_log_line: str,
                    next_unisig_58_library_fixture: upper_layer_libraries.UpperLayerDecodingLibrary,
                ) -> None:
                    ppn_log_line = ppn_profibus_log.ProfibusLogLine.decode_raw_log_line(raw_ppn_log_line, upper_layer_decoding_library=next_unisig_58_library_fixture)
                    assert ppn_log_line
                    ppn_log_line.decode_sdn_or_sda()
                    assert ppn_log_line.unisig_message

                @pytest.mark.parametrize(
                    "raw_ppn_log_line",
                    [
                        "2025-11-02 03:14:06:508 kppn 1.3.3: [99:33 <= 2:33] Received PROFIBUS message [num:47967][mode:SDA][len:18] 4c 89 1d 06 0e 00 cc 7f ff 1a d8 00 67 e2 63 48 c4 9b",
                        "2025-09-28 01:37:13:841 kppn 1.3.3: [99:33 <= 2:33] Received PROFIBUS message [num:55373][mode:SDA][len:18] 21 89 1d 06 0e 00 cc 7f 58 19 50 00 df f7 6c 1e 1d 4f",
                        "2026-03-29 23:33:14:389 kppn 1.3.3: [99:33 <= 2:33] Received PROFIBUS message [num:22933][mode:SDA][len:18] cc 89 1d 06 0e 00 cc 7f c4 86 18 00 d4 fa 89 85 2a ed",
                        "2026-03-29 22:36:04:676 kppn 1.3.3: [99:33 <= 2:33] Received PROFIBUS message [num:186142][mode:SDA][len:18] cc 89 1d 06 0e 00 cc 7f 0c 00 c5 00 fb f1 e3 98 3e 9e",
                    ],
                )
                def test_decode_line_with_stm14_failure(
                    self,
                    raw_ppn_log_line: str,
                    next_unisig_58_library_fixture: upper_layer_libraries.UpperLayerDecodingLibrary,
                ) -> None:
                    ppn_log_line = ppn_profibus_log.ProfibusLogLine.decode_raw_log_line(raw_ppn_log_line, upper_layer_decoding_library=next_unisig_58_library_fixture)
                    assert ppn_log_line
                    ppn_log_line.decode_sdn_or_sda()
                    assert ppn_log_line.unisig_message
                    assert not ppn_log_line.unisig_message.creational_and_decoding_errors

                def test_decode_line_stms_184_176_175_from_file(self, next_unisig_58_library_fixture: upper_layer_libraries.UpperLayerDecodingLibrary) -> None:
                    log_file = ppn_profibus_log.ProfibusLogFile(file_full_path=r"test\resources\ppn\STMs 175 184 176.log_ppn", upper_layer_decoding_library=next_unisig_58_library_fixture)
                    log_file.process()
                    assert log_file.decoded_lines
                    ppn_log_line = log_file.decoded_lines[0]
                    ppn_log_line.decode_sdn_or_sda()
                    assert ppn_log_line.unisig_message
                    assert not ppn_log_line.unisig_message.creational_and_decoding_errors
                    assert isinstance(ppn_log_line.unisig_message, decode_unisig.SdaForUpperLayerTelegram)
                    assert ppn_log_line.unisig_message.upper_layer_decoded_stms
                    assert len(ppn_log_line.unisig_message.upper_layer_decoded_stms) == 3
                    for upper_layer_decoded_stm in ppn_log_line.unisig_message.upper_layer_decoded_stms:
                        assert not upper_layer_decoded_stm.creational_and_decoding_errors

                def test_decode_stm_message_47(self, next_unisig_58_library_fixture: upper_layer_libraries.UpperLayerDecodingLibrary) -> None:
                    ppn_log_line = ppn_profibus_log.ProfibusLogLine.decode_raw_log_line(
                        line="2026-03-29 01:18:03:916 kppn 1.3.3: [99:33 <= 2:33] Received PROFIBUS message [num:1492][mode:SDA][len:48] d5 89 1d 24 01 01 28 20 00 10 17 41 81 40 18 0c 06 0a 05 02 81 40 48 42 14 1c 02 c1 f0 0c 01 e0 12 b3 39 17 80 59 6b 11 4c 01 5d 0e 25 b1 e6 13",
                        upper_layer_decoding_library=next_unisig_58_library_fixture,
                    )
                    assert ppn_log_line
                    ppn_log_line.decode_sdn_or_sda()
                    assert ppn_log_line.unisig_message
                    assert not ppn_log_line.unisig_message.creational_and_decoding_errors
                    assert isinstance(ppn_log_line.unisig_message, decode_unisig.SdaForUpperLayerTelegram)
                    assert ppn_log_line.unisig_message.upper_layer_decoded_stms
                    assert len(ppn_log_line.unisig_message.upper_layer_decoded_stms) == 7
                    stm_message_47 = ppn_log_line.unisig_message.upper_layer_decoded_stms[6]
                    assert stm_message_47.nid_stm == 47
                    assert not stm_message_47.creational_and_decoding_errors
                    for upper_layer_decoded_stm in ppn_log_line.unisig_message.upper_layer_decoded_stms:
                        assert not upper_layer_decoded_stm.creational_and_decoding_errors

                def test_decode_line_with_stm15_and_stm1(self, next_unisig_58_library_fixture: upper_layer_libraries.UpperLayerDecodingLibrary) -> None:
                    ppn_log_line = ppn_profibus_log.ProfibusLogLine.decode_raw_log_line(
                        line="2026-06-01 18:16:17:636 kppn 1.3.3: [99:33 => 2:33] Sending PROFIBUS message [num:20600][rt:1711][mode:SDA][len:22] b1 89 1d 0a 01 01 28 20 00 78 06 50 e7 4b 22 00 59 9d 7a c8 4d b6",
                        upper_layer_decoding_library=next_unisig_58_library_fixture,
                    )
                    assert ppn_log_line
                    ppn_log_line.decode_sdn_or_sda()
                    assert ppn_log_line.unisig_message
                    assert not ppn_log_line.unisig_message.creational_and_decoding_errors
                    assert isinstance(ppn_log_line.unisig_message, decode_unisig.SdaForUpperLayerTelegram)
                    assert ppn_log_line.unisig_message.upper_layer_decoded_stms
                    assert len(ppn_log_line.unisig_message.upper_layer_decoded_stms) == 2
                    for upper_layer_decoded_stm in ppn_log_line.unisig_message.upper_layer_decoded_stms:
                        assert not upper_layer_decoded_stm.creational_and_decoding_errors

                def test_decode_one_line_with_stm7_stm47_stm31_stm2_stm1_stm30_stm5(self, next_unisig_58_library_fixture: upper_layer_libraries.UpperLayerDecodingLibrary) -> None:
                    ppn_log_line = ppn_profibus_log.ProfibusLogLine.decode_raw_log_line(
                        line="2026-03-29 09:46:10:152 kppn 1.3.3: [99:33 <= 2:33] Received PROFIBUS message [num:1710][mode:SDA][len:48] 67 89 1d 24 01 01 28 20 00 10 17 41 81 40 18 0c 06 0a 05 02 81 40 48 42 18 1c 02 c1 f0 0c 11 e0 12 b3 39 17 80 59 ff 2c 02 00 6d 6a 87 67 e3 81",
                        upper_layer_decoding_library=next_unisig_58_library_fixture,
                    )

                    assert ppn_log_line
                    ppn_log_line.decode_sdn_or_sda()
                    assert ppn_log_line.unisig_message
                    assert not ppn_log_line.unisig_message.creational_and_decoding_errors
                    assert isinstance(ppn_log_line.unisig_message, decode_unisig.SdaForUpperLayerTelegram)
                    assert ppn_log_line.unisig_message.upper_layer_decoded_stms
                    assert len(ppn_log_line.unisig_message.upper_layer_decoded_stms) == 7
                    for upper_layer_decoded_stm in ppn_log_line.unisig_message.upper_layer_decoded_stms:
                        assert not upper_layer_decoded_stm.creational_and_decoding_errors

                def test_decode_one_line_with_cfx00951990(self, next_unisig_58_library_fixture: upper_layer_libraries.UpperLayerDecodingLibrary) -> None:
                    ppn_log_line = ppn_profibus_log.ProfibusLogLine.decode_raw_log_line(
                        line="2026-03-29 01:18:03:916 kppn 1.3.3: [99:33 <= 2:33] Received PROFIBUS message [num:1492][mode:SDA][len:48] d5 89 1d 24 01 01 28 20 00 10 17 41 81 40 18 0c 06 0a 05 02 81 40 48 42 14 1c 02 c1 f0 0c 01 e0 12 b3 39 17 80 59 6b 11 4c 01 5d 0e 25 b1 e6 13",
                        upper_layer_decoding_library=next_unisig_58_library_fixture,
                    )

                    assert ppn_log_line
                    ppn_log_line.decode_sdn_or_sda()
                    assert ppn_log_line.unisig_message
                    assert not ppn_log_line.unisig_message.creational_and_decoding_errors
                    assert isinstance(ppn_log_line.unisig_message, decode_unisig.SdaForUpperLayerTelegram)
                    assert ppn_log_line.unisig_message.upper_layer_decoded_stms
                    assert len(ppn_log_line.unisig_message.upper_layer_decoded_stms) == 7
                    for upper_layer_decoded_stm in ppn_log_line.unisig_message.upper_layer_decoded_stms:
                        assert not upper_layer_decoded_stm.creational_and_decoding_errors

                def test_decode_line_with_stms_5_47_7_31_1(self, next_unisig_58_library_fixture: upper_layer_libraries.UpperLayerDecodingLibrary) -> None:
                    ppn_log_line = ppn_profibus_log.ProfibusLogLine.decode_raw_log_line(
                        line="2026-06-01 18:16:18:270 kppn 1.3.3: [99:33 <= 2:33] Received PROFIBUS message [num:121266][mode:SDA][len:32] 82 89 1d 14 01 01 28 20 00 28 09 08 42 83 80 58 3e 01 80 5e 01 67 0e 4e 22 00 86 23 39 5a ab df",
                        upper_layer_decoding_library=next_unisig_58_library_fixture,
                    )
                    assert ppn_log_line
                    ppn_log_line.decode_sdn_or_sda()
                    assert ppn_log_line.unisig_message
                    assert not ppn_log_line.unisig_message.creational_and_decoding_errors
                    assert isinstance(ppn_log_line.unisig_message, decode_unisig.SdaForUpperLayerTelegram)
                    assert ppn_log_line.unisig_message.upper_layer_decoded_stms
                    assert len(ppn_log_line.unisig_message.upper_layer_decoded_stms) == 5
                    for upper_layer_decoded_stm in ppn_log_line.unisig_message.upper_layer_decoded_stms:
                        assert not upper_layer_decoded_stm.creational_and_decoding_errors

    class TestSdn:
        def test_decode_sync_and_reference_time(self, next_unisig_58_library_fixture: upper_layer_libraries.UpperLayerDecodingLibrary) -> None:
            ppn_log_line = ppn_profibus_log.ProfibusLogLine.decode_raw_log_line(
                line="2026-03-28 18:17:17:032 kppn 1.3.3: [127:32 <= 2:32] Received PROFIBUS message [num:129555][mode:SDN][len:25] 03 00 00 a1 b9 dd 02 00 03 00 00 b9 dd 02 00 04 16 24 04 19 ae 91 f6 50 69",
                upper_layer_decoding_library=next_unisig_58_library_fixture,
            )
            assert ppn_log_line
            ppn_log_line.decode_sdn_or_sda()
            assert ppn_log_line.unisig_message
            assert not ppn_log_line.unisig_message.creational_and_decoding_errors
            assert ppn_log_line.unisig_message
            assert isinstance(ppn_log_line.unisig_message, decode_unisig.SdnSyncAndReferenceTimeMulticastMessage)
            assert ppn_log_line.unisig_message.reference_time_n_minus_1_utc.human_format == "19:17:53.796"

        def test_decode_safe_time_layer_startup(self, next_unisig_58_library_fixture: upper_layer_libraries.UpperLayerDecodingLibrary) -> None:
            ppn_log_line = ppn_profibus_log.ProfibusLogLine.decode_raw_log_line(
                line="2026-03-29 22:17:07:522 kppn 1.3.3: [127:39 <= 2:39] Received PROFIBUS message [num:169549][mode:SDN][len:25] 03 00 00 a4 15 a5 00 00 03 00 00 e8 03 00 00 05 00 00 00 41 2d 1a 84 c5 12",
                upper_layer_decoding_library=next_unisig_58_library_fixture,
            )
            assert ppn_log_line
            ppn_log_line.decode_sdn_or_sda()
            assert ppn_log_line.unisig_message
            assert not ppn_log_line.unisig_message.creational_and_decoding_errors
            assert isinstance(ppn_log_line.unisig_message, decode_unisig.SdnSafeTimeLayerStartupForMulticast)
            assert ppn_log_line.unisig_message.sender_dynamic_transfer_time.human_format
            assert ppn_log_line.unisig_message.sender_static_transfer_time.human_format

        def test_decode_line_with_stm1_and_stm8(self, next_unisig_58_library_fixture: upper_layer_libraries.UpperLayerDecodingLibrary) -> None:
            ppn_log_line = ppn_profibus_log.ProfibusLogLine.decode_raw_log_line(
                line="2026-05-28 12:37:16:645 kppn 1.3.3: [127:39 <= 2:39] Received PROFIBUS message [num:39003][mode:SDN][len:51] 03 00 00 8d 40 08 00 00 ff 21 01 01 28 20 00 40 33 40 02 3b 8d c0 00 00 00 00 00 00 00 1d 36 80 00 1c 42 c0 00 1b a4 82 bf 6a ee 08 00 e9 df a7 f2 8d 66",
                upper_layer_decoding_library=next_unisig_58_library_fixture,
            )

            assert ppn_log_line
            ppn_log_line.decode_sdn_or_sda()
            assert ppn_log_line.unisig_message
            assert not ppn_log_line.unisig_message.creational_and_decoding_errors
            assert isinstance(ppn_log_line.unisig_message, decode_unisig.SdnApplicationDataMulticastForUpperLayerTelegram)

        def test_decode_line_with_stm8_and_stm1(self, next_unisig_58_library_fixture: upper_layer_libraries.UpperLayerDecodingLibrary) -> None:
            ppn_log_line = ppn_profibus_log.ProfibusLogLine.decode_raw_log_line(
                line="2026-06-01 17:58:12:336 kppn 1.3.3: [127:39 <= 2:39] Received PROFIBUS message [num:105421][mode:SDN][len:51] 03 00 00 8d c6 0f 00 00 ff 21 01 01 28 20 00 40 33 40 04 46 ec c0 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 02 bf f7 1b 11 00 37 02 7f 75 9b 87",
                upper_layer_decoding_library=next_unisig_58_library_fixture,
            )

            assert ppn_log_line
            ppn_log_line.decode_sdn_or_sda()
            assert ppn_log_line.unisig_message
            assert not ppn_log_line.unisig_message.creational_and_decoding_errors
            assert isinstance(ppn_log_line.unisig_message, decode_unisig.SdnApplicationDataMulticastForUpperLayerTelegram)


class TestNextUnisigS58Library:
    def test_load_json(self, next_unisig_58_library_fixture: upper_layer_libraries.UpperLayerDecodingLibrary) -> None:
        assert next_unisig_58_library_fixture is not None
        assert next_unisig_58_library_fixture.enum_attributes_type_definitions
        assert next_unisig_58_library_fixture.packets_definitions
