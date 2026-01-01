import pytest
from common import ip_address_utils

ip_generation_data = [
    ("239.192", "255.255.0.0", 13313, "239.192.52.1"),
    ("192.168.1", "255.255.255.0", 23, "192.168.1.23"),
    ("10.10.0", "255.255.0.0", 10, "10.10.0.10"),
    ("10.10.0", "255.255.255.0", 10, "10.10.0.10"),
]


@pytest.mark.parametrize(
    "prefix,mask,number,expected",
    [
        ("239.192", "255.255.0.0", 13313, "239.192.52.1"),
        ("192.168.1", "255.255.255.0", 23, "192.168.1.23"),
        ("10.10.0", "255.255.0.0", 10, "10.10.0.10"),
        ("10.10.0", "255.255.255.0", 10, "10.10.0.10"),
    ],
)
def test_generate_ip_address(prefix: str, mask: str, number: int, expected: str) -> None:
    assert ip_address_utils.generate_ip_address(prefix=prefix, mask=mask, number=number) == expected


@pytest.mark.parametrize(
    "subnet_prefix,number,expected_generated_ip",
    [
        ("239.192", 13313, "239.192.52.1"),
        ("239.192", 13549, "239.192.52.237"),
        ("239.192", 13568, "239.192.53.0"),
    ],
)
def test_generate_16_mask_ip_address(subnet_prefix: str, number: int, expected_generated_ip: str) -> None:
    assert ip_address_utils.generate_16_mask_ip_address(number=number, subnet_prefix=subnet_prefix) == expected_generated_ip
