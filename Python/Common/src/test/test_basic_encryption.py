# -*-coding:Utf-8 -*

import pytest
import os

from src.common import basic_encryption


@pytest.mark.parametrize(
    "input_string",
    [
        "no fix change",
        "not/A/bug",
        "not-A-bug",
        "Change, internal",
        "Affected package is not installed.",
        "N/A (Change Request)",
        "pas de FA ",
        "Non examiné ",
        "Non examiné",
    ],
)
def test_basic_encryption_decryption(input_string: str) -> None:

    encoded_string = basic_encryption.encode_basic_encryption_string(input_string)
    decoded_string = basic_encryption.decode_basic_encryption_string(encoded_string)
    assert decoded_string == input_string
