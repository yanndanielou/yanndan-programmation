import socket

from logger import logger_config


def send_udp_message(ip: str, port: int, hex_string: str):
    # Convert the hex string to bytes
    logger_config.print_and_log_info(f"send_udp_message hex_string {hex_string} to {ip}:{port}")
    message = bytes.fromhex(hex_string)

    # Create a UDP socket
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        # Send the message to the specified IP and port
        sock.sendto(message, (ip, port))
        logger_config.print_and_log_info(f"Message {hex_string} sent to {ip}:{port}")
