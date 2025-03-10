from typing import List
import re


class CFXHistoryField:
    def __init__(self, field_id: str, secondary_label: str, old_state: str, new_state: str):
        self.field_id = field_id.strip()
        self.secondary_label = secondary_label.strip()
        self.old_state = old_state.strip()
        self.new_state = new_state.strip()

    def __repr__(self) -> str:
        return f"<CFXHistoryField field_id={self.field_id} secondary_label={self.secondary_label}>"


class CFXHistoryElement:
    def __init__(self, time: str, schema_rev: str, user_name: str, user_login: str, user_groups: str, action: str, state: str):
        self.time = time.strip()
        self.schema_rev = schema_rev.strip()
        self.user_name = user_name.strip()
        self.user_login = user_login.strip()
        self.user_groups = user_groups.strip()
        self.action = action.strip()
        self.state = state.strip()
        self.fields: List[CFXHistoryField] = []

    def add_field(self, field: CFXHistoryField) -> None:
        self.fields.append(field)

    def __repr__(self) -> str:
        return f"<CFXHistoryElement time={self.time} action={self.action} state={self.state} fields={len(self.fields)}>"


def parse_history(text: str) -> List[CFXHistoryElement]:
    history_elements: List[CFXHistoryElement] = []
    history_blocks = text.split("====START====")[1:]

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
            element = CFXHistoryElement(time, schema_rev, user_name, user_login, user_groups, action, state)

            # Identify and parse fields within the block
            fields_section = block.split("==Fields==")[1].strip()
            field_matches = re.finditer(field_regex, fields_section, re.DOTALL)
            for field_match in field_matches:
                field_id, secondary_label, old_state, new_state = field_match.groups()[:4]
                field = CFXHistoryField(field_id, secondary_label, old_state, new_state)
                element.add_field(field)

            history_elements.append(element)

    return history_elements
