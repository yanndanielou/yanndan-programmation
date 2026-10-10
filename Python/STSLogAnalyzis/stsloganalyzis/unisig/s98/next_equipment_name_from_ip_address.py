from common import basic_encryption


def get_equipment_name_from_ip_address(raw_ip_address: str) -> str:

    ret = f"Unknown equipment name for {raw_ip_address}"

    if raw_ip_address == basic_encryption.decode_basic_encryption_string("21/352/37/96"):
        ret = basic_encryption.decode_basic_encryption_string("MGP.Q86D2.QBT2.M3OBU")
    elif raw_ip_address == basic_encryption.decode_basic_encryption_string("21/352/5/46"):
        ret = basic_encryption.decode_basic_encryption_string("MGP.Q86D2.QBT2")
    elif raw_ip_address == basic_encryption.decode_basic_encryption_string("21/352/37/2"):
        ret = basic_encryption.decode_basic_encryption_string("MGP.Q86D2.NFJ")
    elif raw_ip_address == basic_encryption.decode_basic_encryption_string("21/352/37/22"):
        ret = basic_encryption.decode_basic_encryption_string("ITM.Q92D2.NFJ")

    return ret
