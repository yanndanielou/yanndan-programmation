from collections import Counter, OrderedDict
from dataclasses import dataclass
from typing import cast

from common import (
    file_name_utils,
    reports_utils,
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
        self.min_value = self.variable.min_numeric_values_by_number_occurrences
        self.max_value = self.variable.max_numeric_values_by_number_occurrences
        self.mean_value = round(self.variable.mean_numeric_values_by_number_occurrences, 2)
        self.median_value = self.variable.median_numeric_values_by_number_occurrences
        self.deciles = self.variable.deciles_numeric_values_by_number_occurrences
        self.centiles = self.variable.centiles_numeric_values_by_number_occurrences
        self.variance = self.variable.variance_numeric_values_by_number_occurrences
        self.ecart_type = self.variable.ecart_type_numeric_values_by_number_occurrences

        self.high_consumption_threshold = (
            # fmt: off
            200 if self.variable.equipment.equipment_type is atc_logs.EquipmentType.PAL
            else 250 if self.variable.equipment.equipment_type is atc_logs.EquipmentType.PAS 
            else 100 if self.variable.equipment.equipment_type is atc_logs.EquipmentType.PAE 
            else 0
            # fmt: on
        )

        # 1. Distribution (Médiane et Mode)
        donnees_triees = sorted(cast(list[float | int], self.variable.all_instant_states_best_values))
        n = len(donnees_triees)
        self.mediane = donnees_triees[n // 2] if n % 2 != 0 else (donnees_triees[n // 2 - 1] + donnees_triees[n // 2]) / 2
        self.mode = Counter(self.variable.all_instant_states_best_values).most_common(1)[0][0]

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
                    self.duree_max_consecutive = max(self.duree_max_consecutive, pics_consecutifs)
                    pics_consecutifs = 0

        # Vérification si le dernier pic touchait la fin de la liste
        self.duree_max_consecutive = max(self.duree_max_consecutive, pics_consecutifs)

        # 2. Dynamique (Deltas et Pentes)
        deltas = [
            cast(list[int | float], self.variable.all_instant_states_best_values)[i] - cast(list[int | float], self.variable.all_instant_states_best_values)[i - 1]
            for i in range(1, len(cast(list[int | float], self.variable.all_instant_states_best_values)))
        ]
        self.max_hausse_brutale = max(deltas) if deltas else 0

        # 3. Énergie engloutie par les anomalies
        conso_totale = sum(cast(list[int | float], self.variable.all_instant_states_best_values))
        conso_anomalies = sum(x for x in cast(list[int | float], self.variable.all_instant_states_best_values) if x > self.high_consumption_threshold)
        self.ratio_energie_pics = (conso_anomalies / conso_totale * 100) if conso_totale > 0 else 0

        # 4. Saturation au plafond (ex: >= 98%)
        points_saturation = sum(1 for x in cast(list[int | float], self.variable.all_instant_states_best_values) if x >= 98)
        self.taux_saturation = (points_saturation / len(cast(list[int | float], self.variable.all_instant_states_best_values))) * 100

        # 5. Temps de recouvrement (Cool-down) après anomalie
        en_crise = False
        temps_recouvrement = []
        compteur_recouv = 0
        cpu_moyenne = sum(cast(list[int | float], self.variable.all_instant_states_best_values)) / n

        for x in cast(list[int | float], self.variable.all_instant_states_best_values):
            if x > self.high_consumption_threshold:
                en_crise = True
                compteur_recouv = min(compteur_recouv, 0)
            elif en_crise:
                compteur_recouv += 1
                if x <= cpu_moyenne:  # Considéré comme récupéré quand sous la moyenne
                    temps_recouvrement.append(compteur_recouv)
                    en_crise = False
                    compteur_recouv = 0

        self.recouvrement_moyen = (sum(temps_recouvrement) / len(temps_recouvrement)) if temps_recouvrement else 0

        self.nb_anomalies = len(self.anomalies)
        self.taux_anomalie = (self.nb_anomalies / len(self.variable.all_instant_states_best_values)) * 100


def build_temps_cycle_report_from_atc_log(atc_test_results: list[atc_logs.ATCTestResult]) -> None:

    equipments_reports: list[OneEquipmentReport] = []
    for atc_test_result in atc_test_results:
        for atc_test_file in atc_test_result.all_atc_test_files:
            for equipment in atc_test_result.equipments_library.all_equipments:
                for temps_cycle_variable_name_candidate in ["STAB_CPT1", "TEMPS_AS"]:
                    variable = equipment.variables_library.get_variable_with_name_if_exists(temps_cycle_variable_name_candidate)
                    if variable is not None:
                        if variable.equipment.equipment_type in [atc_logs.EquipmentType.PAS, atc_logs.EquipmentType.PAL] and variable.max_numeric_values_by_number_occurrences < 60:
                            logger_config.print_and_log_info(
                                f"Ignore equipment {variable.equipment.name} in {atc_test_file.file_name} because is virtual (so no valid temps cycle). {variable.name} is too low to be real"
                            )
                        else:
                            equipment_report = OneEquipmentReport(variable=variable, atc_test_file=atc_test_file)
                            equipments_reports.append(equipment_report)

        rows_as_list_dict: list[OrderedDict] = []
        for equipment_report in equipments_reports:
            equipment_report_dict = OrderedDict(
                {
                    "file": equipment_report.atc_test_file.file_name,
                    "variable": equipment_report.variable.name,
                    "equipment": equipment_report.variable.equipment.name,
                    "min_value": equipment_report.min_value,
                    "max_value": equipment_report.max_value,
                    "mean_value": equipment_report.mean_value,
                    "median_value": equipment_report.median_value,
                    "mediane": equipment_report.mediane,
                    "high_consumption_threshold": equipment_report.high_consumption_threshold,
                    "variance": equipment_report.variance,
                    "ecart_type": equipment_report.ecart_type,
                    "duree_max_consecutive": equipment_report.duree_max_consecutive,
                    "nb_anomalies": equipment_report.nb_anomalies,
                    "taux_anomalie": equipment_report.taux_anomalie,
                    "mode": equipment_report.mode,
                    "recouvrement_moyen": equipment_report.recouvrement_moyen,
                    "taux_saturation": equipment_report.taux_saturation,
                    "ratio_energie_pics": equipment_report.ratio_energie_pics,
                    "max_hausse_brutale": equipment_report.max_hausse_brutale,
                    "nombre anomalies": len(equipment_report.anomalies),
                }
            )
            rows_as_list_dict.append(equipment_report_dict)
            for decile_index, decile_value in enumerate(equipment_report.deciles):
                equipment_report_dict[f"Decile_{decile_index+1}"] = decile_value
            for centile_index, centile_value in enumerate(equipment_report.centiles):
                equipment_report_dict[f"Centile_{centile_index+1}"] = centile_value

        reports_utils.save_rows_to_output_files(
            rows_as_list_dict=rows_as_list_dict,
            file_base_name=f"{atc_test_file.file_name}_temps_cycle_report",
            output_directory_path=OUTPUT_DIRECTORY,
            suffix_file_name_by_date=reports_utils.SuffixFileNameByDate.NO,
            split_big_files=False,
        )
