import csv
import datetime
from dataclasses import dataclass
from typing import Dict, List, Optional, cast
from warnings import deprecated

from logger import logger_config

from stsloganalyzis.archive import (
    constants,
    decode_action_set_content,
    decode_next_specific_messages_content,
    decode_product_topology_dependant_messages_content,
    decode_specific_message_content,
    decode_xml_message,
    decode_zc_ats_tm_ao_sig_content,
    decode_zc_ats_tracking_status_vb_occupancy_content,
    decode_zc_ats_zc_ats_tracking_status_vb_te_content,
    decode_zc_ats_mal_content,
)
from stsloganalyzis.common import hlf
from stsloganalyzis.topology import (
    line_topology,
)
from stsloganalyzis.zone_controllers import virtual_canton_zc

# CONTENT_OF_FIELD_IN_CASE_OF_DECODING_ERROR = "!!! Decoding Error !!!"


@dataclass
class InvariantMessage:
    message_id: str
    message_number: int

    def __post_init__(self) -> None:
        assert isinstance(self.message_number, int)


class InvariantMessagesManager:
    def __init__(self, messages_list_csv_file_full_path: str) -> None:

        self.all_messages: List[InvariantMessage] = []
        self.all_messages_by_id: Dict[str, InvariantMessage] = dict()

        # Read the CSV file
        with open(messages_list_csv_file_full_path, mode="r", encoding="ANSI") as file:
            csv_reader = csv.DictReader(file, delimiter=";")

            # Iterate through each row in the CSV
            for csv_row in csv_reader:
                message_id: str = csv_row["ID"]
                message_number = int(csv_row["MESSAGE_INDEX"])
                message = InvariantMessage(message_id=message_id, message_number=message_number)
                self.all_messages.append(message)
                self.all_messages_by_id[message_id] = message

    def get_message_by_id(self, message_id: str) -> Optional[InvariantMessage]:
        return self.all_messages_by_id[message_id] if message_id in self.all_messages_by_id else None


class DecodedMessage:

    def __init__(self, message_number: int, xml_decoded_message: decode_xml_message.DecodedXmlMessage) -> None:
        self.message_number = message_number
        self.xml_decoded_message = xml_decoded_message
        self.decoded_fields_flat_directory: Dict[str, constants.FIELD_TYPE] = {}
        self.hlf_decoded: Optional[datetime.datetime] = None

    def get_field_value_human_readable(self, field_name: str) -> constants.HUMAN_READABLE_FIELD_TYPE:
        field_value_by_name = self.decoded_fields_flat_directory[field_name]
        assert field_value_by_name is not None

        if isinstance(field_value_by_name, list):
            human_value = "<" + ",".join([str(field_value_by_name) for field in field_value_by_name]) + ">"
            # logger_config.print_and_log_error(f"<Not supported field {field_name} of type {type(field_name)}")
            # return f"Not supported field {field_name} of type {type(field_name)}"
            return human_value

        return field_value_by_name


class HLFDecoderFromMessage:

    @staticmethod
    def decode_hlf(decoded_message: DecodedMessage) -> None:
        assert "Time" in decoded_message.decoded_fields_flat_directory, f"Not found among {decoded_message.decoded_fields_flat_directory.keys()}"
        time_field_value = cast(int, decoded_message.decoded_fields_flat_directory["Time"])
        time_offset_value = cast(int, decoded_message.decoded_fields_flat_directory["TimeOffset"])
        decade_field_value = cast(int, decoded_message.decoded_fields_flat_directory["Decade"])
        day_on_decade_field_value = cast(int, decoded_message.decoded_fields_flat_directory["DayOnDecade"])

        hlf_decoded = HLFDecoderFromMessage.decode_hlf_fields_to_datetime(time_field_value, time_offset_value, decade_field_value, day_on_decade_field_value)
        decoded_message.hlf_decoded = hlf_decoded

    @deprecated("use HLF module instead")
    @staticmethod
    def decode_hlf_fields_to_datetime(time_field_value: int, time_offset_value: int, decade_field_value: int, day_on_decade_field_value: int) -> datetime.datetime:
        return hlf.decode_hlf_to_datetime(
            time_field_value=time_field_value, time_offset_value=time_offset_value, decade_field_value=decade_field_value, day_on_decade_field_value=day_on_decade_field_value
        )


class MessageDecoder:
    def __init__(
        self,
        xml_message_decoder: decode_xml_message.XmlMessageDecoder,
        action_set_content_decoder: Optional[decode_action_set_content.ActionSetContentDecoder],
        zc_ats_tm_ao_sig_content_decoder: Optional[decode_zc_ats_tm_ao_sig_content.ZcAtsTmAoSigDecoder],
        virtual_canton_zc_library: Optional[virtual_canton_zc.VirtualCantonZcLibrary],
        railway_line: Optional[line_topology.Line] = None,
    ) -> None:
        self.xml_message_decoder = xml_message_decoder
        self.action_set_content_decoder = action_set_content_decoder
        self.zc_ats_mal_message_decoder = decode_zc_ats_mal_content.ZcAtsMalDecoder(railway_line=railway_line) if railway_line else None
        self.cc_ats_tracking_message_decoder = decode_product_topology_dependant_messages_content.CcAtsTrackingMessageDecoder(railway_line=railway_line) if railway_line else None
        self.zc_ats_tm_ao_sig_content_decoder = zc_ats_tm_ao_sig_content_decoder
        self.ats_cc_specific_remote_control_message_decoder = decode_next_specific_messages_content.AtsCcSpecificRemoteControlMessageDecoder(railway_line=railway_line) if railway_line else None
        self.cc_ats_rs_operation_message_decoder = decode_next_specific_messages_content.CcAtsRsOperationMessageDecoder(railway_line=railway_line) if railway_line else None
        self.cc_ats_specific_operation_message_decoder = decode_next_specific_messages_content.CcAtsSpecificOperationMessageDecoder(railway_line=railway_line) if railway_line else None
        self.zc_ats_tracking_status_vb_occ_decoder = (
            decode_zc_ats_tracking_status_vb_occupancy_content.ZcAtsTrackingStatusVbOccDecoder(virtual_canton_zc_library=virtual_canton_zc_library) if virtual_canton_zc_library else None
        )
        self.zc_ats_zc_ats_tracking_status_vb_te_decoder = (
            decode_zc_ats_zc_ats_tracking_status_vb_te_content.ZcAtsTrackingStatusVBTeDecoder(virtual_canton_zc_library=virtual_canton_zc_library) if virtual_canton_zc_library else None
        )

    def decode_raw_hexadecimal_message(
        self,
        message_number: int,
        hexadecimal_content: str,
        equipment_name: str,
        also_decode_additional_fields_in_specific_messages: bool = True,
    ) -> Optional[DecodedMessage]:
        xml_decoded_message = self.xml_message_decoder.decode_xml_fields_in_message_hexadecimal(message_number=message_number, hexadecimal_content=hexadecimal_content)
        assert xml_decoded_message
        decoded_message = None
        if xml_decoded_message:
            decoded_message = DecodedMessage(message_number=message_number, xml_decoded_message=xml_decoded_message)
            decoded_message.decoded_fields_flat_directory.update(xml_decoded_message.decoded_fields_flat_directory)
            if also_decode_additional_fields_in_specific_messages:
                self.decode_additional_fields_in_specific_messages(decoded_message=decoded_message, equipment_name=equipment_name)

            also_decode_hlf: bool = "Time" in decoded_message.decoded_fields_flat_directory

            if also_decode_hlf:
                HLFDecoderFromMessage.decode_hlf(decoded_message=decoded_message)

        return decoded_message

    def decode_additional_fields_in_specific_messages(
        self,
        decoded_message: DecodedMessage,
        equipment_name: str,
    ) -> None:
        decoded: Optional[decode_specific_message_content.SpecificMessageContentDecoded] = None
        try:
            if decoded_message.message_number == decode_action_set_content.ATS_CC_ACTION_SET_MESSAGE_ID and self.action_set_content_decoder:
                decoded = self.action_set_content_decoder.decode(decoded_message=decoded_message)
            elif decoded_message.message_number == decode_zc_ats_tm_ao_sig_content.PAS_ATS_TM_AO_SIG_MESSAGE_ID and self.zc_ats_tm_ao_sig_content_decoder:
                decoded = self.zc_ats_tm_ao_sig_content_decoder.decode(decoded_message=decoded_message, equipment_name=equipment_name)
            elif decoded_message.message_number == decode_zc_ats_tracking_status_vb_occupancy_content.PAS_ATS_TRACKING_STATUS_VB_OCCUPANCY_MESSAGE_ID and self.zc_ats_tracking_status_vb_occ_decoder:
                decoded = self.zc_ats_tracking_status_vb_occ_decoder.decode(decoded_message=decoded_message, equipment_name=equipment_name)
            elif decoded_message.message_number == decode_zc_ats_zc_ats_tracking_status_vb_te_content.ZC_ATS_TRACKING_STATUS_VB_TE_MESSAGE_ID and self.zc_ats_zc_ats_tracking_status_vb_te_decoder:
                decoded = self.zc_ats_zc_ats_tracking_status_vb_te_decoder.decode(decoded_message=decoded_message, equipment_name=equipment_name)
            elif decoded_message.message_number == decode_product_topology_dependant_messages_content.ZC_ATS_MAL_MESSAGE_ID and self.zc_ats_mal_message_decoder:
                decoded = self.zc_ats_mal_message_decoder.decode(decoded_message=decoded_message)
            elif decoded_message.message_number == decode_product_topology_dependant_messages_content.CC_ATS_TRACKING_MESSAGE_ID and self.cc_ats_tracking_message_decoder:
                decoded = self.cc_ats_tracking_message_decoder.decode(decoded_message=decoded_message)
            elif decoded_message.message_number == decode_next_specific_messages_content.CC_ATS_SPE_OPERATION_MESSAGE_ID___disabled and self.cc_ats_specific_operation_message_decoder:
                decoded = self.cc_ats_specific_operation_message_decoder.decode(decoded_message=decoded_message)
            elif decoded_message.message_number == decode_next_specific_messages_content.CC_ATS_SPE_RS_OPERATION_MESSAGE_ID and self.cc_ats_rs_operation_message_decoder:
                decoded = self.cc_ats_rs_operation_message_decoder.decode(decoded_message=decoded_message)
            elif decoded_message.message_number == decode_next_specific_messages_content.ATS_CC_SPE_RC_MESSAGE_ID and self.ats_cc_specific_remote_control_message_decoder:
                decoded = self.ats_cc_specific_remote_control_message_decoder.decode(decoded_message=decoded_message)

            if decoded:
                decoded_message.decoded_fields_flat_directory.update(decoded.fields_with_value)
        except AssertionError as err:
            logger_config.print_and_log_exception(err)
