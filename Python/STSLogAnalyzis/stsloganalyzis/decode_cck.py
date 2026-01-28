from collections import Counter
import matplotlib.pyplot as plt
import csv
import os
import datetime
import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, cast, Self
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from common import file_name_utils
import plotly.graph_objects as go

import re


from logger import logger_config

# CONTENT_OF_FIELD_IN_CASE_OF_DECODING_ERROR = "!!! Decoding Error !!!"

LIAISON_PATTERN_STR = ".*(?P<liaison_full_name>Liaison (?P<liaison_id>\d+A?B?)).*"
LIAISON_PATTERN = re.compile(LIAISON_PATTERN_STR)


def save_cck_mpro_lines_in_excel(trace_lines: List["CckMproTraceLine"], excel_output_file_name: str) -> None:
    """
    Sauvegarde une liste de CckMproTraceLine dans un fichier Excel.

    Args:
        trace_lines: Liste des lignes de trace à sauvegarder
        excel_output_file_name: Nom du fichier Excel de sortie
    """
    if not trace_lines:
        logger_config.print_and_log_info("La liste des traces est vide. Aucun fichier créé.")
        return

    # Créer un workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "CCK MPRO Traces"

    # Ajouter les en-têtes
    headers = ["Timestamp", "Date complète", "Liaison", "ID Liaison", "Ligne brute"]
    for col_idx, header in enumerate(headers, start=1):
        cell = ws.cell(row=1, column=col_idx)
        cell.value = header
        cell.fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
        cell.font = Font(bold=True, color="FFFFFF")
        cell.alignment = Alignment(horizontal="center", vertical="center")

    # Ajouter les données
    for row_idx, trace_line in enumerate(trace_lines, start=2):
        ws.cell(row=row_idx, column=1).value = trace_line.decoded_timestamp
        ws.cell(row=row_idx, column=2).value = trace_line.raw_date_str
        ws.cell(row=row_idx, column=3).value = trace_line.liaison_full_name or "N/A"
        ws.cell(row=row_idx, column=4).value = trace_line.liaison_id or "N/A"
        ws.cell(row=row_idx, column=5).value = trace_line.full_raw_line.strip()

    # Ajuster la largeur des colonnes
    ws.column_dimensions["A"].width = 25
    ws.column_dimensions["B"].width = 25
    ws.column_dimensions["C"].width = 30
    ws.column_dimensions["D"].width = 15
    ws.column_dimensions["E"].width = 80

    # Sauvegarder le fichier
    wb.save(excel_output_file_name)
    logger_config.print_and_log_info(f"Fichier Excel créé: {excel_output_file_name}")
    logger_config.print_and_log_info(f"Total de {len(trace_lines)} lignes sauvegardées")


def plot_bar_graph_list_cck_mpro_lines_by_period(trace_lines: List["CckMproTraceLine"], label: str, interval_minutes: int = 10) -> None:
    if not trace_lines:
        print("La liste des traces est vide.")
        return

    # Trier les trace_lines par timestamp
    trace_lines.sort(key=lambda x: x.decoded_timestamp)

    # Déterminer la période totale (du timestamp le plus tôt au plus tard)
    start_time = trace_lines[0].decoded_timestamp
    end_time = trace_lines[-1].decoded_timestamp

    # Créer des intervalles de temps
    interval_start_times: List[datetime.datetime] = []
    current_time = start_time
    while current_time <= end_time:
        interval_start_times.append(current_time)
        current_time += datetime.timedelta(minutes=interval_minutes)

    # Compter les éléments dans chaque intervalle
    interval_counts: Dict[(datetime.datetime, datetime.datetime), int] = Counter()
    for trace in trace_lines:
        for interval_start in interval_start_times:
            interval_end = interval_start + datetime.timedelta(minutes=interval_minutes)
            if interval_start <= trace.decoded_timestamp < interval_end:
                interval_counts[(interval_start, interval_end)] += 1
                break

    # Préparer les données pour le graphe
    x_labels = [f"{begin.strftime("%H:%M")} - {end.strftime("%H:%M")}" for begin, end in interval_counts.keys()]
    y_values = list(interval_counts.values())
    # Créer et exporter les données dans un fichier Excel
    excel_filename = f"interval_counts_{label.replace(' ', '_')}_{start_time.strftime('%Y%m%d_%H%M%S')}{file_name_utils.get_file_suffix_with_current_datetime()}.xlsx"
    wb = Workbook()
    ws = wb.active
    ws.title = "Interval Counts"

    # Ajouter les en-têtes
    ws["A1"] = "Début Intervalle de temps"
    ws["B1"] = "Fin Intervalle de temps"
    ws["C1"] = "Nombre d'éléments"

    # Style des en-têtes
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF")
    for cell in [ws["A1"], ws["B1"], ws["C1"]]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center")

    # Ajouter les données
    for idx, ((interval_begin, interval_end), count) in enumerate(interval_counts.items(), start=2):
        ws[f"A{idx}"] = interval_begin
        ws[f"B{idx}"] = interval_end
        ws[f"C{idx}"] = count
        ws[f"C{idx}"].alignment = Alignment(horizontal="center")

    # Ajuster la largeur des colonnes
    ws.column_dimensions["A"].width = 25
    ws.column_dimensions["B"].width = 25
    ws.column_dimensions["C"].width = 15

    # Ajouter un résumé
    summary_row = len(interval_counts) + 3
    ws[f"A{summary_row}"] = "Total"
    ws[f"B{summary_row}"] = len(trace_lines)
    ws[f"A{summary_row}"].font = Font(bold=True)
    ws[f"B{summary_row}"].font = Font(bold=True)
    ws[f"B{summary_row}"].alignment = Alignment(horizontal="center")

    # Sauvegarder le fichier
    wb.save(excel_filename)
    logger_config.print_and_log_info(f"Fichier Excel créé: {excel_filename}")

    # Créer et sauvegarder le graphe en HTML avec Plotly
    html_filename = f"interval_counts_{label.replace(' ', '_')}_{start_time.strftime('%Y%m%d_%H%M%S')}{file_name_utils.get_file_suffix_with_current_datetime()}.html"
    fig = go.Figure(
        data=[
            go.Bar(
                x=x_labels,
                y=y_values,
                marker=dict(color="skyblue"),
                text=y_values,
                textposition="auto",
            )
        ]
    )

    fig.update_layout(
        title=f"{len(trace_lines)} {label} par périodes de {interval_minutes} minutes entre {start_time.strftime('%Y-%m-%d %H:%M')} et {end_time.strftime('%Y-%m-%d %H:%M')}",
        xaxis_title="Intervalles de temps (heure début - heure fin)",
        yaxis_title="Nombre de CckMproTraceLine",
        hovermode="x unified",
        template="plotly_white",
        height=600,
        width=1000,
    )

    fig.write_html(html_filename)
    logger_config.print_and_log_info(f"Fichier HTML créé: {html_filename}")

    # Afficher le bar graph
    plt.figure(figsize=(10, 6))
    plt.bar(x_labels, y_values, color="skyblue", width=0.3)
    plt.xlabel("Intervalles de temps (heure début)")
    plt.ylabel("Nombre de CckMproTraceLine")
    plt.title(f"{len(trace_lines)} {label} par périodes de {interval_minutes} minutes entre {start_time.strftime("%Y-%m-%d %H:%M")} et {end_time.strftime("%Y-%m-%d %H:%M")}")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.show()


@dataclass
class CckMproTraceLibrary:
    all_processed_lines: List["CckMproTraceLine"] = field(default_factory=list)
    all_processed_files: List["CckMproTraceFile"] = field(default_factory=list)

    def load_folder(self, folder_full_path: str) -> Self:
        for dirpath, dirnames, filenames in os.walk(folder_full_path):
            for file_name in filenames:
                cck_file = CckMproTraceFile(parent_folder_full_path=dirpath, file_name=file_name)
                self.all_processed_files.append(cck_file)
                self.all_processed_lines += cck_file.all_processed_lines
                assert self.all_processed_lines
        assert self.all_processed_lines
        return self


pass


@dataclass
class CckMproTraceFile:
    parent_folder_full_path: str
    file_name: str
    all_processed_lines: List["CckMproTraceLine"] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.file_full_path = self.parent_folder_full_path + "/" + self.file_name
        with logger_config.stopwatch_with_label(f"Open and read CCK Mpro trace file lines {self.file_full_path}"):
            with open(self.file_full_path, mode="r", encoding="ANSI") as file:
                all_raw_lines = file.readlines()
                logger_config.print_and_log_info(to_print_and_log=f"File {self.file_full_path} has {len(all_raw_lines)} lines", do_not_print=True)
                for line_number, line in enumerate(all_raw_lines):
                    processed_line = CckMproTraceLine(parent_file=self, full_raw_line=line)
                    self.all_processed_lines.append(processed_line)

        logger_config.print_and_log_info(f"{self.file_full_path}: {len(self.all_processed_lines)} lines found")
        assert self.all_processed_lines, f"{self.file_full_path} is empty"


@dataclass
class CckMproTraceLine:
    parent_file: CckMproTraceFile
    full_raw_line: str

    def __post_init__(self) -> None:
        self.raw_date_str = self.full_raw_line[1:23]
        self.year = int(self.raw_date_str[:4])
        self.month = int(self.raw_date_str[5:7])
        self.day = int(self.raw_date_str[8:10])
        self.hour = int(self.raw_date_str[11:13])
        self.minute = int(self.raw_date_str[14:16])
        self.second = int(self.raw_date_str[17:19])
        self.millisecond = int(self.raw_date_str[20:22]) * 10

        match_liaison_pattern = LIAISON_PATTERN.match(self.full_raw_line)
        self.liaison_full_name = match_liaison_pattern.group("liaison_full_name") if match_liaison_pattern else None
        self.liaison_id = match_liaison_pattern.group("liaison_id") if match_liaison_pattern else None
        # self.liaison_name

        # self./
        self.decoded_timestamp = datetime.datetime(year=self.year, month=self.month, day=self.day, hour=self.hour, minute=self.minute, second=self.second, microsecond=self.millisecond * 1000)
        pass
