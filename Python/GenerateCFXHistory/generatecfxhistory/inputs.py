import datetime
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Set, cast

import pandas as pd
from common import file_utils, string_utils
from logger import logger_config

from generatecfxhistory import conversions, role, utils
from generatecfxhistory.constants import (
    ActionType,
    Category,
    RejectionCause,
    RequestType,
    SecurityRelevant,
    State,
)

if TYPE_CHECKING:
    from generatecfxhistory.cfx import ChampFXLibrary

from abc import ABC, abstractmethod

DEFAULT_CHAMPFX_DETAILS_EXCEL_FILE_FULL_PATH: str = "../Input/extract_cfx_details.xlsx"
DEFAULT_CHAMPFX_STATES_CHANGES_EXCEL_FILE_FULL_PATH: str = "../Input/extract_cfx_change_state.xlsx"
DEFAULT_CHAMPFX_EXTENDED_HISTORY_FILE_FULL_PATH: str = "../Input/cfx_extended_history.txt"
DEFAULT_USER_AND_ROLE_DATA_FILE_FULL_PATH: str = "Input/role_data_next_ats.txt"


@dataclass
class ChampFxCreationData:
    cfx_identifier: str
    alternative_cfx_identifier: str
    state: State
    fixed_implemented_in_subsystem: Optional[role.SubSystem]
    fixed_implemented_in_config_unit: str
    system_structure_subsystem: role.SubSystem
    system_structure_config_unit: str
    submit_date: datetime.datetime
    cfx_project_name: str
    safety_relevant: Optional[bool]
    security_relevant: SecurityRelevant
    rejection_cause: Optional[RejectionCause]
    category: Category
    current_owner: role.CfxUser
    request_type: RequestType


@dataclass
class ChangeStateCreationData:
    cfx_identifier: str
    old_state: State
    new_state: State
    action_type: ActionType
    timestamp: datetime.datetime


@dataclass
class ChampFxInputs(ABC):
    user_and_role_data_text_file_full_path: Optional[str]
    _cfx_extended_history_files_contents: List[str]

    @abstractmethod
    def get_all_champfx_entry_creation_data(self, cfx_library: "ChampFXLibrary") -> List["ChampFxCreationData"]:
        pass

    @abstractmethod
    def get_all_change_state_creation_data(self, cfx_library: "ChampFXLibrary") -> List["ChangeStateCreationData"]:
        pass


@dataclass
class ChampFxInputsWithFiles(ChampFxInputs):
    _champfx_details_excel_files_full_data_frames: Dict[str, pd.DataFrame]
    _champfx_states_changes_excel_files_data_frames: Dict[str, pd.DataFrame]

    def print_all_possible_values_by_column(self) -> Dict[str, Any]:
        all_possible_values_by_column = self.get_all_possible_values_by_column()

        logger_config.print_and_log_info("All states:" + str(all_possible_values_by_column["State"]))
        logger_config.print_and_log_info("All Category:" + str(all_possible_values_by_column["Category"]))
        logger_config.print_and_log_info("All RejectionCause:" + str(all_possible_values_by_column["RejectionCause"]))
        logger_config.print_and_log_info("All history.old_state:" + str(all_possible_values_by_column["history.old_state"]))
        logger_config.print_and_log_info("All history.new_state:" + str(all_possible_values_by_column["history.new_state"]))

        all_kind_of_states = all_possible_values_by_column["State"] | all_possible_values_by_column["history.old_state"] | all_possible_values_by_column["history.new_state"]
        logger_config.print_and_log_info("all_kind_of_states:" + str(all_kind_of_states))

        return all_possible_values_by_column

    def get_all_possible_values_by_column(self) -> Dict[str, Set[str]]:

        all_possible_values_by_column: Dict[str, Any] = {}
        combined_data_frames_list = self._champfx_details_excel_files_full_data_frames | self._champfx_states_changes_excel_files_data_frames
        for _, cfx_details_data_frame in combined_data_frames_list.items():
            for col in cfx_details_data_frame.columns:
                # Get the set of values for this column from the current DataFrame
                values: Set[str] = set(cfx_details_data_frame[col])
                if col in all_possible_values_by_column:
                    # Update the current set with the new values
                    all_possible_values_by_column[col].update(values)
                else:
                    # Initialize the set if the column is not present in the dictionary
                    all_possible_values_by_column[col] = values

        return all_possible_values_by_column

    @staticmethod
    def convert_champfx_security_relevant(raw_str_value: str) -> SecurityRelevant:
        if type(raw_str_value) is not str:
            return SecurityRelevant.UNDEFINED
        raw_security_relevant_valid_str_value: Optional[str] = string_utils.text_to_valid_enum_value_text(raw_str_value)
        return SecurityRelevant.UNDEFINED if raw_security_relevant_valid_str_value is None else SecurityRelevant[raw_security_relevant_valid_str_value]

    @staticmethod
    def convert_champfx_rejection_cause(raw_str_value: str) -> Optional[RejectionCause]:
        if type(raw_str_value) is not str:
            return None
        raw_valid_str_value: Optional[str] = string_utils.text_to_valid_enum_value_text(raw_str_value)
        try:
            return RejectionCause.NONE if raw_valid_str_value is None else RejectionCause[raw_valid_str_value]
        except KeyError as key_error:
            logger_config.print_and_log_exception(key_error)
            logger_config.print_and_log_error(f"RejectionCause {raw_valid_str_value} not supported")
            return RejectionCause.TO_BE_ADDED_YDA

    @staticmethod
    def convert_champfx_request_type(raw_str_value: str) -> Optional[RequestType]:
        assert isinstance(raw_str_value, str), f"RequestType {raw_str_value} is not string"

        raw_valid_str_value: Optional[str] = string_utils.text_to_valid_enum_value_text(raw_str_value)

        try:
            return cast(RequestType, RequestType[raw_valid_str_value])
        except KeyError as key_error:
            logger_config.print_and_log_exception(key_error)
            logger_config.print_and_log_error(f"RequestType {raw_valid_str_value} not supported")
            return None

    @staticmethod
    def convert_champfx_category(raw_str_value: str) -> Optional[Category]:
        if type(raw_str_value) is not str:
            return Category.NO_CATEGORY_DEFINED
        raw_valid_str_value: str = string_utils.text_to_valid_enum_value_text(raw_str_value)
        try:
            return Category[raw_valid_str_value]
        except KeyError as key_error:
            logger_config.print_and_log_exception(key_error)
            logger_config.print_and_log_error(f"Category {raw_valid_str_value} not supported")
            return None

    @staticmethod
    def to_optional_boolean(raw_value: str) -> Optional[bool]:
        if raw_value == "Yes":
            return True
        elif raw_value == "No":
            return False
        return None

    @staticmethod
    def build_champfx_entry_creation_data_with_row(row: pd.Series, cfx_library: "ChampFXLibrary") -> ChampFxCreationData:
        cfx_identifier = row["id"]
        alternative_cfx_identifier = row["CFXID"]
        state: State = conversions.convert_state(row["State"])

        raw_project: str = cast(str, row["Project"])
        project_name = string_utils.text_to_valid_enum_value_text(raw_project)

        cfx_project_name = project_name

        raw_safety_relevant: str = row["SafetyRelevant"]
        safety_relevant: Optional[bool] = ChampFxInputsWithFiles.to_optional_boolean(raw_safety_relevant)

        raw_security_relevant: str = row["SecurityRelevant"]
        security_relevant = ChampFxInputsWithFiles.convert_champfx_security_relevant(raw_security_relevant)

        raw_rejection_cause: str = row["RejectionCause"]
        rejection_cause = ChampFxInputsWithFiles.convert_champfx_rejection_cause(raw_rejection_cause)
        if rejection_cause == RejectionCause.TO_BE_ADDED_YDA:
            logger_config.print_and_log_error(f"{cfx_identifier} project {raw_project}: RejectionCause {raw_rejection_cause} not supported")

        raw_request_type = row["RequestType"]
        request_type = ChampFxInputsWithFiles.convert_champfx_request_type(raw_request_type)
        if request_type is None:
            logger_config.print_and_log_error(f"{cfx_identifier} project {raw_project}: Request Type {raw_request_type} not supported")
            request_type = RequestType.TO_BE_ADDED_YDA

        raw_category: str = row["Category"]
        category = ChampFxInputsWithFiles.convert_champfx_category(raw_category) if raw_category else None
        if category is None:
            logger_config.print_and_log_error(f"{cfx_identifier} project {raw_project}: Category {raw_category} not supported")
            category = Category.TO_BE_ADDED_YDA

        current_owner_raw: str = row["CurrentOwner.FullName"]
        assert cfx_library.cfx_users_library.has_user_by_full_name(current_owner_raw), cfx_identifier
        current_owner: role.CfxUser = cfx_library.cfx_users_library.get_cfx_user_by_full_name(current_owner_raw)

        fixed_implemented_in_config_unit: str = row["FixedImplementedIn"]
        fixed_implemented_in_subsystem: Optional[role.SubSystem] = (
            cfx_library.cfx_users_library.get_subsystem_from_champfx_fixed_implemented_in(fixed_implemented_in_config_unit) if fixed_implemented_in_config_unit else None
        )

        submit_date_raw: str = row["SubmitDate"]
        submit_date: datetime.datetime = cast(datetime.datetime, utils.convert_champfx_extract_date(submit_date_raw))
        assert submit_date is not None, f"{cfx_identifier} has invalid submit date {submit_date_raw}"

        system_structure_config_unit: str = row["SystemStructure"]
        temptative_system_structure: Optional[role.SubSystem] = cfx_library.cfx_users_library.get_subsystem_from_champfx_fixed_implemented_in(system_structure_config_unit)

        assert temptative_system_structure, f"{cfx_identifier} could not decode system structure {system_structure_config_unit}"
        system_structure: role.SubSystem = temptative_system_structure

        champfx_creational_data = ChampFxCreationData(
            cfx_identifier=cfx_identifier,
            alternative_cfx_identifier=alternative_cfx_identifier,
            state=state,
            fixed_implemented_in_subsystem=fixed_implemented_in_subsystem,
            system_structure_config_unit=system_structure_config_unit,
            fixed_implemented_in_config_unit=fixed_implemented_in_config_unit,
            system_structure_subsystem=system_structure,
            submit_date=submit_date,
            cfx_project_name=cfx_project_name,
            safety_relevant=safety_relevant,
            security_relevant=security_relevant,
            rejection_cause=rejection_cause,
            category=category,
            current_owner=current_owner,
            request_type=request_type,
        )
        return champfx_creational_data

    def get_all_champfx_entry_creation_data(self, cfx_library: "ChampFXLibrary") -> List["ChampFxCreationData"]:
        all_champfx_creation_data: List["ChampFxCreationData"] = []
        for i, (cfx_details_file_name, cfx_details_data_frame) in enumerate(self._champfx_details_excel_files_full_data_frames.items()):
            with logger_config.stopwatch_with_label(
                label=f"Process {i+1}th / {len(self._champfx_details_excel_files_full_data_frames)} ({round((i+1)/len(self._champfx_details_excel_files_full_data_frames)*100,2)}%) cfx detail file {cfx_details_file_name} with length {len(cfx_details_data_frame)}",
                monitor_ram_usage=True,
            ):
                for _, row in cfx_details_data_frame.iterrows():
                    cfx_id = row["id"]

                    if cfx_id not in cfx_library.champfx_entry_by_id:
                        if cfx_library.ignore_cfx_creation_errors:
                            try:
                                champfx_creation_data = ChampFxInputsWithFiles.build_champfx_entry_creation_data_with_row(row=row, cfx_library=cfx_library)
                                all_champfx_creation_data.append(champfx_creation_data)
                            except Exception as ex:
                                logger_config.print_and_log_exception(ex)
                                logger_config.print_and_log_error(f"Error when creating cfx {cfx_id}")
                                cfx_library.failed_to_create_cfx_ids.append(cfx_id)
                        else:
                            champfx_creation_data = ChampFxInputsWithFiles.build_champfx_entry_creation_data_with_row(row=row, cfx_library=cfx_library)
                            all_champfx_creation_data.append(champfx_creation_data)

        return all_champfx_creation_data

    def get_all_change_state_creation_data(self, cfx_library: "ChampFXLibrary") -> List[ChangeStateCreationData]:

        all_change_state_creation_data: List[ChangeStateCreationData] = []

        for i, (cfx_states_changes_file_name, cfx_states_changes_data_frame) in enumerate(self._champfx_states_changes_excel_files_data_frames.items()):
            with logger_config.stopwatch_with_label(
                label=f"Process {i+1}th / {len(self._champfx_states_changes_excel_files_data_frames)} ({round((i+1)/len(self._champfx_states_changes_excel_files_data_frames)*100,2)}%) state change file {cfx_states_changes_file_name} with length {len(cfx_states_changes_data_frame)}",
                monitor_ram_usage=True,
            ):
                logger_config.print_and_log_info(f"Process {cfx_states_changes_file_name} with size {len(cfx_states_changes_data_frame)}      {cfx_states_changes_data_frame.size}")

                for _, row in cfx_states_changes_data_frame.iterrows():
                    cfx_id = row["id"]

                    if cfx_library.is_cfx_with_id_exists(cfx_id=cfx_id):
                        cfx_request = cfx_library.get_cfx_by_id(cfx_id)
                        history_raw_old_state: str = row["history.old_state"]
                        history_raw_new_state: str = row["history.new_state"]
                        history_raw_action_timestamp_str = row["history.action_timestamp"]
                        history_raw_action_name: str = row["history.action_name"]

                        try:
                            if type(history_raw_old_state) is not str:
                                logger_config.print_and_log_warning(
                                    f"{cfx_id} project {cfx_request._cfx_project_name} ignore change state from {history_raw_old_state} to {history_raw_new_state} {history_raw_action_timestamp_str}  {history_raw_action_name} "
                                )
                                continue

                            old_state: State = conversions.convert_state(history_raw_old_state)
                            new_state: State = conversions.convert_state(history_raw_new_state)
                            action_timestamp = utils.convert_champfx_extract_date(history_raw_action_timestamp_str)
                            assert action_timestamp
                            history_raw_action_name_upper = history_raw_action_name.upper()
                            action_type = ActionType[history_raw_action_name_upper]

                            current_change_state_creation_data = ChangeStateCreationData(
                                cfx_identifier=cfx_id, old_state=old_state, new_state=new_state, action_type=action_type, timestamp=action_timestamp
                            )
                            all_change_state_creation_data.append(current_change_state_creation_data)

                        except Exception as ex:
                            logger_config.print_and_log_exception(ex)
                            logger_config.print_and_log_error(
                                f"Error when creating state change for {cfx_id} project {cfx_request._cfx_project_name} ignore change state from {history_raw_old_state} to {history_raw_new_state} {history_raw_action_timestamp_str}  {history_raw_action_name}"
                            )

        return all_change_state_creation_data


class ChampFxInputsWithFilesBuilder:
    def __init__(self) -> None:

        self.champfx_details_excel_files_full_paths: List[str] = []

        self.champfx_states_changes_excel_files_full_paths: List[str] = []

        self.cfx_extended_history_files_full_paths: List[str] = []

        self.user_and_role_data_text_file_full_path: Optional[str] = None

    def add_champfx_details_excel_file_full_path(self, champfx_details_excel_file_full_path: str) -> "ChampFxInputsWithFilesBuilder":
        self.champfx_details_excel_files_full_paths.append(champfx_details_excel_file_full_path)
        return self

    def add_champfx_details_excel_files_by_directory_and_file_name_mask(self, directory_path: str, filename_pattern: str) -> "ChampFxInputsWithFilesBuilder":
        files_found = file_utils.get_files_by_directory_and_file_name_mask(directory_path=directory_path, filename_pattern=filename_pattern)
        for file in files_found:
            self.add_champfx_details_excel_file_full_path(file)
        # [self.add_champfx_details_excel_file_full_path(file) for file in files_found]
        return self

    def add_champfx_states_changes_excel_file_full_path(self, champfx_states_changes_excel_file_full_path: str) -> "ChampFxInputsWithFilesBuilder":
        self.champfx_states_changes_excel_files_full_paths.append(champfx_states_changes_excel_file_full_path)
        return self

    def add_champfx_states_changes_excel_files_by_directory_and_file_name_mask(self, directory_path: str, filename_pattern: str) -> "ChampFxInputsWithFilesBuilder":
        files_found = file_utils.get_files_by_directory_and_file_name_mask(directory_path=directory_path, filename_pattern=filename_pattern)
        list(map(self.add_champfx_states_changes_excel_file_full_path, files_found))
        return self

    def add_cfx_extended_history_file_full_path(self, cfx_extended_history_file_full_path: str) -> "ChampFxInputsWithFilesBuilder":
        self.cfx_extended_history_files_full_paths.append(cfx_extended_history_file_full_path)
        return self

    def set_user_and_role_data_text_file_full_path(self, user_and_role_data_text_file_full_path: str) -> "ChampFxInputsWithFilesBuilder":
        self.user_and_role_data_text_file_full_path = user_and_role_data_text_file_full_path
        return self

    def set_default_files(self) -> "ChampFxInputsWithFilesBuilder":
        self.add_champfx_details_excel_file_full_path(DEFAULT_CHAMPFX_DETAILS_EXCEL_FILE_FULL_PATH)
        self.add_champfx_states_changes_excel_file_full_path(DEFAULT_CHAMPFX_STATES_CHANGES_EXCEL_FILE_FULL_PATH)
        self.add_cfx_extended_history_file_full_path(DEFAULT_CHAMPFX_EXTENDED_HISTORY_FILE_FULL_PATH)
        self.set_user_and_role_data_text_file_full_path(DEFAULT_USER_AND_ROLE_DATA_FILE_FULL_PATH)
        return self

    def build(self) -> ChampFxInputsWithFiles:
        champfx_details_excel_files_full_data_frames: Dict[str, pd.DataFrame] = dict()
        champfx_states_changes_excel_files_data_frames: Dict[str, pd.DataFrame] = dict()
        cfx_extended_history_files_contents: List[str] = []

        with logger_config.stopwatch_with_label("Build cfx inputs", monitor_ram_usage=True):

            before_cfx_inputs_opening_ram_rss = logger_config.print_and_log_current_ram_usage(prefix="before cfx inputs opening")
            with logger_config.stopwatch_with_label(f"Open {len(self.champfx_details_excel_files_full_paths)} cfx details files", monitor_ram_usage=True):
                for i, champfx_details_excel_file_full_path in enumerate(self.champfx_details_excel_files_full_paths):
                    with logger_config.stopwatch_with_label(
                        f"Open {i+1} / {len(self.champfx_details_excel_files_full_paths)} ({round((i+1)/len(self.champfx_details_excel_files_full_paths)*100,2)}%) cfx details excel file {champfx_details_excel_file_full_path}"
                    ):
                        champfx_details_excel_files_full_data_frames[champfx_details_excel_file_full_path] = pd.read_excel(champfx_details_excel_file_full_path)

            with logger_config.stopwatch_with_label(f"Open {len(self.champfx_states_changes_excel_files_full_paths)} cfx states changes files", monitor_ram_usage=True):
                for i, champfx_states_changes_excel_file_full_path in enumerate(self.champfx_states_changes_excel_files_full_paths):
                    with logger_config.stopwatch_with_label(
                        f"Open {i+1} / {len(self.champfx_states_changes_excel_files_full_paths)} ({(i+1)/len(self.champfx_states_changes_excel_files_full_paths)*100:.2f}%) cfx state changes excel file {champfx_states_changes_excel_file_full_path}"
                    ):
                        champfx_states_changes_excel_files_data_frames[champfx_states_changes_excel_file_full_path] = pd.read_excel(champfx_states_changes_excel_file_full_path)

            with logger_config.stopwatch_with_label(f"Open {len(self.cfx_extended_history_files_full_paths)} cfx extended history files", monitor_ram_usage=True):
                for i, cfx_extended_history_file_full_path in enumerate(self.cfx_extended_history_files_full_paths):
                    with logger_config.stopwatch_with_label(f"Open {i+1} / {len(self.cfx_extended_history_files_full_paths)} cfx extended history file {cfx_extended_history_file_full_path}"):
                        with open(cfx_extended_history_file_full_path, "r", encoding="utf-8") as all_cfx_extended_history_text_file:
                            cfx_extended_history_files_contents.append(all_cfx_extended_history_text_file.read())

            cfx_inputs = ChampFxInputsWithFiles(
                _champfx_details_excel_files_full_data_frames=champfx_details_excel_files_full_data_frames,
                _champfx_states_changes_excel_files_data_frames=champfx_states_changes_excel_files_data_frames,
                _cfx_extended_history_files_contents=cfx_extended_history_files_contents,
                user_and_role_data_text_file_full_path=self.user_and_role_data_text_file_full_path,
            )
            logger_config.print_and_log_current_ram_usage(
                prefix="After cfx inputs opened", previous_reference_rss_value_and_label=[before_cfx_inputs_opening_ram_rss, "Delta compared to before cfx inputs"]
            )
            return cfx_inputs
