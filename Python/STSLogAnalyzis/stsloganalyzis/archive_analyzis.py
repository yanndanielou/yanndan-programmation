from __future__ import annotations
from collections import OrderedDict

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
import humanize

from common import (
    reports_utils,
    date_time_formats,
)
from logger import logger_config
from datetime import datetime

from stsloganalyzis import (
    decode_archive,
    line_topology,
    decode_product_topology_dependant_messages_content,
    constants,
    helpers,
)


@dataclass
class Train:
    cc_id_with_offset: int

    def __post_init__(self) -> None:
        self.last_front_nv_location: Optional[line_topology.ExactLocation] = None


class MovementAutorityLimitForOneZoneController:
    train: Train
    mal_location: line_topology.ExactLocation

    def get_distance_to_train_in_cm(self) -> int:
        pass
        return 0


@dataclass
class ZoneController:
    identifier: str


@dataclass
class FieldLastValue:
    timestamp: datetime
    field_name: str
    field_value: constants.FIELD_TYPE

    def __post_init__(self) -> None:
        self.previous_value: Optional[constants.FIELD_TYPE] = None
        self.previous_timestamp: Optional[datetime] = None

        self.previous_different_value: Optional[constants.FIELD_TYPE] = None
        self.previous_different_value_timestamp: Optional[datetime] = None

    def update_value(self, new_value: constants.FIELD_TYPE, timestamp: datetime) -> bool:

        has_changed = self.previous_value != new_value
        self.previous_value = self.field_value
        self.previous_timestamp = self.timestamp

        if has_changed:
            self.previous_different_value = self.field_value
            self.previous_different_value_timestamp = self.timestamp

        self.field_value = new_value
        self.timestamp = timestamp

        return has_changed


class FieldsLibraryForOneLineId:
    def __init__(self, line_id: str) -> None:
        self.line_id = line_id
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
            new_field = FieldLastValue(timestamp=timestamp, field_value=field_value, field_name=field_name)
            self.last_values.append(new_field)
            return new_field


@dataclass
class SqlArchArchiveLineWithContext:
    sql_arch_line: decode_archive.SqlArchArchiveLine
    previous_line_for_this_id: Optional[SqlArchArchiveLineWithContext]
    archive_analyzis: ArchiveAnalyzis
    all_fields_changed: List[FieldLastValue]

    def __post_init__(self) -> None:
        # self.previous_fields_values: FieldsLibraryForOneLineId = FieldsLibraryForOneLineId()
        pass

    def decode_zc_mal_message(
        self,
    ) -> None:

        decoded_message = self.sql_arch_line.decoded_message
        assert decoded_message is not None

        zone_controller = self.archive_analyzis.get_or_create_zone_controller(self.sql_arch_line.eqp)
        train_cc_id = decoded_message.decoded_fields_flat_directory.get("CCId1")
        assert isinstance(train_cc_id, int)
        train = self.archive_analyzis.get_or_create_train(cc_id_with_offset=train_cc_id)

        pass

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
        self.latest_fields_values_by_line_id: Dict[str, FieldsLibraryForOneLineId] = dict()

        self.handle_lines()

    def get_or_create_zone_controller(self, zone_controller_id: str) -> ZoneController:
        zone_controllers_found = [zone_controller for zone_controller in self.zone_controllers if zone_controller.identifier == zone_controller_id]

        if not zone_controllers_found:
            self.zone_controllers.append(ZoneController(identifier=zone_controller_id))
            return self.get_or_create_zone_controller(zone_controller_id)

        assert len(zone_controllers_found) == 1
        return zone_controllers_found[0]

    def get_or_create_train(self, cc_id_with_offset: int) -> Train:
        trains_found = [train for train in self.trains if train.cc_id_with_offset == cc_id_with_offset]

        if not trains_found:
            self.trains.append(Train(cc_id_with_offset=cc_id_with_offset))
            return self.get_or_create_train(cc_id_with_offset)

        assert len(trains_found) == 1
        return trains_found[0]

    def update_latest_fields_for_line(self, sql_arch_line: decode_archive.SqlArchArchiveLine) -> List[FieldLastValue]:
        """returns all fields changed"""
        line_id = sql_arch_line.id_field
        timestamp = sql_arch_line.date

        all_fields_changed: List[FieldLastValue] = []

        if line_id not in self.latest_fields_values_by_line_id:
            self.latest_fields_values_by_line_id[line_id] = FieldsLibraryForOneLineId(line_id)
        latest_fields_values = self.latest_fields_values_by_line_id[line_id]

        if sql_arch_line.decoded_message:
            for field_name, field_value in sql_arch_line.sqlarch_fields_dict_raw.items():
                field_has_changed = latest_fields_values.update_latest_value_for_field(field_name=field_name, field_value=field_value, timestamp=timestamp)
                if field_has_changed is not None:
                    all_fields_changed.append(field_has_changed)
        else:
            field_has_changed = latest_fields_values.update_latest_value_for_field(field_name=constants.STATE_FIELD_NAME, field_value=sql_arch_line.get_new_state_str(), timestamp=timestamp)
            if field_has_changed is not None:
                all_fields_changed.append(field_has_changed)

        return all_fields_changed

    def handle_lines(self) -> None:
        for sql_arch_line in self.archive_library.all_sqlarch_lines:
            previous_line_for_this_id = self.current_latest_line_by_id.get(sql_arch_line.id_field)
            all_fields_changed = self.update_latest_fields_for_line(sql_arch_line=sql_arch_line)
            line_with_context = SqlArchArchiveLineWithContext(
                sql_arch_line=sql_arch_line, previous_line_for_this_id=previous_line_for_this_id, archive_analyzis=self, all_fields_changed=all_fields_changed
            )
            self.all_sql_arch_lines_with_context.append(line_with_context)
            self.current_latest_line_by_id[sql_arch_line.id_field] = line_with_context

            if (
                line_with_context.sql_arch_line.decoded_message
                and line_with_context.sql_arch_line.decoded_message.message_number == decode_product_topology_dependant_messages_content.ZC_ATS_MAL_MESSAGE_ID
            ):
                line_with_context.decode_zc_mal_message()

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
