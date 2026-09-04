from pathlib import Path
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum, IntEnum, auto
from typing import Self

from logger import logger_config

from stsloganalyzis.atc import atc_logs


class SimechResFileTypeLine(Enum):
    LOG = "LOG"
    SD_FIELDS = "SD_FIELDS"
    SD = "SD"


class SimechResFileBasicCategories(Enum):
    SCE = "SCE"
    EXE = "EXE"


class SimechResFileKnownScenarioInfo(Enum):
    SCE_COMMENT = "SCE_COMMENT"
    SCE_CONTROL = "SCE_CONTROL"
    OTHER = "OTHER"
    SCE_TEST_RESULT = "SCE_TEST_RESULT"
    SIMULATION_ENDED = "SIMULATION_ENDED"


class SimechResFileFirstColumnsByIndex(IntEnum):
    SIMULATION_TIME_IN_MS = 0
    EXE_OR_SCE = auto()
    LINE_TYPE = auto()
    EQUIPMENT_OR_SIMECH_SCENARIO_INFO = auto()


@dataclass
class SimechResFile(atc_logs.ATCTestFile):

    def __post_init__(self) -> None:
        super().__post_init__()
        self.variables_line_dictionary_by_equipment: dict[str, atc_logs.ATCVariablesLineDictionary] = {}
        self.all_values_raw_lines: list[str] = []
        self.simulation_start_at_timestamp: datetime

        return atc_logs.EquipmentRedundancy.UNKNOWN

    def _compute_simulation_start_at(self, all_raw_lines: list[str]) -> None:
        for raw_line in all_raw_lines:
            if 'SIMULATION_ENDED;"SIMU_START_AT:' in raw_line:
                raw_date_as_str = raw_line.split(SimechResFileKnownScenarioInfo.SIMULATION_ENDED.value + ';"SIMU_START_AT:')[1].replace('"', "").replace(";", "").strip()
                logger_config.print_and_log_info(f"raw_date_as_str found:{raw_date_as_str}")

                # Thu May 28 12:55:42 2026
                date_format = "%a %b %d %H:%M:%S %Y"
                self.simulation_start_at_timestamp = datetime.strptime(raw_date_as_str, date_format)
                logger_config.print_and_log_info(f"simulation_start_at parsed:{self.simulation_start_at_timestamp}")

    @logger_config.stopwatch_decorator(inform_beginning=True, monitor_ram_usage=True)
    def compute_all_variables_states(self) -> None:

        all_raw_lines = self.open_and_get_all_raw_lines()
        self._compute_simulation_start_at(all_raw_lines=all_raw_lines)

        def get_cleaned_equipment_name(full_raw_value: str) -> str:
            # .FROM.PAS_06.VARIABLES[A]
            return full_raw_value.replace(".FROM.", "").replace(".VARIABLES", "_").replace("[", "").replace("]", "")

        def get_cleaned_variable_name(full_raw_value: str) -> str:
            # .FIM_DISPO
            # 'STOP_TRANSMISSION

            if full_raw_value.startswith(".") or full_raw_value.startswith("'"):
                full_raw_value = full_raw_value[1:]

            return full_raw_value

        for line_number, raw_line in enumerate(all_raw_lines):

            try:
                raw_line_split = raw_line.split(atc_logs.ATC_LOG_FILES_FIELDS_SEPARATOR)
                line_simulation_time_in_ms_since_beginning = int(raw_line_split[SimechResFileFirstColumnsByIndex.SIMULATION_TIME_IN_MS])

                if raw_line_split[SimechResFileFirstColumnsByIndex.LINE_TYPE] == SimechResFileTypeLine.SD_FIELDS.value:
                    equipment_name = get_cleaned_equipment_name(raw_line_split[SimechResFileFirstColumnsByIndex.EQUIPMENT_OR_SIMECH_SCENARIO_INFO])

                    if self.atc_test_result.is_equipment_name_allowed_for_creation(equipment_name):

                        logger_config.print_and_log_info_if(
                            (equipment_name in self.variables_line_dictionary_by_equipment),
                            (
                                f"Redefine variables for {equipment_name}, previously {len(self.variables_line_dictionary_by_equipment[equipment_name].all_fields_names)} variables"
                                if equipment_name in self.variables_line_dictionary_by_equipment
                                else "NA"
                            ),
                        )
                        raw_useful_values = [get_cleaned_variable_name(raw_variable) for raw_variable in raw_line_split[SimechResFileFirstColumnsByIndex.EQUIPMENT_OR_SIMECH_SCENARIO_INFO.value + 1 :]]
                        self.variables_line_dictionary_by_equipment[equipment_name] = atc_logs.ATCVariablesLineDictionary(all_fields_names=raw_useful_values)
                        logger_config.print_and_log_info(f"For {equipment_name}, {len(raw_useful_values)} variables found")
                elif raw_line_split[SimechResFileFirstColumnsByIndex.LINE_TYPE] == SimechResFileTypeLine.SD.value:
                    equipment_name = get_cleaned_equipment_name(raw_line_split[SimechResFileFirstColumnsByIndex.EQUIPMENT_OR_SIMECH_SCENARIO_INFO])
                    if self.atc_test_result.is_equipment_name_allowed_for_creation(equipment_name):

                        raw_useful_values = raw_line_split[SimechResFileFirstColumnsByIndex.EQUIPMENT_OR_SIMECH_SCENARIO_INFO.value + 1 :]
                        all_fields_names_and_raw_values = self.variables_line_dictionary_by_equipment[equipment_name].get_all_fields_names_and_values_in_data_raw_fields(
                            all_raw_values=raw_useful_values, test_result=self.atc_test_result
                        )
                        fix_specific_fields_values(all_fields_names_and_raw_values)

                        equipment = self.atc_test_result.get_or_create_equipment_by_name_if_allowed(equipment_name)
                        if equipment:
                            time_since_simulation_start = self.simulation_start_at_timestamp + timedelta(milliseconds=line_simulation_time_in_ms_since_beginning)

                            self.create_result_line_if_needed(
                                line_number=line_number,
                                time_according_to_simulation_start=time_since_simulation_start,
                                equipment=equipment,
                                all_fields_names_and_raw_values=all_fields_names_and_raw_values,
                            )
            except ValueError as val_err:
                logger_config.print_and_log_exception(val_err)
                logger_config.print_and_log_error(f"Could not parse line number {line_number} in {self.file_name} ({self.file_full_path})")


def fix_specific_fields_values(raw_variable_values: dict[str, str]) -> int:
    number_of_fixes_applied = _fix_pae_temps_cycle_cyclos_fields_values(raw_variable_values) + _fix_pags_temps_cycle_cyclos_fields_values(raw_variable_values)
    return number_of_fixes_applied


def _fix_pae_temps_cycle_cyclos_fields_values(raw_variable_values: dict[str, str]) -> int:
    number_of_fixes_applied = 0
    # ST_US_MS             calcule 1 / 10000 * VAL + 0 en  s
    pae_temps_cycle_fields_names_with_unit_in_value = [
        "STAB_CPT1",
        "STAB_CPT2",
        "STAB_CPT3",
        "STAB_CPTM1",
        "STAB_CPTM2",
        "STAB_CPTM3",
    ]
    for pae_temps_cycle_field_name_with_unit_in_value in pae_temps_cycle_fields_names_with_unit_in_value:
        if pae_temps_cycle_field_name_with_unit_in_value in raw_variable_values:
            inital_str_value = raw_variable_values[pae_temps_cycle_field_name_with_unit_in_value]
            inital_str_value = inital_str_value.replace(" ms", "")
            intial_float_value = float(inital_str_value)
            raw_variable_values[pae_temps_cycle_field_name_with_unit_in_value] = str(round(intial_float_value * 100, 2))

    pass

    return number_of_fixes_applied


def _fix_pags_temps_cycle_cyclos_fields_values(raw_variable_values: dict[str, str]) -> int:
    number_of_fixes_applied = 0
    for raw_variable_name, _ in raw_variable_values.items():
        if raw_variable_name.startswith("TEMPS_AS"):
            inital_str_value = raw_variable_values[raw_variable_name]
            intial_int_value = int(inital_str_value)
            raw_variable_values[raw_variable_name] = str(intial_int_value // 10)
            number_of_fixes_applied += 1
    return number_of_fixes_applied


class SimechResTestResult(atc_logs.ATCTestResult):

    class Builder(atc_logs.ATCTestResult.Builder):

        def __init__(self, label: str, environment_name: str = "") -> None:
            super().__init__(atc_test_result_created=SimechResTestResult(label, environment_name))

        def add_file(self, file_full_path: str | Path) -> Self:
            self._atc_test_result_created.all_atc_test_files.append(
                SimechResFile(
                    atc_test_result=self._atc_test_result_created,
                    file_full_path=file_full_path,
                )
            )
            return self
