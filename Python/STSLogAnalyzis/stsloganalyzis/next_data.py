from logger import logger_config

from typing import Tuple, Optional, Dict, Set

from stsloganalyzis import (
    decode_action_set_content,
    decode_archive,
    decode_message,
    decode_xml_message,
    line_topology,
)


def get_line_topology() -> line_topology.Line:

    railway_line = line_topology.Line.load_from_csv(
        segments_csv_full_path=r"D:\NEXT\Data\Csv\NEXT_segment.csv",
        track_circuits_csv_full_path=r"D:\NEXT\Data\Csv\NEXT_track_circuit.csv",
        tracking_blocks_csv_full_path=r"D:\NEXT\Data\Csv\NEXT_tracking_block.csv",
        switches_csv_full_path=r"D:\NEXT\Data\Csv\NEXT_switch.csv",
        segments_relations_csv_full_path=r"D:\NEXTTS\Data\Csv\NEXT_tsSegmentRelation.csv",
        tracking_block_on_segments_csv_full_path=r"D:\NEXTTS\Data\Csv\NEXT_tsLocUnitTopo.csv",
        ignore_tracking_blocks_without_circuits=True,
    )
    assert railway_line
    return railway_line


def get_encoders() -> Tuple[line_topology.Line, decode_archive.ArchiveDecoder]:

    messages_list_csv_file_full_path = r"D:\NEXT\Data\Csv\NEXT_message.csv"
    xml_directory_path = r"D:\NEXT\Data\Xml"

    class NextSignedOrUnsignedTypeForIntegerFieldsManager(decode_xml_message.SignedOrUnsignedTypeForIntegerFieldsManagerBase):
        def __init__(self, signed_integer_fields_by_message_id_and_field_name: Optional[Dict[int, Set[str]]] = None) -> None:
            self.signed_integer_fields_by_message_id_and_field_name = signed_integer_fields_by_message_id_and_field_name or {}

        def get_decoding_type_for_field(
            self,
            message_number: int,
            field_name: str,
        ) -> decode_xml_message.SignedOrUnsignedTypeForIntegerFieldsManagerBase.TypeDecoding:
            if message_number == 101 and field_name in ["RestrEnd1Stationning", "RestrEnd2Stationning"]:
                return decode_xml_message.SignedOrUnsignedTypeForIntegerFieldsManagerBase.TypeDecoding.SIGNED
            if message_number == 94 and field_name in ["Stopping_Accuracy"]:
                return decode_xml_message.SignedOrUnsignedTypeForIntegerFieldsManagerBase.TypeDecoding.SIGNED_AND_UNSIGNED

            return decode_xml_message.SignedOrUnsignedTypeForIntegerFieldsManagerBase.TypeDecoding.UNSIGNED_ONLY

    message_manager = decode_message.InvariantMessagesManager(messages_list_csv_file_full_path=messages_list_csv_file_full_path)
    action_set_content_decoder = decode_action_set_content.ActionSetContentDecoder(csv_file_file_path=r"D:\NEXT\Data\Csv\ACTION_SET.csv")
    xml_message_decoder = decode_xml_message.XmlMessageDecoder(
        xml_directory_path=xml_directory_path, signed_or_unsigned_type_for_integer_fields_manager=NextSignedOrUnsignedTypeForIntegerFieldsManager()
    )

    railway_line = get_line_topology()

    archive_decoder = decode_archive.ArchiveDecoder(
        action_set_content_decoder=action_set_content_decoder,
        message_manager=message_manager,
        xml_message_decoder=xml_message_decoder,
        railway_line=railway_line,
    )

    return railway_line, archive_decoder
