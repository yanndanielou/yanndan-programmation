import xml.etree.ElementTree as ET


def hex_to_int(hex_string):
    """Convert a hex string to an integer."""
    return int(hex_string, 16)


def extract_bits(data, start_bit, bit_length):
    """Extract a specific number of bits starting at a given bit index from a list of bytes."""
    start_byte = start_bit // 8
    end_bit = start_bit + bit_length
    end_byte = (end_bit + 7) // 8

    # Get the relevant bytes
    relevant_bytes = data[start_byte:end_byte]
    combined_bits = "".join(f"{byte:08b}" for byte in relevant_bytes)

    # Extract the substring of the combined bits and convert to an integer
    bit_segment = combined_bits[start_bit % 8 : start_bit % 8 + bit_length]
    return int(bit_segment, 2)


def parse_record(record, hex_string, current_bit_index=0):
    """Recursively parse records to decode fields."""
    decoded_fields = {}
    hex_bytes = bytes.fromhex(hex_string.replace(" ", ""))

    for element in record:
        if element.tag == "record" or element.tag == "layer":
            # Recursive call to process nested records
            nested_fields, current_bit_index = parse_record(element, hex_string, current_bit_index)
            decoded_fields.update(nested_fields)
        elif element.tag == "field":
            field_name = element.get("id")
            field_size_bits = int(element.get("size", 0))  # Bits

            field_value = extract_bits(hex_bytes, current_bit_index, field_size_bits)
            current_bit_index += field_size_bits
            field_type = element.get("class")

            if field_type == "int":
                decoded_fields[field_name] = field_value
            else:
                # Handle other types as needed, or store raw bit value
                decoded_fields[field_name] = field_value

            # Debugging print statement
            print(f"Decoded {field_name} ({field_type}): {field_value}")
            # Save the decoded field
            decoded_fields[field_name] = field_value

    return decoded_fields, hex_bytes


def decode_message(hexadecimal_content: str, message_id: int) -> dict:
    # Open the corresponding XML file based on message_id
    xml_filename = f"D:/RIYL1/Data/Xml/MsgId{message_id}scheme.xml"

    try:
        # Load and parse the XML file
        tree = ET.parse(xml_filename)
        root = tree.getroot()
    except FileNotFoundError:
        print(f"File {xml_filename} not found.")
        return {}

    # Debugging print statement
    print(f"XML parsed: Root tag - {root.tag}")

    # Traverse the root record and decode
    decoded_fields, _ = parse_record(root, hexadecimal_content)

    # Final debug statement
    print(f"Decoded fields: {decoded_fields}")

    return decoded_fields


# Example usage
hex_content = "00 0d 23 f2 00 00 8c a0 27 4a"
message_id = 85
decoded = decode_message(hex_content, message_id)
print(decoded)
