import pytest

from stsloganalyzis.unisig.s98 import triple_des_s98, secret_kmac_keys, decode_unisig_s98
from typing import cast
import pyshark.packet.packet
import pyshark


class TestComputeMacFromWiresharkCapture:

    class TestMacRecomputedIsSameAsTransmitted:

        def test_au2_from_pcap_containing_au1_and_au2(self) -> None:
            pcap_file_full_path = r"test\resources\unisig_s98\pas_1_pai_75_Au1_Au2.pcapng"

            simulation = decode_unisig_s98.UnisigS98Simulation()
            simulation.build_unisig_s98_packets_from_load_pcap_file(pcap_file_full_path)
            au2_packet = simulation.unisig_s98_packets[1]
            assert isinstance(au2_packet, decode_unisig_s98.UnisigS98Au2WiresharkPacket)
            au2_packet.recompute_mac()
            assert au2_packet.recomputed_mac_and_transmitted_mac_are_equals

        def ignore_test_au3(self) -> None:
            pcap_file_full_path = r"test\resources\unisig_s98\pas_1_pai_75_Au1_Au2_Au3.pcapng"
            simulation = decode_unisig_s98.UnisigS98Simulation()
            simulation.build_unisig_s98_packets_from_load_pcap_file(pcap_file_full_path)
            au3_packet = simulation.unisig_s98_packets[2]
            assert isinstance(au3_packet, decode_unisig_s98.UnisigS98DtDataWiresharkPacket)
            au3_packet.recompute_mac()
            assert au3_packet.recomputed_mac_and_transmitted_mac_are_equals

        def ignore_test_ar(self) -> None:
            pcap_file_full_path = r"test\resources\unisig_s98\pas_1_pai_75_Au1_Au2_Au3_AR.pcapng"
            simulation = decode_unisig_s98.UnisigS98Simulation()
            simulation.build_unisig_s98_packets_from_load_pcap_file(pcap_file_full_path)
            ar_packet = simulation.unisig_s98_packets[2]
            assert isinstance(ar_packet, decode_unisig_s98.UnisigS98DtDataWiresharkPacket)
            ar_packet.recompute_mac()
            assert ar_packet.recomputed_mac_and_transmitted_mac_are_equals

        def test_dt_offset_answ_1(self) -> None:
            pcap_file_full_path = r"test\resources\unisig_s98\pas_1_pai_75_Au1_Au2_and_pai_pas_dt_OffsetAnsw1.pcapng"
            simulation = decode_unisig_s98.UnisigS98Simulation()
            simulation.build_unisig_s98_packets_from_load_pcap_file(pcap_file_full_path)
            offset_answ_1_packet = simulation.unisig_s98_packets[2]
            assert isinstance(offset_answ_1_packet, decode_unisig_s98.UnisigS98DtDataWiresharkPacket)
            offset_answ_1_packet.recompute_mac()
            assert offset_answ_1_packet.recomputed_mac_and_transmitted_mac_are_equals

        def test_pas_pai_dt_keep_alive_no_user_data(self) -> None:
            pcap_file_full_path = r"test\resources\unisig_s98\pas_1_pai_75_Au1_Au2_and_pas_pai_dt_keep_alive_no_user_data.pcapng"
            simulation = decode_unisig_s98.UnisigS98Simulation()
            simulation.build_unisig_s98_packets_from_load_pcap_file(pcap_file_full_path)
            dt_packet = simulation.unisig_s98_packets[2]
            assert isinstance(dt_packet, decode_unisig_s98.UnisigS98DtDataWiresharkPacket)
            dt_packet.recompute_mac()
            assert dt_packet.recomputed_mac_and_transmitted_mac_are_equals

        def test_pai_pas_dt_keep_alive_no_user_data(self) -> None:
            pcap_file_full_path = r"test\resources\unisig_s98\pas_1_pai_75_Au1_Au2_and_pai_pas_dt_keep_alive_no_user_data.pcapng"
            simulation = decode_unisig_s98.UnisigS98Simulation()
            simulation.build_unisig_s98_packets_from_load_pcap_file(pcap_file_full_path)
            dt_packet = simulation.unisig_s98_packets[2]
            assert isinstance(dt_packet, decode_unisig_s98.UnisigS98DtDataWiresharkPacket)
            dt_packet.recompute_mac()
            assert dt_packet.recomputed_mac_and_transmitted_mac_are_equals

    class TestMacIsAsHumanComputed:

        def test_compute_mac_au2_from_pcap_containing_au1_and_au2(self) -> None:
            pcap_file_full_path = r"test\resources\unisig_s98\pas_1_pai_75_Au1_Au2.pcapng"

            simulation = decode_unisig_s98.UnisigS98Simulation()
            simulation.build_unisig_s98_packets_from_load_pcap_file(pcap_file_full_path)
            au1_packet = simulation.unisig_s98_packets[0]
            assert isinstance(au1_packet, decode_unisig_s98.UnisigS98Au1WiresharkPacket)
            au2_packet = simulation.unisig_s98_packets[1]
            assert isinstance(au2_packet, decode_unisig_s98.UnisigS98Au2WiresharkPacket)

            connexion_zc_pai = triple_des_s98.ConnectionUnisig98(
                secret_kmac_keys.authentication_key_kmac_1,
                secret_kmac_keys.authentication_key_kmac_2,
                secret_kmac_keys.authentication_key_kmac_3,
                au1_packet.calling_etcs_id,
                au1_packet.called_etcs_id,
                192,
                True,
            )
            connexion_zc_pai.start_session(au2_packet.random_number_a_ra.as_byte_array, au1_packet.random_number_b_rb.as_byte_array)
            computed_mac_as_byte_array = connexion_zc_pai.compute_input_mac_au2()
            ed_mac_as_string_of_hexas = triple_des_s98.convert_mac_to_string_of_hexas(computed_mac_as_byte_array)

            assert ed_mac_as_string_of_hexas == "35 f7 fa 7a 7b 6a d3 75"

        def test_compute_mac_pas_pai_dt_offset_answ_1(self) -> None:
            pcap_file_full_path = r"test\resources\unisig_s98\pas_1_pai_75_Au1_Au2_and_pai_pas_dt_OffsetAnsw1.pcapng"

            simulation = decode_unisig_s98.UnisigS98Simulation()
            simulation.build_unisig_s98_packets_from_load_pcap_file(pcap_file_full_path)

            au1_packet = simulation.unisig_s98_packets[0]
            assert isinstance(au1_packet, decode_unisig_s98.UnisigS98Au1WiresharkPacket)
            au2_packet = simulation.unisig_s98_packets[1]
            assert isinstance(au2_packet, decode_unisig_s98.UnisigS98Au2WiresharkPacket)

            connexion_zc_pai = triple_des_s98.ConnectionUnisig98(
                secret_kmac_keys.authentication_key_kmac_1,
                secret_kmac_keys.authentication_key_kmac_2,
                secret_kmac_keys.authentication_key_kmac_3,
                au1_packet.calling_etcs_id,
                au1_packet.called_etcs_id,
                192,
                True,
            )
            connexion_zc_pai.start_session(au2_packet.random_number_a_ra.as_byte_array, au1_packet.random_number_b_rb.as_byte_array)

            pas_pai_dt_offset_answ_1_packet = simulation.unisig_s98_packets[2]
            assert isinstance(pas_pai_dt_offset_answ_1_packet, decode_unisig_s98.UnisigS98DtDataWiresharkPacket)
            data_to_compute_mac = pas_pai_dt_offset_answ_1_packet.get_data_to_compute_mac()
            assert len(data_to_compute_mac.da_bytearray) == 3
            assert len(data_to_compute_mac.length_bytearray) == 2
            assert len(data_to_compute_mac.message_bytearray) == 20
            assert len(data_to_compute_mac.padding_bytearray) == 7

            computed_mac_as_byte_array = connexion_zc_pai.compute_mac_n_blocks(data_to_compute_mac.all_blocks_bytearray)
            ed_mac_as_string_of_hexas = triple_des_s98.convert_mac_to_string_of_hexas(computed_mac_as_byte_array)
            assert ed_mac_as_string_of_hexas == "e2 4f 14 ea f4 65 99 54"


class TestComputeMacFromManualData:

    def test_compute_mac_au2_from_bytearray(self) -> None:

        random_a_wshark: bytearray = bytearray([0x41, 0xB2, 0xF3, 0xE2, 0x4B, 0xA9, 0x9C, 0x20])
        random_b_wshark: bytearray = bytearray([0x37, 0x59, 0x47, 0xAA, 0xA4, 0xBF, 0x44, 0x97])

        etcs_id_initiateur: int = 2130068  # 20 80 94
        etcs_id_repondeur: int = 2130066  # 20 80 92

        connexion_zc_b_PAI75 = triple_des_s98.ConnectionUnisig98(
            secret_kmac_keys.authentication_key_kmac_1, secret_kmac_keys.authentication_key_kmac_2, secret_kmac_keys.authentication_key_kmac_3, etcs_id_initiateur, etcs_id_repondeur, 192, True
        )
        connexion_zc_b_PAI75.start_session(random_a_wshark, random_b_wshark)

        print("Compute AU2 Frame 116675	13:24:26,101385. Expected MAC: 35 f7 fa 7a 7b 6a d3 75 (Random Number A (RA): 41b2f3e24ba99c20, MAC: 35f7fa7a7b6ad375)")
        computed_mac_as_byte_array = connexion_zc_b_PAI75.compute_input_mac_au2()
        triple_des_s98.afficher_64bits(" MAC AU2 cnx1 --> ", computed_mac_as_byte_array)
        ed_mac_as_string_of_hexas = triple_des_s98.convert_mac_to_string_of_hexas(computed_mac_as_byte_array)
        assert ed_mac_as_string_of_hexas == "35 f7 fa 7a 7b 6a d3 75"
        pass

    def test_compute_mac_pas_pai_3_blocks_from_bytearray(self) -> None:
        random_a_wshark: bytearray = bytearray([0x41, 0xB2, 0xF3, 0xE2, 0x4B, 0xA9, 0x9C, 0x20])
        random_b_wshark: bytearray = bytearray([0x37, 0x59, 0x47, 0xAA, 0xA4, 0xBF, 0x44, 0x97])

        etcs_id_initiateur: int = 2130068  # 20 80 94
        etcs_id_repondeur: int = 2130066  # 20 80 92

        connexion_zc_b_PAI75 = triple_des_s98.ConnectionUnisig98(
            secret_kmac_keys.authentication_key_kmac_1, secret_kmac_keys.authentication_key_kmac_2, secret_kmac_keys.authentication_key_kmac_3, etcs_id_initiateur, etcs_id_repondeur, 192, True
        )
        connexion_zc_b_PAI75.start_session(random_a_wshark, random_b_wshark)

        print("Compute Frame 116789	13:24:28,084275, expected MAC 69 4c b0 e5 63 c6 d4 2c (Time Stamp at Last Msg Reception : 379564, MAC : 694cb0e563c6d42c")
        blocks_03: bytearray = bytearray([0x00, 0x13, 0x20, 0x80, 0x92, 0x0A, 0x03, 0x3D, 0xC2, 0x00, 0x05, 0xCA, 0xAC, 0x00, 0x16, 0x02, 0x42, 0x00, 0x05, 0xCA, 0xAC, 0x00, 0x00, 0x00])

        computed_mac_as_byte_array = connexion_zc_b_PAI75.compute_mac_n_blocks(blocks_03)
        ed_mac_as_string_of_hexas = triple_des_s98.convert_mac_to_string_of_hexas(computed_mac_as_byte_array)
        assert ed_mac_as_string_of_hexas == "69 4c b0 e5 63 c6 d4 2c"

    def test_compute_mac_pai_pas_4_blocks_from_bytearray(self) -> None:
        random_a_wshark: bytearray = bytearray([0x41, 0xB2, 0xF3, 0xE2, 0x4B, 0xA9, 0x9C, 0x20])
        random_b_wshark: bytearray = bytearray([0x37, 0x59, 0x47, 0xAA, 0xA4, 0xBF, 0x44, 0x97])

        etcs_id_initiateur: int = 2130068  # 20 80 94
        etcs_id_repondeur: int = 2130066  # 20 80 92

        connexion_zc_b_PAI75 = triple_des_s98.ConnectionUnisig98(
            secret_kmac_keys.authentication_key_kmac_1, secret_kmac_keys.authentication_key_kmac_2, secret_kmac_keys.authentication_key_kmac_3, etcs_id_initiateur, etcs_id_repondeur, 192, True
        )
        connexion_zc_b_PAI75.start_session(random_a_wshark, random_b_wshark)

        print("Compute Frame 116756	13:24:27,624244, expected MAC: e2 4f 14 ea f4 65 99 54 (MAC: e24f14eaf4659954, SAI User Data: 00000064), calcul à 4 blocs")
        blocks_04: bytearray = bytearray(
            [
                0x00,
                0x17,
                0x20,
                0x80,
                0x94,
                0x0B,
                0x02,
                0x00,
                0x00,
                0x00,
                0x16,
                0x02,
                0x42,
                0x00,
                0x05,
                0xCA,
                0x64,
                0x00,
                0x16,
                0x02,
                0x42,
                0x00,
                0x00,
                0x00,
                0x64,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
            ]
        )

        computed_mac_as_byte_array = connexion_zc_b_PAI75.compute_mac_n_blocks(blocks_04)
        ed_mac_as_string_of_hexas = triple_des_s98.convert_mac_to_string_of_hexas(computed_mac_as_byte_array)
        assert ed_mac_as_string_of_hexas == "e2 4f 14 ea f4 65 99 54"
