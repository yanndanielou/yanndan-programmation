import pytest
from common import ip_address_utils

ip_generation_data = [
    ("239.192", "255.255.0.0", 13313, "239.192.52.1"),
    ("192.168.1", "255.255.255.0", 23, "192.168.1.23"),
]


@pytest.mark.parametrize("prefix,mask,number,expected", ip_generation_data)
def test_generate_ip_address(prefix: str, mask: str, number: int, expected: str) -> None:
    assert ip_address_utils.generate_ip_address(prefix=prefix, mask=mask, number=number) == expected
