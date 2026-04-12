from typing import List

import pytest

from stsloganalyzis import decode_xml_message

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
