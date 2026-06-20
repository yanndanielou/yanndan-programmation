from stsloganalyzis.archive import decode_xml_message

# fmt: off

def test_decode_message_101_rc_type_6()->None:

    hexa_content_as_str = "06 10 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00"
    xml_message_decoder = decode_xml_message.XmlMessageDecoder(xml_directory_path=r"D:\NEXT\Data\Xml")
    decoded_message = xml_message_decoder.decode_xml_fields_in_message_hexadecimal(message_number=101, hexadecimal_content=hexa_content_as_str)
    assert decoded_message
    assert "RestrEnd1SegId" not in  decoded_message.all_fields_by_name
    assert "RestrEnd1SegId_0" not in  decoded_message.all_fields_by_name

def test_decode_message_101_rc_type_4()->None: 

    hexa_content_as_str = "04 10 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00"
    xml_message_decoder = decode_xml_message.XmlMessageDecoder(xml_directory_path=r"D:\NEXT\Data\Xml")
    decoded_message = xml_message_decoder.decode_xml_fields_in_message_hexadecimal(message_number=101, hexadecimal_content=hexa_content_as_str)
    assert decoded_message
    assert "RestrEnd1SegId"  in  decoded_message.all_fields_by_name
    assert "RestrEnd1SegId_0" not in  decoded_message.all_fields_by_name

def test_decode_message_210()->None: 
    hexa_content_as_str="00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 41 04 10 41 04 00 00 00 00 01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 43 3C 00 01 19 40 29 38"
    xml_message_decoder = decode_xml_message.XmlMessageDecoder(xml_directory_path=r"D:\NEXT\Data\Xml")
    decoded_message = xml_message_decoder.decode_xml_fields_in_message_hexadecimal(message_number=210, hexadecimal_content=hexa_content_as_str) 
    assert decoded_message.decoded_bytes_message.is_correctly_and_completely_decoded(), f"{decoded_message.decoded_bytes_message.number_of_bits_remaining_to_decode} remaing bits to decode"
    assert decoded_message
    assert "VBOccupancyTrain_0"  in  decoded_message.decoded_fields_flat_directory
    assert "VBOccupancyTrain_1"  in  decoded_message.decoded_fields_flat_directory
    assert "VBOccupancyTrain_2"  in  decoded_message.decoded_fields_flat_directory
    assert "VBOccupancyTrain_3"  in  decoded_message.decoded_fields_flat_directory
