import datetime
import statistics
from collections import Counter, OrderedDict
from dataclasses import dataclass
from pathlib import Path
from typing import cast


import numpy
import pandas
from common import (
    pandas_utils,
)
from logger import logger_config

from stsloganalyzis.atc import atc_logs, simech_res
from stsloganalyzis.common import common_filters

OUTPUT_DIRECTORY = "output_temps_cycle"


@dataclass
class InstantTempsCycleVariableState:
    timestamp: datetime.datetime
    value: int | float
    equipment_report: "OneEquipmentReport"
    other_interesting_variables_values_by_name: dict[str, atc_logs.VariableStateTypeWithNone]


def get_other_interesting_variables_names(equipment_type: atc_logs.EquipmentType) -> list[str]:
    if equipment_type == atc_logs.EquipmentType.PAE:
        return [
            "FAS_VF",
            "EBF_VITESSE",
            "FODR_VITODO",
        ]
    return []


def get_min_relevant_value_for_variable(variable_name: str) -> int | None:
    if variable_name.startswith("TEMPS_AS"):
        return 30
    if variable_name.startswith("STAB_CPT"):
        return 30
    return None


def get_threshold_high_for_variable(variable: atc_logs.Variable) -> int | None:
    return (
        180
        if variable.equipment.equipment_type is atc_logs.EquipmentType.PAL and variable.name.startswith("TEMPS_AS")
        else (
            230
            if variable.equipment.equipment_type is atc_logs.EquipmentType.PAS and variable.name.startswith("TEMPS_AS")
            else 110 if variable.equipment.equipment_type is atc_logs.EquipmentType.PAE and variable.name.startswith("STAB_CPT") else None
        )
    )


def get_threshold_very_high_for_variable(variable: atc_logs.Variable) -> int | None:
    return (
        200
        if variable.equipment.equipment_type is atc_logs.EquipmentType.PAL and variable.name.startswith("TEMPS_AS")
        else (
            260
            if variable.equipment.equipment_type is atc_logs.EquipmentType.PAS and variable.name.startswith("TEMPS_AS")
            else 120 if variable.equipment.equipment_type is atc_logs.EquipmentType.PAE and variable.name.startswith("STAB_CPT") else None
        )
    )


def get_temps_cycle_variables_names_by_equipment(equipment: atc_logs.Equipment) -> list[str]:
    return ["TEMPS_AS"] if equipment.equipment_type in [atc_logs.EquipmentType.PAL, atc_logs.EquipmentType.PAS, atc_logs.EquipmentType.MES] else ["STAB_CPT1"]


def get_other_interesting_variables_at_one_atc_log_instant_variable_state(
    atc_log_instant_variable_state: atc_logs.InstantVariableState, other_interesting_variables_names: list[str]
) -> dict[str, atc_logs.VariableStateTypeWithNone]:
    ret: dict[str, atc_logs.VariableStateTypeWithNone] = {}
    for other_interesting_variables_name in other_interesting_variables_names:
        interesting_instant_variable_states = [
            interesting_instant_variable_state
            for interesting_instant_variable_state in atc_log_instant_variable_state.result_line.all_variables_states
            if interesting_instant_variable_state.variable.name == other_interesting_variables_name
        ]
        for interesting_instant_variable_state in interesting_instant_variable_states:
            ret[interesting_instant_variable_state.variable.name] = interesting_instant_variable_state.best_value

    return ret


class OneEquipmentReport:

    def __init__(self, atc_test_result: atc_logs.ATCTestResult, variable: atc_logs.Variable) -> None:
        super().__init__()
        logger_config.print_and_log_info(
            f"Create report for {atc_test_result.label} {variable.equipment.name} {variable.name} from {atc_test_result.all_atc_test_files[0].file_name}", do_not_print=True
        )

        self.variable_name = variable.name
        self.equipment_name = variable.equipment.name
        self.equipment_type = variable.equipment.equipment_type
        self.end_of_test_timestamp = cast(datetime.datetime, atc_test_result.all_variables_states_changes_sorted_by_timestamp[-1].previous_state.result_line.best_timestamp)

        other_interesting_variables_names = get_other_interesting_variables_names(self.equipment_type)
        self.all_unfiltered_instant_states_chronologically_sorted = [
            InstantTempsCycleVariableState(
                equipment_report=self,
                timestamp=cast(datetime.datetime, instant_variable_state.result_line.best_timestamp),
                value=cast(int | float, instant_variable_state.best_value),
                other_interesting_variables_values_by_name=get_other_interesting_variables_at_one_atc_log_instant_variable_state(instant_variable_state, other_interesting_variables_names),
            )
            for instant_variable_state in variable.instant_states_chronologically_sorted
        ]

        min_relevant_value = get_min_relevant_value_for_variable(self.variable_name)
        self.all_relevant_values_only_instant_states_chronologically_sorted = [
            InstantTempsCycleVariableState(
                equipment_report=self,
                timestamp=instant_variable_state.timestamp,
                value=instant_variable_state.value,
                other_interesting_variables_values_by_name=instant_variable_state.other_interesting_variables_values_by_name,
            )
            for instant_variable_state in self.all_unfiltered_instant_states_chronologically_sorted
            if min_relevant_value is None or instant_variable_state.value > min_relevant_value
        ]
        self.all_relevant_values = [instant_state.value for instant_state in self.all_relevant_values_only_instant_states_chronologically_sorted]

        self.environment_name = atc_test_result.environment_name
        self.file_name = atc_test_result.all_atc_test_files[0].file_name
        self.equipment_redundancy = atc_test_result.get_equipment_redundancy_by_name(variable.equipment.name).name

        self.atc_test_file_file_full_path = atc_test_result.all_atc_test_files[0].file_full_path
        self.atc_test_result_label = atc_test_result.label

        self.number_relevant_values = len(self.all_relevant_values)

        self.min_of_relevant_values = min(self.all_relevant_values)
        self.max_value = variable.max_numeric_values_by_number_occurrences
        self.mean_of_relevant_values = round(numpy.mean(self.all_relevant_values), 2)
        self.median_of_relevant_values = numpy.median(self.all_relevant_values).item()
        self.deciles_of_relevant_values = cast(list[float], numpy.percentile(self.all_relevant_values, numpy.arange(10, 100, 10)))
        self.centiles_of_relevant_values = cast(list[float], numpy.percentile(self.all_relevant_values, numpy.arange(1, 100, 1)))
        self.variance_of_relevant_values = statistics.pvariance(self.all_relevant_values)
        self.ecart_type_of_relevant_values = statistics.pstdev(self.all_relevant_values)

        self.high_consumption_threshold = get_threshold_high_for_variable(variable)
        self.very_high_consumption_threshold = get_threshold_very_high_for_variable(variable)

        # 1. Distribution (Médiane et Mode)
        relevant_values_sorted_by_value = sorted(self.all_relevant_values)
        n = len(relevant_values_sorted_by_value)
        self.mode = Counter(self.all_relevant_values).most_common(1)[0][0]

        # 3. Identification des anomalies et segments de surconsommation
        self.anomalies_high = []
        self.anomalies_very_high = [value for value in self.all_relevant_values if self.very_high_consumption_threshold and value > self.very_high_consumption_threshold]
        high_pics_consecutifs_above_high = 0
        self.duree_max_above_high_consecutive = 0
        self.total_anomalies_high_consecutives = 0

        for i, cpu in enumerate(self.all_relevant_values):
            if self.high_consumption_threshold and cpu > self.high_consumption_threshold:
                self.anomalies_high.append((i, cpu))
                high_pics_consecutifs_above_high += 1
            else:
                if high_pics_consecutifs_above_high > 0:
                    self.duree_max_above_high_consecutive = max(self.duree_max_above_high_consecutive, high_pics_consecutifs_above_high)
                    high_pics_consecutifs_above_high = 0

        # Vérification si le dernier pic touchait la fin de la liste
        self.duree_max_above_high_consecutive = max(self.duree_max_above_high_consecutive, high_pics_consecutifs_above_high)

        # 2. Dynamique (Deltas et Pentes)
        deltas = [self.all_relevant_values[i] - self.all_relevant_values[i - 1] for i in range(1, len(self.all_relevant_values))]
        self.max_hausse_brutale = max(deltas) if deltas else 0

        # 3. Énergie engloutie par les anomalies
        conso_totale = sum(self.all_relevant_values)
        conso_anomalies_high = sum(x for x in self.all_relevant_values if x > self.high_consumption_threshold) if self.high_consumption_threshold else 0
        self.ratio_energie_pics_high = (conso_anomalies_high / conso_totale * 100) if conso_totale > 0 else 0
        conso_anomalies_very_high = sum(x for x in self.all_relevant_values if x > self.very_high_consumption_threshold) if self.very_high_consumption_threshold else 0
        self.ratio_energie_pics_very_high = (conso_anomalies_very_high / conso_totale * 100) if conso_totale > 0 else 0

        # 5. Temps de recouvrement (Cool-down) après anomalie
        en_crise = False
        temps_recouvrement = []
        compteur_recouv_high = 0
        cpu_moyenne = sum(self.all_relevant_values) / n

        for x in self.all_relevant_values:
            if self.high_consumption_threshold and x > self.high_consumption_threshold:
                en_crise = True
                compteur_recouv_high = min(compteur_recouv_high, 0)
            elif en_crise:
                compteur_recouv_high += 1
                if x <= cpu_moyenne:  # Considéré comme récupéré quand sous la moyenne
                    temps_recouvrement.append(compteur_recouv_high)
                    en_crise = False
                    compteur_recouv_high = 0

        self.recouvrement_moyen_high = (sum(temps_recouvrement) / len(temps_recouvrement)) if temps_recouvrement else 0

        self.nb_anomalies_high = len(self.anomalies_high)
        self.taux_anomalie_high = (self.nb_anomalies_high / len(self.all_relevant_values)) * 100
        self.taux_anomalie_very_high = (len(self.anomalies_very_high) / len(self.all_relevant_values)) * 100


def process_root_folders_and_environments(root_folders_and_environments: list[tuple[str, str]]) -> None:
    equipments_reports_sorted_chronologically = sorted(build_temps_cycle_reports_from_root_folders_and_environments(root_folders_and_environments), key=lambda x: x.end_of_test_timestamp)
    build_temps_cycle_excel_report_from_atc_log_results(equipments_reports=equipments_reports_sorted_chronologically)

    try:
        create_global_graphs_for_equipment_reports(equipments_reports_sorted_chronologically)
    except MemoryError as mem_err:
        logger_config.print_and_log_exception(mem_err)


@logger_config.stopwatch_decorator(inform_beginning=True, monitor_ram_usage=True)
def build_temps_cycle_reports_from_root_folders_and_environments(
    root_folders_and_environments: list[tuple[str, str]],
) -> list[OneEquipmentReport]:
    equipments_reports: list[OneEquipmentReport] = []

    number_of_input_files_processed = 0
    files_paths_not_handled_because_errors: list[str] = []
    for environment_name, root_result_files_folder_path in root_folders_and_environments:
        all_input_files = [full_path for full_path in Path(root_result_files_folder_path).rglob("*.res")]
        logger_config.print_and_log_info(f"{len(all_input_files)} files matching in {root_result_files_folder_path}")
        for input_file_it, input_file_path in enumerate(all_input_files):
            number_of_input_files_processed += 1
            try:
                atc_test_result = build_atc_test_result_from_simech_file_path(environment_name=environment_name, input_file_path=input_file_path, label=f"{number_of_input_files_processed}")
                logger_config.print_and_log_info(f"Handle {input_file_it+1} th / {len(all_input_files)} ({round((input_file_it+1)/len(all_input_files)*100,1)}%) input file {input_file_path}")
                equipments_reports += build_temps_cycle_equipment_report_from_atc_log_result(atc_test_result)
            except AssertionError as ass_err:
                logger_config.print_and_log_exception(ass_err)
                logger_config.print_and_log_error(f"Could not compute temps cycle for {input_file_path}")
                files_paths_not_handled_because_errors.append(str(input_file_path))

    logger_config.print_and_log_error_if(len(files_paths_not_handled_because_errors), f"Files not handled because errors: \n{'\n'.join(files_paths_not_handled_because_errors)}")

    return equipments_reports


def build_atc_test_result_from_simech_file_path(
    environment_name: str,
    input_file_path: str | Path,
    label: str,
) -> atc_logs.ATCTestResult:
    atc_test_result = (
        simech_res.SimechResTestResult.Builder(
            label=label,
            environment_name=environment_name,
        )
        .add_file(
            file_full_path=input_file_path,
        )
        .add_variables_names_creation_filter(
            variables_filter=atc_logs.VariableNameFilter(
                white_or_black_list=common_filters.WhiteOrBlackListFilterType.WHITELIST,
                filter_type=common_filters.StringFilterType.BEGIN_WITH_STRING,
                variables_names=[
                    "CHEURE",
                    "CDECALAGE",
                    "CJOUR",
                    "CDECENIE",
                    "FAS_VF",
                    "EBF_VITESSE",
                    "FODR_VITODO",
                    "TEMPS_AS",
                    "STAB_CPT",
                    "HLF",
                ],
            )
        )
        .add_equipments_names_creation_filter(
            equipments_filter=atc_logs.EquipmentNameFilter(
                white_or_black_list=common_filters.WhiteOrBlackListFilterType.BLACKLIST,
                filter_type=common_filters.StringFilterType.CONTAINS,
                variables_names=[
                    ".KINEMATICS",
                    ".TO.EUROBALISE",
                    "EUROBALISE_CC",
                    "MOTOR.IXL",
                ],
            )
        )
        .build()
    )
    return atc_test_result


def build_equipment_line_in_eqpt_type_excel_report(equipment_report: OneEquipmentReport) -> OrderedDict[str, datetime.datetime | str | int | float | numpy.float64 | None]:

    current_report_line_dict = OrderedDict(
        {
            "Date": (equipment_report.end_of_test_timestamp.replace(microsecond=0).replace(second=0).replace(minute=0) if equipment_report.end_of_test_timestamp else None),
            "File name": equipment_report.file_name,
            "environment": equipment_report.environment_name,
            "variable": equipment_report.variable_name,
            "equipment": equipment_report.equipment_name,
            "equipment type": equipment_report.equipment_type.name,
            "redundancy status": equipment_report.equipment_redundancy,
            f"min_of_relevant_values {equipment_report.variable_name} by test": equipment_report.min_of_relevant_values,
            f"max_value {equipment_report.variable_name} by test": equipment_report.max_value,
            f"mean_of_relevant_values {equipment_report.variable_name} by test": equipment_report.mean_of_relevant_values,
            f"median_of_relevant_values {equipment_report.variable_name} by test": equipment_report.median_of_relevant_values,
            f"Number relevant values {equipment_report.variable_name} by test": len(equipment_report.all_relevant_values),
            f"duree_max_consecutive above high {equipment_report.variable_name} by test": equipment_report.duree_max_above_high_consecutive,
            f"nombre anomalies high {equipment_report.variable_name} by test": len(equipment_report.anomalies_high),
            f"taux_anomalie high (%) {equipment_report.variable_name} by test": equipment_report.taux_anomalie_high,
            f"nombre anomalies very high {equipment_report.variable_name} by test": len(equipment_report.anomalies_very_high),
            f"taux_anomalie very high (%) {equipment_report.variable_name} by test": equipment_report.taux_anomalie_very_high,
            f"variance_of_relevant_values {equipment_report.variable_name} by test": equipment_report.variance_of_relevant_values,
            f"ecart_type_of_relevant_values {equipment_report.variable_name} by test": equipment_report.ecart_type_of_relevant_values,
            f"mode {equipment_report.variable_name} by test": equipment_report.mode,
            f"recouvrement_moyen high {equipment_report.variable_name} by test": equipment_report.recouvrement_moyen_high,
            f"ratio_energie_pics high (%) {equipment_report.variable_name} by test": equipment_report.ratio_energie_pics_high,
            f"ratio_energie_pics very high (%) {equipment_report.variable_name} by test": equipment_report.ratio_energie_pics_very_high,
            f"max_hausse_brutale {equipment_report.variable_name} by test": equipment_report.max_hausse_brutale,
            f"Number not relevant (filtered) values {equipment_report.variable_name} by test": len(equipment_report.all_unfiltered_instant_states_chronologically_sorted)
            - len(equipment_report.all_relevant_values),
            f"high_consumption_threshold {equipment_report.variable_name} by test": equipment_report.high_consumption_threshold,
            f"very_high_consumption_threshold {equipment_report.variable_name} by test": equipment_report.very_high_consumption_threshold,
            "File full path": equipment_report.atc_test_file_file_full_path,
            "label": equipment_report.atc_test_result_label,
        }
    )
    for decile_index, decile_value in enumerate(equipment_report.deciles_of_relevant_values):
        current_report_line_dict[f"Decile_{decile_index+1}"] = decile_value
    for centile_index, centile_value in enumerate(equipment_report.centiles_of_relevant_values):
        if centile_index > 90:
            current_report_line_dict[f"Centile_{centile_index+1}"] = centile_value
    return current_report_line_dict


@logger_config.stopwatch_decorator(inform_beginning=True, monitor_ram_usage=True)
def create_global_graphs_for_equipment_reports(
    equipments_reports_sorted_chronologically: list[OneEquipmentReport],
) -> None:

    all_equipments_names = {equipment_report.equipment_name for equipment_report in equipments_reports_sorted_chronologically}
    all_environment_names = {equipment_report.environment_name for equipment_report in equipments_reports_sorted_chronologically}

    for environment_name in all_environment_names:
        try:
            create_global_graphs_by_equipment_in_sheet_all_states_for_equipments_reports(
                equipments_reports_sorted_chronologically=equipments_reports_sorted_chronologically,
                all_equipments_names=all_equipments_names,
                only_environment_name_to_keep_if_defined=environment_name,
            )
        except MemoryError as ex:
            logger_config.print_and_log_exception(ex)

    for equipment_name in all_equipments_names:
        try:
            create_global_graphs_by_environment_in_sheet_all_states_for_equipments_reports(
                equipments_reports_sorted_chronologically=equipments_reports_sorted_chronologically,
                all_environment_names=all_environment_names,
                only_equipment_name_to_keep_if_defined=equipment_name,
            )

        except MemoryError as ex:
            logger_config.print_and_log_exception(ex)


@logger_config.stopwatch_decorator(inform_beginning=True, monitor_ram_usage=True)
def create_global_graphs_by_equipment_in_sheet_all_states_for_equipments_reports(
    equipments_reports_sorted_chronologically: list[OneEquipmentReport],
    all_equipments_names: set[str],
    only_environment_name_to_keep_if_defined: str | None = None,
) -> None:
    data_per_sheet_name: dict[str, pandas.DataFrame] = {}

    only_environment_name_label = f"_{only_environment_name_to_keep_if_defined}" if only_environment_name_to_keep_if_defined else ""

    for equipment_name in all_equipments_names:
        all_lines_of_equipment: list[OrderedDict] = []
        for equipments_report in [
            equipment_report
            for equipment_report in equipments_reports_sorted_chronologically
            if equipment_report.equipment_name == equipment_name
            # fmt: off
            and (only_environment_name_to_keep_if_defined is None or only_environment_name_to_keep_if_defined == equipment_report.environment_name)
            # fmt: on
        ]:

            for instant_state in equipments_report.all_relevant_values_only_instant_states_chronologically_sorted:
                new_line = OrderedDict(
                    {
                        "Date": instant_state.timestamp,
                        f"{equipments_report.variable_name} {instant_state.equipment_report.equipment_name}": instant_state.value,
                    },
                )
                for other_interesting_variables_name, other_interesting_variables_value in instant_state.other_interesting_variables_values_by_name.items():
                    new_line[other_interesting_variables_name] = other_interesting_variables_value

                all_lines_of_equipment.append(new_line)

        if all_lines_of_equipment:
            data_per_sheet_name[equipment_name] = pandas.DataFrame(
                all_lines_of_equipment,
                index=None,
            )

    pandas_utils.to_excel_wait_if_file_is_locked(
        data_per_sheet_name,
        f"{OUTPUT_DIRECTORY}\\graph_all_temps_cycles{only_environment_name_label}_all_states",
        suffix_file_name_by_date=True,
    )


@logger_config.stopwatch_decorator(inform_beginning=True, monitor_ram_usage=True)
def create_global_graphs_by_environment_in_sheet_all_states_for_equipments_reports(
    equipments_reports_sorted_chronologically: list[OneEquipmentReport],
    all_environment_names: set[str],
    only_equipment_name_to_keep_if_defined: str | None = None,
) -> None:
    data_per_sheet_name: dict[str, pandas.DataFrame] = {}

    only_equipment_name_label = f"_{only_equipment_name_to_keep_if_defined}" if only_equipment_name_to_keep_if_defined else ""

    for environment_name in all_environment_names:
        all_lines_of_equipment: list[OrderedDict] = []
        for equipments_report in [
            equipment_report
            for equipment_report in equipments_reports_sorted_chronologically
            if equipment_report.environment_name == environment_name
            # fmt: off
            and (only_equipment_name_to_keep_if_defined is None or only_equipment_name_to_keep_if_defined == equipment_report.equipment_name)
            # fmt: on
        ]:
            for instant_state in equipments_report.all_relevant_values_only_instant_states_chronologically_sorted:
                new_line = OrderedDict(
                    {
                        "Date": instant_state.timestamp,
                        f"{equipments_report.variable_name} {instant_state.equipment_report.equipment_name}": instant_state.value,
                    },
                )
                for other_interesting_variables_name, other_interesting_variables_value in instant_state.other_interesting_variables_values_by_name.items():
                    new_line[other_interesting_variables_name] = other_interesting_variables_value

                all_lines_of_equipment.append(new_line)

        if all_lines_of_equipment:
            data_per_sheet_name[environment_name] = pandas.DataFrame(
                all_lines_of_equipment,
                index=None,
            )

    pandas_utils.to_excel_wait_if_file_is_locked(
        data_per_sheet_name,
        f"{OUTPUT_DIRECTORY}\\graph_all_temps_cycles{only_equipment_name_label}_all_states",
        suffix_file_name_by_date=True,
    )


def build_temps_cycle_equipment_report_from_atc_log_result(
    atc_test_result: atc_logs.ATCTestResult,
) -> list[OneEquipmentReport]:
    equipments_reports: list[OneEquipmentReport] = []
    for equipment in atc_test_result.equipments_library.all_equipments:
        at_least_one_variable_found = False
        for temps_cycle_variable_name_candidate in get_temps_cycle_variables_names_by_equipment(equipment):
            variable = equipment.variables_library.get_variable_with_name_if_exists(temps_cycle_variable_name_candidate)
            if variable is not None:
                at_least_one_variable_found = True

                if (
                    variable.equipment.equipment_type in [atc_logs.EquipmentType.PAS, atc_logs.EquipmentType.PAL]
                    and variable.name.startswith(("STAB_CPT1", "TEMPS_AS"))
                    and variable.max_numeric_values_by_number_occurrences < 60
                ):
                    logger_config.print_and_log_info(
                        f"Ignore equipment {variable.equipment.name} in {atc_test_result.environment_name} in file {atc_test_result.all_atc_test_files[0].file_name} because is virtual (so no valid temps cycle). {variable.name} is too low ({variable.max_numeric_values_by_number_occurrences}) to be real"
                    )
                else:
                    equipment_report = OneEquipmentReport(variable=variable, atc_test_result=atc_test_result)
                    equipments_reports.append(equipment_report)
        logger_config.print_and_log_error_if(
            not at_least_one_variable_found,
            f"No temps cycle variable {','.join(temps_cycle_variable_name_candidate)}found in {atc_test_result.all_atc_test_files[0].file_name} for equipment {equipment.name} in {atc_test_result.environment_name}",
        )
    return equipments_reports


@logger_config.stopwatch_decorator(inform_beginning=True)
def build_temps_cycle_excel_report_from_atc_log_results(
    equipments_reports: list[OneEquipmentReport],
) -> None:
    data_per_sheet_name: dict[str, pandas.DataFrame] = {}
    for equipment_type in atc_logs.EquipmentType:
        data_per_sheet_name[equipment_type.name] = pandas.DataFrame(
            data=[build_equipment_line_in_eqpt_type_excel_report(equipment_report=equipment_report) for equipment_report in equipments_reports if equipment_report.equipment_type == equipment_type],
            index=None,
        )

    pandas_utils.to_excel_wait_if_file_is_locked(
        data_per_sheet_name,
        f"{OUTPUT_DIRECTORY}\\temps_cycle_report",
        suffix_file_name_by_date=True,
    )
