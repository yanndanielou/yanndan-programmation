import re
from collections import OrderedDict, defaultdict
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import cast

from common import file_name_utils, file_utils, reports_utils, string_utils
from logger import logger_config

from stsloganalyzis.unisig import upper_layer_libraries
from stsloganalyzis.unisig.s5758 import decode_unisig_s57_s58

EARLIEST_VALID_PPN_LOG_TIMESTAMP = datetime(year=2000, month=1, day=1)


class SendingMode(Enum):
    SDA = "SDA"
    SDN = "SDN"


@dataclass
class ServiceAccessPoint:
    number: int
    name: str


@dataclass
class PpnConnectionSession:
    left_to_right_interlocutors_without_arrow_description: str

    @dataclass
    class SessionInterlocutor:
        random_number_representing_sequence_number_byte_1_of_4: int
        random_number_representing_sequence_number_byte_2_of_4: int
        random_number_representing_sequence_number_byte_3_of_4: int
        random_number_representing_sequence_number_byte_4_of_4: int
        address: int
        sap: int
        session: "PpnConnectionSession"

        def update_lowest_order_byte_sequence_number(self, lowest_order_byte_sequence_number: int) -> str | None:
            """Returns none or error description"""

            error = (
                f"{self.session.left_to_right_interlocutors_without_arrow_description}: non continuous sequence. From {self.random_number_representing_sequence_number_byte_1_of_4} to {lowest_order_byte_sequence_number}"
                if lowest_order_byte_sequence_number != self.random_number_representing_sequence_number_byte_1_of_4 + 1
                and lowest_order_byte_sequence_number != 0
                and self.random_number_representing_sequence_number_byte_1_of_4 != 255
                else None
            )
            if self.random_number_representing_sequence_number_byte_1_of_4 > lowest_order_byte_sequence_number:
                # logger_config.print_and_log_info(
                #    f"{self.session.left_to_right_interlocutors_without_arrow_description}: overflow of lower order byte sequence number from {self.random_number_representing_sequence_number_byte_1_of_4} to {lowest_order_byte_sequence_number}",
                #    do_not_print=True,
                # )

                self.random_number_representing_sequence_number_byte_2_of_4 += 1
                if self.random_number_representing_sequence_number_byte_2_of_4 == 256:
                    self.random_number_representing_sequence_number_byte_2_of_4 = 0
                    logger_config.print_and_log_info(f"{self.session.left_to_right_interlocutors_without_arrow_description}: overflow of new_random_number_representing_sequence_number_byte_2_of_4")

                    self.random_number_representing_sequence_number_byte_3_of_4 += 1
                    if self.random_number_representing_sequence_number_byte_3_of_4 == 256:
                        self.random_number_representing_sequence_number_byte_3_of_4 = 0
                        logger_config.print_and_log_info(f"{self.session.left_to_right_interlocutors_without_arrow_description}: overflow of random_number_representing_sequence_number_byte_3_of_4")

                        self.random_number_representing_sequence_number_byte_4_of_4 += 1
                        if self.random_number_representing_sequence_number_byte_4_of_4 == 256:
                            self.random_number_representing_sequence_number_byte_4_of_4 = 0
                            logger_config.print_and_log_info(
                                f"{self.session.left_to_right_interlocutors_without_arrow_description}: overflow of random_number_representing_sequence_number_byte_4_of_4"
                            )

            self.random_number_representing_sequence_number_byte_1_of_4 = lowest_order_byte_sequence_number

            return error

    def __post_init__(self) -> None:
        self.last_step = PpnConnectionSession.Step.CONNECT_REQUEST_RECEIVED
        self.connection_initiator: PpnConnectionSession.SessionInterlocutor | None = None
        self.connection_responder: PpnConnectionSession.SessionInterlocutor | None = None

    def get_interlocutor_by_address(self, address: int) -> "PpnConnectionSession.SessionInterlocutor | None":
        for interlocutor in [self.connection_initiator, self.connection_responder]:
            if interlocutor and interlocutor.address == address:
                return interlocutor
        return None

    def register_connect_request_telegram(self, connect_request_telegram: decode_unisig_s57_s58.SdaConnectRequestOrConfirmTelegram) -> None:
        if connect_request_telegram.profibus_log_line:
            self.connection_initiator = PpnConnectionSession.SessionInterlocutor(
                session=self,
                address=connect_request_telegram.profibus_log_line.source_address,
                sap=connect_request_telegram.profibus_log_line.source_sap,
                random_number_representing_sequence_number_byte_1_of_4=connect_request_telegram.random_number_representing_sequence_number_byte_1_of_4,
                random_number_representing_sequence_number_byte_2_of_4=connect_request_telegram.random_number_representing_sequence_number_byte_2_of_4,
                random_number_representing_sequence_number_byte_3_of_4=connect_request_telegram.random_number_representing_sequence_number_byte_3_of_4,
                random_number_representing_sequence_number_byte_4_of_4=connect_request_telegram.random_number_representing_sequence_number_byte_4_of_4,
            )

        self.last_step = PpnConnectionSession.Step.CONNECT_CONFIRM_RECEIVED

    def register_connect_confirm_telegram(self, connect_confirm_telegram: decode_unisig_s57_s58.SdaConnectRequestOrConfirmTelegram) -> None:
        if connect_confirm_telegram.profibus_log_line:
            self.connection_responder = PpnConnectionSession.SessionInterlocutor(
                session=self,
                address=connect_confirm_telegram.profibus_log_line.source_address,
                sap=connect_confirm_telegram.profibus_log_line.source_sap,
                random_number_representing_sequence_number_byte_1_of_4=connect_confirm_telegram.random_number_representing_sequence_number_byte_1_of_4,
                random_number_representing_sequence_number_byte_2_of_4=connect_confirm_telegram.random_number_representing_sequence_number_byte_2_of_4,
                random_number_representing_sequence_number_byte_3_of_4=connect_confirm_telegram.random_number_representing_sequence_number_byte_3_of_4,
                random_number_representing_sequence_number_byte_4_of_4=connect_confirm_telegram.random_number_representing_sequence_number_byte_4_of_4,
            )

        self.last_step = PpnConnectionSession.Step.CONNECT_CONFIRM_RECEIVED

    def register_disconnect_telegram(self, _: decode_unisig_s57_s58.SdaDisconnectTelegram) -> None:
        self.last_step = PpnConnectionSession.Step.DISCONNECT_RECEIVED

    class Step(Enum):
        CONNECT_REQUEST_RECEIVED = "CONNECT_REQUEST_RECEIVED"
        CONNECT_CONFIRM_RECEIVED = "CONNECT_CONFIRM_RECEIVED"
        DISCONNECT_RECEIVED = "DISCONNECT_RECEIVED"


class PpnConnectionsLibrary:

    def __init__(self) -> None:
        self.all_ppn_connections_sessions: list[PpnConnectionSession] = []
        self.current_ppn_connections_by_source_and_target_addresses: dict[tuple[tuple[int, int], tuple[int, int]], PpnConnectionSession] = {}

    def get_current_connection_by_source_and_target_addresses(self, source_address: int, source_sap: int, target_address: int, target_sap: int) -> PpnConnectionSession | None:
        existing_connection_found = self.current_ppn_connections_by_source_and_target_addresses.get(((source_address, source_sap), (target_address, target_sap)))
        if existing_connection_found:
            return existing_connection_found
        return None

    def register_connect_request_telegram(self, connect_request_telegram: decode_unisig_s57_s58.SdaConnectRequestOrConfirmTelegram) -> None:
        assert connect_request_telegram.profibus_log_line
        connection = PpnConnectionSession(connect_request_telegram.profibus_log_line.interlocutors_with_translation_without_direction)
        connection.register_connect_request_telegram(connect_request_telegram)
        self.all_ppn_connections_sessions.append(connection)
        self.current_ppn_connections_by_source_and_target_addresses[
            (
                (connect_request_telegram.profibus_log_line.source_address, connect_request_telegram.profibus_log_line.source_sap),
                (connect_request_telegram.profibus_log_line.target_address, connect_request_telegram.profibus_log_line.target_sap),
            )
        ] = connection

    def register_connect_confirm_telegram(self, connect_confirm_telegram: decode_unisig_s57_s58.SdaConnectRequestOrConfirmTelegram) -> None:
        assert connect_confirm_telegram.profibus_log_line
        connection = self.get_existing_current_connection_by_profibus_log_line(connect_confirm_telegram.profibus_log_line)
        if not connection:
            logger_config.print_and_log_error(f"Connect confirm telegram {connect_confirm_telegram} without previous connect telegram")
            connection = PpnConnectionSession(connect_confirm_telegram.profibus_log_line.interlocutors_with_translation_without_direction)
            connection.register_connect_confirm_telegram(connect_confirm_telegram)
            self.all_ppn_connections_sessions.append(connection)
            self.current_ppn_connections_by_source_and_target_addresses[
                (
                    (connect_confirm_telegram.profibus_log_line.source_address, connect_confirm_telegram.profibus_log_line.source_sap),
                    (connect_confirm_telegram.profibus_log_line.target_address, connect_confirm_telegram.profibus_log_line.target_sap),
                )
            ] = connection
            self.current_ppn_connections_by_source_and_target_addresses[
                (
                    (connect_confirm_telegram.profibus_log_line.target_address, connect_confirm_telegram.profibus_log_line.target_sap),
                    (connect_confirm_telegram.profibus_log_line.source_address, connect_confirm_telegram.profibus_log_line.source_sap),
                )
            ] = connection

        connection.register_connect_confirm_telegram(connect_confirm_telegram)

    def register_disconnect_telegram(self, disconnect_telegram: decode_unisig_s57_s58.SdaDisconnectTelegram) -> None:
        assert disconnect_telegram.profibus_log_line
        connection = self.get_existing_current_connection_by_profibus_log_line(disconnect_telegram.profibus_log_line)
        if not connection or not connection.connection_initiator or not connection.connection_responder:
            logger_config.print_and_log_warning(
                f"No connection found before disconnect telegram at {disconnect_telegram.profibus_log_line.timestamp} in {disconnect_telegram.profibus_log_line.file_path} line  {disconnect_telegram.profibus_log_line.line_number} between {disconnect_telegram.profibus_log_line.source_name} and {disconnect_telegram.profibus_log_line.target_name}"
            )
            return
        connection.register_disconnect_telegram(disconnect_telegram)
        self.current_ppn_connections_by_source_and_target_addresses.pop(
            ((connection.connection_initiator.address, connection.connection_initiator.sap), (connection.connection_responder.address, connection.connection_responder.sap)), None
        )
        self.current_ppn_connections_by_source_and_target_addresses.pop(
            ((connection.connection_responder.address, connection.connection_responder.sap), (connection.connection_initiator.address, connection.connection_initiator.sap)), None
        )

    def get_existing_current_connection_by_profibus_log_line(self, profibus_log_line: "ProfibusLogLine") -> PpnConnectionSession | None:
        existing_connection_found = self.get_current_connection_by_source_and_target_addresses(
            profibus_log_line.source_address, profibus_log_line.source_sap, profibus_log_line.target_address, profibus_log_line.target_sap
        )
        if existing_connection_found:
            return existing_connection_found
        return self.get_current_connection_by_source_and_target_addresses(
            profibus_log_line.target_address, profibus_log_line.target_sap, profibus_log_line.source_address, profibus_log_line.source_sap
        )


@dataclass
class ProfibusLogLibrary:
    all_ppn_logs_paths: list[str]
    label: str
    upper_layer_decoding_library: upper_layer_libraries.UpperLayerDecodingLibrary | None = None

    @classmethod
    def from_directory(
        cls,
        directory_path: str,
        filename_pattern: str = "profibus*",
        label: str | None = None,
        upper_layer_decoding_library: upper_layer_libraries.UpperLayerDecodingLibrary | None = None,
    ) -> "ProfibusLogLibrary":
        all_ppn_logs_paths = file_utils.get_files_by_directory_and_file_name_mask(
            directory_path=directory_path,
            file_sort_order=file_utils.FileSortOrder.TIMESTAMP_OLDER_TO_NEWER,
            filename_pattern=filename_pattern,
        )
        if label is None:
            label = file_name_utils.get_directory_name_from_directory_full_path(directory_path)
        return ProfibusLogLibrary(
            all_ppn_logs_paths=all_ppn_logs_paths,
            label=label,
            upper_layer_decoding_library=upper_layer_decoding_library,
        )

    @classmethod
    def from_file_full_path(
        cls,
        ppn_log_full_path: str,
        label: str | None = None,
        upper_layer_decoding_library: upper_layer_libraries.UpperLayerDecodingLibrary | None = None,
    ) -> "ProfibusLogLibrary":
        if label is None:
            label = file_name_utils.get_file_name_with_extension_from_full_path(ppn_log_full_path)
        return ProfibusLogLibrary(
            all_ppn_logs_paths=[ppn_log_full_path],
            label=label,
            upper_layer_decoding_library=upper_layer_decoding_library,
        )

    def __post_init__(self) -> None:

        self.ppn_connections_library = PpnConnectionsLibrary()

        if self.upper_layer_decoding_library is None:
            self.upper_layer_decoding_library = upper_layer_libraries.UpperLayerDecodingLibrary.from_next_json_file_full_path(
                json_file_full_path=r"D:\temp\GenTel\0.1-0-Original_Edition\GenTel\rom\unisig_s58.json"
            )

        self.decoded_files: list[ProfibusLogFile] = []
        self.decoded_files_sorted_by_line_timestamp: list[ProfibusLogFile] = []
        self.decoded_lines: list[ProfibusLogLine] = []
        for ppn_log_path in self.all_ppn_logs_paths:
            decoded_file = ProfibusLogFile(
                file_full_path=ppn_log_path,
                upper_layer_decoding_library=self.upper_layer_decoding_library,
            )
            self.decoded_files.append(decoded_file)

        self._process_files()
        self._decode_sdn_or_sda()

        self.all_unisig_messages = [log_line.unisig_message for decoded_file in self.decoded_files for log_line in decoded_file.decoded_lines if log_line.unisig_message is not None]
        self.all_sda_unisig_messages = [
            log_line.unisig_message
            for decoded_file in self.decoded_files
            for log_line in decoded_file.decoded_lines
            if log_line.unisig_message is not None and isinstance(log_line.unisig_message, decode_unisig_s57_s58.OnboardSdaUnisigMessage)
        ]

        self.all_upper_layer_telegram = [upper_layer_telegram for upper_layer_telegram in self.all_unisig_messages if isinstance(upper_layer_telegram, decode_unisig_s57_s58.SdaForUpperLayerTelegram)]
        self.all_sl4_upper_layer_telegram = [
            upper_layer_telegram
            for upper_layer_telegram in self.all_unisig_messages
            if isinstance(upper_layer_telegram, decode_unisig_s57_s58.SdaForUpperLayerTelegram)
            and upper_layer_telegram.command_type == decode_unisig_s57_s58.OnboardSdaUnisigMessage.CommandTypeSubset57.SL4_TELEGRAM_FOR_UPPER_LAYER
        ]
        # [unisig_message for log_line in self.decoded_lines for unisig_message in log_line.unisig_messages]
        self.all_upper_layer_stms = [stm_message for upper_layer_telegram in self.all_upper_layer_telegram for stm_message in upper_layer_telegram.upper_layer_decoded_stms]

        self.sdn_sync_and_reference_time_messages = [
            sync_and_reference_time_message
            for sync_and_reference_time_message in self.all_unisig_messages
            if isinstance(sync_and_reference_time_message, decode_unisig_s57_s58.SdnSyncAndReferenceTimeMulticastMessage)
        ]

        self.sdn_safe_time_layer_startup_messages = [
            sync_and_reference_time_message
            for sync_and_reference_time_message in self.all_unisig_messages
            if isinstance(sync_and_reference_time_message, decode_unisig_s57_s58.SdnSafeTimeLayerStartupForMulticast)
        ]

        self.unisig_messages_errors = [error for unisig_message in self.all_unisig_messages for error in unisig_message.creational_and_decoding_errors]
        self.stm_messages_errors = [error for stm_message in self.all_upper_layer_stms for error in stm_message.creational_and_decoding_errors]
        self.all_creational_errors = self.unisig_messages_errors + self.stm_messages_errors

        self.all_interlocutors = {log_line.interlocutors_with_translation_without_direction for log_line in self.decoded_lines}

        self.compute_errors_stats()
        self._print_stats()
        self._recalculate_all_crcs()
        self.save_errors()

    def get_upper_layer_stms_by_stm_ids(self, allowed_stm_ids: list[int]) -> list[decode_unisig_s57_s58.UpperLayerStm]:
        return [upper_layer_stm for upper_layer_stm in self.all_upper_layer_stms if upper_layer_stm.nid_stm in allowed_stm_ids]

    def save_upper_layer_stms_by_stm_ids(self, allowed_stm_ids: list[int], label: str = "") -> None:
        interesting_stm_messages = self.get_upper_layer_stms_by_stm_ids(allowed_stm_ids)
        self.save_selected_stm_messages(
            interesting_stm_messages,
            file_base_name=f"{self.label} {label} stm messages {' '.join(str(interesting_stm_id) for interesting_stm_id in allowed_stm_ids)}",
        )

    def save_all_usual_reports(self) -> None:

        self.save_all_stm_messages_with_bad_crc()
        self.save_sdn_safe_time_layer_startup_messages()
        self.save_sdn_sync_and_reference_time_messages()
        self.save_all_stm_messages_with_errors()

        self.save_all_unisig_messages_that_have_context_to_compute_crc()
        self.save_all_unisig_messages_with_bad_crc()

        self.save_all_sda_messages_with_timestamp()
        self.save_all_stm_messages()
        self.save_all_unisig_messages()
        self.save_stm_messages_for_each_interlocutor()

    @logger_config.stopwatch_decorator(monitor_ram_usage=True)
    def save_all_sda_messages_with_timestamp(self) -> None:

        self.save_selected_unisig_messages(
            file_base_name=f"{self.label} SDA messages with timestamp",
            selected_unisig_messages=[
                unisig_message for unisig_message in self.all_unisig_messages if isinstance(unisig_message, decode_unisig_s57_s58.OnboardSdaUnisigMessage) and unisig_message.stl_time_stamp is not None
            ],
        )

    @logger_config.stopwatch_decorator(monitor_ram_usage=True)
    def save_stm_messages_for_each_interlocutor(self) -> None:
        for interlocutors in self.all_interlocutors:
            self.save_selected_stm_messages(
                interesting_stm_messages=[
                    interesting_stm_message
                    for interesting_stm_message in self.all_upper_layer_stms
                    if interesting_stm_message.upper_layer_telegram.profibus_log_line
                    and interesting_stm_message.upper_layer_telegram.profibus_log_line.interlocutors_with_translation_without_direction == interlocutors
                ],
                file_base_name=string_utils.format_filename(f"{self.label} {interlocutors}"),
            )

    @logger_config.stopwatch_decorator(monitor_ram_usage=True)
    def save_all_stm_messages_with_errors(self) -> None:
        self.save_selected_stm_messages(
            [stm_message for stm_message in self.all_upper_layer_stms if stm_message.creational_and_decoding_errors or stm_message.upper_layer_telegram.creational_and_decoding_errors],
            file_base_name=f"{self.label} all STM messages with errors",
        )

    @logger_config.stopwatch_decorator(monitor_ram_usage=True)
    def save_all_stm_messages_with_bad_crc(self) -> None:
        self.save_selected_stm_messages(
            [stm_message for stm_message in self.all_upper_layer_stms if stm_message.upper_layer_telegram.recomputed_crc_and_transmitted_crc_are_equals == False],
            file_base_name=f"{self.label} all STM messages with bad crc",
        )

    @logger_config.stopwatch_decorator(monitor_ram_usage=True)
    def save_all_stm_messages(self) -> None:
        self.save_selected_stm_messages(self.all_upper_layer_stms, file_base_name=f"{self.label} all STM messages")

    @logger_config.stopwatch_decorator(monitor_ram_usage=True)
    def save_selected_stm_messages(self, interesting_stm_messages: list[decode_unisig_s57_s58.UpperLayerStm], file_base_name: str) -> None:
        logger_config.print_and_log_info(f"save_selected_stm_messages {len(interesting_stm_messages)} STM messages to {file_base_name}")

        reports_utils.save_rows_to_output_files(
            rows_as_list_dict=[
                OrderedDict(
                    {
                        "timestamp": interesting_stm_message.upper_layer_telegram.profibus_log_line.timestamp if interesting_stm_message.upper_layer_telegram.profibus_log_line else None,
                        "Line Source": interesting_stm_message.upper_layer_telegram.profibus_log_line.source_name if interesting_stm_message.upper_layer_telegram.profibus_log_line else None,
                        "Line Target": interesting_stm_message.upper_layer_telegram.profibus_log_line.target_name if interesting_stm_message.upper_layer_telegram.profibus_log_line else None,
                        "interlocutors": (
                            interesting_stm_message.upper_layer_telegram.profibus_log_line.interlocutors_with_translation_without_direction
                            if interesting_stm_message.upper_layer_telegram.profibus_log_line
                            else None
                        ),
                        "Line Mode": interesting_stm_message.upper_layer_telegram.profibus_log_line.mode.name if interesting_stm_message.upper_layer_telegram.profibus_log_line else None,
                        "Line length": interesting_stm_message.upper_layer_telegram.profibus_log_line.length if interesting_stm_message.upper_layer_telegram.profibus_log_line else None,
                        "file path": interesting_stm_message.upper_layer_telegram.profibus_log_line.file_path if interesting_stm_message.upper_layer_telegram.profibus_log_line else None,
                        "line number": interesting_stm_message.upper_layer_telegram.profibus_log_line.line_number if interesting_stm_message.upper_layer_telegram.profibus_log_line else None,
                        "nid stm": interesting_stm_message.nid_stm,
                        "message type": interesting_stm_message.upper_layer_telegram.__class__.__name__,
                        "stm l_message": interesting_stm_message.l_message,
                        "stm data_without_header_size_in_bits": interesting_stm_message.data_without_header_size_in_bits,
                        "Number of errors (only this STM message)": len(interesting_stm_message.creational_and_decoding_errors),
                        "Number of errors (unisig message)": len(interesting_stm_message.upper_layer_telegram.creational_and_decoding_errors),
                        "Number of errors (STM + unisig message)": len(
                            interesting_stm_message.upper_layer_telegram.creational_and_decoding_errors + interesting_stm_message.upper_layer_telegram.creational_and_decoding_errors
                        ),
                        "STM messages decoded in this line": ",".join([str(stm_message.nid_stm) for stm_message in interesting_stm_message.upper_layer_telegram.upper_layer_decoded_stms]),
                        "lowest_order_byte_sequence_number": interesting_stm_message.upper_layer_telegram.lowest_order_byte_sequence_number,
                        "Unisig message: all_data_aka_net_data": (
                            interesting_stm_message.upper_layer_telegram.all_data_aka_net_data.as_base_16 if interesting_stm_message.upper_layer_telegram.all_data_aka_net_data else None
                        ),
                        "Transmitted CRC": interesting_stm_message.upper_layer_telegram.crc.as_base_16_str if interesting_stm_message.upper_layer_telegram.crc else None,
                        "Recomputed CRC: base 16": (
                            interesting_stm_message.upper_layer_telegram.recomputed_crc.as_base_16_str if interesting_stm_message.upper_layer_telegram.recomputed_crc else None
                        ),
                        "Recomputed CRC: all_data_for_checksum_computation_base_16": (
                            interesting_stm_message.upper_layer_telegram.recomputed_crc.all_data_for_checksum_computation_base_16
                            if interesting_stm_message.upper_layer_telegram.recomputed_crc
                            else None
                        ),
                        "Recomputed CRC: explanations_for_debug": (
                            interesting_stm_message.upper_layer_telegram.recomputed_crc.explanations_for_debug if interesting_stm_message.upper_layer_telegram.recomputed_crc else None
                        ),
                        "recomputed_crc_and_transmitted_crc_are_equals": interesting_stm_message.upper_layer_telegram.recomputed_crc_and_transmitted_crc_are_equals,
                        "Safe time layer timestamp (ms)": interesting_stm_message.upper_layer_telegram.stl_time_stamp.in_ms if interesting_stm_message.upper_layer_telegram.stl_time_stamp else None,
                        "Safe time layer timestamp (human_format)": (
                            interesting_stm_message.upper_layer_telegram.stl_time_stamp.human_format if interesting_stm_message.upper_layer_telegram.stl_time_stamp else None
                        ),
                        "STM message: number remaining bits to decode": interesting_stm_message.number_remaining_undecoded_bits,
                        "STM message: remaining bits to decode": interesting_stm_message.remaining_undecoded_bits,
                        "log line: number remaining bits to decode": interesting_stm_message.upper_layer_telegram.number_remaining_undecoded_bits,
                        "log line: remaining bits to decode": interesting_stm_message.upper_layer_telegram.remaining_undecoded_bits,
                        "STM message errors": interesting_stm_message.creational_and_decoding_errors,
                        "Unisig message errors": interesting_stm_message.upper_layer_telegram.creational_and_decoding_errors,
                        "All errors (STM message + unisig message)": interesting_stm_message.creational_and_decoding_errors
                        + interesting_stm_message.upper_layer_telegram.creational_and_decoding_errors,
                        **{field_name: field_value for field_name, field_value in interesting_stm_message.fields_names_and_values.items()},
                    }
                )
                for interesting_stm_message in interesting_stm_messages
            ],
            file_base_name=file_base_name,
            create_csv_file=False,
            create_txt_file=False,
            split_big_files=False,
            chunk_size=200000,
        )

    @logger_config.stopwatch_decorator(monitor_ram_usage=True)
    def save_sdn_sync_and_reference_time_messages(self) -> None:

        reports_utils.save_rows_to_output_files(
            rows_as_list_dict=[
                OrderedDict(
                    {
                        "timestamp": sdn_sync_and_reference_time_message.profibus_log_line.timestamp if sdn_sync_and_reference_time_message.profibus_log_line else None,
                        "Line Source": sdn_sync_and_reference_time_message.profibus_log_line.source_name if sdn_sync_and_reference_time_message.profibus_log_line else None,
                        "Line Target": sdn_sync_and_reference_time_message.profibus_log_line.target_name if sdn_sync_and_reference_time_message.profibus_log_line else None,
                        "interlocutors": (
                            sdn_sync_and_reference_time_message.profibus_log_line.interlocutors_with_translation_without_direction if sdn_sync_and_reference_time_message.profibus_log_line else None
                        ),
                        "Line length": sdn_sync_and_reference_time_message.profibus_log_line.length if sdn_sync_and_reference_time_message.profibus_log_line else None,
                        "file path": sdn_sync_and_reference_time_message.profibus_log_line.file_path if sdn_sync_and_reference_time_message.profibus_log_line else None,
                        "line number": sdn_sync_and_reference_time_message.profibus_log_line.line_number if sdn_sync_and_reference_time_message.profibus_log_line else None,
                        "header sequence_number": sdn_sync_and_reference_time_message.header.sequence_number,
                        "reference_sync_n": sdn_sync_and_reference_time_message.reference_sync_n.value_as_int,
                        "reference_time_n_minus_1_bytes_reordered_in_ms": sdn_sync_and_reference_time_message.reference_time_n_minus_1_utc.in_ms,
                        "reference_time_n_minus_1_bytes_reordered": sdn_sync_and_reference_time_message.reference_time_n_minus_1_utc.human_format,
                        "Number of errors (unisig message)": len(sdn_sync_and_reference_time_message.creational_and_decoding_errors),
                        "Transmitted CRC": sdn_sync_and_reference_time_message.crc.as_base_16_str if sdn_sync_and_reference_time_message.crc else None,
                    }
                )
                for sdn_sync_and_reference_time_message in self.sdn_sync_and_reference_time_messages
            ],
            file_base_name=f"{self.label} all sdn_sync_and_reference_time_messages",
            create_csv_file=False,
            create_txt_file=False,
            split_big_files=False,
            chunk_size=200000,
        )

    @logger_config.stopwatch_decorator(monitor_ram_usage=True)
    def save_sdn_safe_time_layer_startup_messages(self) -> None:

        reports_utils.save_rows_to_output_files(
            rows_as_list_dict=[
                OrderedDict(
                    {
                        "timestamp": sdn_safe_time_layer_startup_message.profibus_log_line.timestamp if sdn_safe_time_layer_startup_message.profibus_log_line else None,
                        "Line Source": sdn_safe_time_layer_startup_message.profibus_log_line.source_name if sdn_safe_time_layer_startup_message.profibus_log_line else None,
                        "Line Target": sdn_safe_time_layer_startup_message.profibus_log_line.target_name if sdn_safe_time_layer_startup_message.profibus_log_line else None,
                        "interlocutors": (
                            sdn_safe_time_layer_startup_message.profibus_log_line.interlocutors_with_translation_without_direction if sdn_safe_time_layer_startup_message.profibus_log_line else None
                        ),
                        "Line length": sdn_safe_time_layer_startup_message.profibus_log_line.length if sdn_safe_time_layer_startup_message.profibus_log_line else None,
                        "file path": sdn_safe_time_layer_startup_message.profibus_log_line.file_path if sdn_safe_time_layer_startup_message.profibus_log_line else None,
                        "line number": sdn_safe_time_layer_startup_message.profibus_log_line.line_number if sdn_safe_time_layer_startup_message.profibus_log_line else None,
                        "header sequence_number": sdn_safe_time_layer_startup_message.header.sequence_number,
                        "configuration_data_prefix_x": sdn_safe_time_layer_startup_message.configuration_data_prefix_x,
                        "configuration_data_prefix_y": sdn_safe_time_layer_startup_message.configuration_data_prefix_y,
                        "configuration_data_prefix_z": sdn_safe_time_layer_startup_message.configuration_data_prefix_z,
                        "sender_dynamic_transfer_time": sdn_safe_time_layer_startup_message.sender_dynamic_transfer_time.human_format,
                        "sender_static_transfer_time": sdn_safe_time_layer_startup_message.sender_static_transfer_time.human_format,
                        "remaining_undecoded_bits": sdn_safe_time_layer_startup_message.remaining_undecoded_bits,
                        "number_remaining_undecoded_bits": sdn_safe_time_layer_startup_message.number_remaining_undecoded_bits,
                        "Number of errors (unisig message)": len(sdn_safe_time_layer_startup_message.creational_and_decoding_errors),
                        "Transmitted CRC": sdn_safe_time_layer_startup_message.crc.as_base_16_str if sdn_safe_time_layer_startup_message.crc else None,
                    }
                )
                for sdn_safe_time_layer_startup_message in self.sdn_safe_time_layer_startup_messages
            ],
            file_base_name=f"{self.label} all sdn_sync_and_reference_time_messages",
            create_csv_file=False,
            create_txt_file=False,
            split_big_files=False,
            chunk_size=200000,
        )

    @logger_config.stopwatch_decorator(monitor_ram_usage=True)
    def save_all_unisig_messages(self) -> None:
        logger_config.print_and_log_info(f"save_all_unisig_messages {len(self.all_unisig_messages)} unisig messages")
        self.save_selected_unisig_messages(
            selected_unisig_messages=self.all_unisig_messages,
            file_base_name=f"{self.label} all unisig messages",
        )

    @logger_config.stopwatch_decorator()
    def save_all_unisig_messages_that_have_context_to_compute_crc(self) -> None:
        self.save_selected_unisig_messages(
            selected_unisig_messages=[unisig_message for unisig_message in self.all_unisig_messages if unisig_message.recomputed_crc_and_transmitted_crc_are_equals is not None],
            file_base_name=f"{self.label} all unisig messages that have context to compute crc",
        )

    @logger_config.stopwatch_decorator()
    def save_all_unisig_messages_with_bad_crc(self) -> None:
        self.save_selected_unisig_messages(
            selected_unisig_messages=[unisig_message for unisig_message in self.all_unisig_messages if unisig_message.recomputed_crc_and_transmitted_crc_are_equals == False],
            file_base_name=f"{self.label} all unisig messages with bad crc",
        )

    def save_selected_unisig_messages(self, selected_unisig_messages: list[decode_unisig_s57_s58.OnboardUnisigMessage], file_base_name: str) -> None:
        with logger_config.stopwatch_with_label(f"save_selected_unisig_messages {len(self.all_unisig_messages)} unisig messages", monitor_ram_usage=True, inform_beginning=True):

            reports_utils.save_rows_to_output_files(
                rows_as_list_dict=[
                    OrderedDict(
                        {
                            "timestamp": unisig_message.profibus_log_line.timestamp if unisig_message.profibus_log_line else None,
                            "Line Source": unisig_message.profibus_log_line.source_name if unisig_message.profibus_log_line else None,
                            "Line Target": unisig_message.profibus_log_line.target_name if unisig_message.profibus_log_line else None,
                            "interlocutors": unisig_message.profibus_log_line.interlocutors_with_translation_without_direction if unisig_message.profibus_log_line else None,
                            "Line Mode": unisig_message.profibus_log_line.mode.name if unisig_message.profibus_log_line else None,
                            "Line length": unisig_message.profibus_log_line.length if unisig_message.profibus_log_line else None,
                            "file path": unisig_message.profibus_log_line.file_path if unisig_message.profibus_log_line else None,
                            "line number": unisig_message.profibus_log_line.line_number if unisig_message.profibus_log_line else None,
                            "duration since previous line": unisig_message.profibus_log_line.excessive_duration_since_previous_line if unisig_message.profibus_log_line else None,
                            "excessive duration since previous line": unisig_message.profibus_log_line.excessive_duration_since_previous_line if unisig_message.profibus_log_line else None,
                            "message type": unisig_message.__class__.__name__,
                            "Unisig message: all_data_aka_net_data": (
                                unisig_message.all_data_aka_net_data.as_base_16
                                if isinstance(unisig_message, decode_unisig_s57_s58.OnboardSdaUnisigMessage) and unisig_message.all_data_aka_net_data
                                else None
                            ),
                            "Number of errors": len(unisig_message.creational_and_decoding_errors),
                            "lowest_order_byte_sequence_number": (
                                unisig_message.lowest_order_byte_sequence_number if isinstance(unisig_message, decode_unisig_s57_s58.OnboardSdaUnisigMessage) else None
                            ),
                            "Transmitted CRC": unisig_message.crc.as_base_16_str if isinstance(unisig_message, decode_unisig_s57_s58.OnboardSdaUnisigMessage) and unisig_message.crc else None,
                            "recomputed_crc_and_transmitted_crc_are_equals": unisig_message.recomputed_crc_and_transmitted_crc_are_equals,
                            "Recomputed CRC (base 16)": unisig_message.recomputed_crc.as_base_16_str if unisig_message.recomputed_crc else None,
                            "Data to compute CRC (base 16)": unisig_message.recomputed_crc.all_data_for_checksum_computation_base_16 if unisig_message.recomputed_crc else None,
                            "Recomputed CRC: explanations_for_debug": unisig_message.recomputed_crc.explanations_for_debug if unisig_message.recomputed_crc else None,
                            "Safe time layer timestamp (ms)": (
                                unisig_message.stl_time_stamp.in_ms if isinstance(unisig_message, decode_unisig_s57_s58.OnboardSdaUnisigMessage) and unisig_message.stl_time_stamp else None
                            ),
                            "Safe time layer timestamp (human_format)": (
                                unisig_message.stl_time_stamp.human_format if isinstance(unisig_message, decode_unisig_s57_s58.OnboardSdaUnisigMessage) and unisig_message.stl_time_stamp else None
                            ),
                            "errors": unisig_message.creational_and_decoding_errors,
                        }
                    )
                    for unisig_message in selected_unisig_messages
                ],
                file_base_name=file_base_name,
                create_csv_file=False,
                create_txt_file=False,
                split_big_files=False,
                chunk_size=200000,
            )

    @logger_config.stopwatch_decorator()
    def _process_files(self) -> None:

        for decoded_file in self.decoded_files:
            with logger_config.stopwatch_with_label(f"{self.label} Process {decoded_file.file_name_with_extension}", monitor_ram_usage=True):
                decoded_file.process()

        files_sorted_by_earlieast_timestamp = sorted(self.decoded_files, key=lambda file: file.earliest_line_timestamp_except_bad_timestamp)
        files_sorted_by_latest_timestamp = sorted(self.decoded_files, key=lambda file: file.latest_valid_line_timestamp)

        logger_config.print_and_log_error_if(
            files_sorted_by_earlieast_timestamp != files_sorted_by_latest_timestamp,
            f"{self.label} Sorting files by earliest date {[file.file_name_with_extension for file in files_sorted_by_earlieast_timestamp]} is not equal to sorting files by latest date {[file.file_name_with_extension for file in files_sorted_by_latest_timestamp]}",
        )
        if files_sorted_by_earlieast_timestamp == files_sorted_by_latest_timestamp and files_sorted_by_earlieast_timestamp != self.decoded_files:
            logger_config.print_and_log_warning(
                f"{self.label} Sorting files by modification date {[file.file_name_with_extension for file in self.decoded_files]} is not equal to sorting files by earliest and latest date {[file.file_name_with_extension for file in files_sorted_by_latest_timestamp]}"
            )
            logger_config.print_and_log_info(f"{self.label} New files sorting : {[file.file_name_with_extension for file in self.decoded_files]}")
            self.decoded_files = files_sorted_by_earlieast_timestamp

    @logger_config.stopwatch_decorator()
    def _decode_sdn_or_sda(self) -> None:
        for decoded_file in self.decoded_files:
            with logger_config.stopwatch_with_label(f"{self.label} Decode SDN or SDA for {len(decoded_file.decoded_lines)} lines of {decoded_file.file_name_with_extension}", monitor_ram_usage=True):
                for decoded_line in decoded_file.decoded_lines:
                    logger_config.print_and_log_info_if(
                        decoded_line.line_number and decoded_line.line_number % 50000 == 0,
                        f"{self.label} {decoded_line.line_number}/{len(decoded_file.decoded_lines)} ({round(cast(int,decoded_line.line_number)/len(decoded_file.decoded_lines)*100,2)}%) lines decoded SDA/SDN in {decoded_file.file_name_with_extension}",
                        print_ram_usage=True,
                    )
                    decoded_line.decode_sdn_or_sda(self.ppn_connections_library)

    def compute_errors_stats(self) -> None:
        self.occurences_by_creational_error_type: dict[str, list[datetime | None]] = defaultdict(list)

        for unisig_message in self.all_unisig_messages:
            for error in unisig_message.creational_and_decoding_errors:
                self.occurences_by_creational_error_type[error].append(unisig_message.profibus_log_line.timestamp if unisig_message.profibus_log_line else None)

        for stm_message in self.all_upper_layer_stms:
            for error in stm_message.creational_and_decoding_errors:
                self.occurences_by_creational_error_type[error].append(stm_message.upper_layer_telegram.profibus_log_line.timestamp if stm_message.upper_layer_telegram.profibus_log_line else None)

    def _print_stats(self) -> None:
        logger_config.print_and_log_info(f"Stats of {self.label}")
        logger_config.print_and_log_info(f"{len(self.decoded_files)} files")
        logger_config.print_and_log_info(f"{len([log_line for log_file in self.decoded_files for log_line in log_file.decoded_lines])} lines")
        logger_config.print_and_log_info(f"{len(self.all_unisig_messages)} unisig_messages")
        logger_config.print_and_log_info(f"{len(self.all_upper_layer_telegram)} upper layer telegrams")
        logger_config.print_and_log_info(f"{len(self.all_sl4_upper_layer_telegram)} SL4 upper layer telegrams")
        logger_config.print_and_log_info(f"{len(self.all_upper_layer_stms)} STM messages founds")

        logger_config.print_and_log_info(f"{len(self.all_creational_errors)} creational errors")

        number_of_types_of_errors = len(self.occurences_by_creational_error_type.items())
        logger_config.print_and_log_error_if(number_of_types_of_errors, f"{number_of_types_of_errors}: types of errors")

        number_of_errors_occurences = sum([len(values) for values in self.occurences_by_creational_error_type.values()])
        logger_config.print_and_log_error_if(number_of_errors_occurences, f"{number_of_errors_occurences}: errors occurences")

    @logger_config.stopwatch_decorator(monitor_ram_usage=True, inform_beginning=True)
    def _recalculate_all_crcs(self) -> None:

        sda_unisig_messages_to_compute_crc = [unisig_message for unisig_message in self.all_sda_unisig_messages if unisig_message.can_src_be_computed()]
        logger_config.print_and_log_info(f"Recompute CRC of {len(sda_unisig_messages_to_compute_crc)}/{len(self.all_sda_unisig_messages)} SDA messages")
        for sda_unisig_message_index, sda_unisig_message_to_compute_crc in enumerate(sda_unisig_messages_to_compute_crc):
            logger_config.print_and_log_info_if(sda_unisig_message_index + 1 % 1000 == 0, f"{sda_unisig_message_index}/{len(sda_unisig_messages_to_compute_crc)} CRC computed")
            try:
                sda_unisig_message_to_compute_crc.prepare_data_and_recompute_crc()
            except AssertionError as ass_err:
                logger_config.print_and_log_exception(ass_err)
                logger_config.print_and_log_info(
                    f"Could not compute CRC of {sda_unisig_message_to_compute_crc.command_type} {sda_unisig_message_to_compute_crc.profibus_log_line.file_path if sda_unisig_message_to_compute_crc.profibus_log_line else 'NA'}:{sda_unisig_message_to_compute_crc.profibus_log_line.line_number if sda_unisig_message_to_compute_crc.profibus_log_line else 'NA'}"
                )

        for file in self.decoded_files:
            recomputed_crc_and_transmitted_crc_comparison_result: dict[bool | None, int] = defaultdict(int)

            for unisig_message in file.unisig_messages:
                recomputed_crc_and_transmitted_crc_comparison_result[unisig_message.recomputed_crc_and_transmitted_crc_are_equals] += 1

            logger_config.print_and_log_info(f"Statistics of CRC recomputed in {file.file_full_path}: {recomputed_crc_and_transmitted_crc_comparison_result}")
            pass

    @logger_config.stopwatch_decorator(monitor_ram_usage=True)
    def save_errors(self) -> None:

        reports_utils.save_rows_to_output_files(
            rows_as_list_dict=[
                OrderedDict(
                    {
                        "Error": error,
                        "Number occurences": len(all_timestamps),
                    }
                )
                for error, all_timestamps in self.occurences_by_creational_error_type.items()
            ],
            file_base_name=f"{self.label} all errors",
            create_csv_file=False,
            create_txt_file=False,
            split_big_files=False,
        )


@dataclass
class ProfibusLogFile:
    file_full_path: str
    encoding: str = "utf-8"
    upper_layer_decoding_library: upper_layer_libraries.UpperLayerDecodingLibrary | None = None

    def __post_init__(self) -> None:
        self.decoded_lines: list[ProfibusLogLine] = []
        self._lines_with_valid_timestamp_sorted_by_timestamp: list[ProfibusLogLine] = []
        if self.upper_layer_decoding_library is None:
            self.upper_layer_decoding_library = upper_layer_libraries.UpperLayerDecodingLibrary.from_next_json_file_full_path(
                json_file_full_path=r"D:\temp\GenTel\0.1-0-Original_Edition\GenTel\rom\unisig_s58.json"
            )
        self.file_name_with_extension = file_name_utils.get_file_name_with_extension_from_full_path(self.file_full_path)

    @property
    def lines_with_valid_timestamp_sorted_by_timestamp(self) -> list["ProfibusLogLine"]:
        return sorted(
            [decoded_line_with_valid_timestamp for decoded_line_with_valid_timestamp in self.decoded_lines if decoded_line_with_valid_timestamp.timestamp >= EARLIEST_VALID_PPN_LOG_TIMESTAMP],
            key=lambda state: state.timestamp,
        )

    @property
    def earliest_line_timestamp_except_bad_timestamp(self) -> datetime:
        assert self.decoded_lines
        earliest_valid_line = self.lines_with_valid_timestamp_sorted_by_timestamp[0]
        ret = earliest_valid_line.timestamp
        logger_config.print_and_log_info(f"File {self.file_full_path}: earliest timestamp is {ret}")
        return ret

    @property
    def latest_valid_line_timestamp(self) -> datetime:
        assert self.decoded_lines
        earliest_valid_line = self.lines_with_valid_timestamp_sorted_by_timestamp[-1]
        ret = earliest_valid_line.timestamp
        logger_config.print_and_log_info(f"File {self.file_full_path}: latest timestamp is {ret}")
        return ret

    def process(self, library: ProfibusLogLibrary | None = None) -> None:

        with logger_config.stopwatch_with_label(f"Process {self.file_full_path}", monitor_ram_usage=True, inform_beginning=True) and open(self.file_full_path, "r", encoding=self.encoding) as f:
            lines = f.readlines()
            for line_number, line in enumerate(lines):
                try:
                    decoded_line = ProfibusLogLine.from_raw_log_line(
                        line=line,
                        upper_layer_decoding_library=self.upper_layer_decoding_library,
                        file_path=self.file_full_path,
                        line_number=line_number + 1,
                        previous_line_timestamp=library.decoded_lines[-1].timestamp if library and library.decoded_lines else self.decoded_lines[-1].timestamp if self.decoded_lines else None,
                    )
                    if decoded_line is not None:
                        self.decoded_lines.append(decoded_line)
                        if library:
                            library.decoded_lines.append(decoded_line)

                except ValueError as val_err:
                    logger_config.print_and_log_exception(val_err)
                    logger_config.print_and_log_error(f"Could not decode line {line} in file {self.file_full_path} line {line_number+1}")

    @property
    def unisig_messages(self) -> list[decode_unisig_s57_s58.OnboardUnisigMessage]:
        return [log_line.unisig_message for log_line in self.decoded_lines if log_line.unisig_message is not None]


@dataclass
class ProfibusLogLine:
    timestamp: datetime
    source_name: str
    target_name: str
    source_address: int
    target_address: int
    source_sap: int
    target_sap: int
    raw_interlocutors: str
    raw_interlocutors_without_direction: str
    interlocutors_with_translation: str
    interlocutors_with_translation_without_direction: str
    sequence: int
    mode: SendingMode
    length: int
    bytes_hexa_str: str
    upper_layer_decoding_library: upper_layer_libraries.UpperLayerDecodingLibrary
    file_path: str | None
    line_number: int | None
    previous_line_timestamp: datetime | None

    def __str__(self) -> str:
        return f"At {self.timestamp} between {self.interlocutors_with_translation_without_direction} in {self.file_path}:{self.line_number} ({(self.previous_line_timestamp-self.timestamp).total_seconds if self.previous_line_timestamp else 'NA'} since previous line)"

    def __post_init__(self) -> None:
        self.unisig_message: decode_unisig_s57_s58.OnboardUnisigMessage | None = None
        self.duration_since_previous_line_absolute_value = (
            max(self.previous_line_timestamp, self.timestamp) - min(self.previous_line_timestamp, self.timestamp) if self.previous_line_timestamp is not None else None
        )
        self.duration_since_previous_line = self.timestamp - self.previous_line_timestamp if self.previous_line_timestamp is not None else None
        self.excessive_duration_since_previous_line = self.duration_since_previous_line_absolute_value.total_seconds > 120 if self.duration_since_previous_line_absolute_value is not None else None

    @staticmethod
    def get_equipment_name_from_address(address: int) -> str:

        equipment_name_dictionnary_by_sap = {
            2: "EVC",
            3: "JRU",
            5: "DMI",
            99: "STM NExT",
            127: "MCast",
        }

        return equipment_name_dictionnary_by_sap.get(address) or f"Unknown {address}"

    @staticmethod
    def get_function_name_from_sap(sap: int) -> str:
        function_name_dictionnary_by_sap = {
            2: "/JD",
            4: "/CH 1",
            10: "/CH 1",
            32: "/Time",
            33: "/STM control",
            37: "/Train",
            38: "/Break",
            39: "/Odometer",
            44: "/CH 1 derog",
        }

        return function_name_dictionnary_by_sap.get(sap) or f"Unknown {sap}"

    @staticmethod
    def from_raw_log_line(
        line: str,
        upper_layer_decoding_library: upper_layer_libraries.UpperLayerDecodingLibrary | None = None,
        file_path: str | None = None,
        line_number: int | None = None,
        previous_line_timestamp: datetime | None = None,
    ) -> "ProfibusLogLine|None":
        if upper_layer_decoding_library is None:
            upper_layer_decoding_library = upper_layer_libraries.UpperLayerDecodingLibrary.from_next_json_file_full_path(
                json_file_full_path=r"D:\temp\GenTel\0.1-0-Original_Edition\GenTel\rom\unisig_s58.json"
            )

        line = line.lstrip("\x00")

        line = line.strip()

        fields = line.split(" ")
        if len(fields) <= 4:
            print(f"-> bad line format\n{line}")
            return None

        # Extract time: 1970-01-01 02:18:14:652
        timestamp = datetime.strptime(f"{fields[0]} {fields[1]}", "%Y-%m-%d %H:%M:%S:%f")

        # Extract source and target: [99:37 <= 2:37]
        sap_pattern = re.compile(r"\[(\d+):(\d+) (<=|=>) (\d+):(\d+)\]")
        match = sap_pattern.search(line)
        if match:

            left_part_address = int(match.group(1))
            left_part_sap = int(match.group(2))

            left_part_with_translation = (
                f"{ProfibusLogLine.get_equipment_name_from_address(left_part_address)}/{ProfibusLogLine.get_function_name_from_sap(left_part_sap)}({left_part_address}:{left_part_sap})"
            )

            right_part_address = int(match.group(4))
            right_part_sap = int(match.group(5))

            right_part_with_translation = (
                f"{ProfibusLogLine.get_equipment_name_from_address(right_part_address)}/{ProfibusLogLine.get_function_name_from_sap(right_part_sap)}({right_part_address}:{right_part_sap})"
            )

            raw_interlocutors = line[match.start() : match.end()]
            interlocutors_with_translation = f"[{left_part_with_translation} {match.group(3)} {right_part_with_translation}]"

            if match.group(3) == "=>":
                source_address = left_part_address
                source_sap = left_part_sap
                target_address = right_part_address
                target_sap = right_part_sap
            else:
                source_address = right_part_address
                source_sap = right_part_sap
                target_address = left_part_address
                target_sap = left_part_sap

        else:
            source_address = target_address = -1
            source_sap = target_sap = -1
            interlocutors_with_translation = "Unknwown raw_interlocutors_description"
            raw_interlocutors = "Unknown raw_interlocutors"

        # Extract sequence: [num:43548]
        seq_pattern = re.compile(r"\[num:(\d+)\]")
        match = seq_pattern.search(line)
        if match:
            sequence = int(match.group(1))
        else:
            sequence = 0

        # Extract mode: [mode:SDA]
        mode_pattern = re.compile(r"\[mode:(SDN|SDA)\]")
        match = mode_pattern.search(line)
        if match:
            mode = match.group(1)
        else:
            mode = ""

        # Extract length: [len:51]
        len_pattern = re.compile(r"\[len:(\d+)\]")
        match = len_pattern.search(line)
        if match:
            length = int(match.group(1))
        else:
            length = 0

        # Extract trailing bytes
        bytes_hexa = line.split("]")[-1].strip()

        translated_source = f"{ProfibusLogLine.get_equipment_name_from_address(source_address)}/{ProfibusLogLine.get_function_name_from_sap(source_sap)}"
        translated_target = f"{ProfibusLogLine.get_equipment_name_from_address(target_address)}/{ProfibusLogLine.get_function_name_from_sap(target_sap)}"

        if mode in ("SDA", "SDN"):
            return ProfibusLogLine(
                timestamp=timestamp,
                source_address=source_address,
                target_address=target_address,
                source_sap=source_sap,
                target_sap=target_sap,
                source_name=translated_source,
                target_name=translated_target,
                raw_interlocutors=raw_interlocutors,
                raw_interlocutors_without_direction=raw_interlocutors.replace("<", "").replace(">", "").replace("=", "<=>"),
                interlocutors_with_translation=interlocutors_with_translation,
                interlocutors_with_translation_without_direction=interlocutors_with_translation.replace("<", "").replace(">", "").replace("=", "<=>"),
                sequence=sequence,
                mode=SendingMode[mode],
                length=length,
                bytes_hexa_str=bytes_hexa,
                upper_layer_decoding_library=upper_layer_decoding_library,
                file_path=file_path,
                line_number=line_number,
                previous_line_timestamp=previous_line_timestamp,
            )
        else:
            return None

    def decode_sdn_or_sda(self, ppn_connections_library: PpnConnectionsLibrary | None = None) -> None:
        if ppn_connections_library is None:
            ppn_connections_library = PpnConnectionsLibrary()

        if self.mode == SendingMode.SDA:
            try:
                self.unisig_message = decode_unisig_s57_s58.OnboardSdaUnisigMessage.from_sda_hexa_bytes_str(
                    profibus_log_line=self,
                    bytes_hexa_str=self.bytes_hexa_str,
                    upper_layer_decoding_library=self.upper_layer_decoding_library,
                    ppn_connections_library=ppn_connections_library,
                )

                assert cast(
                    decode_unisig_s57_s58.OnboardSdaUnisigMessage, self.unisig_message
                ).byte_message_decoded.is_correctly_and_completely_decoded, (
                    f"Line is not completely decoded, {len(cast(decode_unisig_s57_s58.OnboardSdaUnisigMessage, self.unisig_message).byte_message_decoded)} bits remaining"
                )

            except (AssertionError, ValueError) as ass_err:
                logger_config.print_and_log_exception(ass_err)
                logger_config.print_and_log_error(
                    f"Could not decode SDA message at {self.timestamp} between {self.interlocutors_with_translation_without_direction} in file {self.file_path} line {self.line_number}, bytes_hexa_str:{self.bytes_hexa_str}"
                )

        else:
            try:
                self.unisig_message = decode_unisig_s57_s58.SdnOnboardUnisigMessage.decode_sdn_bytes_hexa(
                    profibus_log_line=self,
                    bytes_hexa=self.bytes_hexa_str,
                    upper_layer_decoding_library=self.upper_layer_decoding_library,
                    ppn_connections_library=ppn_connections_library,
                )
            except (AssertionError, ValueError) as ass_err:
                logger_config.print_and_log_exception(ass_err)
