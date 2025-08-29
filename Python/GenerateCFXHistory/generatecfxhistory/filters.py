import datetime
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, List, Optional, Set, cast

from common import string_utils
from logger import logger_config

from generatecfxhistory.role import SubSystem

if TYPE_CHECKING:
    from generatecfxhistory.cfx import ChampFXEntry


class ChampFXtSaticCriteriaFilter(ABC):
    def __init__(self, label: str = "") -> None:
        self._cache_result_by_cfx: dict["ChampFXEntry", bool] = dict()
        self._number_of_results_obtained_by_cache_usage = 0
        self._label = label

    @abstractmethod
    def match_cfx_entry_without_cache(self, cfx_entry: "ChampFXEntry") -> bool:
        """This method must be overridden in child classes."""

    def match_cfx_entry_with_cache(self, cfx_entry: "ChampFXEntry") -> bool:
        if cfx_entry in self._cache_result_by_cfx:
            self._number_of_results_obtained_by_cache_usage += 1
            return self._cache_result_by_cfx[cfx_entry]

        new_result_computed = self.match_cfx_entry_without_cache(cfx_entry)
        self._cache_result_by_cfx[cfx_entry] = new_result_computed
        return new_result_computed

    @property
    def label(self) -> str:
        return self._label


class ChampFXWhitelistFilter(ChampFXtSaticCriteriaFilter, ABC):
    @abstractmethod
    def __init__(
        self,
        label: Optional[str] = None,
    ):
        super().__init__()
        self._cfx_to_treat_whitelist_ids: Set[str] = set()
        self._label: str = "" if label is None else label

    def match_cfx_entry_without_cache(self, cfx_entry: "ChampFXEntry") -> bool:
        return self.match_cfx_identifier(cfx_entry.cfx_identifier)

    def match_cfx_identifier(self, cfx_identifier: str) -> bool:
        return cfx_identifier in self._cfx_to_treat_whitelist_ids


class ChampFXWhiteListBasedOnListFilter(ChampFXWhitelistFilter):
    def __init__(
        self,
        cfx_to_treat_ids: Set[str] | List[str],
        label: Optional[str] = None,
    ):
        super().__init__(label=label)

        if label is None:
            self._label = f"list {len(cfx_to_treat_ids)} white listed"

        self._cfx_to_treat_whitelist_ids.update(cfx_to_treat_ids)


class ChampFXWhiteListBasedOnFileFilter(ChampFXWhitelistFilter):
    def __init__(self, cfx_to_treat_whitelist_text_file_full_path: str, label: Optional[str] = None):
        super().__init__(label=label)

        self._cfx_to_treat_whitelist_text_file_full_path: str = cfx_to_treat_whitelist_text_file_full_path

        if label is None:
            self._label: str = self._cfx_to_treat_whitelist_text_file_full_path
            self._label = string_utils.right_part_after_last_occurence(self._label, "/")
            self._label = string_utils.right_part_after_last_occurence(self._label, "\\")
            self._label += " "

        with logger_config.stopwatch_with_label(f"Load ChampFXWhiteListBasedOnFileFilter {cfx_to_treat_whitelist_text_file_full_path}"):
            with open(self._cfx_to_treat_whitelist_text_file_full_path, "r", encoding="utf-8") as cfx_known_by_cstmr_text_file:
                self._cfx_to_treat_whitelist_ids.update([line.strip() for line in cfx_known_by_cstmr_text_file.readlines()])
        logger_config.print_and_log_info(f"Number of cfx_to_treat_whitelist_ids:{len(self._cfx_to_treat_whitelist_ids)}")


class ChampFXFieldFilter(ChampFXtSaticCriteriaFilter, ABC):

    @abstractmethod
    def __init__(
        self,
        field_name: str,
        field_label: str,
        field_accepted_values: Optional[List[Any]] = None,
        field_forbidden_values: Optional[List[Any]] = None,
        field_accepted_contained_texts: Optional[List[Any]] = None,
        field_forbidden_contained_texts: Optional[List[Any]] = None,
        forced_label: Optional[str] = None,
    ) -> None:
        super().__init__()
        self.field_name = field_name
        self.field_label = field_label
        self.field_accepted_values = field_accepted_values
        self.field_forbidden_values = field_forbidden_values
        self.field_accepted_contained_texts = field_accepted_contained_texts
        self.field_forbidden_contained_texts = field_forbidden_contained_texts

        if forced_label:
            self._label = forced_label

        else:
            label: str = f"{self.field_label}"

            if self.field_accepted_values:
                label = f"{label} among {self.field_accepted_values}" if len(self.field_accepted_values) > 1 else f"{label} {self.field_accepted_values}"
            elif self.field_forbidden_values:
                label = f"{label} without {self.field_forbidden_values}"
            elif self.field_accepted_contained_texts:
                label = (
                    f"{label} contains texts {self.field_accepted_contained_texts}" if len(self.field_accepted_contained_texts) > 1 else f"{label} contains text {self.field_accepted_contained_texts}"
                )
            elif self.field_forbidden_contained_texts:
                label = (
                    f"{label} does not contain any of text {self.field_forbidden_contained_texts}"
                    if len(self.field_forbidden_contained_texts) > 1
                    else f"{label} does not contain {self.field_forbidden_contained_texts}"
                )

            label = label.translate({ord(i): None for i in "'[]"})
            self._label = label

    def match_cfx_entry_without_cache(self, cfx_entry: "ChampFXEntry") -> bool:
        attribute_entry = getattr(cfx_entry, self.field_name)
        if self.field_accepted_values is not None:
            return attribute_entry in self.field_accepted_values
        elif self.field_forbidden_values:
            return attribute_entry not in self.field_forbidden_values
        elif self.field_accepted_contained_texts:
            match_found = any(text in attribute_entry for text in self.field_accepted_contained_texts)
            return match_found
        elif self.field_forbidden_contained_texts:
            match_found = any(text in attribute_entry for text in self.field_forbidden_contained_texts)
            return not match_found
        else:
            return False


class ChampFxFilterFieldSecurityRelevant(ChampFXFieldFilter):
    def __init__(self, field_accepted_values: Optional[List[Any]] = None, field_forbidden_values: Optional[List[Any]] = None, forced_label: Optional[str] = None) -> None:
        super().__init__(
            field_name="_security_relevant",
            field_label="Security Relevant",
            field_accepted_values=field_accepted_values,
            field_forbidden_values=field_forbidden_values,
            forced_label=forced_label,
        )


class ChampFxFilterFieldSafetyRelevant(ChampFXFieldFilter):
    def __init__(self, field_accepted_value: Optional[bool] = None, field_forbidden_value: Optional[bool] = None, forced_label: Optional[str] = None) -> None:
        super().__init__(
            field_name="_safety_relevant",
            field_label="Safety Relevant",
            field_accepted_values=[field_accepted_value],
            field_forbidden_values=[field_forbidden_value],
            forced_label=forced_label,
        )


class ChampFxFilterFieldProject(ChampFXFieldFilter):
    def __init__(self, field_accepted_values: Optional[List[str]] = None, field_forbidden_values: Optional[List[str]] = None, forced_label: Optional[str] = None) -> None:
        super().__init__(
            field_name="_cfx_project_name",
            field_label="Project",
            field_accepted_values=field_accepted_values,
            field_forbidden_values=field_forbidden_values,
            forced_label=forced_label,
        )


class ChampFxFilterFieldSubsystem(ChampFXFieldFilter):
    def __init__(self, field_accepted_values: Optional[List[Any]] = None, field_forbidden_values: Optional[List[Any]] = None, forced_label: Optional[str] = None) -> None:
        super().__init__(
            field_name="_subsystem",
            field_label="Subsystem",
            field_accepted_values=field_accepted_values,
            field_forbidden_values=field_forbidden_values,
            forced_label=forced_label,
        )


class ChampFxFilterFieldCategory(ChampFXFieldFilter):
    def __init__(self, field_accepted_values: Optional[List[Any]] = None, field_forbidden_values: Optional[List[Any]] = None, forced_label: Optional[str] = None) -> None:
        super().__init__(
            field_name="_category",
            field_label="Category",
            field_accepted_values=field_accepted_values,
            field_forbidden_values=field_forbidden_values,
            forced_label=forced_label,
        )


class ChampFxFilterFieldType(ChampFXFieldFilter):
    def __init__(self, field_accepted_values: Optional[List[Any]] = None, field_forbidden_values: Optional[List[Any]] = None, forced_label: Optional[str] = None) -> None:
        super().__init__(
            field_name="_request_type",
            field_label="Type",
            field_accepted_values=field_accepted_values,
            field_forbidden_values=field_forbidden_values,
            forced_label=forced_label,
        )


class ChampFxFilterFieldConfigUnit(ChampFXFieldFilter):
    def __init__(
        self,
        field_accepted_values: Optional[List[Any]] = None,
        field_forbidden_values: Optional[List[Any]] = None,
        field_accepted_contained_texts: Optional[List[Any]] = None,
        field_forbidden_contained_texts: Optional[List[Any]] = None,
        forced_label: Optional[str] = None,
    ) -> None:
        super().__init__(
            field_name="_config_unit",
            field_label="Config Unit",
            field_accepted_values=field_accepted_values,
            field_forbidden_values=field_forbidden_values,
            field_accepted_contained_texts=field_accepted_contained_texts,
            field_forbidden_contained_texts=field_forbidden_contained_texts,
            forced_label=forced_label,
        )


@dataclass
class ChampFXRoleAtSpecificDateFilter:
    timestamp: datetime.datetime
    roles_at_date_allowed: List[SubSystem]

    def match_cfx_entry(self, cfx_entry: "ChampFXEntry") -> bool:
        role_at_date = cfx_entry.get_current_role_at_date(self.timestamp)
        return role_at_date in self.roles_at_date_allowed


@dataclass
class ChampFXRoleDependingOnDateFilter:
    roles_at_date_allowed: List[SubSystem]
    label: str = field(init=False)

    def __post_init__(self) -> None:
        label: str = f"{self.roles_at_date_allowed}"
        self.label = label

    def match_cfx_entry(self, cfx_entry: "ChampFXEntry", timestamp: datetime.datetime) -> bool:
        return ChampFXRoleAtSpecificDateFilter(roles_at_date_allowed=self.roles_at_date_allowed, timestamp=timestamp).match_cfx_entry(cfx_entry=cfx_entry)


class ChampFxFilter:

    def __init__(
        self,
        role_depending_on_date_filter: Optional[ChampFXRoleDependingOnDateFilter] = None,
        field_filters: Optional[List[ChampFXtSaticCriteriaFilter]] = None,
        cfx_to_treat_whitelist_text_file_full_path: Optional[str] = None,
        whitelist_filter: Optional[ChampFXWhitelistFilter] = None,
        label: Optional[str] = None,
    ):
        if field_filters is None:
            field_filters = []

        self.role_depending_on_date_filter: Optional[ChampFXRoleDependingOnDateFilter] = role_depending_on_date_filter
        self._field_filters: List[ChampFXtSaticCriteriaFilter] = field_filters
        self._cfx_to_treat_whitelist_text_file_full_path: Optional[str] = cfx_to_treat_whitelist_text_file_full_path
        self._cfx_to_treat_whitelist_ids: Optional[Set[str]] = None
        self.label: str = label if label is not None else ""

        self._static_criteria_filters: List[ChampFXtSaticCriteriaFilter] = self._field_filters

        self._white_list_filter: Optional[ChampFXWhitelistFilter] = (
            ChampFXWhiteListBasedOnFileFilter(cfx_to_treat_whitelist_text_file_full_path) if cfx_to_treat_whitelist_text_file_full_path is not None else whitelist_filter
        )
        if self._white_list_filter is not None:
            self._static_criteria_filters.append(self._white_list_filter)

        self._compute_label()

    def _compute_label(self) -> None:

        label = self.label

        if label is None:
            label = " "
        else:
            label += " "

        if self.role_depending_on_date_filter:
            label = f"{label}role {self.role_depending_on_date_filter.roles_at_date_allowed} per date"

        if len(self._field_filters) > 0:
            label = f"{label}{[field_filter.label for field_filter in self._field_filters]}"

        if self._white_list_filter:
            label = f"{label}{self._white_list_filter.label}"

        label = label.translate({ord(i): None for i in "'[]"})

        self.label = label

    def static_criteria_match_cfx_entry(self, cfx_entry: "ChampFXEntry") -> bool:

        if self._white_list_filter is not None:
            if not self._white_list_filter.match_cfx_entry_with_cache(cfx_entry=cfx_entry):
                return False

        for field_filter in self._field_filters:
            if not field_filter.match_cfx_entry_with_cache(cfx_entry=cfx_entry):
                return False

        return True

    def match_role_depending_on_date_filter_if_filter_exists(self, cfx_entry: "ChampFXEntry", timestamp: Optional[datetime.datetime] = None) -> bool:
        if self.role_depending_on_date_filter:
            if not self.role_depending_on_date_filter.match_cfx_entry(cfx_entry=cfx_entry, timestamp=cast(datetime.datetime, timestamp)):
                return False

        return True

    def match_cfx_entry(self, cfx_entry: "ChampFXEntry", timestamp: Optional[datetime.datetime] = None) -> bool:

        if not self.static_criteria_match_cfx_entry(cfx_entry):
            return False

        if not self.match_role_depending_on_date_filter_if_filter_exists(cfx_entry=cfx_entry, timestamp=cast(datetime.datetime, timestamp)):
            return False

        return True
