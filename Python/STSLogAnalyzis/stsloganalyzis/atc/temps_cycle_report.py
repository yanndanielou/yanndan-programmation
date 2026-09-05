import statistics
from collections import Counter, OrderedDict
from dataclasses import dataclass
from typing import cast

import numpy
import pandas
from common import (
    pandas_utils,
)
from logger import logger_config

from stsloganalyzis.atc import atc_logs

OUTPUT_DIRECTORY = "output_temps_cycle"


@dataclass
class OneEquipmentReport:

    variable: atc_logs.Variable
    atc_test_file: atc_logs.ATCTestFile

    def __post_init__(self) -> None:
        super().__init__()
        logger_config.print_and_log_info(f"Create report for {self.atc_test_file.file_name} {self.variable.equipment.name} {self.variable.name}")

        self.all_relevant_values = [value for value in cast(list[int | float], self.variable.all_instant_states_best_values) if value > 50]
        self.number_relevant_values = len(self.all_relevant_values)

        self.min_of_relevant_values = min(self.all_relevant_values)
        self.max_value = self.variable.max_numeric_values_by_number_occurrences
        self.mean_of_relevant_values = round(numpy.mean(self.all_relevant_values), 2)
        self.median_of_relevant_values = numpy.median(self.all_relevant_values).item()
        self.deciles_of_relevant_values = cast(list[float], numpy.percentile(self.all_relevant_values, numpy.arange(10, 100, 10)))
        self.centiles_of_relevant_values = cast(list[float], numpy.percentile(self.all_relevant_values, numpy.arange(1, 100, 1)))
        self.variance_of_relevant_values = statistics.pvariance(self.all_relevant_values)
        self.ecart_type_of_relevant_values = statistics.pstdev(self.all_relevant_values)

        self.high_consumption_threshold = (
            # fmt: off
            180 if self.variable.equipment.equipment_type is atc_logs.EquipmentType.PAL
            else 230 if self.variable.equipment.equipment_type is atc_logs.EquipmentType.PAS 
            else 100 if self.variable.equipment.equipment_type is atc_logs.EquipmentType.PAE 
            else 0
            # fmt: on
        )
        self.very_high_consumption_threshold = (
            # fmt: off
            200 if self.variable.equipment.equipment_type is atc_logs.EquipmentType.PAL
            else 260 if self.variable.equipment.equipment_type is atc_logs.EquipmentType.PAS 
            else 120 if self.variable.equipment.equipment_type is atc_logs.EquipmentType.PAE 
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


def build_temps_cycle_report_from_atc_log(atc_test_results: list[atc_logs.ATCTestResult]) -> None:

    equipments_reports: list[OneEquipmentReport] = []

    for atc_test_result in atc_test_results:
        for atc_test_file in atc_test_result.all_atc_test_files:
            for equipment in atc_test_result.equipments_library.all_equipments:
                at_least_one_variable_found = False
                for temps_cycle_variable_name_candidate in ["STAB_CPT1", "TEMPS_AS"]:
                    variable = equipment.variables_library.get_variable_with_name_if_exists(temps_cycle_variable_name_candidate)
                    if variable is not None:
                        at_least_one_variable_found = True

                        if variable.equipment.equipment_type in [atc_logs.EquipmentType.PAS, atc_logs.EquipmentType.PAL] and variable.max_numeric_values_by_number_occurrences < 60:
                            logger_config.print_and_log_info(
                                f"Ignore equipment {variable.equipment.name} in {atc_test_file.file_name} because is virtual (so no valid temps cycle). {variable.name} is too low to be real"
                            )
                        else:
                            equipment_report = OneEquipmentReport(variable=variable, atc_test_file=atc_test_file)
                            equipments_reports.append(equipment_report)
                logger_config.print_and_log_error_if(not at_least_one_variable_found, f"No temps cycle variable found in {atc_test_file.file_name} for equipment {equipment.name}")

    data_per_sheet_name: dict[str, pandas.DataFrame] = {}
    for equipment_type in atc_logs.EquipmentType:
        rows_as_list_dict: list[OrderedDict] = []

        for equipment_report in equipments_reports:
            if equipment_report.variable.equipment.equipment_type == equipment_type:
                equipment_report_dict = OrderedDict(
                    {
                        "File name": equipment_report.atc_test_file.file_name,
                        "label": equipment_report.atc_test_file.atc_test_result.label,
                        "environment": equipment_report.atc_test_file.atc_test_result.environment_name,
                        "variable": equipment_report.variable.name,
                        "equipment": equipment_report.variable.equipment.name,
                        "equipment type": equipment_report.variable.equipment.equipment_type.name,
                        "redundancy status": equipment_report.atc_test_file.atc_test_result.get_equipment_redundancy_by_name(equipment_report.variable.equipment.name).name,
                        "min_of_relevant_values": equipment_report.min_of_relevant_values,
                        "max_value": equipment_report.max_value,
                        "mean_of_relevant_values": equipment_report.mean_of_relevant_values,
                        "median_of_relevant_values": equipment_report.median_of_relevant_values,
                        "mediane_relevant_values": equipment_report.mediane_relevant_values,
                        "variance_of_relevant_values": equipment_report.variance_of_relevant_values,
                        "ecart_type_of_relevant_values": equipment_report.ecart_type_of_relevant_values,
                        "Number relevant values": len(equipment_report.all_relevant_values),
                        "Number not relevant (filtered) values": len(equipment_report.variable.instant_states_chronologically_sorted) - len(equipment_report.all_relevant_values),
                        "duree_max_consecutive above high": equipment_report.duree_max_above_high_consecutive,
                        "nombre anomalies high": len(equipment_report.anomalies_high),
                        "taux_anomalie high (%)": equipment_report.taux_anomalie_high,
                        "nombre anomalies very high": len(equipment_report.anomalies_very_high),
                        "taux_anomalie very high (%)": equipment_report.taux_anomalie_very_high,
                        "mode": equipment_report.mode,
                        "recouvrement_moyen high": equipment_report.recouvrement_moyen_high,
                        "ratio_energie_pics high (%)": equipment_report.ratio_energie_pics_high,
                        "ratio_energie_pics very high (%)": equipment_report.ratio_energie_pics_very_high,
                        "max_hausse_brutale": equipment_report.max_hausse_brutale,
                        "high_consumption_threshold": equipment_report.high_consumption_threshold,
                        "very_high_consumption_threshold": equipment_report.very_high_consumption_threshold,
                        "File full path": equipment_report.atc_test_file.file_full_path,
                    }
                )
                rows_as_list_dict.append(equipment_report_dict)
                for decile_index, decile_value in enumerate(equipment_report.deciles_of_relevant_values):
                    equipment_report_dict[f"Decile_{decile_index+1}"] = decile_value
                for centile_index, centile_value in enumerate(equipment_report.centiles_of_relevant_values):
                    if centile_index > 90:
                        equipment_report_dict[f"Centile_{centile_index+1}"] = centile_value

        data_per_sheet_name[equipment_type.name] = pandas.DataFrame(rows_as_list_dict, index=None)

    pandas_utils.to_excel_wait_if_file_is_locked(
        data_per_sheet_name,
        f"{OUTPUT_DIRECTORY}\\temps_cycle_report",
        suffix_file_name_by_date=True,
    )
