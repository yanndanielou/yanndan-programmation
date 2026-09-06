import datetime
from warnings import deprecated
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


class OneEquipmentReport:

    def __init__(self, atc_test_file: atc_logs.ATCTestFile, variable: atc_logs.Variable) -> None:
        super().__init__()
        logger_config.print_and_log_info(f"Create report for {atc_test_file.file_name} {variable.equipment.name} {variable.name}", do_not_print=True)

        self.variable_name = variable.name
        self.equipment_name = variable.equipment.name
        self.equipment_type = variable.equipment.equipment_type
        self.end_of_test_timestamp = cast(datetime.datetime, atc_test_file.atc_test_result.all_variables_states_changes_sorted_by_timestamp[-1].previous_state.result_line.best_timestamp)

        self.all_unfiltered_instant_states_chronologically_sorted = [
            InstantTempsCycleVariableState(
                equipment_report=self,
                timestamp=cast(datetime.datetime, instant_variable_state.result_line.best_timestamp),
                value=cast(int | float, instant_variable_state.best_value),
            )
            for instant_variable_state in variable.instant_states_chronologically_sorted
        ]

        self.environment_name = atc_test_file.atc_test_result.environment_name
        self.file_name = atc_test_file.file_name
        self.equipment_redundancy = atc_test_file.atc_test_result.get_equipment_redundancy_by_name(variable.equipment.name).name

        self.atc_test_file_file_full_path = atc_test_file.file_full_path
        self.atc_test_result_label = atc_test_file.atc_test_result.label

        self.all_relevant_values = [value for value in cast(list[int | float], variable.all_instant_states_best_values) if value > 50]
        self.number_relevant_values = len(self.all_relevant_values)

        self.min_of_relevant_values = min(self.all_relevant_values)
        self.max_value = variable.max_numeric_values_by_number_occurrences
        self.mean_of_relevant_values = round(numpy.mean(self.all_relevant_values), 2)
        self.median_of_relevant_values = numpy.median(self.all_relevant_values).item()
        self.deciles_of_relevant_values = cast(list[float], numpy.percentile(self.all_relevant_values, numpy.arange(10, 100, 10)))
        self.centiles_of_relevant_values = cast(list[float], numpy.percentile(self.all_relevant_values, numpy.arange(1, 100, 1)))
        self.variance_of_relevant_values = statistics.pvariance(self.all_relevant_values)
        self.ecart_type_of_relevant_values = statistics.pstdev(self.all_relevant_values)

        self.high_consumption_threshold = (
            # fmt: off
            180 if variable.equipment.equipment_type is atc_logs.EquipmentType.PAL
            else 230 if variable.equipment.equipment_type is atc_logs.EquipmentType.PAS 
            else 100 if variable.equipment.equipment_type is atc_logs.EquipmentType.PAE 
            else 0
            # fmt: on
        )
        self.very_high_consumption_threshold = (
            # fmt: off
            200 if variable.equipment.equipment_type is atc_logs.EquipmentType.PAL
            else 260 if variable.equipment.equipment_type is atc_logs.EquipmentType.PAS 
            else 120 if variable.equipment.equipment_type is atc_logs.EquipmentType.PAE 
            else 0
            # fmt: on
        )

        # 1. Distribution (Médiane et Mode)
        relevant_values_sorted_by_value = sorted(self.all_relevant_values)
        n = len(relevant_values_sorted_by_value)
        self.mediane_relevant_values = relevant_values_sorted_by_value[n // 2] if n % 2 != 0 else (relevant_values_sorted_by_value[n // 2 - 1] + relevant_values_sorted_by_value[n // 2]) / 2
        self.mode = Counter(self.all_relevant_values).most_common(1)[0][0]

        # 3. Identification des anomalies et segments de surconsommation
        self.anomalies_high = []
        self.anomalies_very_high = [value for value in self.all_relevant_values if value > self.very_high_consumption_threshold]
        high_pics_consecutifs_above_high = 0
        self.duree_max_above_high_consecutive = 0
        self.total_anomalies_high_consecutives = 0

        for i, cpu in enumerate(self.all_relevant_values):
            if cpu > self.high_consumption_threshold:
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
        conso_anomalies_high = sum(x for x in self.all_relevant_values if x > self.high_consumption_threshold)
        self.ratio_energie_pics_high = (conso_anomalies_high / conso_totale * 100) if conso_totale > 0 else 0
        conso_anomalies_very_high = sum(x for x in self.all_relevant_values if x > self.very_high_consumption_threshold)
        self.ratio_energie_pics_very_high = (conso_anomalies_very_high / conso_totale * 100) if conso_totale > 0 else 0

        # 5. Temps de recouvrement (Cool-down) après anomalie
        en_crise = False
        temps_recouvrement = []
        compteur_recouv_high = 0
        cpu_moyenne = sum(self.all_relevant_values) / n

        for x in self.all_relevant_values:
            if x > self.high_consumption_threshold:
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
    equipments_reports = build_temps_cycle_reports_from_root_folders_and_environments(root_folders_and_environments)
    build_temps_cycle_excel_report_from_atc_log_results(equipments_reports=equipments_reports)


@logger_config.stopwatch_decorator(inform_beginning=True)
def build_temps_cycle_reports_from_root_folders_and_environments(
    root_folders_and_environments: list[tuple[str, str]],
) -> list[OneEquipmentReport]:
    equipments_reports: list[OneEquipmentReport] = []

    number_of_input_files_processed = 0
    files_paths_not_handled_because_errors: list[str] = []
    for environment_name, root_result_files_folder_path in root_folders_and_environments:
        all_input_files = [full_path for full_path in Path(root_result_files_folder_path).rglob("*.res")]
        for input_file_it, input_file_path in enumerate(all_input_files):
            number_of_input_files_processed += 1
            try:
                atc_test_result = build_atc_test_result_from_file_path(environment_name=environment_name, input_file_path=input_file_path, label=f"{number_of_input_files_processed}")
                logger_config.print_and_log_info(f"Handle {input_file_it+1} th / {len(all_input_files)} ({round((input_file_it+1)/len(all_input_files)*100,1)}%) input file {input_file_path}")
                equipments_reports += build_temps_cycle_equipment_report_from_atc_log_result(atc_test_result)
            except AssertionError as ass_err:
                logger_config.print_and_log_exception(ass_err)
                logger_config.print_and_log_error(f"Could not compute temps cycle for {input_file_path}")
                files_paths_not_handled_because_errors.append(str(input_file_path))

    logger_config.print_and_log_error_if(len(files_paths_not_handled_because_errors), f"Files not handled because errors: \n{'\n'.join(files_paths_not_handled_because_errors)}")

    return equipments_reports


@logger_config.stopwatch_decorator(inform_beginning=True)
@deprecated("Too much ram usage")
def process_root_folders_and_environments_build_results_then_reports(
    root_folders_and_environments: list[tuple[str, str]],
) -> None:

    atc_test_results = build_atc_test_results_from_root_folders_and_environments(root_folders_and_environments=root_folders_and_environments)
    create_global_graphs_by_platform(atc_test_results)
    equipments_reports = build_temps_cycle_report_from_atc_log_results(atc_test_results)
    build_temps_cycle_excel_report_from_atc_log_results(equipments_reports=equipments_reports)


def build_atc_test_result_from_file_path(
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


@deprecated("Too much ram usage")
def build_atc_test_results_from_root_folders_and_environments(
    root_folders_and_environments: list[tuple[str, str]],
) -> list[atc_logs.ATCTestResult]:

    files_paths_not_handled_because_errors: list[str] = []
    atc_test_results: list[atc_logs.ATCTestResult] = []
    for environment_name, root_result_files_folder_path in root_folders_and_environments:
        all_input_files = [full_path for full_path in Path(root_result_files_folder_path).rglob("*.res")]
        for input_file_it, input_file_path in enumerate(all_input_files):
            try:
                atc_test_result = build_atc_test_result_from_file_path(environment_name=environment_name, input_file_path=input_file_path, label=f"{len(atc_test_results)+1}")
                logger_config.print_and_log_info(f"Handle {input_file_it+1} th / {len(all_input_files)} ({round((input_file_it+1)/len(all_input_files)*100,1)}%) input file {input_file_path}")
                atc_test_results.append(atc_test_result)
            except AssertionError as ass_err:
                logger_config.print_and_log_exception(ass_err)
                logger_config.print_and_log_error(f"Could not compute temps cycle for {input_file_path}")
                files_paths_not_handled_because_errors.append(str(input_file_path))

    logger_config.print_and_log_error_if(len(files_paths_not_handled_because_errors), f"Files not handled because errors: \n{'\n'.join(files_paths_not_handled_because_errors)}")
    return atc_test_results


def build_lines_in_one_simulation_equipment_report(equipment_report: OneEquipmentReport) -> list[OrderedDict[str, datetime.datetime | str | int | float | numpy.float64 | None]]:
    return [
        OrderedDict(
            {
                "Horodate": instant_state.timestamp,
                "variable": equipment_report.variable_name,
                "value": instant_state.value,
            },
        )
        for instant_state in equipment_report.all_unfiltered_instant_states_chronologically_sorted
    ]


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
            "min_of_relevant_values": equipment_report.min_of_relevant_values,
            "max_value": equipment_report.max_value,
            "mean_of_relevant_values": equipment_report.mean_of_relevant_values,
            "median_of_relevant_values": equipment_report.median_of_relevant_values,
            "mediane_relevant_values": equipment_report.mediane_relevant_values,
            "Number relevant values": len(equipment_report.all_relevant_values),
            "Number not relevant (filtered) values": len(equipment_report.all_unfiltered_instant_states_chronologically_sorted) - len(equipment_report.all_relevant_values),
            "duree_max_consecutive above high": equipment_report.duree_max_above_high_consecutive,
            "nombre anomalies high": len(equipment_report.anomalies_high),
            "taux_anomalie high (%)": equipment_report.taux_anomalie_high,
            "nombre anomalies very high": len(equipment_report.anomalies_very_high),
            "taux_anomalie very high (%)": equipment_report.taux_anomalie_very_high,
            "variance_of_relevant_values": equipment_report.variance_of_relevant_values,
            "ecart_type_of_relevant_values": equipment_report.ecart_type_of_relevant_values,
            "mode": equipment_report.mode,
            "recouvrement_moyen high": equipment_report.recouvrement_moyen_high,
            "ratio_energie_pics high (%)": equipment_report.ratio_energie_pics_high,
            "ratio_energie_pics very high (%)": equipment_report.ratio_energie_pics_very_high,
            "max_hausse_brutale": equipment_report.max_hausse_brutale,
            "high_consumption_threshold": equipment_report.high_consumption_threshold,
            "very_high_consumption_threshold": equipment_report.very_high_consumption_threshold,
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


def get_temps_cycle_variable_name_by_equipment(equipment: atc_logs.Equipment) -> str:
    return "TEMPS_AS" if equipment.equipment_type in [atc_logs.EquipmentType.PAL, atc_logs.EquipmentType.PAS, atc_logs.EquipmentType.MES] else "STAB_CPT1"


@logger_config.stopwatch_decorator(inform_beginning=True, monitor_ram_usage=True)
@deprecated("Too much ram usage")
def create_global_graphs_by_platform(
    atc_test_results: list[atc_logs.ATCTestResult],
) -> None:
    atc_test_results_sorted_chronologically = sorted(
        atc_test_results, key=lambda x: cast(datetime.datetime, x.all_variables_states_changes_sorted_by_timestamp[-1].previous_state.result_line.best_timestamp), reverse=True
    )
    all_equipments_names = {equipment.name for atc_test_result in atc_test_results for equipment in atc_test_result.equipments_library.all_equipments}
    all_environment_names = {atc_test_result.environment_name for atc_test_result in atc_test_results}

    try:
        create_global_graphs_by_platform_all_states(atc_test_results_sorted_chronologically, all_equipments_names, all_environment_names)
    except Exception as ex:
        logger_config.print_and_log_exception(ex)

    try:
        create_global_graphs_by_platform_all_continuous_states(atc_test_results_sorted_chronologically, all_equipments_names, all_environment_names)
    except Exception as ex:
        logger_config.print_and_log_exception(ex)


@logger_config.stopwatch_decorator(inform_beginning=True, monitor_ram_usage=True)
@deprecated("Too much ram usage")
def create_global_graphs_by_platform_all_states(
    atc_test_results_sorted_chronologically: list[atc_logs.ATCTestResult],
    all_equipments_names: set[str],
    all_environment_names: set[str],
) -> None:
    data_per_sheet_name: dict[str, pandas.DataFrame] = {}
    for equipment_name in all_equipments_names:
        all_lines_of_equipment: list[OrderedDict] = []
        for atc_test_result in atc_test_results_sorted_chronologically:
            equipment_found = atc_test_result.get_existing_equipment_by_name(equipment_name)
            if equipment_found:
                temps_cycle_variable_name = get_temps_cycle_variable_name_by_equipment(equipment_found)
                variable = equipment_found.variables_library.get_variable_with_name_if_exists(temps_cycle_variable_name)
                if variable:
                    new_lines = [
                        OrderedDict(
                            {
                                "Date": instant_state.result_line.best_timestamp,
                                temps_cycle_variable_name: instant_state.best_value,
                            },
                        )
                        for instant_state in variable.instant_states_chronologically_sorted
                        if instant_state.best_value > 30
                    ]
                    all_lines_of_equipment += new_lines

        data_per_sheet_name[equipment_name] = pandas.DataFrame(
            all_lines_of_equipment,
            index=None,
        )

    for equipment_name in all_equipments_names:
        for environment_name in all_environment_names:
            all_lines_of_equipment = []
            for atc_test_result in [atc_test_result for atc_test_result in atc_test_results_sorted_chronologically if atc_test_result.environment_name == environment_name]:
                equipment_found = atc_test_result.get_existing_equipment_by_name(equipment_name)
                if equipment_found:
                    temps_cycle_variable_name = get_temps_cycle_variable_name_by_equipment(equipment_found)
                    variable = equipment_found.variables_library.get_variable_with_name_if_exists(temps_cycle_variable_name)
                    if variable:
                        new_lines = [
                            OrderedDict(
                                {
                                    "Date": instant_state.result_line.best_timestamp,
                                    temps_cycle_variable_name: instant_state.best_value,
                                },
                            )
                            for instant_state in variable.instant_states_chronologically_sorted
                            if instant_state.best_value > 50
                        ]
                        all_lines_of_equipment += new_lines

            data_per_sheet_name[f"{equipment_name}_{environment_name}"] = pandas.DataFrame(
                all_lines_of_equipment,
                index=None,
            )

    pandas_utils.to_excel_wait_if_file_is_locked(
        data_per_sheet_name,
        f"{OUTPUT_DIRECTORY}\\gaph_all_temps_cycles_all_states",
        suffix_file_name_by_date=True,
    )


@logger_config.stopwatch_decorator(inform_beginning=True, monitor_ram_usage=True)
@deprecated("Too much ram usage")
def create_global_graphs_by_platform_all_continuous_states(
    atc_test_results_sorted_chronologically: list[atc_logs.ATCTestResult],
    all_equipments_names: set[str],
    all_environment_names: set[str],
) -> None:
    data_per_sheet_name: dict[str, pandas.DataFrame] = {}

    for equipment_name in all_equipments_names:
        all_lines_of_equipment: list[OrderedDict] = []
        for atc_test_result in atc_test_results_sorted_chronologically:
            equipment_found = atc_test_result.get_existing_equipment_by_name(equipment_name)
            if equipment_found:
                temps_cycle_variable_name = get_temps_cycle_variable_name_by_equipment(equipment_found)
                variable = equipment_found.variables_library.get_variable_with_name_if_exists(temps_cycle_variable_name)
                if variable:

                    new_lines: list[OrderedDict] = []
                    for continuous_state in variable.continuous_states_chronologically_sorted:
                        if continuous_state.best_value != 0:
                            new_lines.append(
                                OrderedDict(
                                    {
                                        "Date": continuous_state.all_instant_variable_states[0].result_line.best_timestamp,
                                        temps_cycle_variable_name: continuous_state.best_value,
                                    },
                                )
                            )
                            new_lines.append(
                                OrderedDict(
                                    {
                                        "Date": continuous_state.all_instant_variable_states[-1].result_line.best_timestamp,
                                        temps_cycle_variable_name: continuous_state.best_value,
                                    },
                                )
                            )
                        all_lines_of_equipment += new_lines

        data_per_sheet_name[equipment_name] = pandas.DataFrame(
            all_lines_of_equipment,
            index=None,
        )

    for equipment_name in all_equipments_names:
        for environment_name in all_environment_names:
            all_lines_of_equipment = []
            for atc_test_result in [atc_test_result for atc_test_result in atc_test_results_sorted_chronologically if atc_test_result.environment_name == environment_name]:
                equipment_found = atc_test_result.get_existing_equipment_by_name(equipment_name)
                if equipment_found:
                    temps_cycle_variable_name = get_temps_cycle_variable_name_by_equipment(equipment_found)
                    variable = equipment_found.variables_library.get_variable_with_name_if_exists(temps_cycle_variable_name)
                    if variable:
                        new_lines = []
                        for continuous_state in variable.continuous_states_chronologically_sorted:
                            if continuous_state.best_value != 0:
                                new_lines.append(
                                    OrderedDict(
                                        {
                                            "Date": continuous_state.all_instant_variable_states[0].result_line.best_timestamp,
                                            temps_cycle_variable_name: continuous_state.best_value,
                                        },
                                    )
                                )
                                new_lines.append(
                                    OrderedDict(
                                        {
                                            "Date": continuous_state.all_instant_variable_states[-1].result_line.best_timestamp,
                                            temps_cycle_variable_name: continuous_state.best_value,
                                        },
                                    )
                                )
                            all_lines_of_equipment += new_lines

            data_per_sheet_name[f"{equipment_name}_{environment_name}"] = pandas.DataFrame(
                all_lines_of_equipment,
                index=None,
            )

    pandas_utils.to_excel_wait_if_file_is_locked(
        data_per_sheet_name,
        f"{OUTPUT_DIRECTORY}\\gaph_all_temps_cycles_all_continuous_states",
        suffix_file_name_by_date=True,
    )


@logger_config.stopwatch_decorator(inform_beginning=True)
def build_temps_cycle_report_from_atc_log_result(
    atc_test_result: atc_logs.ATCTestResult,
) -> list[OneEquipmentReport]:
    equipments_reports: list[OneEquipmentReport] = []
    for atc_test_file in atc_test_result.all_atc_test_files:
        for equipment in atc_test_result.equipments_library.all_equipments:
            at_least_one_variable_found = False
            for temps_cycle_variable_name_candidate in ["STAB_CPT1", "TEMPS_AS"]:
                variable = equipment.variables_library.get_variable_with_name_if_exists(temps_cycle_variable_name_candidate)
                if variable is not None:
                    at_least_one_variable_found = True

                    if variable.equipment.equipment_type in [atc_logs.EquipmentType.PAS, atc_logs.EquipmentType.PAL] and variable.max_numeric_values_by_number_occurrences < 60:
                        logger_config.print_and_log_info(
                            f"Ignore equipment {variable.equipment.name} in {atc_test_file.atc_test_result.environment_name} in file {atc_test_file.file_name} because is virtual (so no valid temps cycle). {variable.name} is too low ({variable.max_numeric_values_by_number_occurrences}) to be real"
                        )
                    else:
                        equipment_report = OneEquipmentReport(variable=variable, atc_test_file=atc_test_file)

                        equipments_reports.append(equipment_report)
            logger_config.print_and_log_error_if(
                not at_least_one_variable_found, f"No temps cycle variable found in {atc_test_file.file_name} for equipment {equipment.name} in {atc_test_result.environment_name}"
            )
    return equipments_reports


def build_temps_cycle_equipment_report_from_atc_log_result(
    atc_test_result: atc_logs.ATCTestResult,
) -> list[OneEquipmentReport]:
    equipments_reports: list[OneEquipmentReport] = []
    for atc_test_file in atc_test_result.all_atc_test_files:
        for equipment in atc_test_result.equipments_library.all_equipments:
            at_least_one_variable_found = False
            for temps_cycle_variable_name_candidate in ["STAB_CPT1", "TEMPS_AS"]:
                variable = equipment.variables_library.get_variable_with_name_if_exists(temps_cycle_variable_name_candidate)
                if variable is not None:
                    at_least_one_variable_found = True

                    if variable.equipment.equipment_type in [atc_logs.EquipmentType.PAS, atc_logs.EquipmentType.PAL] and variable.max_numeric_values_by_number_occurrences < 60:
                        logger_config.print_and_log_info(
                            f"Ignore equipment {variable.equipment.name} in {atc_test_file.atc_test_result.environment_name} in file {atc_test_file.file_name} because is virtual (so no valid temps cycle). {variable.name} is too low ({variable.max_numeric_values_by_number_occurrences}) to be real"
                        )
                    else:
                        equipment_report = OneEquipmentReport(variable=variable, atc_test_file=atc_test_file)
                        equipments_reports.append(equipment_report)
            logger_config.print_and_log_error_if(
                not at_least_one_variable_found, f"No temps cycle variable found in {atc_test_file.file_name} for equipment {equipment.name} in {atc_test_result.environment_name}"
            )
    return equipments_reports


@logger_config.stopwatch_decorator(inform_beginning=True)
@deprecated("Too much ram usage")
def build_temps_cycle_report_from_atc_log_results(
    atc_test_results: list[atc_logs.ATCTestResult],
) -> list[OneEquipmentReport]:

    equipments_reports: list[OneEquipmentReport] = []

    for atc_test_result in atc_test_results:
        equipments_reports += build_temps_cycle_equipment_report_from_atc_log_result(atc_test_result)
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
