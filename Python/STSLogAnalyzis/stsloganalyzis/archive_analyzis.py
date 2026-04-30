from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, cast

from enum import IntEnum

import copy

import humanize
from common import (
    date_time_formats,
    reports_utils,
)
from logger import logger_config

from stsloganalyzis import (
    constants,
    decode_archive,
    decode_product_topology_dependant_messages_content,
    helpers,
    line_topology,
    decode_message,
)


@dataclass
class Train:
    cc_id_with_offset: int

    def __post_init__(self) -> None:
        self.last_front_nv_location: Optional[line_topology.ExactLocation] = None


@dataclass
class MovementAuthorityLimitForOneZoneController:
    label: str
    train: Train
    zone_controller: ZoneController
    mal_location: line_topology.ExactLocation
    raw_mal_type: int

    def __post_init__(self) -> None:
        self.mal_type: "MovementAuthorityLimitForOneZoneController.MALType" = MovementAuthorityLimitForOneZoneController.MALType(self.raw_mal_type)

    def get_distance_to_train_in_cm(self) -> int:
        return 0

    @property
    def field_names_and_values_in_report(self) -> List[Tuple[str, constants.HUMAN_READABLE_FIELD_TYPE]]:
        field_names_and_values: List[Tuple[str, constants.HUMAN_READABLE_FIELD_TYPE]] = []
        mal_tc_label = self.mal_location.get_track_circuit_id_string_if_no() if self.mal_location else "None"
        mal_tb_label = self.mal_location.get_tracking_block_id_string_if_no() if self.mal_location else "None"

        field_names_and_values.append((f"MAL for {str(self.train)} TB", f"type {self.mal_type.name} {mal_tb_label}"))
        field_names_and_values.append((f"MAL for {str(self.train)} TC", f"type {self.mal_type.name} {mal_tc_label}"))
        field_names_and_values.append((f"MAL for {str(self.train)} location", f"type {self.mal_type.name} {self.mal_location}"))
        field_names_and_values.append((f"MAL for {str(self.train)} Type", f"type {self.mal_type.name}"))
        return field_names_and_values

    def __str__(self) -> str:
        return f"MAL for {str(self.train)} type {self.mal_type} at {self.mal_location.get_tracking_block_id_string_if_no}"

    class MALType(IntEnum):
        AUTOMATIC_TRAIN = 0  # 0 = AT (train contrôlé)
        MT_MANUAL = 1  # 1 = MT (train en manuel)
        UNEQUIPPED_TRAIN = 2  # 2 = UT (train non équipé ou muet)
        HOME_SIGNAL = 3  # 3 = HS (Origine de manoeuvre)
        TRACK_LIMIT = 4  # 4 = Track_Limit (Limite de voie)
        DEFAULT = 5  # 5 = Default (Défaut)
        NOT_USED_6 = 6
        NOT_USED_7 = 7


@dataclass
class ZoneController:
    identifier: str


@dataclass
class FieldLastValue:
    object_id: str
    timestamp: datetime
    field_name: str
    field_value: constants.FIELD_TYPE

    def __post_init__(self) -> None:
        self.previous_value: Optional[constants.FIELD_TYPE] = None
        self.previous_timestamp: Optional[datetime] = None

        self.previous_different_value: Optional[constants.FIELD_TYPE] = None
        self.previous_different_value_timestamp: Optional[datetime] = None

        if self.object_id == "S_TRAIN_CC_48_SPEED_TRACKING" and self.field_name == "State":
            pause = 1

    def update_value(self, new_value: constants.FIELD_TYPE, new_timestamp: datetime) -> bool:

        if self.object_id == "S_TRAIN_CC_48_SPEED_TRACKING" and self.field_name == "State":
            pause = 1

        has_changed = self.field_value != new_value

        if has_changed:
            self.previous_different_value = self.field_value
            self.previous_different_value_timestamp = self.timestamp

        self.previous_value = self.field_value
        self.previous_timestamp = self.timestamp

        self.field_value = new_value
        self.timestamp = new_timestamp

        assert self.previous_different_value != self.field_value

        return has_changed


class FieldsLibraryForOneObject:
    def __init__(self, line_id: str) -> None:
        self.object_id = line_id
        self.last_values: List[FieldLastValue] = []

    def get_field(self, field_name: str) -> Optional[FieldLastValue]:
        fields_found = [field_found for field_found in self.last_values if field_found.field_name == field_name]
        if fields_found:
            assert len(fields_found) == 1
            return fields_found[0]
        return None

    def get_latest_value_for_field(self, field_name: str) -> Tuple[Optional[constants.FIELD_TYPE], Optional[datetime]]:
        field_found = self.get_field(field_name)
        if field_found:
            return field_found.field_value, field_found.timestamp
        return None, None

    def update_latest_value_for_field(self, field_name: str, field_value: constants.FIELD_TYPE, timestamp: datetime) -> Optional[FieldLastValue]:
        field_found = self.get_field(field_name)
        if field_found:
            if field_found.update_value(field_value, timestamp):
                return field_found
            else:
                return None
        else:
            new_field = FieldLastValue(object_id=self.object_id, timestamp=timestamp, field_value=field_value, field_name=field_name)
            self.last_values.append(new_field)
            return new_field


@dataclass
class SqlArchArchiveLineWithContext:
    sql_arch_line: decode_archive.SqlArchArchiveLine
    previous_line_for_this_id: Optional[SqlArchArchiveLineWithContext]
    archive_analyzis: ArchiveAnalyzis
    all_fields_changed: List[FieldLastValue]

    def __post_init__(self) -> None:
        self.all_fields_changed = copy.deepcopy(self.all_fields_changed)

    @property
    def decoded_message(self) -> decode_message.DecodedMessage:
        decoded_message = cast(decode_message.DecodedMessage, self.sql_arch_line.decoded_message)
        assert decoded_message is not None
        return decoded_message

    @property
    def decoded_fields_flat_directory(self) -> Dict[str, constants.FIELD_TYPE]:
        return self.decoded_message.decoded_fields_flat_directory

    def get_all_changes_since_previous(self) -> List[OrderedDict[str, Any]]:
        to_ret: List[OrderedDict[str, Any]] = []

        for changed_field in self.all_fields_changed:

            if not helpers.is_field_name_to_be_ignored(field_name=changed_field.field_name):

                previous_date = changed_field.previous_different_value_timestamp
                exact_time_delta = date_time_formats.format_duration_timedelta_to_string(self.sql_arch_line.date - previous_date) if previous_date else "NA"
                approximative_time_delta = humanize.precisedelta(self.sql_arch_line.date - previous_date, minimum_unit="milliseconds") if previous_date else "NA"
                old_timestamp = str(previous_date)
                to_ret.append(
                    OrderedDict(
                        {
                            "date": self.sql_arch_line.get_date_raw_str(),
                            "id": self.sql_arch_line.id_field,
                            "id_msg": self.sql_arch_line.decoded_message.message_number if self.sql_arch_line.decoded_message else "NA",
                            "field": changed_field.field_name,
                            "old_value": changed_field.previous_different_value,
                            "new_value": changed_field.field_value,
                            "change_value": f"{changed_field.previous_different_value} -> {changed_field.field_value}",
                            "exact_time_delta": exact_time_delta,
                            "approximative_time_delta": approximative_time_delta,
                            "old_timestamp": old_timestamp,
                        }
                    )
                )

        return to_ret


@dataclass
class ArchiveAnalyzis:
    railway_line: line_topology.Line
    archive_library: decode_archive.ArchiveLibrary

    label: str

    def __post_init__(self) -> None:
        self.trains: List[Train] = []
        self.zone_controllers: List[ZoneController] = []

        self.all_sql_arch_lines_with_context: List[SqlArchArchiveLineWithContext] = []
        self.current_latest_line_by_id: Dict[str, SqlArchArchiveLineWithContext] = dict()
        self.latest_fields_values_by_object_id: Dict[str, FieldsLibraryForOneObject] = dict()

        self.handle_lines()

    def get_or_create_zone_controller(self, zone_controller_id: str) -> ZoneController:
        zone_controllers_found = [zone_controller for zone_controller in self.zone_controllers if zone_controller.identifier == zone_controller_id]

        if not zone_controllers_found:
            self.zone_controllers.append(ZoneController(identifier=zone_controller_id))
            return self.get_or_create_zone_controller(zone_controller_id)

        assert len(zone_controllers_found) == 1
        return zone_controllers_found[0]

    def get_or_create_train_by_cc_id_field_name(self, decoded_fields_flat_directory: Dict[str, constants.FIELD_TYPE], cc_id_field_name: str) -> Train:
        train_cc_id = decoded_fields_flat_directory.get("CCId1")
        assert isinstance(train_cc_id, int)
        return self.get_or_create_train_by_cc_id(cc_id_with_offset=train_cc_id)

    def get_or_create_train_by_cc_id(self, cc_id_with_offset: int) -> Train:
        trains_found = [train for train in self.trains if train.cc_id_with_offset == cc_id_with_offset]

        if not trains_found:
            self.trains.append(Train(cc_id_with_offset=cc_id_with_offset))
            return self.get_or_create_train_by_cc_id(cc_id_with_offset)

        assert len(trains_found) == 1
        return trains_found[0]

    def update_field_for_line(self, sql_arch_line: decode_archive.SqlArchArchiveLine, field_name: str, field_value: constants.HUMAN_READABLE_FIELD_TYPE) -> List[FieldLastValue]:
        return self.update_fields_for_line(sql_arch_line=sql_arch_line, fields_names_and_values=[(field_name, field_value)])

    def update_fields_for_line(self, sql_arch_line: decode_archive.SqlArchArchiveLine, fields_names_and_values: List[Tuple[str, constants.HUMAN_READABLE_FIELD_TYPE]]) -> List[FieldLastValue]:
        object_id = sql_arch_line.id_field
        timestamp = sql_arch_line.date

        all_fields_changed: List[FieldLastValue] = []

        if object_id not in self.latest_fields_values_by_object_id:
            self.latest_fields_values_by_object_id[object_id] = FieldsLibraryForOneObject(object_id)
        latest_fields_values = self.latest_fields_values_by_object_id[object_id]

        for field_name, field_value in fields_names_and_values:
            field_has_changed = latest_fields_values.update_latest_value_for_field(field_name=field_name, field_value=field_value, timestamp=timestamp)
            if field_has_changed is not None:
                all_fields_changed.append(field_has_changed)

        return all_fields_changed

    def update_latest_raw_fields_for_line(self, sql_arch_line: decode_archive.SqlArchArchiveLine) -> List[FieldLastValue]:
        """returns all fields changed"""
        if sql_arch_line.decoded_message:
            fields_names_and_values = [pair for pair in sql_arch_line.sqlarch_fields_dict_raw.items()]
            return self.update_fields_for_line(sql_arch_line=sql_arch_line, fields_names_and_values=fields_names_and_values)
        else:
            return self.update_field_for_line(sql_arch_line=sql_arch_line, field_name=constants.STATE_FIELD_NAME, field_value=sql_arch_line.get_new_state_str())

    def decode_zc_mal_message(self, sql_arch_line: decode_archive.SqlArchArchiveLine) -> List[FieldLastValue]:
        all_fields_changed: List[FieldLastValue] = []

        decoded_message = sql_arch_line.decoded_message
        assert decoded_message is not None

        zone_controller = self.get_or_create_zone_controller(sql_arch_line.eqp)
        train = self.get_or_create_train_by_cc_id_field_name(decoded_fields_flat_directory=decoded_message.decoded_fields_flat_directory, cc_id_field_name="CCId1")

        vital_mal = MovementAuthorityLimitForOneZoneController(
            label="Vital MAL",
            train=train,
            zone_controller=zone_controller,
            mal_location=helpers.decode_one_exact_location(
                decoded_fields_flat_directory=decoded_message.decoded_fields_flat_directory, segment_id_field_name="MALSegIdV", abscissa_field_name="MALOffsetV", railway_line=self.railway_line
            ),
            raw_mal_type=cast(int, decoded_message.decoded_fields_flat_directory.get("MALType")),
        )
        non_vital_mal = MovementAuthorityLimitForOneZoneController(
            label="Non vital MAL",
            train=train,
            zone_controller=zone_controller,
            mal_location=helpers.decode_one_exact_location(
                decoded_fields_flat_directory=decoded_message.decoded_fields_flat_directory, segment_id_field_name="MALSegIdNv", abscissa_field_name="MALOffsetNv", railway_line=self.railway_line
            ),
            raw_mal_type=cast(int, decoded_message.decoded_fields_flat_directory.get("MALType")),
        )

        for mal in [vital_mal, non_vital_mal]:
            all_fields_changed += self.update_fields_for_line(sql_arch_line=sql_arch_line, fields_names_and_values=mal.field_names_and_values_in_report)

        return all_fields_changed

    def handle_lines(self) -> None:
        for sql_arch_line in self.archive_library.all_sqlarch_lines:
            previous_line_for_this_id = self.current_latest_line_by_id.get(sql_arch_line.id_field)
            all_fields_changed = self.update_latest_raw_fields_for_line(sql_arch_line=sql_arch_line)

            if sql_arch_line.decoded_message and sql_arch_line.decoded_message.message_number == decode_product_topology_dependant_messages_content.ZC_ATS_MAL_MESSAGE_ID:
                all_fields_changed += self.decode_zc_mal_message(sql_arch_line=sql_arch_line)

            line_with_context = SqlArchArchiveLineWithContext(
                sql_arch_line=sql_arch_line, previous_line_for_this_id=previous_line_for_this_id, archive_analyzis=self, all_fields_changed=all_fields_changed
            )
            self.all_sql_arch_lines_with_context.append(line_with_context)
            self.current_latest_line_by_id[sql_arch_line.id_field] = line_with_context

    @logger_config.stopwatch_decorator(inform_beginning=True, monitor_ram_usage=True)
    def create_reports_all_sqlarch_changes_since_previous(self, output_directory_path: str, file_base_name: Optional[str] = None) -> int:
        if file_base_name is None:
            file_base_name = f"{self.label}_all_changes"

        rows_as_list_dict: List[Dict[str, Any]] = []

        for line_with_context in self.all_sql_arch_lines_with_context:
            # all_changes_since_previous = line_with_context.sql_arch_line.get_all_changes_since_previous(
            #    previous_line_for_this_id=line_with_context.previous_line_for_this_id.sql_arch_line if line_with_context.previous_line_for_this_id else None
            # )
            all_changes_since_previous = line_with_context.get_all_changes_since_previous()
            if all_changes_since_previous:
                rows_as_list_dict += all_changes_since_previous

        # logger_config.print_and_log_info(f"{len(rows_as_list_dict)} lines changed detected, report created")
        reports_utils.save_rows_to_output_files(rows_as_list_dict=rows_as_list_dict, file_base_name=file_base_name, output_directory_path=output_directory_path, suffix_file_name_by_date=False)
        reports_utils.save_rows_to_output_files(rows_as_list_dict=rows_as_list_dict, file_base_name=file_base_name, output_directory_path=output_directory_path, suffix_file_name_by_date=True)
        return len(rows_as_list_dict)
