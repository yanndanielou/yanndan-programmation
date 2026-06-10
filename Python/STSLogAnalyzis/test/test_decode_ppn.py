from stsloganalyzis.ppn import ppn_log
from stsloganalyzis.unisig import decode_unisig


def test_decode_one_disconnect_sl0() -> None:
    ppn_log_line = ppn_log.ProfibusLogLine.decode_raw_log_line(
        "2026-05-28 12:37:05:492 kppn 1.3.3: [99:44 => 5:44] Sending PROFIBUS message [num:4138][rt:2363][mode:SDA][len:23] 76 c5 01 05 69 64 6c 65 20 63 79 63 6c 65 20 74 69 6d 65 2d 6f 75 74"
    )
    assert ppn_log_line
    disconnect = ppn_log_line.decode_sdn_or_sna()
    assert disconnect
    assert isinstance(disconnect, decode_unisig.SdaDisconnectTelegram)
    assert disconnect.byte_message_decoded.is_correctly_and_completely_decoded()
    print(disconnect.disconnect_reason_text)


def test_decode_one_disconnect_sl4() -> None:
    ppn_log_line = ppn_log.ProfibusLogLine.decode_raw_log_line(
        "2026-05-28 12:37:06:666 kppn 1.3.3: [99:33 => 2:33] Sending PROFIBUS message [num:4143][rt:2397][mode:SDA][len:50] 7f 85 01 05 69 64 6c 65 20 63 79 63 6c 65 20 74 69 6d 65 2d 6f 75 74 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 d9 5c c9 44 a2 45"
    )
    assert ppn_log_line
    disconnect = ppn_log_line.decode_sdn_or_sna()
    assert disconnect
    assert isinstance(disconnect, decode_unisig.SdaDisconnectTelegram)
    assert disconnect.byte_message_decoded.is_correctly_and_completely_decoded()
    print(disconnect.disconnect_reason_text)
