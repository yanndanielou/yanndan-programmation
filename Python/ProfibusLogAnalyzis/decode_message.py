import xml.etree.ElementTree as ET


def hex_to_int(hex_string):
    """Convert a hex string to an integer."""
    return int(hex_string, 16)


def decode_message(hexadecimal_content: str, message_id: int) -> dict:
    # Open the corresponding XML file based on message_id
    xml_filename = f"D:/RIYL1/Data/Xml/MsgId{message_id}scheme.xml"

    # Load and parse the XML file
    tree = ET.parse(xml_filename)
    root = tree.getroot()

    # Split the hexadecimal string into bytes
    hex_bytes = hexadecimal_content.split()

    # Initialize a dictionary to store decoded fields
    decoded_fields = {}

    # Traverse through XML schema and decode each field
    for field in root.findall(".//Record/Field"):
        field_name = field.get("name")
        field_size = int(field.get("size"))  # Size in bytes
        field_type = field.get("type")

        # Extract the appropriate number of hex bytes for this field
        field_hex = hex_bytes[:field_size]
        hex_bytes = hex_bytes[field_size:]  # Remove processed bytes

        # Convert hex to field value
        if field_type == "int":
            field_value = hex_to_int("".join(field_hex))
        else:
            # Add other types if known, or default to raw hex
            field_value = "".join(field_hex)

        # Save the decoded field
        decoded_fields[field_name] = field_value

    return decoded_fields


# Example usage
hex_content = "00 0d 23 f2 00 00 8c a0 27 4a"
message_id = 85
decoded = decode_message(hex_content, message_id)
print(decoded)
