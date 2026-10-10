def byte_array_to_string_base_10(as_byte_array: bytearray) -> str:
    ret = ""
    for i in range(len(as_byte_array)):
        ret += f"{int(as_byte_array[i])}:"
    ret = ret[:-1]
    return ret


def byte_array_to_string_base_16(as_byte_array: bytearray) -> str:
    ret = ""
    for i in range(len(as_byte_array)):
        ret += f"{hex(int(as_byte_array[i]))[2:]}:"
    ret = ret[:-1]
    return ret
