"""Example module that performs addition"""

from logger import logger_config
from sendudpmessages import cbtc

import time


# Example usage
ip_address = "172.40.0.41"  # Replace with the target IP
port_number = 61440  # Replace with the target port


def send_during_one_second(
    cbtc_sender: cbtc.CbtcSender, counter_value: int, reverse_display_color: bool
) -> None:
    for i in range(1, 10):
        cbtc_sender.send_pae_affcar_message(
            ip=ip_address,
            port=port_number,
            counter_value=counter_value,
            reverse_display_color=reverse_display_color,
        )
        time.sleep(0.1)


def main() -> None:
    """Main function"""
    logger_config.configure_logger_with_random_log_file_suffix("sendudpmessages")

    cbtc_sender = cbtc.CbtcSender()
    send_during_one_second(cbtc_sender=cbtc_sender, counter_value=9, reverse_display_color=False)
    send_during_one_second(cbtc_sender=cbtc_sender, counter_value=9, reverse_display_color=False)
    send_during_one_second(cbtc_sender=cbtc_sender, counter_value=8, reverse_display_color=False)
    send_during_one_second(cbtc_sender=cbtc_sender, counter_value=7, reverse_display_color=False)
    send_during_one_second(cbtc_sender=cbtc_sender, counter_value=6, reverse_display_color=False)
    # send_during_one_second(cbtc_sender=cbtc_sender, counter_value=5, display_color=False)
    send_during_one_second(cbtc_sender=cbtc_sender, counter_value=5, reverse_display_color=True)
    send_during_one_second(cbtc_sender=cbtc_sender, counter_value=5, reverse_display_color=True)
    send_during_one_second(cbtc_sender=cbtc_sender, counter_value=5, reverse_display_color=True)
    send_during_one_second(cbtc_sender=cbtc_sender, counter_value=5, reverse_display_color=True)
    send_during_one_second(cbtc_sender=cbtc_sender, counter_value=5, reverse_display_color=True)
    send_during_one_second(cbtc_sender=cbtc_sender, counter_value=5, reverse_display_color=True)

    logger_config.print_and_log_info("End. Nominal end of application")


if __name__ == "__main__":
    # sys.argv[1:]
    main()
