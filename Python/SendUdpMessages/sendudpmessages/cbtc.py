import socket

from logger import logger_config
from sendudpmessages import udp


class CbtcSender:
    def __init__(self):
        self._bim: int = 0

    def send_pae_affcar_message(
        self, ip: str, port: int, counter_value: int, reverse_display_color: bool
    ):
        # Convert the hex string to bytes
        self._bim += 1
        if self._bim > 255:
            self._bim = 0

        bim_str = f"{self._bim:0>2X}".lower()
        counter_value_str = f"{counter_value:0>2X}".lower()
        reverse_display_color_str = "01" if reverse_display_color else "00"

        hex_string = (
            f"12{bim_str}0000671401044c0100000000{counter_value_str}{reverse_display_color_str}00"
        )
        # hex_data = "12890000671401044c0100000000090000"  # Replace with the hex string
        # udp.send_udp_message(ip=ip, port=port, hex_string=hex_data)

        udp.send_udp_message(ip=ip, port=port, hex_string=hex_string)
