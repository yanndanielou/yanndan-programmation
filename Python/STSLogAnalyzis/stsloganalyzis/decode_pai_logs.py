import datetime
import os
import re
from collections import Counter
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional, Self, Tuple, cast

import matplotlib.pyplot as plt
import plotly.graph_objects as go
from common import file_name_utils, string_utils, custom_iterator
from logger import logger_config
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill

# CONTENT_OF_FIELD_IN_CASE_OF_DECODING_ERROR = "!!! Decoding Error !!!"


class AlarmLineType(Enum):
    EVT_ALA = auto()
    DEB_ALA = auto()
    FIN_ALA = auto()
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
class SaatMissingAcknowledgmentTerminalTechniqueAlarm(TerminalTechniqueEventAlarm):
    def __post_init__(self) -> None:
        super().__post_init__()
        self.chaine = self.raise_line.alarm_full_text.split(",")[3]
        self.repetition = int(self.raise_line.alarm_full_text.split(",")[4][0])


@dataclass
class SaharaTerminalTechniqueAlarm(TerminalTechniqueEventAlarm):
    pass


@dataclass
class TerminalTechniqueArchivesMaintLogBackToPast:
    previous_line: "TerminalTechniqueArchivesMaintLogLine"
    next_line: "TerminalTechniqueArchivesMaintLogLine"


@dataclass
class TerminalTechniqueArchivesMaintLibrary:
    name: str

    def __post_init__(self) -> None:
        self.all_processed_lines: List["TerminalTechniqueArchivesMaintLogLine"] = []
        self.all_processed_files: List["TerminalTechniqueArchivesMaintFile"] = []
        self.currently_opened_alarms: List[TerminalTechniqueClosableAlarm] = []
        self.ignored_end_alarms_without_alarm_begin: List[TerminalTechniqueClosableAlarm] = []
        self.sahara_alarms: List[SaharaTerminalTechniqueAlarm] = []
        self.equipments_with_alarms: List[TerminalTechniqueEquipmentWithAlarms] = []
        self.back_to_past_detected: List[TerminalTechniqueArchivesMaintLogBackToPast] = []

    def load_folder(self, folder_full_path: str) -> Self:

        last_line = None
        for dirpath, dirnames, filenames in os.walk(folder_full_path):
            for file_name in filenames:
                file = TerminalTechniqueArchivesMaintFile(parent_folder_full_path=dirpath, file_name=file_name, library=self, last_line=last_line)
                last_line = file.last_line
                self.all_processed_files.append(file)
                self.all_processed_lines += file.all_processed_lines

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

    def export_equipments_with_alarms_to_excel(self, output_folder_path: str, equipment_names_to_ignore: List[str], excel_output_file_name_without_extension: str = "equipments_alarms") -> None:
        """
        Exporte tous les équipements et leurs alarmes dans un fichier Excel.

        Args:
            output_folder_path: Chemin du dossier de sortie
            equipment_names_to_ignore: Liste des noms d'équipements à ignorer
            excel_output_file_name_without_extension: Nom du fichier Excel sans extension
        """
        if not self.equipments_with_alarms:
            logger_config.print_and_log_info("Aucun équipement avec alarmes. Aucun fichier créé.")
            return

        # Créer un workbook
        wb = Workbook()
        ws = wb.active
        ws.title = "Equipments Alarms"

        # Ajouter les en-têtes
        headers = [
            "Equipment Name",
            "Alarm Raise Timestamp",
            "Type alarm (class name)",
            "Alarm Type",
            "Raise alarm: Timestamp",
            "Raise alarm: File name",
            "Raise alarm: Line number",
            "End alarm (if any): Timestamp",
            "End alarm (if any): File name",
            "End alarm (if any): Line number",
            "Full Text",
        ]

        for col_idx, header in enumerate(headers, start=1):
            cell = ws.cell(row=1, column=col_idx)
            cell.value = header
            cell.fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
            cell.font = Font(bold=True, color="FFFFFF")
            cell.alignment = Alignment(horizontal="center", vertical="center")

        # Ajouter les données
        row_idx = 2
        for equipment in self.equipments_with_alarms:
            if equipment.name not in equipment_names_to_ignore:
                for alarm in equipment.alarms:
                    column_it = custom_iterator.SimpleIntCustomIncrementDecrement(initial_value=1)
                    ws.cell(row=row_idx, column=column_it.postfix_increment()).value = equipment.name
                    ws.cell(row=row_idx, column=column_it.postfix_increment()).value = type(alarm).__name__
                    ws.cell(row=row_idx, column=column_it.postfix_increment()).value = alarm.alarm_type.name
                    ws.cell(row=row_idx, column=column_it.postfix_increment()).value = alarm.raise_line.decoded_timestamp
                    ws.cell(row=row_idx, column=column_it.postfix_increment()).value = alarm.raise_line.parent_file.file_name
                    ws.cell(row=row_idx, column=column_it.postfix_increment()).value = alarm.raise_line.line_number
                    ws.cell(row=row_idx, column=column_it.postfix_increment()).value = alarm.end_alarm_line.decoded_timestamp if alarm.end_alarm_line else "NA"
                    ws.cell(row=row_idx, column=column_it.postfix_increment()).value = alarm.end_alarm_line.parent_file.file_name if alarm.end_alarm_line else "NA"
                    ws.cell(row=row_idx, column=column_it.postfix_increment()).value = alarm.end_alarm_line.line_number if alarm.end_alarm_line else "NA"
                    ws.cell(row=row_idx, column=column_it.postfix_increment()).value = alarm.full_text.strip()
                    row_idx += 1

        # Ajuster la largeur des colonnes
        ws.column_dimensions["A"].width = 25
        ws.column_dimensions["B"].width = 25
        ws.column_dimensions["C"].width = 20
        ws.column_dimensions["D"].width = 35
        ws.column_dimensions["E"].width = 30
        ws.column_dimensions["F"].width = 15
        ws.column_dimensions["G"].width = 60

        # Sauvegarder le fichier
        wb.save(output_folder_path + "/" + self.name + excel_output_file_name_without_extension + "_" + file_name_utils.get_file_suffix_with_current_datetime() + ".xlsx")
        logger_config.print_and_log_info(f"Fichier Excel créé: {excel_output_file_name_without_extension}.xlsx")
        total_alarms = sum(len(equipment.alarms) for equipment in self.equipments_with_alarms)
        logger_config.print_and_log_info(f"Total de {total_alarms} alarmes sauvegardées")

    def plot_alarms_by_period(self, output_folder_path: str, equipment_names_to_ignore: List[str], interval_minutes: int = 10, do_show: bool = False) -> None:
        """
        Génère un bar graph montrant les événements par intervalle de temps.

        Args:
            output_folder_path: Chemin du dossier de sortie
            equipment_names_to_ignore: Liste des noms d'équipements à ignorer
            interval_minutes: Intervalle de temps en minutes (par défaut 10)
            do_show: Afficher le graphique matplotlib
        """
        if not self.all_processed_lines:
            logger_config.print_and_log_info("La liste des traces est vide. Aucun fichier créé.")
            return

        with logger_config.stopwatch_with_label("plot_alarms_by_period"):

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
            for back_to_past in self.back_to_past_detected:
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
            x_labels = [f"{begin.strftime("%H:%M")} - {end.strftime("%H:%M")}" for begin, end in interval_back_to_past_count.keys()]
            y_back_to_past = list(interval_back_to_past_count.values())
            y_sahara = list(interval_sahara_count.values())

            # Récupérer tous les noms d'équipements uniques (en ordre d'apparition)
            equipment_names: List[str] = []
            for interval_counts in interval_equipment_counts.values():
                for name in interval_counts.keys():
                    if name not in equipment_names:
                        equipment_names.append(name)

            # Créer et exporter les données dans un fichier Excel
            excel_filename = f"alarms_by_period_{self.name}_{start_time.strftime('%Y%m%d_%H%M%S')}{file_name_utils.get_file_suffix_with_current_datetime()}.xlsx"
            wb = Workbook()
            ws = wb.active
            ws.title = "Alarms By Period"

            # Ajouter les en-têtes
            headers = ["Début Intervalle", "Fin Intervalle", "Back to Past", "Sahara"]
            headers.extend(equipment_names)

            for col_idx, header in enumerate(headers, start=1):
                cell = ws.cell(row=1, column=col_idx)
                cell.value = header
                cell.fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
                cell.font = Font(bold=True, color="FFFFFF")
                cell.alignment = Alignment(horizontal="center", vertical="center")

            # Ajouter les données
            for idx, ((interval_begin, interval_end), back_to_past_count) in enumerate(interval_back_to_past_count.items(), start=2):
                ws[f"A{idx}"] = interval_begin
                ws[f"B{idx}"] = interval_end
                ws[f"C{idx}"] = back_to_past_count
                ws[f"D{idx}"] = interval_sahara_count[(interval_begin, interval_end)]

                for col_idx, equipment_name in enumerate(equipment_names, start=5):
                    count = interval_equipment_counts[(interval_begin, interval_end)].get(equipment_name, 0)
                    ws.cell(row=idx, column=col_idx).value = count
                    ws.cell(row=idx, column=col_idx).alignment = Alignment(horizontal="center")

                ws[f"C{idx}"].alignment = Alignment(horizontal="center")
                ws[f"D{idx}"].alignment = Alignment(horizontal="center")

            # Ajuster la largeur des colonnes
            ws.column_dimensions["A"].width = 25
            ws.column_dimensions["B"].width = 25
            ws.column_dimensions["C"].width = 15
            ws.column_dimensions["D"].width = 15
            for col_idx, _ in enumerate(equipment_names, start=5):
                col_letter = chr(64 + col_idx)  # Convert number to letter
                ws.column_dimensions[col_letter].width = 20

            # Ajouter un résumé
            summary_row = len(interval_back_to_past_count) + 3
            ws[f"A{summary_row}"] = "Total"
            ws[f"C{summary_row}"] = len(self.back_to_past_detected)
            ws[f"D{summary_row}"] = len(self.sahara_alarms)
            ws[f"A{summary_row}"].font = Font(bold=True)
            ws[f"C{summary_row}"].font = Font(bold=True)
            ws[f"D{summary_row}"].font = Font(bold=True)
            ws[f"C{summary_row}"].alignment = Alignment(horizontal="center")
            ws[f"D{summary_row}"].alignment = Alignment(horizontal="center")

            # Sauvegarder le fichier Excel
            wb.save(output_folder_path + "/" + excel_filename)
            logger_config.print_and_log_info(f"Fichier Excel créé: {excel_filename}")

            # Créer et sauvegarder le graphe en HTML avec Plotly
            html_filename = f"alarms_by_period_{self.name}_{start_time.strftime('%Y%m%d_%H%M%S')}{file_name_utils.get_file_suffix_with_current_datetime()}.html"

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
                title=f"Alarmes par périodes de {interval_minutes} minutes entre {start_time.strftime('%Y-%m-%d %H:%M')} et {end_time.strftime('%Y-%m-%d %H:%M')}",
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
            plt.title(f"Alarmes par périodes de {interval_minutes} minutes entre {start_time.strftime("%Y-%m-%d %H:%M")} et {end_time.strftime("%Y-%m-%d %H:%M")}")
            plt.xticks(x_pos, x_labels, rotation=45, ha="right")
            plt.legend(loc="upper left", bbox_to_anchor=(1, 1))
            plt.tight_layout()
            if do_show:
                plt.show()


@dataclass
class TerminalTechniqueArchivesMaintFile:
    parent_folder_full_path: str
    file_name: str
    library: "TerminalTechniqueArchivesMaintLibrary"
    last_line: Optional["TerminalTechniqueArchivesMaintLogLine"]
    all_processed_lines: List["TerminalTechniqueArchivesMaintLogLine"] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.file_full_path = self.parent_folder_full_path + "\\" + self.file_name

        with logger_config.stopwatch_with_label(f"Open and read file  {self.file_full_path}", inform_beginning=False, enable_print=False, enabled=False):
            with open(self.file_full_path, mode="r", encoding="ANSI") as file:
                all_raw_lines = file.readlines()
                # logger_config.print_and_log_info(to_print_and_log=f"File {self.file_full_path} has {len(all_raw_lines)} lines")
                for line_number, line in enumerate(all_raw_lines):
                    if len(line) > 3:
                        processed_line = TerminalTechniqueArchivesMaintLogLine(parent_file=self, full_raw_line=line, line_number=line_number, previous_line=self.last_line)
                        self.all_processed_lines.append(processed_line)
                        self.last_line = processed_line


@dataclass
class TerminalTechniqueArchivesMaintLogLine:
    parent_file: TerminalTechniqueArchivesMaintFile
    full_raw_line: str
    line_number: int
    previous_line: Optional["TerminalTechniqueArchivesMaintLogLine"]

    def __post_init__(self) -> None:
        self.raw_date_str = self.full_raw_line[0:22]

        self.full_raw_line_split_by_tab = self.full_raw_line.split("\t")
        self.alarm_type = AlarmLineType[self.full_raw_line_split_by_tab[2]]

        # 2025-12-29	01:45:53.30
        self.raw_date_str_with_microseconds = self.raw_date_str + "0000"
        self.decoded_timestamp = datetime.datetime.strptime(self.raw_date_str_with_microseconds, "%Y-%m-%d	%H:%M:%S.%f")

        if self.previous_line and self.previous_line.decoded_timestamp > self.decoded_timestamp:
            back_to_past = TerminalTechniqueArchivesMaintLogBackToPast(previous_line=self.previous_line, next_line=self)
            self.parent_file.library.back_to_past_detected.append(back_to_past)

        assert len(self.full_raw_line_split_by_tab) == 4
        self.alarm_full_text = self.full_raw_line_split_by_tab[3]

        self.alarm: Optional[TerminalTechniqueAlarm] = None

        if self.alarm_type == AlarmLineType.FIN_ALA:
            found_unclosed_alarms = [alarm for alarm in self.parent_file.library.currently_opened_alarms if alarm.full_text == self.alarm_full_text]
            if found_unclosed_alarms:
                assert len(found_unclosed_alarms) == 1
                found_unclosed_alarm = found_unclosed_alarms[0]
                assert found_unclosed_alarm.end_alarm_line is None
                self.alarm = found_unclosed_alarm
                self.alarm.end_alarm_line = self
            else:
                self.alarm = TerminalTechniqueClosableAlarm(raise_line=self, full_text=self.alarm_full_text, alarm_type=self.alarm_type)
                self.alarm.end_alarm_line = self
                self.parent_file.library.ignored_end_alarms_without_alarm_begin.append(self)

        elif "SAHARA" in self.alarm_full_text:
            self.alarm = SaharaTerminalTechniqueAlarm(raise_line=self, full_text=self.alarm_full_text, alarm_type=self.alarm_type)
            self.parent_file.library.sahara_alarms.append(self.alarm)
        elif "Absence acquittement SAAT" in self.alarm_full_text:
            self.alarm = SaatMissingAcknowledgmentTerminalTechniqueAlarm(raise_line=self, full_text=self.alarm_full_text, alarm_type=self.alarm_type)
        elif self.alarm_type == AlarmLineType.DEB_ALA:
            self.alarm = TerminalTechniqueClosableAlarm(raise_line=self, full_text=self.alarm_full_text, alarm_type=self.alarm_type)
        elif self.alarm_type == AlarmLineType.EVT_ALA:
            self.alarm = TerminalTechniqueAlarm(raise_line=self, full_text=self.alarm_full_text, alarm_type=self.alarm_type)
        elif self.alarm_type == AlarmLineType.CSI:
            self.alarm = TerminalTechniqueCsiAlarm(raise_line=self, full_text=self.alarm_full_text, alarm_type=self.alarm_type)
        else:
            assert False, f"Alarm type {self.alarm_type} for {self.parent_file.file_name} {self.line_number} {self.alarm_full_text}"
