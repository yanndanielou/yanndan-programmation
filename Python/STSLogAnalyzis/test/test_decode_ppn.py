import pytest

from stsloganalyzis.ppn import ppn_log
from stsloganalyzis.unisig import decode_unisig


def test_decode_one_disconnect_sl0() -> None:
    ppn_log_line = ppn_log.ProfibusLogLine.decode_raw_log_line(
        "2026-05-28 12:37:05:492 kppn 1.3.3: [99:44 => 5:44] Sending PROFIBUS message [num:4138][rt:2363][mode:SDA][len:23] 76 c5 01 05 69 64 6c 65 20 63 79 63 6c 65 20 74 69 6d 65 2d 6f 75 74"
    )
    assert ppn_log_line
    ppn_log_line.decode_sdn_or_sna()
    disconnect = ppn_log_line.unisig_messages[0]
    assert disconnect
    assert isinstance(disconnect, decode_unisig.SdaDisconnectTelegram)
    assert disconnect.byte_message_decoded.is_correctly_and_completely_decoded()
    print(disconnect.disconnect_reason_text)


def test_decode_one_disconnect_sl4() -> None:
    ppn_log_line = ppn_log.ProfibusLogLine.decode_raw_log_line(
        "2026-05-28 12:37:06:666 kppn 1.3.3: [99:33 => 2:33] Sending PROFIBUS message [num:4143][rt:2397][mode:SDA][len:50] 7f 85 01 05 69 64 6c 65 20 63 79 63 6c 65 20 74 69 6d 65 2d 6f 75 74 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 d9 5c c9 44 a2 45"
    )
    assert ppn_log_line
    ppn_log_line.decode_sdn_or_sna()
    disconnect = ppn_log_line.unisig_messages[0]
    assert disconnect
    assert isinstance(disconnect, decode_unisig.SdaDisconnectTelegram)
    assert disconnect.byte_message_decoded.is_correctly_and_completely_decoded()
    print(disconnect.disconnect_reason_text)


@pytest.mark.parametrize(
    "raw_ppn_log_line",
    [
        "2026-05-22 15:17:08:758 kppn 1.3.3: [99:33 => 2:33] Sending PROFIBUS message [num:197704][rt:3903][mode:SDA][len:18] e0 89 1d 06 0f 00 ca 00 95 d1 b2 04 c0 fd 4f 34 44 a1",
        "2026-05-22 15:26:13:149 kppn 1.3.3: [99:37 => 2:37] Sending PROFIBUS message [num:199067][rt:1679][mode:SDA][len:18] f4 89 1d 06 0f 00 ca 00 23 20 bb 04 75 e8 c4 a2 d6 ad",
    ],
)
def test_decode_line_with_stm15(
    raw_ppn_log_line: str,
) -> None:
    ppn_log_line = ppn_log.ProfibusLogLine.decode_raw_log_line(raw_ppn_log_line)
    assert ppn_log_line
    ppn_log_line.decode_sdn_or_sna()
    assert ppn_log_line.unisig_messages


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
    raw_ppn_log_line: str,
) -> None:
    ppn_log_line = ppn_log.ProfibusLogLine.decode_raw_log_line(raw_ppn_log_line)
    assert ppn_log_line
    ppn_log_line.decode_sdn_or_sna()
    assert ppn_log_line.unisig_messages


def test_decode_line_with_stm1_and_stm8() -> None:
    ppn_log_line = ppn_log.ProfibusLogLine.decode_raw_log_line(
        "2026-05-28 12:37:16:645 kppn 1.3.3: [127:39 <= 2:39] Received PROFIBUS message [num:39003][mode:SDN][len:51] 03 00 00 8d 40 08 00 00 ff 21 01 01 28 20 00 40 33 40 02 3b 8d c0 00 00 00 00 00 00 00 1d 36 80 00 1c 42 c0 00 1b a4 82 bf 6a ee 08 00 e9 df a7 f2 8d 66"
    )

    assert ppn_log_line
    ppn_log_line.decode_sdn_or_sna()
    assert ppn_log_line.unisig_messages


def test_decode_line_with_stm8_and_stm1() -> None:
    ppn_log_line = ppn_log.ProfibusLogLine.decode_raw_log_line(
        "2026-06-01 17:58:12:336 kppn 1.3.3: [127:39 <= 2:39] Received PROFIBUS message [num:105421][mode:SDN][len:51] 03 00 00 8d c6 0f 00 00 ff 21 01 01 28 20 00 40 33 40 04 46 ec c0 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 02 bf f7 1b 11 00 37 02 7f 75 9b 87"
    )

    assert ppn_log_line
    ppn_log_line.decode_sdn_or_sna()
    assert ppn_log_line.unisig_messages


def test_decode_line_with_stm15_and_stm1() -> None:
    ppn_log_line = ppn_log.ProfibusLogLine.decode_raw_log_line(
        "2026-06-01 18:16:17:636 kppn 1.3.3: [99:33 => 2:33] Sending PROFIBUS message [num:20600][rt:1711][mode:SDA][len:22] b1 89 1d 0a 01 01 28 20 00 78 06 50 e7 4b 22 00 59 9d 7a c8 4d b6"
    )

    assert ppn_log_line
    ppn_log_line.decode_sdn_or_sna()
    assert ppn_log_line.unisig_messages


def test_decode_line_with_stms_5_47_7_31_1() -> None:
    ppn_log_line = ppn_log.ProfibusLogLine.decode_raw_log_line(
        "2026-06-01 18:16:18:270 kppn 1.3.3: [99:33 <= 2:33] Received PROFIBUS message [num:121266][mode:SDA][len:32] 82 89 1d 14 01 01 28 20 00 28 09 08 42 83 80 58 3e 01 80 5e 01 67 0e 4e 22 00 86 23 39 5a ab df"
    )
    assert ppn_log_line
    ppn_log_line.decode_sdn_or_sna()
    assert ppn_log_line.unisig_messages
