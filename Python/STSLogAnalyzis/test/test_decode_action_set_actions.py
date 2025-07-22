import pytest

import datetime

from stsloganalyzis import decode_action_set_content


class TestRiyl:

    def test_first_bit(self) -> None:
        csv_file_path = r"D:\RIYL1TS\Data\Csv\RIYL1_tsActionSet.csv"
        first_bit_on_only = "100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
        expected = "AS_P_1Y12_PLT_STOP_REQUEST"
        result = decode_action_set_content.decode_bitfield_returns_only_true(csv_file_path, first_bit_on_only)
        assert len(result) == 1
        assert result[0] == expected

    def test_two_first_bits(self) -> None:
        csv_file_path = r"D:\RIYL1TS\Data\Csv\RIYL1_tsActionSet.csv"
        first_bit_on_only = "110000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
        result = decode_action_set_content.decode_bitfield_returns_only_true(csv_file_path, first_bit_on_only)
        assert len(result) == 2
        assert "AS_P_1Y12_PLT_STOP_REQUEST" in result
        assert "AS_P_1Y12_PLT_END_OF_RUN" in result
        assert result[0] != result[1]

    def test_big_trip(self) -> None:
        csv_file_path = r"D:\RIYL1TS\Data\Csv\RIYL1_tsActionSet.csv"
        bit_fiedld = "100100100000000100100100100100100100100100100100100100100100100100100100110100100100001001100100100100100100100100100100100100100100100100100100100110010000000000000000000000000000000000000000000000000000111111101100110100111111110011111111111111111111111111111111111111111111111111111111111111111111110000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
        result = decode_action_set_content.decode_bitfield_returns_only_true(csv_file_path, bit_fiedld)
        assert len(result) == 141

        """
train;AfTrmvActionSet:319;::addStoppingPlatform P_1Y12 served = true
message;AfTsAtsCcActionSetMessageRp:218;::readMessage 192: Train T40 {102 cc: 102}. Stop at: P_1Y12 (action set [0])
train;AfTrmvActionSet:319;::addStoppingPlatform P_1Z12 served = true
message;AfTsAtsCcActionSetMessageRp:218;::readMessage 192: Train T40 {102 cc: 102}. Stop at: P_1Z12 (action set [3])
train;AfTrmvActionSet:319;::addStoppingPlatform P_1A12 served = true
message;AfTsAtsCcActionSetMessageRp:218;::readMessage 192: Train T40 {102 cc: 102}. Stop at: P_1A12 (action set [6])
train;AfTrmvActionSet:319;::addStoppingPlatform P_1B22 served = true
message;AfTsAtsCcActionSetMessageRp:218;::readMessage 192: Train T40 {102 cc: 102}. Stop at: P_1B22 (action set [15])
train;AfTrmvActionSet:319;::addStoppingPlatform P_1B32 served = true
message;AfTsAtsCcActionSetMessageRp:218;::readMessage 192: Train T40 {102 cc: 102}. Stop at: P_1B32 (action set [18])
train;AfTrmvActionSet:319;::addStoppingPlatform P_1B42 served = true
message;AfTsAtsCcActionSetMessageRp:218;::readMessage 192: Train T40 {102 cc: 102}. Stop at: P_1B42 (action set [21])
train;AfTrmvActionSet:319;::addStoppingPlatform P_1C12 served = true
message;AfTsAtsCcActionSetMessageRp:218;::readMessage 192: Train T40 {102 cc: 102}. Stop at: P_1C12 (action set [24])
train;AfTrmvActionSet:319;::addStoppingPlatform P_1C22 served = true
message;AfTsAtsCcActionSetMessageRp:218;::readMessage 192: Train T40 {102 cc: 102}. Stop at: P_1C22 (action set [27])
train;AfTrmvActionSet:319;::addStoppingPlatform P_1C32 served = true
message;AfTsAtsCcActionSetMessageRp:218;::readMessage 192: Train T40 {102 cc: 102}. Stop at: P_1C32 (action set [30])
train;AfTrmvActionSet:319;::addStoppingPlatform P_1C42 served = true
message;AfTsAtsCcActionSetMessageRp:218;::readMessage 192: Train T40 {102 cc: 102}. Stop at: P_1C42 (action set [33])
train;AfTrmvActionSet:319;::addStoppingPlatform P_1D22 served = true
message;AfTsAtsCcActionSetMessageRp:218;::readMessage 192: Train T40 {102 cc: 102}. Stop at: P_1D22 (action set [36])
train;AfTrmvActionSet:319;::addStoppingPlatform P_1D52 served = true
message;AfTsAtsCcActionSetMessageRp:218;::readMessage 192: Train T40 {102 cc: 102}. Stop at: P_1D52 (action set [39])
train;AfTrmvActionSet:319;::addStoppingPlatform P_1E22 served = true
message;AfTsAtsCcActionSetMessageRp:218;::readMessage 192: Train T40 {102 cc: 102}. Stop at: P_1E22 (action set [42])
train;AfTrmvActionSet:319;::addStoppingPlatform P_1F42 served = true
message;AfTsAtsCcActionSetMessageRp:218;::readMessage 192: Train T40 {102 cc: 102}. Stop at: P_1F42 (action set [45])
train;AfTrmvActionSet:319;::addStoppingPlatform P_1F52 served = true
message;AfTsAtsCcActionSetMessageRp:218;::readMessage 192: Train T40 {102 cc: 102}. Stop at: P_1F52 (action set [48])
train;AfTrmvActionSet:319;::addStoppingPlatform P_1F72 served = true
message;AfTsAtsCcActionSetMessageRp:218;::readMessage 192: Train T40 {102 cc: 102}. Stop at: P_1F72 (action set [51])
train;AfTrmvActionSet:319;::addStoppingPlatform P_1F82 served = true
message;AfTsAtsCcActionSetMessageRp:218;::readMessage 192: Train T40 {102 cc: 102}. Stop at: P_1F82 (action set [54])
train;AfTrmvActionSet:319;::addStoppingPlatform P_1F92 served = true
message;AfTsAtsCcActionSetMessageRp:218;::readMessage 192: Train T40 {102 cc: 102}. Stop at: P_1F92 (action set [57])
train;AfTrmvActionSet:319;::addStoppingPlatform P_1G12 served = true
message;AfTsAtsCcActionSetMessageRp:218;::readMessage 192: Train T40 {102 cc: 102}. Stop at: P_1G12 (action set [60])
train;AfTrmvActionSet:319;::addStoppingPlatform P_1G22 served = true
message;AfTsAtsCcActionSetMessageRp:218;::readMessage 192: Train T40 {102 cc: 102}. Stop at: P_1G22 (action set [63])
train;AfTrmvActionSet:319;::addStoppingPlatform P_1H22 served = true
message;AfTsAtsCcActionSetMessageRp:218;::readMessage 192: Train T40 {102 cc: 102}. Stop at: P_1H22 (action set [66])
train;AfTrmvActionSet:319;::addStoppingPlatform P_1J12 served = true
message;AfTsAtsCcActionSetMessageRp:218;::readMessage 192: Train T40 {102 cc: 102}. Stop at: P_1J12 (action set [69])
train;AfTrmvActionSet:319;::addStoppingPlatform P_1J22 served = true
message;AfTsAtsCcActionSetMessageRp:218;::readMessage 192: Train T40 {102 cc: 102}. Stop at: P_1J22 (action set [72])
message;AfTsAtsCcActionSetMessageRp:215;::readMessage 192: Train T40 {102 cc: 102}. End of run at: AS_P_1J22 (action set [73])
message;AfTsAtsCcActionSetMessageRp:218;::readMessage 192: Train T40 {102 cc: 102}. Stop at: P_1J22 (action set [73])
train;AfTrmvActionSet:319;::addStoppingPlatform P_1Y11 served = true
message;AfTsAtsCcActionSetMessageRp:218;::readMessage 192: Train T40 {102 cc: 102}. Stop at: P_1Y11 (action set [75])
train;AfTrmvActionSet:319;::addStoppingPlatform P_1Z11 served = true
message;AfTsAtsCcActionSetMessageRp:218;::readMessage 192: Train T40 {102 cc: 102}. Stop at: P_1Z11 (action set [78])
train;AfTrmvActionSet:319;::addStoppingPlatform P_1A11 served = true
message;AfTsAtsCcActionSetMessageRp:218;::readMessage 192: Train T40 {102 cc: 102}. Stop at: P_1A11 (action set [81])
train;AfTrmvActionSet:319;::addStoppingPlatform P_1A21 served = false
message;AfTsAtsCcActionSetMessageRp:218;::readMessage 192: Train T40 {102 cc: 102}. Stop at: P_1A21 (action set [86])
train;AfTrmvActionSet:319;::addStoppingPlatform P_1B11 served = false
message;AfTsAtsCcActionSetMessageRp:218;::readMessage 192: Train T40 {102 cc: 102}. Stop at: P_1B11 (action set [89])
train;AfTrmvActionSet:319;::addStoppingPlatform P_1B21 served = true
message;AfTsAtsCcActionSetMessageRp:218;::readMessage 192: Train T40 {102 cc: 102}. Stop at: P_1B21 (action set [90])
train;AfTrmvActionSet:319;::addStoppingPlatform P_1B31 served = true
message;AfTsAtsCcActionSetMessageRp:218;::readMessage 192: Train T40 {102 cc: 102}. Stop at: P_1B31 (action set [93])
train;AfTrmvActionSet:319;::addStoppingPlatform P_1B41 served = true
message;AfTsAtsCcActionSetMessageRp:218;::readMessage 192: Train T40 {102 cc: 102}. Stop at: P_1B41 (action set [96])
train;AfTrmvActionSet:319;::addStoppingPlatform P_1C11 served = true
message;AfTsAtsCcActionSetMessageRp:218;::readMessage 192: Train T40 {102 cc: 102}. Stop at: P_1C11 (action set [99])
train;AfTrmvActionSet:319;::addStoppingPlatform P_1C21 served = true
message;AfTsAtsCcActionSetMessageRp:218;::readMessage 192: Train T40 {102 cc: 102}. Stop at: P_1C21 (action set [102])
train;AfTrmvActionSet:319;::addStoppingPlatform P_1C31 served = true
message;AfTsAtsCcActionSetMessageRp:218;::readMessage 192: Train T40 {102 cc: 102}. Stop at: P_1C31 (action set [105])
train;AfTrmvActionSet:319;::addStoppingPlatform P_1C41 served = true
message;AfTsAtsCcActionSetMessageRp:218;::readMessage 192: Train T40 {102 cc: 102}. Stop at: P_1C41 (action set [108])
train;AfTrmvActionSet:319;::addStoppingPlatform P_1D21 served = true
message;AfTsAtsCcActionSetMessageRp:218;::readMessage 192: Train T40 {102 cc: 102}. Stop at: P_1D21 (action set [111])
train;AfTrmvActionSet:319;::addStoppingPlatform P_1D51 served = true
message;AfTsAtsCcActionSetMessageRp:218;::readMessage 192: Train T40 {102 cc: 102}. Stop at: P_1D51 (action set [114])
train;AfTrmvActionSet:319;::addStoppingPlatform P_1E21 served = true
message;AfTsAtsCcActionSetMessageRp:218;::readMessage 192: Train T40 {102 cc: 102}. Stop at: P_1E21 (action set [117])
train;AfTrmvActionSet:319;::addStoppingPlatform P_1F41 served = true
message;AfTsAtsCcActionSetMessageRp:218;::readMessage 192: Train T40 {102 cc: 102}. Stop at: P_1F41 (action set [120])
train;AfTrmvActionSet:319;::addStoppingPlatform P_1F51 served = true
message;AfTsAtsCcActionSetMessageRp:218;::readMessage 192: Train T40 {102 cc: 102}. Stop at: P_1F51 (action set [123])
train;AfTrmvActionSet:319;::addStoppingPlatform P_1F71 served = true
message;AfTsAtsCcActionSetMessageRp:218;::readMessage 192: Train T40 {102 cc: 102}. Stop at: P_1F71 (action set [126])
train;AfTrmvActionSet:319;::addStoppingPlatform P_1F81 served = true
message;AfTsAtsCcActionSetMessageRp:218;::readMessage 192: Train T40 {102 cc: 102}. Stop at: P_1F81 (action set [129])
train;AfTrmvActionSet:319;::addStoppingPlatform P_1F91 served = true
message;AfTsAtsCcActionSetMessageRp:218;::readMessage 192: Train T40 {102 cc: 102}. Stop at: P_1F91 (action set [132])
train;AfTrmvActionSet:319;::addStoppingPlatform P_1G11 served = true
message;AfTsAtsCcActionSetMessageRp:218;::readMessage 192: Train T40 {102 cc: 102}. Stop at: P_1G11 (action set [135])
train;AfTrmvActionSet:319;::addStoppingPlatform P_1G21 served = true
message;AfTsAtsCcActionSetMessageRp:218;::readMessage 192: Train T40 {102 cc: 102}. Stop at: P_1G21 (action set [138])
train;AfTrmvActionSet:319;::addStoppingPlatform P_1H21 served = true
message;AfTsAtsCcActionSetMessageRp:218;::readMessage 192: Train T40 {102 cc: 102}. Stop at: P_1H21 (action set [141])
train;AfTrmvActionSet:319;::addStoppingPlatform P_1J11 served = true
message;AfTsAtsCcActionSetMessageRp:218;::readMessage 192: Train T40 {102 cc: 102}. Stop at: P_1J11 (action set [144])
train;AfTrmvActionSet:319;::addStoppingPlatform P_1J21 served = true
readMessage 192: Train T40 {102 cc: 102}. Stop at: P_1J21 (action set [147])
readMessage 192: Train T40 {102 cc: 102}. End of run at: AS_P_1J21 (action set [148])
readMessage 192: Train T40 {102 cc: 102}. Stop at: P_1J21 (action set [148])
readMessage 192: Train T40 {102 cc: 102}. End of run at: AS_P_1TT1 (action set [151])
readMessage 192: Train T40 {102 cc: 102}. Stop at: P_1TT1 (action set [151])

        
        
        """
        assert "AS_PTA_P1Y1_1_PTA_END_OF_RUN" in result  # 204])
        assert "AS_PTA_P1Y1_2_PTA_END_OF_RUN" in result  # 205])
        assert "AS_PTA_P1Y1_3_PTA_END_OF_RUN" in result  # 206])
        assert "AS_PTA_P1Y1_4_PTA_END_OF_RUN" in result  # 207])
        assert "AS_PTA_P1Y1_5_PTA_END_OF_RUN" in result  # 208])
        assert "AS_PTA_P1Y1_6_PTA_END_OF_RUN" in result  # 209])
        assert "AS_PTA_P1A1_2_PTA_END_OF_RUN" in result  # 210])
        assert "AS_PTA_P1B1_2_PTA_END_OF_RUN" in result  # 212])
        assert "AS_PTA_P1B3_2_PTA_END_OF_RUN" in result  # 213])
        assert "AS_PTA_P1D2_2_PTA_END_OF_RUN" in result  # 216])
        assert "AS_PTA_P1F4_2_PTA_END_OF_RUN" in result  # 217])
        assert "AS_PTA_P1F7_2_PTA_END_OF_RUN" in result  # 219])
        assert "AS_PTA_P1J2_1_PTA_END_OF_RUN" in result  # 222])
        assert "AS_PTA_P1J2_2_PTA_END_OF_RUN" in result  # 223])
        assert "AS_PTA_P1J2_3_PTA_END_OF_RUN" in result  # 224])
        assert "AS_PTA_P1J2_4_PTA_END_OF_RUN" in result  # 225])
        assert "AS_PTA_P1J2_5_PTA_END_OF_RUN" in result  # 226])
        assert "AS_PTA_P1J2_6_PTA_END_OF_RUN" in result  # 227])
        assert "AS_PTA_P1J2_7_PTA_END_OF_RUN" in result  # 228])
        assert "AS_PTA_P1J2_8_PTA_END_OF_RUN" in result  # 229])
        assert "AS_PTA_DSWT_1_PTA_END_OF_RUN" in result  # 232])
        assert "AS_PTA_DSWT_2_PTA_END_OF_RUN" in result  # 233])
        assert "AS_PTA_DSWT_3_PTA_END_OF_RUN" in result  # 234])
        assert "AS_PTA_DSWT_4_PTA_END_OF_RUN" in result  # 235])
        assert "AS_PTA_DST1_3_PTA_END_OF_RUN" in result  # 236])
        assert "AS_PTA_DST1_2_PTA_END_OF_RUN" in result  # 237])
        assert "AS_PTA_DST1_1_PTA_END_OF_RUN" in result  # 238])
        assert "AS_PTA_DST2_3_PTA_END_OF_RUN" in result  # 239])
        assert "AS_PTA_DST2_2_PTA_END_OF_RUN" in result  # 240])
        assert "AS_PTA_DST2_1_PTA_END_OF_RUN" in result  # 241])
        assert "AS_PTA_DST3_3_PTA_END_OF_RUN" in result  # 242])
        assert "AS_PTA_DST3_2_PTA_END_OF_RUN" in result  # 243])
        assert "AS_PTA_DST3_1_PTA_END_OF_RUN" in result  # 244])
        assert "AS_PTA_DST4_3_PTA_END_OF_RUN" in result  # 245])
        assert "AS_PTA_DST4_2_PTA_END_OF_RUN" in result  # 246])
        assert "AS_PTA_DST4_1_PTA_END_OF_RUN" in result  # 247])
        assert "AS_PTA_DST5_3_PTA_END_OF_RUN" in result  # 248])
        assert "AS_PTA_DST5_2_PTA_END_OF_RUN" in result  # 249])
        assert "AS_PTA_DST5_1_PTA_END_OF_RUN" in result  # 250])
        assert "AS_PTA_DST6_3_PTA_END_OF_RUN" in result  # 251])
        assert "AS_PTA_DST6_2_PTA_END_OF_RUN" in result  # 252])
        assert "AS_PTA_DST6_1_PTA_END_OF_RUN" in result  # 253])
        assert "AS_PTA_DST7_3_PTA_END_OF_RUN" in result  # 254])
        assert "AS_PTA_DST7_2_PTA_END_OF_RUN" in result  # 255])
        assert "AS_PTA_DST7_1_PTA_END_OF_RUN" in result  # 256])
        assert "AS_PTA_DST8_3_PTA_END_OF_RUN" in result  # 257])
        assert "AS_PTA_DST8_2_PTA_END_OF_RUN" in result  # 258])
        assert "AS_PTA_DST8_1_PTA_END_OF_RUN" in result  # 259])
        assert "AS_PTA_DS_ZT01_PTA_END_OF_RUN" in result  # 260])
        assert "AS_PTA_DS_ZT02_PTA_END_OF_RUN" in result  # 261])
        assert "AS_PTA_DS_ZT03_PTA_END_OF_RUN" in result  # 262])
        assert "AS_PTA_DS_TT_PTA_END_OF_RUN" in result  # 263])
        assert "AS_PTA_DSTB4_1_PTA_END_OF_RUN" in result  # 264])
        assert "AS_PTA_DSTB4_2_PTA_END_OF_RUN" in result  # 265])
        assert "AS_PTA_DSTB3_1_PTA_END_OF_RUN" in result  # 266])
        assert "AS_PTA_DSTB3_2_PTA_END_OF_RUN" in result  # 267])
        assert "AS_PTA_DSTB5_1_PTA_END_OF_RUN" in result  # 268])
        assert "AS_PTA_DNT1_1_PTA_END_OF_RUN" in result  # 269])
        assert "AS_PTA_DNT1_2_PTA_END_OF_RUN" in result  # 270])
        assert "AS_PTA_DNT1_3_PTA_END_OF_RUN" in result  # 271])
        assert "AS_PTA_DNT2_1_PTA_END_OF_RUN" in result  # 272])
        assert "AS_PTA_DNT2_2_PTA_END_OF_RUN" in result  # 273])
        assert "AS_PTA_DNT2_3_PTA_END_OF_RUN" in result  # 274])
        assert "AS_PTA_DNT3_1_PTA_END_OF_RUN" in result  # 275])
        assert "AS_PTA_DNT3_2_PTA_END_OF_RUN" in result  # 276])
        assert "AS_PTA_DNT3_3_PTA_END_OF_RUN" in result  # 277])
        assert "AS_PTA_DNT4_1_PTA_END_OF_RUN" in result  # 278])
        assert "AS_PTA_DNT4_2_PTA_END_OF_RUN" in result  # 279])
        assert "AS_PTA_DNT4_3_PTA_END_OF_RUN" in result  # 280])
        assert "AS_PTA_DNT5_1_PTA_END_OF_RUN" in result  # 281])
        assert "AS_PTA_DNT5_2_PTA_END_OF_RUN" in result  # 282])
        assert "AS_PTA_DNT5_3_PTA_END_OF_RUN" in result  # 283])
        assert "AS_PTA_DNT6_1_PTA_END_OF_RUN" in result  # 284])
        assert "AS_PTA_DNT6_2_PTA_END_OF_RUN" in result  # 285])
        assert "AS_PTA_DNT6_3_PTA_END_OF_RUN" in result  # 286])
        assert "AS_PTA_DNT7_1_PTA_END_OF_RUN" in result  # 287])
        assert "AS_PTA_DNT7_2_PTA_END_OF_RUN" in result  # 288])
        assert "AS_PTA_DNT7_3_PTA_END_OF_RUN" in result  # 289])
        assert "AS_PTA_DNT8_1_PTA_END_OF_RUN" in result  # 290])
        assert "AS_PTA_DNT8_2_PTA_END_OF_RUN" in result  # 291])
        assert "AS_PTA_DNT8_3_PTA_END_OF_RUN" in result  # 292])
        assert "AS_PTA_DNTB1_PTA_END_OF_RUN" in result  # 293])
        assert "AS_PTA_DNTB2_PTA_END_OF_RUN" in result  # 294])
        assert "AS_PTA_DNTB4_PTA_END_OF_RUN" in result  # 295])
        assert "AS_PTA_DNZT1_PTA_END_OF_RUN" in result  # 296])
        assert "AS_PTA_DNZT2_PTA_END_OF_RUN" in result  # 297])
        assert "AS_PTA_DNWT_1_PTA_END_OF_RUN" in result  # 298])
        assert "AS_PTA_DNWT_2_PTA_END_OF_RUN" in result  # 299])
        assert "AS_PTA_DNWT_3_PTA_END_OF_RUN" in result  # 300])
        assert "AS_PTA_DNWT_4_PTA_END_OF_RUN" in result  # 301])
