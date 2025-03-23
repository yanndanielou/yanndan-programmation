from typing import List, Dict, Optional
import re
from datetime import datetime

from logger import logger_config


CURRENT_OWNER_FIELD_MODIFICATION_ID = "CurrentOwner"


def decode_time(time: str) -> Optional[datetime]:
    try:
        # Assume the time format is "YYYY-MM-DD HH:MM:SS ±HH:MM"
        return datetime.strptime(time.strip(), "%Y-%m-%d %H:%M:%S %z")
    except ValueError:
        logger_config.print_and_log_error(f"Warning: Unable to decode time '{time}'")
        return None


class AllCFXCompleteHistoryExport:
    @staticmethod
    def parse_full_complete_extended_histories_text_file(all_cfx_complete_extended_histories_text_file_path: str) -> List["CFXEntryCompleteHistory"]:
        all_cfx_complete_history: List[CFXEntryCompleteHistory] = list()

        complete_history_by_cfx: Dict[str, int] = dict()
        with logger_config.stopwatch_with_label(f"Read {all_cfx_complete_extended_histories_text_file_path}"):
            with open(all_cfx_complete_extended_histories_text_file_path, "r", encoding="utf-8") as all_cfx_extended_history_text_file:
                all_cfx_extended_history_text_file_content = all_cfx_extended_history_text_file.read()

        without_first_line = all_cfx_extended_history_text_file_content.split("CFXID|at_field_history.audit_trail_text|\n")[1]

        cfx_extended_histories_raw_text_list = without_first_line.split("====END====\n\n|\n")
        logger_config.print_and_log_info(f"cfx_extended_histories_raw_text_list:{len(cfx_extended_histories_raw_text_list)}")

        cfx_extended_histories_raw_text_unique_only = set(cfx_extended_histories_raw_text_list)
        logger_config.print_and_log_info(f"cfx_extended_histories_raw_text_unique_only:{len(cfx_extended_histories_raw_text_unique_only)}")

        for all_cfx_extended_history_split_by_end in cfx_extended_histories_raw_text_unique_only:
            cfx_id = all_cfx_extended_history_split_by_end.split("|====START====\n")[0]
            complete_history_by_cfx[cfx_id] = len(all_cfx_extended_history_split_by_end)

        biggest_history_cfxs = dict(reversed(sorted(complete_history_by_cfx.items(), key=lambda item: item[1])))
        logger_config.print_and_log_info(f"biggest_history_cfxs:{biggest_history_cfxs}")

        for all_cfx_extended_history_split_by_end in cfx_extended_histories_raw_text_unique_only:
            cfx_id = all_cfx_extended_history_split_by_end.split("|====START====\n")[0]

            # cfx_complete_history = parse_history(cfx_id=cfx_id, extended_history_text=all_cfx_extended_history_split_by_end)
            # all_cfx_complete_history.append(cfx_complete_history)

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


def parse_history(cfx_id: str, extended_history_text: str) -> CFXEntryCompleteHistory:

    cfx_complete_history = CFXEntryCompleteHistory(cfx_id=cfx_id)
    history_blocks = extended_history_text.split("====START====")[1:]

    for block in history_blocks:
        block = block.strip()
        if not block:
            continue

        # Define regular expressions for extracting elements and fields
        element_regex = r"Time\s*:\s*(.*?)\nSchema Rev\s*:\s*(.*?)\nUser Name\s*:\s*(.*?)\nUser Login\s*:\s*(.*?)\nUser Groups\s*:\s*(.*?)\nAction\s*:\s*(.*?)\nState\s*:\s*(.*?)\n==Fields=="
        field_regex = r"(.+?)\s*\((\d+:\d+)\)\s*Old\s*:\s*(.*?)\s*New\s*:(.*?)(?=(\n.+?\s*\(\d+:\d+\)|\n====END====|\Z))"

        # Parse history element details
        element_match = re.search(element_regex, block, re.DOTALL)
        if element_match:
            time, schema_rev, user_name, user_login, user_groups, action, state = element_match.groups()
            decoded_time = decode_time(time)
            if not decoded_time:
                logger_config.print_and_log_error(f"Could not decode time {time} for {cfx_id}")
            element = CFXHistoryElement(cfx_id, time, decoded_time, schema_rev, user_name, user_login, user_groups, action, state)

            # Identify and parse fields within the block
            fields_section = block.split("==Fields==")[1].strip()
            field_matches = re.finditer(field_regex, fields_section, re.DOTALL)
            for field_match in field_matches:
                field_id, secondary_label, old_state, new_state = field_match.groups()[:4]
                field = CFXHistoryField(cfx_id=cfx_id, field_id=field_id, secondary_label=secondary_label, old_state=old_state, new_state=new_state, change_timestamp=element._decoded_time)
                element.add_field(field)

            cfx_complete_history.add_field_history_element(element)

    return cfx_complete_history


def profile_load_full():
    all_history: List["CFXEntryCompleteHistory"] = AllCFXCompleteHistoryExport.parse_full_complete_extended_histories_text_file("Input/cfx_extended_history.txt")
    pass


if __name__ == "__main__":
    # import cProfile
    # import re

    # cProfile.run("profile_load_full()")
    profile_load_full()
