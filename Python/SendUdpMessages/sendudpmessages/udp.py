import socket

def send_udp_message(ip, port, hex_string):
    # Convert the hex string to bytes
    message = bytes.fromhex(hex_string)
    
    # Create a UDP socket
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        # Send the message to the specified IP and port
        sock.sendto(message, (ip, port))
        print(f"Message sent to {ip}:{port}")

# Example usage
ip_address = '192.168.1.100'    # Replace with the target IP
port_number = 12345             # Replace with the target port
hex_data = '48656c6c6f20554b'   # Replace with the hex string

send_udp_message(ip_address, port_number, hex_data)
