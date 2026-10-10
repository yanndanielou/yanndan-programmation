from common import basic_encryption


def get_equipment_name_from_ip_address(raw_ip_address: str) -> str:

    if raw_ip_address == "10.241.26.85":
        return basic_encryption.decode_basic_encryption_string("MGP.Q86D2.QBT2.M3OBU")
    if raw_ip_address == "10.241.4.35":
        return basic_encryption.decode_basic_encryption_string("MGP.Q86D2.QBT2")
    if raw_ip_address == "10.241.26.1":
        return basic_encryption.decode_basic_encryption_string("MGP.Q86D2.NFJ")
    if raw_ip_address == "10.241.26.11":
        return basic_encryption.decode_basic_encryption_string("ITM.Q92D2.NFJ")
    assert False, f"Unknown equipment name for {raw_ip_address}"
