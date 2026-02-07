import pandas as pd
import datetime
import os
from collections import Counter
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional, Self, Tuple, cast, Any

import matplotlib.pyplot as plt
import plotly.graph_objects as go
from common import custom_iterator, file_name_utils
from logger import logger_config

# CONTENT_OF_FIELD_IN_CASE_OF_DECODING_ERROR = "!!! Decoding Error !!!"


class AlarmLineType(Enum):
    EVT_ALA = auto()
    DEB_ALA = auto()
    FIN_ALA = auto()
    OUV_SESSION = auto()
    FERM_SESSION = auto()
    CMD_ESSAIS = auto()
    CMD_CPT_RENDU = auto()
    CSI = auto()


@dataclass
class TerminalTechniqueEquipmentWithAlarms:
    name: str

    def __post_init__(self) -> None:
        self.alarms: List[TerminalTechniqueAlarm] = []


@dataclass
class TerminalTechniqueAlarm:
    raise_line: "TerminalTechniqueArchivesMaintLogLine"
    full_text: str
    alarm_type: AlarmLineType

    def __post_init__(self) -> None:
        self.end_alarm_line: Optional["TerminalTechniqueArchivesMaintLogLine"] = None
        self.equipment_name = self.full_text.split(" ")[0]
        self.equipment = self.raise_line.parent_file.library.get_or_create_equipment_with_alarms(self.equipment_name)
        self.equipment.alarms.append(self)


@dataclass
class TerminalTechniqueCsiAlarm(TerminalTechniqueAlarm):
    pass


@dataclass
class TerminalTechniqueEventAlarm(TerminalTechniqueAlarm):
    pass


@dataclass
class TerminalTechniqueClosableAlarm(TerminalTechniqueAlarm):

    def __post_init__(self) -> None:
        super().__post_init__()
        self.end_alarm_line: Optional["TerminalTechniqueArchivesMaintLogLine"] = None


@dataclass
class TerminalTechniqueSessionAlarm(TerminalTechniqueClosableAlarm):

    def __post_init__(self) -> None:
        super().__post_init__()
        self.session_name = self.raise_line.alarm_full_text


@dataclass
class TerminalTechniqueMccsHAlarm(TerminalTechniqueClosableAlarm):
    pass


@dataclass
class SaatMissingAcknowledgmentTerminalTechniqueAlarm(TerminalTechniqueEventAlarm):
    def __post_init__(self) -> None:
        super().__post_init__()
        self.chaine = self.raise_line.alarm_full_text.split(",")[3]
        self.repetition = int(self.raise_line.alarm_full_text.split(",")[4][0])


@dataclass
class SaharaTerminalTechniqueAlarm(TerminalTechniqueEventAlarm):
    last_back_to_past_detected: Optional["TerminalTechniqueArchivesMaintLogBackToPast"]
    last_mesd_alarm_group: Optional["TerminalTechniqueMesdAlarmsGroup"]

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.last_mesd_alarm_group:
            self.last_mesd_alarm_group.following_sahara_alarms.append(self)

        if self.last_back_to_past_detected and not self.last_back_to_past_detected.next_sahara_alarm:
            self.last_back_to_past_detected.next_sahara_alarm = self


@dataclass
class TerminalTechniqueArchivesMaintLogBackToPast:
    previous_line: "TerminalTechniqueArchivesMaintLogLine"
    next_line: "TerminalTechniqueArchivesMaintLogLine"

    def __post_init__(self) -> None:
        self.next_mesd_alarms_group: Optional[TerminalTechniqueMesdAlarmsGroup] = None
        self.next_sahara_alarm: Optional[SaharaTerminalTechniqueAlarm] = None
        self.next_back_to_past: Optional[TerminalTechniqueArchivesMaintLogBackToPast] = None
        if self.previous_line.parent_file.library.all_back_to_past_detected:
            self.previous_line.parent_file.library.all_back_to_past_detected[-1].next_back_to_past = self


@dataclass
class TerminalTechniqueMesdAlarmsGroup:
    library: "TerminalTechniqueArchivesMaintLibrary"
    number_of_group_in_library: int
    alarm_lines: List["TerminalTechniqueArchivesMaintLogLine"]
    last_back_to_past_detected: Optional[TerminalTechniqueArchivesMaintLogBackToPast]
    following_sahara_alarms: List[SaharaTerminalTechniqueAlarm] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.previous_group = self.library.all_mesd_alarms_groups[self.number_of_group_in_library - 2] if self.library.all_mesd_alarms_groups else None

    @property
    def first_line(self) -> "TerminalTechniqueArchivesMaintLogLine":
        return self.alarm_lines[0]

    @property
    def last_line(self) -> "TerminalTechniqueArchivesMaintLogLine":
        return self.alarm_lines[-1]


@dataclass
class TerminalTechniqueArchivesMaintLibrary:
    name: str

    def __post_init__(self) -> None:
        self.all_processed_lines: List["TerminalTechniqueArchivesMaintLogLine"] = []
        self.all_processed_files: List["TerminalTechniqueArchivesMaintFile"] = []
        self.currently_opened_alarms: List[TerminalTechniqueClosableAlarm] = []
        self.all_mesd_alarms_groups: List["TerminalTechniqueMesdAlarmsGroup"] = []
        self.ignored_end_alarms_without_alarm_begin: List[TerminalTechniqueClosableAlarm] = []
        self.sahara_alarms: List[SaharaTerminalTechniqueAlarm] = []
        self.mccs_hs_alarms: List[TerminalTechniqueMccsHAlarm] = []
        self.sessions_alarms: List[TerminalTechniqueSessionAlarm] = []
        self.equipments_with_alarms: List[TerminalTechniqueEquipmentWithAlarms] = []
        self.all_back_to_past_detected: List[TerminalTechniqueArchivesMaintLogBackToPast] = []
        self.mccs_alarms_files_names_and_line_numbers: List[Tuple[str, int]] = []

    def load_folder(self, folder_full_path: str) -> Self:

        last_line = None
        for dirpath, dirnames, filenames in os.walk(folder_full_path):
            for file_name in filenames:
                file = TerminalTechniqueArchivesMaintFile(parent_folder_full_path=dirpath, file_name=file_name, library=self, last_line=last_line)
                last_line = file.last_line
                self.all_processed_files.append(file)

                assert self.all_processed_lines
        assert self.all_processed_lines

        logger_config.print_and_log_info(f"{self.name}: ignored_end_alarms_without_alarm_begin:{len(self.ignored_end_alarms_without_alarm_begin)}")
        logger_config.print_and_log_info(f"{self.name}: currently_opened_alarms:{len(self.currently_opened_alarms)}")
        for equipment in self.equipments_with_alarms:
            logger_config.print_and_log_info(f"{self.name}: Equipment {equipment.name} has {len(equipment.alarms)} alarms")
        assert len(self.ignored_end_alarms_without_alarm_begin) < len(self.all_processed_lines), f"{len(self.ignored_end_alarms_without_alarm_begin)} too meny previously opened alarms"
        assert len(self.ignored_end_alarms_without_alarm_begin) < 50000, f"{len(self.ignored_end_alarms_without_alarm_begin)} ignored previously opened alarms"
        assert len(self.currently_opened_alarms) < 1000, f"{len(self.currently_opened_alarms)} opened alarms"

        return self

    def get_or_create_equipment_with_alarms(self, equipment_name: str) -> "TerminalTechniqueEquipmentWithAlarms":
        equipments_found = [equipment for equipment in self.equipments_with_alarms if equipment.name == equipment_name]
        if equipments_found:
            assert len(equipments_found) == 1
            return equipments_found[0]

        equipment = TerminalTechniqueEquipmentWithAlarms(name=equipment_name)
        self.equipments_with_alarms.append(equipment)
        return equipment

    def export_equipments_with_alarms_to_excel(self, output_folder_path: str, equipment_names_to_ignore: List[str]) -> None:
        """
        Exporte tous les équipements et leurs alarmes dans un fichier Excel.

        Args:
            output_folder_path: Chemin du dossier de sortie
            equipment_names_to_ignore: Liste des noms d'équipements à ignorer
        """
        with logger_config.stopwatch_with_label(f"{self.name} export_equipments_with_alarms_to_excel"):
            try:
                if not self.equipments_with_alarms:
                    logger_config.print_and_log_error("Aucun équipement avec alarmes. Aucun fichier créé.")
                    return

                # Préparer les données pour les équipements
                equipment_data: List[Dict[str, Any]] = []
                for equipment in self.equipments_with_alarms:
                    if equipment.name not in equipment_names_to_ignore:
                        for alarm in equipment.alarms:
                            equipment_data.append(
                                {
                                    "Equipment Name": equipment.name,
                                    "Type alarm (class name)": type(alarm).__name__,
                                    "Alarm Type": alarm.alarm_type.name,
                                    "Raise alarm: Timestamp": alarm.raise_line.decoded_timestamp,
                                    "Raise alarm: File name": alarm.raise_line.parent_file.file_name,
                                    "Raise alarm: Line number": alarm.raise_line.line_number_inside_file,
                                    "End alarm (if any): Timestamp": alarm.end_alarm_line.decoded_timestamp if alarm.end_alarm_line else "NA",
                                    "End alarm (if any): File name": alarm.end_alarm_line.parent_file.file_name if alarm.end_alarm_line else "NA",
                                    "End alarm (if any): Line number": alarm.end_alarm_line.line_number_inside_file if alarm.end_alarm_line else "NA",
                                    "Full Text": alarm.full_text.strip(),
                                }
                            )

                # Créer plusieurs fichiers CSV (un par 'feuille')
                suffix = file_name_utils.get_file_suffix_with_current_datetime()

                try:
                    df_equipment = pd.DataFrame(equipment_data)
                    equipments_csv = output_folder_path + "/" + f"{self.name}_equipments_with_alarms_all_{suffix}.csv"
                    df_equipment.to_csv(equipments_csv, index=False)
                except Exception as e:
                    logger_config.print_and_log_exception(e)

                # SAHARA
                try:
                    sahara_data: List[Dict[str, Any]] = []
                    for sahara_alarm in self.sahara_alarms:
                        sahara_data.append(
                            {
                                "Timestamp": sahara_alarm.raise_line.decoded_timestamp,
                                "File Name": sahara_alarm.raise_line.parent_file.file_name,
                                "Line Number": sahara_alarm.raise_line.line_number_inside_file,
                                "Alarm Type": sahara_alarm.alarm_type.name,
                                "Full Text": sahara_alarm.full_text.strip(),
                            }
                        )
                    df_sahara = pd.DataFrame(sahara_data)
                    sahara_csv = output_folder_path + "/" + f"{self.name}_equipments_with_alarms_sahara_alarms_{suffix}.csv"
                    df_sahara.to_csv(sahara_csv, index=False)
                except Exception as e:
                    logger_config.print_and_log_exception(e)

                # MCCS H
                try:
                    mccs_data: List[Dict[str, Any]] = []
                    for mccs_alarm in self.mccs_hs_alarms:
                        mccs_data.append(
                            {
                                "Alarm Type": mccs_alarm.alarm_type.name,
                                "Duration in seconds": (mccs_alarm.end_alarm_line.decoded_timestamp - mccs_alarm.raise_line.decoded_timestamp).total_seconds() if mccs_alarm.end_alarm_line else None,
                                "Timestamp": mccs_alarm.raise_line.decoded_timestamp,
                                "File Name": mccs_alarm.raise_line.parent_file.file_name,
                                "Line Number": mccs_alarm.raise_line.line_number_inside_file,
                                "End Timestamp": mccs_alarm.end_alarm_line.decoded_timestamp if mccs_alarm.end_alarm_line else "NA",
                                "End File Name": mccs_alarm.end_alarm_line.parent_file.file_name if mccs_alarm.end_alarm_line else "NA",
                                "End Line Number": mccs_alarm.end_alarm_line.line_number_inside_file if mccs_alarm.end_alarm_line else "NA",
                                "Full Text": mccs_alarm.full_text.strip(),
                            }
                        )
                    df_mccs = pd.DataFrame(mccs_data)
                    mccs_csv = output_folder_path + "/" + f"{self.name}_equipments_with_alarms__mccs_h_alarms_{suffix}.csv"
                    df_mccs.to_csv(mccs_csv, index=False)
                except Exception as e:
                    logger_config.print_and_log_exception(e)

                # Back to Past
                try:
                    btp_data: List[Dict[str, Any]] = []
                    for back_to_past in self.all_back_to_past_detected:
                        duration = (back_to_past.next_line.decoded_timestamp - back_to_past.previous_line.decoded_timestamp).total_seconds()
                        btp_data.append(
                            {
                                "Previous Line Timestamp": back_to_past.previous_line.decoded_timestamp,
                                "Previous Line Number": back_to_past.previous_line.line_number_inside_file,
                                "Next Line Timestamp": back_to_past.next_line.decoded_timestamp,
                                "Next Line Number": back_to_past.next_line.line_number_inside_file,
                                "Duration (seconds)": duration,
                            }
                        )
                    df_btp = pd.DataFrame(btp_data)
                    btp_csv = output_folder_path + "/" + f"{self.name}_equipments_with_alarms_back_to_past_{suffix}.csv"
                    df_btp.to_csv(btp_csv, index=False)
                except Exception as e:
                    logger_config.print_and_log_exception(e)

                logger_config.print_and_log_info(f"Fichiers CSV créés avec suffixe: {suffix}")
                total_alarms = sum(len(equipment.alarms) for equipment in self.equipments_with_alarms)
                logger_config.print_and_log_info(f"Total de {total_alarms} alarmes sauvegardées")
                logger_config.print_and_log_info(
                    f"Fichiers créés: Equipments ({len(equipment_data)}), SAHARA Alarms ({len(self.sahara_alarms)}), MCCS H Alarms ({len(self.mccs_hs_alarms)}), Back to Past ({len(self.all_back_to_past_detected)})"
                )
            except Exception as e:
                logger_config.print_and_log_exception(e)

    def plot_alarms_by_period(self, output_folder_path: str, equipment_names_to_ignore: List[str], interval_minutes: int = 10, do_show: bool = False) -> None:
        """
        Génère un bar graph montrant les événements par intervalle de temps.

        Args:
            output_folder_path: Chemin du dossier de sortie
            equipment_names_to_ignore: Liste des noms d'équipements à ignorer
            interval_minutes: Intervalle de temps en minutes (par défaut 10)
            do_show: Afficher le graphique matplotlib
        """

        try:
            if not self.all_processed_lines:
                logger_config.print_and_log_error("La liste des traces est vide. Aucun fichier créé.")
                return

            with logger_config.stopwatch_with_label(f"{self.name} plot_alarms_by_period"):

                # Déterminer la période totale
                start_time = self.all_processed_lines[0].decoded_timestamp
                end_time = self.all_processed_lines[-1].decoded_timestamp

                # Créer des intervalles de temps
                interval_start_times: List[datetime.datetime] = []
                current_time = start_time
                while current_time <= end_time:
                    interval_start_times.append(current_time)
                    current_time += datetime.timedelta(minutes=interval_minutes)

                # Initialiser les compteurs pour chaque intervalle
                interval_back_to_past_count: Dict[Tuple[datetime.datetime, datetime.datetime], int] = {}
                interval_sahara_count: Dict[Tuple[datetime.datetime, datetime.datetime], int] = {}
                interval_equipment_counts: Dict[Tuple[datetime.datetime, datetime.datetime], Dict[str, int]] = {}

                for interval_start in interval_start_times:
                    interval_end = interval_start + datetime.timedelta(minutes=interval_minutes)
                    interval_back_to_past_count[(interval_start, interval_end)] = 0
                    interval_sahara_count[(interval_start, interval_end)] = 0
                    interval_equipment_counts[(interval_start, interval_end)] = {}

                # Compter les back_to_past_detected
                for back_to_past in self.all_back_to_past_detected:
                    timestamp = back_to_past.previous_line.decoded_timestamp
                    for interval_start in interval_start_times:
                        interval_end = interval_start + datetime.timedelta(minutes=interval_minutes)
                        if interval_start <= timestamp < interval_end:
                            interval_back_to_past_count[(interval_start, interval_end)] += 1
                            break

                # Compter les sahara_alarms
                for sahara_alarm in self.sahara_alarms:
                    timestamp = sahara_alarm.raise_line.decoded_timestamp
                    for interval_start in interval_start_times:
                        interval_end = interval_start + datetime.timedelta(minutes=interval_minutes)
                        if interval_start <= timestamp < interval_end:
                            interval_sahara_count[(interval_start, interval_end)] += 1
                            break

                # Compter les alarmes par équipement
                for equipment in self.equipments_with_alarms:
                    if equipment.name not in equipment_names_to_ignore:
                        for alarm in equipment.alarms:
                            timestamp = alarm.raise_line.decoded_timestamp
                            for interval_start in interval_start_times:
                                interval_end = interval_start + datetime.timedelta(minutes=interval_minutes)
                                if interval_start <= timestamp < interval_end:
                                    if equipment.name not in interval_equipment_counts[(interval_start, interval_end)]:
                                        interval_equipment_counts[(interval_start, interval_end)][equipment.name] = 0
                                    interval_equipment_counts[(interval_start, interval_end)][equipment.name] += 1
                                    break

                # Préparer les données pour le graphe
                x_labels = [f"{begin.strftime("('%Y%m%d_%H:%M")} - {end.strftime("%H:%M")}" for begin, end in interval_back_to_past_count.keys()]
                y_back_to_past = list(interval_back_to_past_count.values())
                y_sahara = list(interval_sahara_count.values())

                # Récupérer tous les noms d'équipements uniques (en ordre d'apparition)
                equipment_names: List[str] = []
                for interval_counts in interval_equipment_counts.values():
                    for name in interval_counts.keys():
                        if name not in equipment_names:
                            equipment_names.append(name)

                # Créer et exporter les données dans un fichier Excel
                excel_filename = f"{self.name}_alarms_by_period{file_name_utils.get_file_suffix_with_current_datetime()}.xlsx"

                # Préparer les données pour le DataFrame
                excel_data: List[Dict[str, Any]] = []
                for (interval_begin, interval_end), back_to_past_count in interval_back_to_past_count.items():
                    row_data: Dict[str, Any] = {
                        "Début Intervalle": interval_begin,
                        "Fin Intervalle": interval_end,
                        "Back to Past": back_to_past_count,
                        "Sahara": interval_sahara_count[(interval_begin, interval_end)],
                    }
                    for equipment_name in equipment_names:
                        count = interval_equipment_counts[(interval_begin, interval_end)].get(equipment_name, 0)
                        row_data[equipment_name] = count
                    excel_data.append(row_data)

                df = pd.DataFrame(excel_data)
                df.to_excel(output_folder_path + "/" + excel_filename, index=False)
                logger_config.print_and_log_info(f"Fichier Excel créé: {excel_filename}")

                # Créer et sauvegarder le graphe en HTML avec Plotly
                html_filename = f"{self.name}_alarms_by_period_{file_name_utils.get_file_suffix_with_current_datetime()}.html"

                fig_data = [
                    go.Bar(
                        name="Back to Past",
                        x=x_labels,
                        y=y_back_to_past,
                        marker=dict(color="orangered"),
                        text=y_back_to_past,
                        textposition="auto",
                    ),
                    go.Bar(
                        name="Sahara",
                        x=x_labels,
                        y=y_sahara,
                        marker=dict(color="gold"),
                        text=y_sahara,
                        textposition="auto",
                    ),
                ]

                # Ajouter les équipements
                colors = ["steelblue", "lightseagreen", "mediumseagreen", "lightcoral", "plum", "khaki", "lightcyan", "lightsalmon"]
                for equipment_idx, equipment_name in enumerate(equipment_names):
                    y_equipment = [
                        interval_equipment_counts[(interval_start, interval_start + datetime.timedelta(minutes=interval_minutes))].get(equipment_name, 0) for interval_start in interval_start_times
                    ]
                    fig_data.append(
                        go.Bar(
                            name=equipment_name,
                            x=x_labels,
                            y=y_equipment,
                            marker=dict(color=colors[equipment_idx % len(colors)]),
                            text=y_equipment,
                            textposition="auto",
                        )
                    )

                fig = go.Figure(data=fig_data)

                fig.update_layout(
                    title=f"{self.name} Alarmes par périodes de {interval_minutes} minutes entre {start_time.strftime('%Y-%m-%d %H:%M')} et {end_time.strftime('%Y-%m-%d %H:%M')}",
                    xaxis_title="Intervalles de temps (heure début - heure fin)",
                    yaxis_title="Nombre",
                    barmode="group",
                    hovermode="x unified",
                    template="plotly_white",
                    height=600,
                    width=1400,
                )

                fig.write_html(output_folder_path + "/" + html_filename)
                logger_config.print_and_log_info(f"Fichier HTML créé: {html_filename}")

                # Afficher le bar graph matplotlib
                plt.figure(figsize=(16, 8))
                x_pos = range(len(x_labels))
                width = 0.8 / (len(equipment_names) + 2)

                plt.bar([p - 0.4 for p in x_pos], y_back_to_past, width, label="Back to Past", color="orangered")
                plt.bar([p - 0.4 + width for p in x_pos], y_sahara, width, label="Sahara", color="gold")

                for equipment_idx, equipment_name in enumerate(equipment_names):
                    y_equipment = [
                        interval_equipment_counts[(interval_start, interval_start + datetime.timedelta(minutes=interval_minutes))].get(equipment_name, 0) for interval_start in interval_start_times
                    ]
                    plt.bar([p - 0.4 + width * (2 + equipment_idx) for p in x_pos], y_equipment, width, label=equipment_name, color=colors[equipment_idx % len(colors)])

                plt.xlabel("Intervalles de temps (heure début - heure fin)")
                plt.ylabel("Nombre")
                plt.title(f"{self.name} Alarmes par périodes de {interval_minutes} minutes entre {start_time.strftime("%Y-%m-%d %H:%M")} et {end_time.strftime("%Y-%m-%d %H:%M")}")
                plt.xticks(x_pos, x_labels, rotation=45, ha="right")
                plt.legend(loc="upper left", bbox_to_anchor=(1, 1))
                plt.tight_layout()
                if do_show:
                    plt.show()

        except Exception as e:
            logger_config.print_and_log_exception(e)

    def plot_sahara_alarms_by_period(self, output_folder_path: str, interval_minutes: int = 10, do_show: bool = False) -> None:
        """
        Génère un bar graph montrant les alarmes SAHARA par intervalle de temps.

        Args:
            output_folder_path: Chemin du dossier de sortie
            interval_minutes: Intervalle de temps en minutes (par défaut 10)
            do_show: Afficher le graphique matplotlib
        """

        try:
            if not self.all_processed_lines:
                logger_config.print_and_log_error("La liste des traces est vide. Aucun fichier créé.")
                return

            # Déterminer la période totale
            start_time = self.all_processed_lines[0].decoded_timestamp
            end_time = self.all_processed_lines[-1].decoded_timestamp

            # Créer des intervalles de temps
            intervals: List[Tuple[datetime.datetime, datetime.datetime]] = []
            interval_start_times: List[datetime.datetime] = []
            current_time = start_time
            while current_time <= end_time:
                interval_start_time = current_time
                interval_start_times.append(current_time)
                current_time += datetime.timedelta(minutes=interval_minutes)
                interval_end_time = current_time
                intervals.append((interval_start_time, interval_end_time))

            logger_config.print_and_log_info(f"plot_sahara_alarms_by_period: {len(interval_start_times)} intervals of {interval_minutes} minutes between {start_time} and {end_time}")

            interval_sahara_counts: Dict[Tuple[datetime.datetime, datetime.datetime], int] = Counter()

            for interval in intervals:
                interval_sahara_counts[interval] = 0

            # Compter les alarmes SAHARA dans chaque intervalle
            for sahara_alarm in self.sahara_alarms:
                timestamp = sahara_alarm.raise_line.decoded_timestamp
                for interval_start in interval_start_times:
                    interval_end = interval_start + datetime.timedelta(minutes=interval_minutes)
                    if interval_start <= timestamp < interval_end:
                        # logger_config.print_and_log_info(f"plot_sahara_alarms_by_period: Sahara alarm {sahara_alarm.raise_line.full_raw_line} counted in interval {(interval_start, interval_end)}")
                        interval_sahara_counts[(interval_start, interval_end)] += 1
                        break

            # Préparer les données pour le graphe
            x_labels = [f"{begin.strftime("('%Y%m%d %H:%M")} - {end.strftime("%H:%M")}" for begin, end in interval_sahara_counts.keys()]
            y_values = list(interval_sahara_counts.values())

            # Créer et exporter les données dans un fichier Excel
            excel_filename = f"{self.name}_sahara_alarms_by_period{file_name_utils.get_file_suffix_with_current_datetime()}.xlsx"

            # Préparer les données pour le DataFrame
            excel_data: List[Dict[str, Any]] = []
            for (interval_begin, interval_end), count in interval_sahara_counts.items():
                excel_data.append(
                    {
                        "Début Intervalle de temps": interval_begin,
                        "Fin Intervalle de temps": interval_end,
                        "Nombre d'alarmes SAHARA": count,
                    }
                )

            df = pd.DataFrame(excel_data)
            df.to_excel(output_folder_path + "/" + excel_filename, index=False)
            logger_config.print_and_log_info(f"Fichier Excel créé: {excel_filename}")

            # Créer et sauvegarder le graphe en HTML avec Plotly
            html_filename = f"{self.name}_sahara_alarms_by_period_{file_name_utils.get_file_suffix_with_current_datetime()}.html"
            fig = go.Figure(
                data=[
                    go.Bar(
                        x=x_labels,
                        y=y_values,
                        marker=dict(color="gold"),
                        text=y_values,
                        textposition="auto",
                    )
                ]
            )

            fig.update_layout(
                title=f"{self.name} {len(self.sahara_alarms)} alarmes SAHARA par périodes de {interval_minutes} minutes entre {start_time.strftime('%Y-%m-%d %H:%M')} et {end_time.strftime('%Y-%m-%d %H:%M')}",
                xaxis_title="Intervalles de temps (heure début - heure fin)",
                yaxis_title="Nombre d'alarmes SAHARA",
                hovermode="x unified",
                template="plotly_white",
                height=600,
                width=1000,
            )

            fig.write_html(output_folder_path + "/" + html_filename)
            logger_config.print_and_log_info(f"Fichier HTML créé: {html_filename}")

            # Afficher le bar graph
            plt.figure(figsize=(12, 6))
            plt.bar(x_labels, y_values, color="gold", width=0.6)
            plt.xlabel("Intervalles de temps (heure début - heure fin)")
            plt.ylabel("Nombre d'alarmes SAHARA")
            plt.title(
                f"{self.name} {len(self.sahara_alarms)} alarmes SAHARA par périodes de {interval_minutes} minutes entre {start_time.strftime("%Y-%m-%d %H:%M")} et {end_time.strftime("%Y-%m-%d %H:%M")}"
            )
            plt.xticks(rotation=45, ha="right")
            plt.tight_layout()
            if do_show:
                plt.show()

        except Exception as e:
            logger_config.print_and_log_exception(e)

    def plot_back_to_past_by_period(self, output_folder_path: str, interval_minutes: int = 10, do_show: bool = False) -> None:
        """
        Génère un bar graph montrant les événements back_to_past par intervalle de temps.

        Args:
            output_folder_path: Chemin du dossier de sortie
            interval_minutes: Intervalle de temps en minutes (par défaut 10)
            do_show: Afficher le graphique matplotlib
        """

        with logger_config.stopwatch_with_label(f"{self.name} plot_back_to_past_by_period"):

            try:
                if not self.all_processed_lines:
                    logger_config.print_and_log_error("La liste des traces est vide. Aucun fichier créé.")
                    return

                # Déterminer la période totale
                start_time = self.all_processed_lines[0].decoded_timestamp
                end_time = self.all_processed_lines[-1].decoded_timestamp

                # Créer des intervalles de temps
                intervals: List[Tuple[datetime.datetime, datetime.datetime]] = []
                interval_start_times: List[datetime.datetime] = []
                current_time = start_time
                while current_time <= end_time:
                    interval_start_time = current_time
                    interval_start_times.append(current_time)
                    current_time += datetime.timedelta(minutes=interval_minutes)
                    interval_end_time = current_time
                    intervals.append((interval_start_time, interval_end_time))

                interval_back_to_past_counts: Dict[Tuple[datetime.datetime, datetime.datetime], int] = Counter()
                for interval in intervals:
                    interval_back_to_past_counts[interval] = 0
                # Compter les back_to_past_detected dans chaque intervalle
                for back_to_past in self.all_back_to_past_detected:
                    timestamp = back_to_past.previous_line.decoded_timestamp
                    for interval_start in interval_start_times:
                        interval_end = interval_start + datetime.timedelta(minutes=interval_minutes)
                        if interval_start <= timestamp < interval_end:
                            interval_back_to_past_counts[(interval_start, interval_end)] += 1
                            break

                # Préparer les données pour le graphe
                x_labels = [f"{begin.strftime("%Y%m%d_%H:%M")} - {end.strftime("%H:%M")}" for begin, end in interval_back_to_past_counts.keys()]
                y_values = list(interval_back_to_past_counts.values())

                # Créer et exporter les données dans un fichier Excel
                excel_filename = f"{self.name}_back_to_past_by_period{file_name_utils.get_file_suffix_with_current_datetime()}.xlsx"

                # Préparer les données pour le DataFrame
                excel_data: List[Dict[str, Any]] = []
                for (interval_begin, interval_end), count in interval_back_to_past_counts.items():
                    excel_data.append(
                        {
                            "Début Intervalle de temps": interval_begin,
                            "Fin Intervalle de temps": interval_end,
                            "Nombre d'événements Back to Past": count,
                        }
                    )

                df = pd.DataFrame(excel_data)
                df.to_excel(output_folder_path + "/" + excel_filename, index=False)
                logger_config.print_and_log_info(f"Fichier Excel créé: {excel_filename}")

                # Créer et sauvegarder le graphe en HTML avec Plotly
                html_filename = f"{self.name}_back_to_past_by_period{file_name_utils.get_file_suffix_with_current_datetime()}.html"
                fig = go.Figure(
                    data=[
                        go.Bar(
                            x=x_labels,
                            y=y_values,
                            marker=dict(color="orangered"),
                            text=y_values,
                            textposition="auto",
                        )
                    ]
                )

                fig.update_layout(
                    title=f"{self.name} {len(self.all_back_to_past_detected)} événements Back to Past par périodes de {interval_minutes} minutes entre {start_time.strftime('%Y-%m-%d %H:%M')} et {end_time.strftime('%Y-%m-%d %H:%M')}",
                    xaxis_title="Intervalles de temps (heure début - heure fin)",
                    yaxis_title="Nombre d'événements Back to Past",
                    hovermode="x unified",
                    template="plotly_white",
                    height=600,
                    width=1000,
                )

                fig.write_html(output_folder_path + "/" + html_filename)
                logger_config.print_and_log_info(f"Fichier HTML créé: {html_filename}")

                # Afficher le bar graph
                plt.figure(figsize=(12, 6))
                plt.bar(x_labels, y_values, color="orangered", width=0.6)
                plt.xlabel("Intervalles de temps (heure début - heure fin)")
                plt.ylabel("Nombre d'événements Back to Past")
                plt.title(
                    f"{self.name} {len(self.all_back_to_past_detected)} événements Back to Past par périodes de {interval_minutes} minutes entre {start_time.strftime("%Y-%m-%d %H:%M")} et {end_time.strftime("%Y-%m-%d %H:%M")}"
                )
                plt.xticks(rotation=45, ha="right")
                plt.tight_layout()
                if do_show:
                    plt.show()

            except Exception as e:
                logger_config.print_and_log_exception(e)

    def plot_sahara_mccs_back_to_past_by_period(self, output_folder_path: str, interval_minutes: int = 10, do_show: bool = False) -> None:
        """
        Génère un bar graph montrant SAHARA, MCCS H et Back to Past par intervalle de temps.

        Args:
            output_folder_path: Chemin du dossier de sortie
            interval_minutes: Intervalle de temps en minutes (par défaut 10)
            do_show: Afficher le graphique matplotlib
        """
        with logger_config.stopwatch_with_label(f"{self.name} plot_sahara_mccs_back_to_past_by_period"):

            try:
                if not self.all_processed_lines:
                    logger_config.print_and_log_error("La liste des traces est vide. Aucun fichier créé.")
                    return

                # Déterminer la période totale
                start_time = self.all_processed_lines[0].decoded_timestamp
                end_time = self.all_processed_lines[-1].decoded_timestamp

                # Créer des intervalles de temps
                intervals: List[Tuple[datetime.datetime, datetime.datetime]] = []
                interval_start_times: List[datetime.datetime] = []
                current_time = start_time
                while current_time <= end_time:
                    interval_start_time = current_time
                    interval_start_times.append(current_time)
                    current_time += datetime.timedelta(minutes=interval_minutes)
                    interval_end_time = current_time
                    intervals.append((interval_start_time, interval_end_time))

                # Compter les événements dans chaque intervalle
                interval_sahara_counts: Dict[Tuple[datetime.datetime, datetime.datetime], int] = Counter()
                interval_mccs_counts: Dict[Tuple[datetime.datetime, datetime.datetime], int] = Counter()
                interval_back_to_past_counts: Dict[Tuple[datetime.datetime, datetime.datetime], int] = Counter()

                for interval in intervals:
                    interval_sahara_counts[interval] = 0
                    interval_mccs_counts[interval] = 0
                    interval_back_to_past_counts[interval] = 0

                # Compter les sahara_alarms
                for sahara_alarm in self.sahara_alarms:
                    timestamp = sahara_alarm.raise_line.decoded_timestamp
                    for interval_start in interval_start_times:
                        interval_end = interval_start + datetime.timedelta(minutes=interval_minutes)
                        if interval_start <= timestamp < interval_end:
                            interval_sahara_counts[(interval_start, interval_end)] += 1
                            break

                # Compter les mccs_hs_alarms
                for mccs_alarm in self.mccs_hs_alarms:
                    timestamp = mccs_alarm.raise_line.decoded_timestamp
                    for interval_start in interval_start_times:
                        interval_end = interval_start + datetime.timedelta(minutes=interval_minutes)
                        if interval_start <= timestamp < interval_end:
                            interval_mccs_counts[(interval_start, interval_end)] += 1
                            break

                # Compter les back_to_past_detected
                for back_to_past in self.all_back_to_past_detected:
                    timestamp = back_to_past.previous_line.decoded_timestamp
                    for interval_start in interval_start_times:
                        interval_end = interval_start + datetime.timedelta(minutes=interval_minutes)
                        if interval_start <= timestamp < interval_end:
                            interval_back_to_past_counts[(interval_start, interval_end)] += 1
                            break

                # Initialiser les compteurs pour les intervalles manquants
                for interval_start in interval_start_times:
                    interval_end = interval_start + datetime.timedelta(minutes=interval_minutes)
                    if (interval_start, interval_end) not in interval_sahara_counts:
                        interval_sahara_counts[(interval_start, interval_end)] = 0
                    if (interval_start, interval_end) not in interval_mccs_counts:
                        interval_mccs_counts[(interval_start, interval_end)] = 0
                    if (interval_start, interval_end) not in interval_back_to_past_counts:
                        interval_back_to_past_counts[(interval_start, interval_end)] = 0

                # Préparer les données pour le graphe
                x_labels = [f"{begin.strftime("('%Y%m%d_%H:%M")} - {end.strftime("%H:%M")}" for begin, end in interval_sahara_counts.keys()]
                y_sahara = [interval_sahara_counts[(begin, end)] for begin, end in interval_sahara_counts.keys()]
                y_mccs = [interval_mccs_counts[(begin, end)] for begin, end in interval_sahara_counts.keys()]
                y_back_to_past = [interval_back_to_past_counts[(begin, end)] for begin, end in interval_sahara_counts.keys()]

                # Créer et exporter les données dans un fichier Excel
                excel_filename = f"{self.name}_sahara_mccs_back_to_past_by_period{file_name_utils.get_file_suffix_with_current_datetime()}.xlsx"

                # Préparer les données pour le DataFrame
                excel_data: List[Dict[str, Any]] = []
                for (interval_begin, interval_end), sahara_count in interval_sahara_counts.items():
                    excel_data.append(
                        {
                            "Début Intervalle de temps": interval_begin,
                            "Fin Intervalle de temps": interval_end,
                            "Nombre SAHARA": sahara_count,
                            "Nombre MCCS H": interval_mccs_counts[(interval_begin, interval_end)],
                            "Nombre Back to Past": interval_back_to_past_counts[(interval_begin, interval_end)],
                        }
                    )

                df = pd.DataFrame(excel_data)
                df.to_excel(output_folder_path + "/" + excel_filename, index=False)
                logger_config.print_and_log_info(f"Fichier Excel créé: {excel_filename}")

                # Créer et sauvegarder le graphe en HTML avec Plotly
                html_filename = f"{self.name}_sahara_mccs_back_to_past_by_period{file_name_utils.get_file_suffix_with_current_datetime()}.html"
                fig = go.Figure(
                    data=[
                        go.Bar(
                            name="SAHARA",
                            x=x_labels,
                            y=y_sahara,
                            marker=dict(color="gold"),
                            text=y_sahara,
                            textposition="auto",
                        ),
                        go.Bar(
                            name="MCCS H",
                            x=x_labels,
                            y=y_mccs,
                            marker=dict(color="steelblue"),
                            text=y_mccs,
                            textposition="auto",
                        ),
                        go.Bar(
                            name="Back to Past",
                            x=x_labels,
                            y=y_back_to_past,
                            marker=dict(color="orangered"),
                            text=y_back_to_past,
                            textposition="auto",
                        ),
                    ]
                )

                fig.update_layout(
                    title=f"{self.name} SAHARA, MCCS H et Back to Past par périodes de {interval_minutes} minutes entre {start_time.strftime('%Y-%m-%d %H:%M')} et {end_time.strftime('%Y-%m-%d %H:%M')}",
                    xaxis_title="Intervalles de temps (heure début - heure fin)",
                    yaxis_title="Nombre d'événements",
                    barmode="group",
                    hovermode="x unified",
                    template="plotly_white",
                    height=600,
                    width=1200,
                )

                fig.write_html(output_folder_path + "/" + html_filename)
                logger_config.print_and_log_info(f"Fichier HTML créé: {html_filename}")

                # Afficher le bar graph matplotlib
                plt.figure(figsize=(14, 7))
                x_pos = range(len(x_labels))
                width = 0.25

                plt.bar([p - width for p in x_pos], y_sahara, width, label="SAHARA", color="gold")
                plt.bar(x_pos, y_mccs, width, label="MCCS H", color="steelblue")
                plt.bar([p + width for p in x_pos], y_back_to_past, width, label="Back to Past", color="orangered")

                plt.xlabel("Intervalles de temps (heure début - heure fin)")
                plt.ylabel("Nombre d'événements")
                plt.title(
                    f"{self.name} SAHARA, MCCS H et Back to Past par périodes de {interval_minutes} minutes entre {start_time.strftime("%Y-%m-%d %H:%M")} et {end_time.strftime("%Y-%m-%d %H:%M")}"
                )
                plt.xticks(x_pos, x_labels, rotation=45, ha="right")
                plt.legend()
                plt.tight_layout()
                if do_show:
                    plt.show()

            except Exception as e:
                logger_config.print_and_log_exception(e)

    def dump_all_events_to_text_file(self, output_folder_path: str) -> None:
        """
        Dump tous les événements (MCCS H alarms, SAHARA alarms, Back to Past)
        dans un fichier texte par ordre chronologique.

        Args:
            output_folder_path: Chemin du dossier de sortie
        """
        with logger_config.stopwatch_with_label(f"{self.name} dump_all_events_to_text_file"):
            try:
                if not self.all_processed_lines:
                    logger_config.print_and_log_error("La liste des traces est vide. Aucun fichier créé.")
                    return

                # Créer une liste contenant tous les événements avec leurs timestamps
                events: List[Tuple[datetime.datetime, str, str]] = []

                # Ajouter les MCCS H alarms
                for mccs_alarm in self.mccs_hs_alarms:
                    timestamp = mccs_alarm.raise_line.decoded_timestamp
                    event_text = f"[MCCS H ALARM] {timestamp} | File: {mccs_alarm.raise_line.parent_file.file_name}:{mccs_alarm.raise_line.line_number_inside_file} | {mccs_alarm.full_text.strip()}"
                    events.append((timestamp, "MCCS_H", event_text))

                # Ajouter les SAHARA alarms
                for sahara_alarm in self.sahara_alarms:
                    timestamp = sahara_alarm.raise_line.decoded_timestamp
                    event_text = (
                        f"[SAHARA ALARM] {timestamp} | File: {sahara_alarm.raise_line.parent_file.file_name}:{sahara_alarm.raise_line.line_number_inside_file} | {sahara_alarm.full_text.strip()}"
                    )
                    events.append((timestamp, "SAHARA", event_text))

                # Ajouter les Back to Past events
                for back_to_past in self.all_back_to_past_detected:
                    timestamp = back_to_past.previous_line.decoded_timestamp
                    next_timestamp = back_to_past.next_line.decoded_timestamp
                    time_diff = (next_timestamp - timestamp).total_seconds()
                    event_text = f"[BACK TO PAST] {timestamp} | Previous: {back_to_past.previous_line.parent_file.file_name}:{back_to_past.previous_line.line_number_inside_file} | Next: {back_to_past.next_line.parent_file.file_name}:{back_to_past.next_line.line_number_inside_file} | Jump: {time_diff:.2f}s backward"
                    events.append((timestamp, "BACK_TO_PAST", event_text))

                # Trier tous les événements par timestamp
                events.sort(key=lambda x: x[0])

                # Écrire dans le fichier texte
                text_filename = f"{self.name}_all_events{file_name_utils.get_file_suffix_with_current_datetime()}.txt"

                with open(output_folder_path + "/" + text_filename, mode="w", encoding="utf-8") as f:
                    f.write(f"{'='*120}\n")
                    f.write(f"Chronological dump of all events for {self.name}\n")
                    f.write(f"Total events: {len(events)} (MCCS H: {len(self.mccs_hs_alarms)}, SAHARA: {len(self.sahara_alarms)}, Back to Past: {len(self.all_back_to_past_detected)})\n")
                    f.write(f"{'='*120}\n\n")

                    for timestamp, event_type, event_text in events:
                        f.write(event_text + "\n")

                logger_config.print_and_log_info(f"Fichier texte créé: {text_filename}")
                logger_config.print_and_log_info(
                    f"Total de {len(events)} événements exportés (MCCS H: {len(self.mccs_hs_alarms)}, SAHARA: {len(self.sahara_alarms)}, Back to Past: {len(self.all_back_to_past_detected)})"
                )

            except Exception as e:
                logger_config.print_and_log_exception(e)

    def export_back_to_past_with_context_to_excel(self, output_folder_path: str) -> None:

        with logger_config.stopwatch_with_label(f"{self.name}: export_back_to_past_with_context_to_excel", inform_beginning=False, enable_print=False, enabled=False):
            try:
                rows: List[Dict[str, Any]] = []
                for back_to_past in self.all_back_to_past_detected:
                    rows.append(
                        {
                            "Timestamp": back_to_past.previous_line.decoded_timestamp,
                            "File name and line number": back_to_past.previous_line.parent_file.file_name + ":" + str(back_to_past.previous_line.line_number_inside_file),
                            "Lines until next back to past": (
                                str(back_to_past.next_back_to_past.previous_line.line_number_in_library - back_to_past.previous_line.line_number_in_library)
                                if back_to_past.next_back_to_past
                                else "No folling back to past"
                            ),
                            "Lines until next MESD alarms": (
                                str(back_to_past.next_mesd_alarms_group.first_line.line_number_in_library - back_to_past.previous_line.line_number_in_library)
                                if back_to_past.next_mesd_alarms_group
                                else "No folling MED group"
                            ),
                            "Lines until next sahara alarms": (
                                str(back_to_past.next_sahara_alarm.raise_line.line_number_in_library - back_to_past.previous_line.line_number_in_library)
                                if back_to_past.next_sahara_alarm
                                else "No folling SAHARA group"
                            ),
                        }
                    )

                df = pd.DataFrame(rows)
                filename = f"{self.name}_back_to_past_with_context{file_name_utils.get_file_suffix_with_current_datetime()}.xlsx"
                df.to_excel(output_folder_path + "/" + filename, index=False)
                logger_config.print_and_log_info(f"Fichier Excel créé: {filename}")

            except Exception as e:
                logger_config.print_and_log_exception(e)

    def export_sahara_alarms_with_context_to_excel(self, output_folder_path: str) -> None:
        """
        Exporte toutes les SAHARA alarms dans un fichier Excel avec le contexte:
        - Nombre de MCCS H alarms qui précèdent directement l'alarme SAHARA
        - Nombre de lignes depuis le dernier Back to Past event

        Args:
            output_folder_path: Chemin du dossier de sortie
        """
        try:
            if not self.sahara_alarms:
                logger_config.print_and_log_error("Aucune alarme SAHARA. Aucun fichier créé.")
                return

            with logger_config.stopwatch_with_label(f"{self.name}: Créer une map pour accès rapide aux back_to_past par l'index de la ligne"):
                # Créer une map pour accès rapide aux back_to_past par l'index de la ligne
                back_to_past_by_previous_line_index: Dict[int, TerminalTechniqueArchivesMaintLogBackToPast] = {}
                for back_to_past in self.all_back_to_past_detected:
                    for line_idx, line in enumerate(self.all_processed_lines):
                        if line is back_to_past.previous_line:
                            back_to_past_by_previous_line_index[line_idx] = back_to_past
                            break

            # Préparer les données pour le DataFrame
            excel_data: List[Dict[str, Any]] = []
            for idx, sahara_alarm in enumerate(self.sahara_alarms):
                # Trouver l'index de cette alarme dans all_processed_lines
                sahara_line_idx = None
                for line_idx, line in enumerate(self.all_processed_lines):
                    if line is sahara_alarm.raise_line:
                        sahara_line_idx = line_idx
                        break

                # Compter les MCCS H alarms qui précèdent directement
                currently_parsed_line_index = sahara_alarm.raise_line.line_number_in_library
                mesd_count_preceding = 0
                while "MESD" in self.all_processed_lines[currently_parsed_line_index - 1].alarm.equipment_name:
                    logger_config.print_and_log_info(
                        f"export_sahara_alarms_with_context_to_excel: {self.all_processed_lines[currently_parsed_line_index-1].alarm.equipment_name}, index {currently_parsed_line_index} is MEDS. Current sahara is at position {sahara_alarm.raise_line.line_number_in_library}"
                    )
                    mesd_count_preceding += 1
                    currently_parsed_line_index -= 1

                # Compter les lignes depuis le dernier Back to Past
                lines_since_last_back_to_past = 0
                if sahara_line_idx is not None:
                    last_back_to_past_idx = -1
                    # Trouver le dernier Back to Past avant cette alarme
                    for btp_idx in sorted(back_to_past_by_previous_line_index.keys()):
                        if btp_idx < sahara_line_idx:
                            last_back_to_past_idx = btp_idx
                        else:
                            break

                    if last_back_to_past_idx >= 0:
                        lines_since_last_back_to_past = sahara_line_idx - last_back_to_past_idx
                    else:
                        # Pas de Back to Past avant, on compte depuis le début
                        lines_since_last_back_to_past = sahara_line_idx + 1

                excel_data.append(
                    {
                        "Index": idx,
                        "Timestamp": sahara_alarm.raise_line.decoded_timestamp,
                        "File Path": sahara_alarm.raise_line.parent_file.file_full_path,
                        "File Name": sahara_alarm.raise_line.parent_file.file_name,
                        "Line Number": sahara_alarm.raise_line.line_number_inside_file,
                        "Full Text": sahara_alarm.full_text.strip(),
                        "Preceding MESD Alarms Count": mesd_count_preceding,
                        "Lines Since Last Back to Past": lines_since_last_back_to_past,
                    }
                )

            # Créer et sauvegarder le fichier Excel
            df = pd.DataFrame(excel_data)
            excel_filename = f"{self.name}_sahara_alarms_context{file_name_utils.get_file_suffix_with_current_datetime()}.xlsx"
            df.to_excel(output_folder_path + "/" + excel_filename, index=False)
            logger_config.print_and_log_info(f"Fichier Excel créé: {excel_filename}")
            logger_config.print_and_log_info(f"Total de {len(self.sahara_alarms)} alarmes SAHARA exportées avec contexte")

        except Exception as e:
            logger_config.print_and_log_exception(e)

    def export_mesd_alarms_groups_to_excel(self, output_folder_path: str) -> None:
        """Export all MESD alarms groups to Excel."""
        with logger_config.stopwatch_with_label(f"{self.name}: export_mesd_alarms_groups_to_excel", inform_beginning=False, enable_print=False, enabled=False):

            try:
                if not self.all_mesd_alarms_groups:
                    logger_config.print_and_log_error("Aucun groupe MESD. Aucun fichier créé.")
                    return

                # Préparer les données pour le DataFrame
                excel_data: List[Dict[str, Any]] = []
                for group in self.all_mesd_alarms_groups:
                    excel_data.append(
                        {
                            "Group Index": group.number_of_group_in_library,
                            "Line Count": len(group.alarm_lines),
                            "Start timestamp": group.first_line.decoded_timestamp,
                            "End timestamp": group.last_line.decoded_timestamp,
                            "group duration (seconds)": (group.last_line.decoded_timestamp - group.first_line.decoded_timestamp).total_seconds(),
                            "Last (previous) goup: lines since": (
                                (group.first_line.line_number_in_library - group.previous_group.last_line.line_number_in_library) if group.previous_group else "No previous group"
                            ),
                            "Last (previous) goup: duration since (seconds)": (
                                (group.first_line.decoded_timestamp - group.previous_group.last_line.decoded_timestamp).total_seconds() if group.previous_group else "No previous group"
                            ),
                            "Group - Start File Name": group.first_line.parent_file.file_name,
                            "Group - Start Line Number": group.first_line.line_number_inside_file,
                            "Last Back to Past - lines until group": (
                                (group.first_line.line_number_in_library - group.last_back_to_past_detected.previous_line.line_number_in_library)
                                if group.last_back_to_past_detected
                                else "No previous back to past"
                            ),
                            "Last Back to Past - timestamp": group.last_back_to_past_detected.previous_line.decoded_timestamp if group.last_back_to_past_detected else "No previous back to past",
                            "Last back to past - seconds until group": (
                                (group.first_line.decoded_timestamp - group.last_back_to_past_detected.previous_line.decoded_timestamp).total_seconds()
                                if group.last_back_to_past_detected
                                else "No previous back to past"
                            ),
                            "Second until next sahara alarm": (
                                (group.following_sahara_alarms[0].raise_line.decoded_timestamp - group.last_line.decoded_timestamp).total_seconds()
                                if group.following_sahara_alarms
                                else "NA (no next sahara alarm until next group)"
                            ),
                            "Lines until next sahara alarm": (
                                group.following_sahara_alarms[0].raise_line.line_number_in_library - group.last_line.line_number_in_library
                                if group.following_sahara_alarms
                                else "NA (no next sahara alarm until next group)"
                            ),
                            "Group - First line Full Text": group.first_line.full_raw_line.strip(),
                        }
                    )

                # Créer et sauvegarder le fichier Excel
                df = pd.DataFrame(excel_data)
                excel_filename = f"{self.name}_mesd_alarms_groups{file_name_utils.get_file_suffix_with_current_datetime()}.xlsx"
                df.to_excel(output_folder_path + "/" + excel_filename, index=False)
                logger_config.print_and_log_info(f"Fichier Excel créé: {excel_filename}")
                logger_config.print_and_log_info(f"Total de {len(self.all_mesd_alarms_groups)} groupes MESD exportés")
            except Exception as e:
                logger_config.print_and_log_exception(e)


@dataclass
class TerminalTechniqueArchivesMaintFile:
    parent_folder_full_path: str
    file_name: str
    library: "TerminalTechniqueArchivesMaintLibrary"
    last_line: Optional["TerminalTechniqueArchivesMaintLogLine"]

    def __post_init__(self) -> None:
        self.file_full_path = self.parent_folder_full_path + "\\" + self.file_name

        with logger_config.stopwatch_with_label(f"{self.library.name}: Open and read file  {self.file_full_path}", inform_beginning=True, enable_print=False, enabled=False):
            try:
                with open(self.file_full_path, mode="r", encoding="ANSI") as file:
                    all_raw_lines = file.readlines()
                    # logger_config.print_and_log_info(to_print_and_log=f"File {self.file_full_path} has {len(all_raw_lines)} lines")
                    for line_number, line in enumerate(all_raw_lines):
                        if len(line) > 3:
                            try:
                                processed_line = TerminalTechniqueArchivesMaintLogLine(parent_file=self, full_raw_line=line, line_number_inside_file=line_number + 1, previous_line=self.last_line)
                                self.library.all_processed_lines.append(processed_line)
                                self.last_line = processed_line
                            except Exception as e:
                                logger_config.print_and_log_exception(e)
                                logger_config.print_and_log_error(f"Could not process line {line} in {self.file_name} {line_number+1}")
            except OSError as err:
                logger_config.print_and_log_exception(err)
                logger_config.print_and_log_error(f"Error while parsing {self.file_full_path }")


@dataclass
class TerminalTechniqueArchivesMaintLogLine:
    parent_file: TerminalTechniqueArchivesMaintFile
    full_raw_line: str
    line_number_inside_file: int

    previous_line: Optional["TerminalTechniqueArchivesMaintLogLine"]

    def __post_init__(self) -> None:
        self.line_number_in_library = len(self.parent_file.library.all_processed_lines) + 1
        self.raw_date_str = self.full_raw_line[0:22]

        self.full_raw_line_split_by_tab = self.full_raw_line.split("\t")
        self.alarm_type = AlarmLineType[self.full_raw_line_split_by_tab[2]]

        # 2025-12-29	01:45:53.30
        self.raw_date_str_with_microseconds = self.raw_date_str + "0000"
        self.decoded_timestamp = datetime.datetime.strptime(self.raw_date_str_with_microseconds, "%Y-%m-%d	%H:%M:%S.%f")

        if self.previous_line and self.previous_line.decoded_timestamp > self.decoded_timestamp:
            back_to_past = TerminalTechniqueArchivesMaintLogBackToPast(previous_line=self.previous_line, next_line=self)
            self.parent_file.library.all_back_to_past_detected.append(back_to_past)

        assert len(self.full_raw_line_split_by_tab) == 4
        self.alarm_full_text = self.full_raw_line_split_by_tab[3]

        self.alarm: TerminalTechniqueAlarm = cast("TerminalTechniqueAlarm", None)

        if self.alarm_type in [AlarmLineType.FIN_ALA, AlarmLineType.FERM_SESSION]:
            found_unclosed_alarms = [alarm for alarm in self.parent_file.library.currently_opened_alarms if alarm.full_text == self.alarm_full_text]
            if found_unclosed_alarms:
                while len(found_unclosed_alarms) > 1:
                    never_closed_alarm = found_unclosed_alarms[0]
                    logger_config.print_and_log_warning(
                        f"Alarm {never_closed_alarm.full_text} is re-opened at {found_unclosed_alarms[0].raise_line.decoded_timestamp} and not closed between. {len(found_unclosed_alarms)} unclosed alarms found \n({'\n'.join(alarm.raise_line.full_raw_line + " in " + alarm.raise_line.parent_file.file_name + ":"+str(alarm.raise_line.line_number_inside_file)  for alarm in found_unclosed_alarms)}) for {self.alarm_full_text} when trying to close {self.full_raw_line} in {self.parent_file.file_name}:{self.line_number_inside_file}"
                    )
                    self.parent_file.library.currently_opened_alarms.remove(found_unclosed_alarms[0])
                    found_unclosed_alarms = [alarm for alarm in self.parent_file.library.currently_opened_alarms if alarm.full_text == self.alarm_full_text]

                found_unclosed_alarm = found_unclosed_alarms[0]
                self.parent_file.library.currently_opened_alarms.remove(found_unclosed_alarm)
                assert found_unclosed_alarm.end_alarm_line is None
                self.alarm = found_unclosed_alarm
                self.alarm.end_alarm_line = self
            else:
                self.alarm = TerminalTechniqueClosableAlarm(raise_line=self, full_text=self.alarm_full_text, alarm_type=self.alarm_type)
                self.alarm.end_alarm_line = self
                self.parent_file.library.ignored_end_alarms_without_alarm_begin.append(self.alarm)

        elif "SAHARA" in self.alarm_full_text:
            last_back_to_past_detected = self.parent_file.library.all_back_to_past_detected[-1] if self.parent_file.library.all_back_to_past_detected else None
            last_mesd_alarm_group = self.parent_file.library.all_mesd_alarms_groups[-1] if self.parent_file.library.all_mesd_alarms_groups else None
            self.alarm = SaharaTerminalTechniqueAlarm(
                raise_line=self, full_text=self.alarm_full_text, alarm_type=self.alarm_type, last_back_to_past_detected=last_back_to_past_detected, last_mesd_alarm_group=last_mesd_alarm_group
            )
            self.parent_file.library.sahara_alarms.append(self.alarm)

        elif "Absence acquittement SAAT" in self.alarm_full_text:
            self.alarm = SaatMissingAcknowledgmentTerminalTechniqueAlarm(raise_line=self, full_text=self.alarm_full_text, alarm_type=self.alarm_type)
        elif self.alarm_type == AlarmLineType.DEB_ALA and ("MCCS A HS" in self.alarm_full_text or "MCCS B HS" in self.alarm_full_text):
            self.alarm = TerminalTechniqueMccsHAlarm(raise_line=self, full_text=self.alarm_full_text, alarm_type=self.alarm_type)
            self.parent_file.library.mccs_hs_alarms.append(self.alarm)

            self.parent_file.library.currently_opened_alarms.append(self.alarm)
        elif self.alarm_type == AlarmLineType.DEB_ALA:
            self.alarm = TerminalTechniqueClosableAlarm(raise_line=self, full_text=self.alarm_full_text, alarm_type=self.alarm_type)
            self.parent_file.library.currently_opened_alarms.append(self.alarm)
        elif self.alarm_type == AlarmLineType.OUV_SESSION:
            session_alarm = TerminalTechniqueSessionAlarm(raise_line=self, full_text=self.alarm_full_text, alarm_type=self.alarm_type)
            self.alarm = session_alarm
            self.parent_file.library.currently_opened_alarms.append(self.alarm)
            self.parent_file.library.sessions_alarms.append(session_alarm)

        elif self.alarm_type in [AlarmLineType.EVT_ALA, AlarmLineType.CMD_ESSAIS, AlarmLineType.CMD_CPT_RENDU]:
            self.alarm = TerminalTechniqueAlarm(raise_line=self, full_text=self.alarm_full_text, alarm_type=self.alarm_type)
        elif self.alarm_type == AlarmLineType.CSI:
            self.alarm = TerminalTechniqueCsiAlarm(raise_line=self, full_text=self.alarm_full_text, alarm_type=self.alarm_type)
        else:
            assert False, f"Alarm type {self.alarm_type} for {self.parent_file.file_name} {self.line_number_inside_file} {self.alarm_full_text}"

        if "MESD" in self.alarm.equipment_name:
            if not self.parent_file.library.all_mesd_alarms_groups or self.parent_file.library.all_mesd_alarms_groups[-1].alarm_lines[-1] != self.parent_file.library.all_processed_lines[-1]:
                last_back_to_past_detected = self.parent_file.library.all_back_to_past_detected[-1] if self.parent_file.library.all_back_to_past_detected else None
                alarm_group = TerminalTechniqueMesdAlarmsGroup(
                    library=self.parent_file.library,
                    number_of_group_in_library=len(self.parent_file.library.all_mesd_alarms_groups) + 1,
                    alarm_lines=[self],
                    last_back_to_past_detected=last_back_to_past_detected,
                )
                self.parent_file.library.all_mesd_alarms_groups.append(alarm_group)
                if last_back_to_past_detected and not last_back_to_past_detected.next_mesd_alarms_group:
                    last_back_to_past_detected.next_mesd_alarms_group = alarm_group

            else:
                self.parent_file.library.all_mesd_alarms_groups[-1].alarm_lines.append(self)
