import pytest

from stsloganalyzis.unisig.s98 import triple_des_s98, secret_kmac_keys

random_a_wshark: bytearray = bytearray([0x41, 0xB2, 0xF3, 0xE2, 0x4B, 0xA9, 0x9C, 0x20])
random_b_wshark: bytearray = bytearray([0x37, 0x59, 0x47, 0xAA, 0xA4, 0xBF, 0x44, 0x97])

etcsid_initiateur: int = 2130068  # 20 80 94
etcsid_repondeur: int = 2130066  # 20 80 92


def test_au2_from_bytearray() -> None:

    connexion_ZcB_PAI75 = triple_des_s98.Connection_U98(secret_kmac_keys.Key1_TE, secret_kmac_keys.Key2_TE, secret_kmac_keys.Key3_TE, etcsid_initiateur, etcsid_repondeur, 192, True)
    connexion_ZcB_PAI75.start_session(random_a_wshark, random_b_wshark)

    print("Compute AU2 Frame 116675	13:24:26,101385. Expected MAC: 35 f7 fa 7a 7b 6a d3 75 (Random Number A (RA): 41b2f3e24ba99c20, MAC: 35f7fa7a7b6ad375)")
    computed_mac_as_byte_array = connexion_ZcB_PAI75.compute_input_mac_au2()
    triple_des_s98.afficher_64bits(" MAC AU2 cnx1 --> ", computed_mac_as_byte_array)
    computed_mac_as = triple_des_s98.convert_mac_to_string_of_hexas(computed_mac_as_byte_array)
    assert computed_mac_as == "35 f7 fa 7a 7b 6a d3 75"
    pass


def test_mac_pas_pai_3_blocks_from_bytearray() -> None:

    connexion_ZcB_PAI75 = triple_des_s98.Connection_U98(secret_kmac_keys.Key1_TE, secret_kmac_keys.Key2_TE, secret_kmac_keys.Key3_TE, etcsid_initiateur, etcsid_repondeur, 192, True)
    connexion_ZcB_PAI75.start_session(random_a_wshark, random_b_wshark)

    print("Compute Frame 116789	13:24:28,084275, expected MAC 69 4c b0 e5 63 c6 d4 2c (Time Stamp at Last Msg Reception : 379564, MAC : 694cb0e563c6d42c")
    blocks_03: bytearray = bytearray([0x00, 0x13, 0x20, 0x80, 0x92, 0x0A, 0x03, 0x3D, 0xC2, 0x00, 0x05, 0xCA, 0xAC, 0x00, 0x16, 0x02, 0x42, 0x00, 0x05, 0xCA, 0xAC, 0x00, 0x00, 0x00])

    computed_mac_as_byte_array = connexion_ZcB_PAI75.compute_mac_n_blocks(3, blocks_03)
    computed_mac_as = triple_des_s98.convert_mac_to_string_of_hexas(computed_mac_as_byte_array)
    assert computed_mac_as == "69 4c b0 e5 63 c6 d4 2c"


def test_mac_pai_pas_4_blocks_from_bytearray() -> None:

    connexion_ZcB_PAI75 = triple_des_s98.Connection_U98(secret_kmac_keys.Key1_TE, secret_kmac_keys.Key2_TE, secret_kmac_keys.Key3_TE, etcsid_initiateur, etcsid_repondeur, 192, True)
    connexion_ZcB_PAI75.start_session(random_a_wshark, random_b_wshark)

    print("Compute Frame 116756	13:24:27,624244, expected MAC: e2 4f 14 ea f4 65 99 54 (MAC: e24f14eaf4659954, SAI User Data: 00000064), calcul à 4 blocs")
    blocks_04: bytearray = bytearray(
        [0x00, 0x17, 0x20, 0x80, 0x94, 0x0B, 0x02, 0x00, 0x00, 0x00, 0x16, 0x02, 0x42, 0x00, 0x05, 0xCA, 0x64, 0x00, 0x16, 0x02, 0x42, 0x00, 0x00, 0x00, 0x64, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
    )

    computed_mac_as_byte_array = connexion_ZcB_PAI75.compute_mac_n_blocks(4, blocks_04)
    computed_mac_as = triple_des_s98.convert_mac_to_string_of_hexas(computed_mac_as_byte_array)
    assert computed_mac_as == "e2 4f 14 ea f4 65 99 54"
