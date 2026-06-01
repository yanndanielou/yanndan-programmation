import json
import re
from enum import Enum
from typing import Dict, List


class WhiteOrBlackListFilterType(Enum):
    WHITELIST = "WHITELIST"
    BLACKLIST = "BLACKLIST"


class StringFilterType(Enum):
    EQUALS_TO = "EQUALS_TO"
    BEGIN_WITH_STRING = "BEGIN_WITH_STRING"
    MATCHES_REGEX = "MATCHES_REGEX"
    CONTAINS = "CONTAINS"


class StringFieldValueBasedFilter:

    def __init__(self, white_or_black_list: WhiteOrBlackListFilterType, field_values: List[str], filter_type: StringFilterType) -> None:
        super().__init__()
        self.white_or_black_list = white_or_black_list
        self.is_whitelist = white_or_black_list == WhiteOrBlackListFilterType.WHITELIST
        self.filter_type = filter_type
        self.filter_field_values = field_values
        self.rejected_count: int = 0
        self.rejected_count_by_item: Dict[str, int] = dict()

    def do_passes(self, string_value: str) -> bool:
        try:

            match = False
            if self.filter_type == StringFilterType.EQUALS_TO:
                match = string_value in self.filter_field_values
            elif self.filter_type == StringFilterType.CONTAINS:
                match = any(filter_field_value in string_value for filter_field_value in self.filter_field_values)
            elif self.filter_type == StringFilterType.BEGIN_WITH_STRING:
                match = any(string_value.startswith(filter_field_value) for filter_field_value in self.filter_field_values)
            elif self.filter_type == StringFilterType.MATCHES_REGEX:
                match = any(bool(re.search(filter_field_value, string_value)) for filter_field_value in self.filter_field_values)
            else:
                assert False, f"Not handled {self.filter_type}"

            ret = match if self.is_whitelist else not match
            if not ret:
                if string_value not in self.rejected_count_by_item:
                    self.rejected_count_by_item[string_value] = 0

                self.rejected_count_by_item[string_value] += 1

            return ret
        except (TypeError, ValueError, json.JSONDecodeError, KeyError):
            return False
