def encode_basic_encryption_string(input_string_to_encrypt: str) -> str:
    return encode_caesar_cipher_string(input_string_to_encrypt, 1)


def decode_basic_encryption_string(input_string_to_decrypt: str) -> str:
    return decode_caesar_cipher_string(input_string_to_decrypt, 1)


def encode_caesar_cipher_string(input_string_to_encrypt: str, offset: int) -> str:
    ret = ""
    for input_char in input_string_to_encrypt:
        as_char = ord(input_char)
        ret += chr(as_char + offset)
    assert isinstance(ret, str)
    return ret


def decode_caesar_cipher_string(input_string_to_decrypt: str, offset: int) -> str:
    return encode_caesar_cipher_string(input_string_to_decrypt, -offset)
