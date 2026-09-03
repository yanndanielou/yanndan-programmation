from collections import Counter
from common import (
    file_name_utils,
    reports_utils,
)
from typing import cast
from collections import OrderedDict
from dataclasses import dataclass

from common import file_name_utils
from logger import logger_config

from stsloganalyzis.atc import atc_logs

OUTPUT_DIRECTORY = "output_temps_cycle"


@dataclass
class OneEquipmentReport:
    equipment_name: str
    variable: atc_logs.Variable

    def __post_init__(self) -> None:
        super().__init__()
        self.min_value = self.variable.min_numeric_values_by_number_occurrences
        self.max_value = self.variable.max_numeric_values_by_number_occurrences
        self.mean_value = round(self.variable.mean_numeric_values_by_number_occurrences, 2)
        self.median_value = self.variable.median_numeric_values_by_number_occurrences
        self.deciles = self.variable.deciles_numeric_values_by_number_occurrences
        self.variance = self.variable.variance_numeric_values_by_number_occurrences
        self.ecart_type = self.variable.ecart_type_numeric_values_by_number_occurrences

        # 1. Distribution (Médiane et Mode)
        donnees_triees = sorted(cast(list[float | int], self.variable.all_instant_states_best_values))
        n = len(donnees_triees)
        mediane = donnees_triees[n // 2] if n % 2 != 0 else (donnees_triees[n // 2 - 1] + donnees_triees[n // 2]) / 2
        self.mode = Counter(self.variable.all_instant_states_best_values).most_common(1)[0][0]

        # 2. Définition dynamique du seuil (Moyenne + X * Écart-type)
        # On plafonne le seuil à 100% si vos données sont en pourcentage
        multiplicateur_ecart_type = 2
        self.high_consumption_threshold = min(self.mean_value + (multiplicateur_ecart_type * self.ecart_type), 100.0)

        # 3. Identification des anomalies et segments de surconsommation
        self.anomalies = []
        pics_consecutifs = 0
        self.duree_max_consecutive = 0
        self.total_anomalies_consecutives = 0

        for i, cpu in enumerate(cast(list[int | float], self.variable.all_instant_states_best_values)):
            if cpu > self.high_consumption_threshold:
                self.anomalies.append((i, cpu))
                pics_consecutifs += 1
            else:
                if pics_consecutifs > 0:
                    if pics_consecutifs > self.duree_max_consecutive:
                        self.duree_max_consecutive = pics_consecutifs
                    pics_consecutifs = 0

        # Vérification si le dernier pic touchait la fin de la liste
        if pics_consecutifs > self.duree_max_consecutive:
            self.duree_max_consecutive = pics_consecutifs

        self.nb_anomalies = len(self.anomalies)
        self.taux_anomalie = (self.nb_anomalies / len(self.variable.all_instant_states_best_values)) * 100


@dataclass
class OneSimulationReport:
    name: str

    def __post_init__(self) -> None:
        self.equipments_reports: list[OneEquipmentReport] = []


def build_temps_cycle_report_from_atc_log(atc_test_result: atc_logs.ATCTestResult) -> None:

    simulations_reports: list[OneSimulationReport] = []
    for atc_test_file in atc_test_result.all_atc_test_files:
        simulation_report = OneSimulationReport(file_name_utils.get_file_name_without_extension_from_full_path(atc_test_file.file_name))
        simulations_reports.append(simulation_report)
        for equipment in atc_test_result.equipments_library.all_equipments:
            for temps_cycle_variable_name_candidate in ["STAB_CPT1", "TEMPS_AS"]:
                variable = equipment.variables_library.get_variable_with_name_if_exists(temps_cycle_variable_name_candidate)
                if variable is not None:
                    equipment_report = OneEquipmentReport(equipment_name=equipment.name, variable=variable)
                    simulation_report.equipments_reports.append(equipment_report)

        rows_as_list_dict: list[OrderedDict] = []
        for equipment_report in simulation_report.equipments_reports:
            equipment_report_dict = OrderedDict(
                {
                    "file": atc_test_file.file_name,
                    "variable": equipment_report.variable.name,
                    "equipment": equipment_report.variable.equipment.name,
                    "min_value": equipment_report.min_value,
                    "max_value": equipment_report.max_value,
                    "mean_value": equipment_report.mean_value,
                    "median_value": equipment_report.median_value,
                    "high_consumption_threshold": equipment_report.high_consumption_threshold,
                    "variance": equipment_report.variance,
                    "ecart_type": equipment_report.ecart_type,
                    "duree_max_consecutive": equipment_report.duree_max_consecutive,
                    "nb_anomalies": equipment_report.nb_anomalies,
                    "taux_anomalie": equipment_report.taux_anomalie,
                    "mode": equipment_report.mode,
                }
            )
            rows_as_list_dict.append(equipment_report_dict)
            for decile_index, decile_value in enumerate(equipment_report.deciles):
                equipment_report_dict[f"Decile_{decile_index+1}"] = decile_value

        reports_utils.save_rows_to_output_files(
            rows_as_list_dict=rows_as_list_dict,
            file_base_name=f"{atc_test_file.file_name}_temps_cycle_report",
            output_directory_path=OUTPUT_DIRECTORY,
            suffix_file_name_by_date=reports_utils.SuffixFileNameByDate.NO,
            split_big_files=False,
        )
