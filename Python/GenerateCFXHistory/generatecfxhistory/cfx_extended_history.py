from typing import List, Dict, Optional, Set
import re
from datetime import datetime

from dataclasses import dataclass

from logger import logger_config


CURRENT_OWNER_FIELD_MODIFICATION_ID = "CurrentOwner"

ONE_LINE_FIELDS_TO_RETRIVE_ON_CFX_SUBMIT = [
    "Category",
    "CauseType",
    "CurrentOwner",
    "Description",
    "DetectedInPhase",
    "DocumentationFixedID",
    "DocumentationFixedVersion",
    "DocumentationID",
    "DocumentationVersion",
    "EnvironmentType",
    "Headline",
    "OriginatedInPhase",
    "Priority",
    "Project",
    "RequestOwner",
    "RequestType",
    "SafetyRelevant",
    "SecurityContext",
    "SecurityContextExtended",
    "State",
    "SystemStructure",
]

ONE_LINE_FIELDS_PATTERNS_TO_RETRIVE_ON_CFX_SUBMIT = [r"(?P<field>" + field_name + ")\s*\(\d+\)\n\s*(?P<value>.*)\n" for field_name in ONE_LINE_FIELDS_TO_RETRIVE_ON_CFX_SUBMIT]


def decode_time(full_raw_time: str) -> Optional[datetime]:
    stipped_full_raw_time = full_raw_time.strip()
    try:
        # Assume the time format is "YYYY-MM-DD HH:MM:SS ±HH:MM"
        return datetime.strptime(stipped_full_raw_time, "%Y-%m-%d %H:%M:%S %z")
    except ValueError:
        logger_config.print_and_log_warning(f"Unable to decode time '{full_raw_time}'. Will try without timezone")
        try:
            time_until_secnds = stipped_full_raw_time[:19]
            return datetime.strptime(time_until_secnds, "%Y-%m-%d %H:%M:%S")

        except ValueError:
            logger_config.print_and_log_error(f"Warning: Unable to decode time '{full_raw_time}'")
            return None


@dataclass
class CFXRawCompleteHistoryExport:
    cfx_id: str
    # history_lines: List[str]
    history_full_text: str


class AllCFXCompleteHistoryExport:

    @staticmethod
    def parse_full_complete_extended_histories_text_file(
        all_cfx_complete_extended_histories_text_file_path: str, cfx_to_treat_whitelist_ids: Optional[Set | List[str]]
    ) -> List["CFXEntryCompleteHistory"]:
        with logger_config.stopwatch_with_label(f"Opene and read {all_cfx_complete_extended_histories_text_file_path}"):
            with open(all_cfx_complete_extended_histories_text_file_path, "r", encoding="utf-8") as all_cfx_extended_history_text_file:
                return AllCFXCompleteHistoryExport.parse_full_complete_extended_histories_text_files_contents([all_cfx_extended_history_text_file.read()], cfx_to_treat_whitelist_ids)

    @staticmethod
    def parse_full_complete_extended_histories_text_files_contents(
        all_cfx_complete_extended_histories_text_files_contents: List[str], cfx_to_treat_whitelist_ids: Optional[Set | List[str]]
    ) -> List["CFXEntryCompleteHistory"]:
        all_cfx_complete_history: List[CFXEntryCompleteHistory] = list()

        complete_history_len_by_cfx: Dict[str, int] = dict()
        raw_history_by_cfx: Dict[str, CFXRawCompleteHistoryExport] = dict()

        for all_cfx_extended_history_text_file_content in all_cfx_complete_extended_histories_text_files_contents:

            with logger_config.stopwatch_with_label("Split extended history content by CFX"):
                without_first_line = all_cfx_extended_history_text_file_content.split("id|at_field_history.audit_trail_text|\n")[1]
                split_by_end = without_first_line.split("====END====\n\n|\n")
                for one_cfx_history_description_raw in split_by_end:

                    cfx_id = one_cfx_history_description_raw.split("|")[0]

                    full_text = one_cfx_history_description_raw
                    raw_history = CFXRawCompleteHistoryExport(cfx_id=cfx_id, history_full_text=full_text)
                    raw_history_by_cfx[cfx_id] = raw_history
                    complete_history_len_by_cfx[cfx_id] = len(one_cfx_history_description_raw)

            sorted_cfxs = sorted(complete_history_len_by_cfx.items(), key=lambda item: item[1], reverse=True)
            top_10_biggest_history_cfxs = dict(sorted_cfxs[:10])
            logger_config.print_and_log_info(f"biggest_history_cfxs:{top_10_biggest_history_cfxs}")

            cfx_processed: Set[str] = set()
            for cfx_id, raw_complete_history_export in raw_history_by_cfx.items():
                with logger_config.stopwatch_alert_if_exceeds_duration(
                    label=f"Processing complete history of {cfx_id}",
                    duration_threshold_to_alert_info_in_s=0.2,
                    duration_threshold_to_alert_warning_in_s=0.5,
                    duration_threshold_to_alert_error_in_s=1,
                    duration_threshold_to_alert_critical_in_s=5,
                ):

                    if cfx_to_treat_whitelist_ids is None or cfx_id in cfx_to_treat_whitelist_ids:
                        cfx_complete_history = parse_history(cfx_id=cfx_id, extended_history_text=raw_complete_history_export.history_full_text)
                        all_cfx_complete_history.append(cfx_complete_history)
                        cfx_processed.add(cfx_id)

                        if len(cfx_processed) % 200 == 0:
                            logger_config.print_and_log_info(f"Number of CFX processed:{len(cfx_processed)}. Just processed {cfx_id}")

        logger_config.print_and_log_info(f"cfx_extended_history_text_file_content_split_by_cfx:{len(all_cfx_complete_history)}")

        return all_cfx_complete_history


class CFXHistoryField:
    def __init__(self, cfx_id: str, field_id: str, secondary_label: str, old_state: str, new_state: str, change_timestamp: datetime):
        self.cfx_id = cfx_id
        self.field_id = field_id.strip()
        self.secondary_label = secondary_label.strip()
        self.old_state = old_state.strip()
        self.new_state = new_state.strip()
        self.change_timestamp = change_timestamp
        self.change_timestamp_without_timezone = change_timestamp.replace(tzinfo=None)

    def __post_init__(self) -> None:
        pass

    def __repr__(self) -> str:
        return f"<CFXHistoryField field_id={self.field_id} secondary_label={self.secondary_label}>"


class CFXHistoryElement:
    def __init__(self, cfx_id: str, time: str, decoded_time: Optional[datetime], schema_rev: str, user_name: str, user_login: str, user_groups: str, action: str, state: str):
        self._cfx_id = cfx_id
        self._raw_time: str = time.strip()
        self._decoded_time: Optional[datetime] = decoded_time
        self._schema_rev = schema_rev.strip()
        self._user_name = user_name.strip()
        self._user_login = user_login.strip()
        self._user_groups = user_groups.strip()
        self._action = action.strip()
        self._state = state.strip()
        self._fields: List[CFXHistoryField] = []

    def get_all_current_owner_field_modifications(self) -> List[CFXHistoryField]:
        all_current_owner_field_modification = [field for field in self._fields if field.field_id == CURRENT_OWNER_FIELD_MODIFICATION_ID]
        return all_current_owner_field_modification

    @property
    def decoded_time(self) -> Optional[datetime]:
        return self._decoded_time

    @property
    def action(self) -> str:
        return self._action

    @property
    def state(self) -> str:
        return self._state

    @property
    def fields(self) -> List[CFXHistoryField]:
        return self._fields

    def add_field(self, field: CFXHistoryField) -> None:
        self._fields.append(field)

    def __repr__(self) -> str:
        return f"<CFXHistoryElement time={self._decoded_time} action={self._action} state={self._state} fields={len(self._fields)}>"


class CFXEntryCompleteHistory:
    def __init__(self, cfx_id: str):
        self.cfx_id = cfx_id
        self._history_elements: List[CFXHistoryElement] = []

    def add_field_history_element(self, field: CFXHistoryElement) -> None:
        self._history_elements.append(field)

    def get_all_current_owner_field_modifications(self) -> List[CFXHistoryField]:
        all_current_owner_field_modification = [field for history_element in self._history_elements for field in history_element.get_all_current_owner_field_modifications()]
        return all_current_owner_field_modification

    @property
    def history_elements(self) -> List[CFXHistoryElement]:
        return self._history_elements


def get_one_line_field_when_cfx_submit_regex(field_name: str) -> str:
    one_line_field_when_cfx_submit_regex = r"(?P<field>" + field_name + ")\s*\(\d+\)\n\s*(?P<value>.*)\n"
    # one_line_field_when_cfx_submit_regex = "(?P<field>" + field_name + ")\\s*\\(\\d+\\)\\n\\s*(?P<value>.+)\\n"
    return one_line_field_when_cfx_submit_regex


def parse_history(cfx_id: str, extended_history_text: str) -> CFXEntryCompleteHistory:

    cfx_complete_history = CFXEntryCompleteHistory(cfx_id=cfx_id)
    history_blocks = extended_history_text.split("====START====")[1:]

    for block in history_blocks:
        block = block.strip()
        if not block:
            continue

        # Define regular expressions for extracting elements and fields
        element_regex = r"Time\s*:\s*(.*?)\nSchema Rev\s*:\s*(.*?)\nUser Name\s*:\s*(.*?)\nUser Login\s*:\s*(.*?)\nUser Groups\s*:\s*(.*?)\nAction\s*:\s*(.*?)\nState\s*:\s*(.*?)\n==Fields=="
        field_update_regex = r"(.+?)\s*\((\d+:\d+)\)\s*Old\s*:\s*(.*?)\s*New\s*:(.*?)(?=(\n.+?\s*\(\d+:\d+\)|\n====END====|\Z))"
        # field_submit_regex_not_working = r"(.+?)\s*\((\d+:\d+)\)\s*\s*:(.*?)(?=(\n.+?\s*\(\d+:\d+\)|\n====END====|\Z))"
        # field_submit_regex_try1 = r"(?P<field>[A-Za-z]+):\s+(?P<value>[\w\s\(\)/\.]+)"
        # field_submit_regex_try2 = r"(?P<field>[A-Za-z]+)\s*\(\d+\)\n\s*(?P<value>[\w\s\(\)/\.]+)"

        # Parse history element details
        element_match = re.search(element_regex, block, re.DOTALL)
        if element_match:
            time, schema_rev, user_name, user_login, user_groups, action, state = element_match.groups()
            decoded_time = decode_time(time)
            if not decoded_time:
                logger_config.print_and_log_error(f"Could not decode time {time} for {cfx_id}")

            # logger_config.print_and_log_info(f"Create CFXHistoryElement {cfx_id, time, action, state}")
            element = CFXHistoryElement(cfx_id, time, decoded_time, schema_rev, user_name, user_login, user_groups, action, state)

            # Identify and parse fields within the block
            fields_section = block.split("==Fields==")[1].strip()
            # logger_config.print_and_log_info(f"Split fields CFXHistoryElement {cfx_id, action, state}")

            fields_created: list[CFXHistoryField] = []
            if action == "Submit":

                for one_line_field_to_retrieve in ONE_LINE_FIELDS_PATTERNS_TO_RETRIVE_ON_CFX_SUBMIT:
                    # field_pattern = get_one_line_field_when_cfx_submit_regex(one_line_field_to_retrieve)
                    field_submit_match = re.search(one_line_field_to_retrieve, fields_section)
                    if field_submit_match:
                        # field_id, new_state = field_submit_match.groups()[:2]
                        # field = CFXHistoryField(cfx_id=cfx_id, field_id=field_id, secondary_label="", old_state="", new_state=new_state, change_timestamp=element.decoded_time)
                        # element.add_field(field)
                        # fields_created.append(field)
                        # logger_config.print_and_log_info(f"Found field {field_id} with value {new_state} for {cfx_id}")
                        pass
                    """
                    field_submit_matches = re.finditer(field_submit_regex_try2, fields_section, re.DOTALL)
                    logger_config.print_and_log_info(f"Has computed fields submit CFXHistoryElement {cfx_id, action}")

                    for field_match in field_submit_matches:
                        field_id, secondary_label, new_state = field_match.groups()[:3]
                        field = CFXHistoryField(cfx_id=cfx_id, field_id=field_id, secondary_label=secondary_label, old_state=None, new_state=new_state, change_timestamp=element.decoded_time)
                        element.add_field(field)
                        fields_created.append(field)
                    """
            else:
                field_update_matches = re.finditer(field_update_regex, fields_section, re.DOTALL)
                # logger_config.print_and_log_info(f"Has computed field_update_matches CFXHistoryElement {cfx_id, action}")

                for field_match in field_update_matches:
                    field_id, secondary_label, old_state, new_state = field_match.groups()[:4]
                    field = CFXHistoryField(cfx_id=cfx_id, field_id=field_id, secondary_label=secondary_label, old_state=old_state, new_state=new_state, change_timestamp=element.decoded_time)
                    element.add_field(field)
                    fields_created.append(field)

            # logger_config.print_and_log_info(f"Has just created {len(fields_created)} fields CFXHistoryElement {cfx_id, action}")
            cfx_complete_history.add_field_history_element(element)

    return cfx_complete_history
