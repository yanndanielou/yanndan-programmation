import datetime
import os
import re
from collections import Counter
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional, Self, Tuple

import matplotlib.pyplot as plt
import plotly.graph_objects as go
from common import file_name_utils, string_utils
from logger import logger_config
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill

# CONTENT_OF_FIELD_IN_CASE_OF_DECODING_ERROR = "!!! Decoding Error !!!"

LIAISON_PATTERN_STR = r".*(?P<liaison_full_name>Liaison (?P<liaison_id>\d+A?B?)).*"
LIAISON_PATTERN = re.compile(LIAISON_PATTERN_STR)

LINK_STATE_CHANGE_PATTERN_STR = r".*changement d'état : (?P<old_state>.*) => (?P<new_state>.*)"
LINK_STATE_CHANGE_PATTERN = re.compile(LINK_STATE_CHANGE_PATTERN_STR)


def save_cck_mpro_lines_in_excel(trace_lines: List["CckMproTraceLine"], output_folder_path: str, excel_output_file_name_without_extension: str) -> None:
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
    wb.save(output_folder_path + "/" + excel_output_file_name_without_extension + ".xlsx")
    logger_config.print_and_log_info(f"Fichier Excel créé: {excel_output_file_name_without_extension}")
    logger_config.print_and_log_info(f"Total de {len(trace_lines)} lignes sauvegardées")


def plot_bar_graph_list_cck_mpro_lines_by_period(trace_lines: List["CckMproTraceLine"], output_folder_path: str, label: str, interval_minutes: int = 10) -> None:
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
    interval_counts: Dict[Tuple[datetime.datetime, datetime.datetime], int] = Counter()
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
    wb.save(output_folder_path + "/" + excel_filename)
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

    fig.write_html(output_folder_path + "/" + html_filename)
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
class CckMproTraceSpecificEvent:
    trace_line: "CckMproTraceLine"

    def __post_init__(self) -> None:
        assert self.trace_line.liaison
        self.liaison = self.trace_line.liaison


@dataclass
class CckMproProblemEnchainementNumeroProtocolaire(CckMproTraceSpecificEvent):
    additional_info: str = ""


class EtatLiaisonMpro(Enum):
    OK = auto()
    KO = auto()
    NON_CONNU = auto()


@dataclass
class CckMproTemporaryLossLink:
    loss_link_event: "CckMproChangementEtatLiaison"
    link_back_to_normal_event: "CckMproChangementEtatLiaison"


@dataclass
class CckMproChangementEtatLiaison(CckMproTraceSpecificEvent):
    additional_info: str = ""

    def __post_init__(self) -> None:
        super().__post_init__()

        match = LINK_STATE_CHANGE_PATTERN.match(self.trace_line.full_raw_line)
        assert match
        self.previous_state = EtatLiaisonMpro[string_utils.text_to_valid_enum_value_text(match.group("old_state"))]
        self.new_state = EtatLiaisonMpro[match.group("new_state").upper()]
        # change_states = self.trace_line.full_raw_line.split("changement d'état : ")[1]
        # states = change_states.split(" => ")
        # self.previous_state = EtatLiaisonMpro[string_utils.text_to_valid_enum_value_text(states[0])]
        # self.new_state = EtatLiaisonMpro[string_utils.text_to_valid_enum_value_text(states[1])]


@dataclass
class CckMproTraceLibrary:
    all_processed_lines: List["CckMproTraceLine"] = field(default_factory=list)
    all_processed_files: List["CckMproTraceFile"] = field(default_factory=list)
    all_problem_enchainement_numero_protocolaire: List["CckMproProblemEnchainementNumeroProtocolaire"] = field(default_factory=list)
    all_problem_enchainement_numero_protocolaire_per_link: Dict["CckMproLiaison", List["CckMproProblemEnchainementNumeroProtocolaire"]] = field(default_factory=dict)
    all_changement_etats_liaisons_mpro: List["CckMproChangementEtatLiaison"] = field(default_factory=list)
    all_changement_etats_liaisons_mpro_per_link: Dict["CckMproLiaison", List["CckMproChangementEtatLiaison"]] = field(default_factory=dict)
    lines_per_liaison: Dict[Optional["CckMproLiaison"], List["CckMproTraceLine"]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.all_temporary_loss_link: List[CckMproTemporaryLossLink] = []
        self.all_liaisons: List[CckMproLiaison] = []
        self.liaison_by_identifier: Dict[str, CckMproLiaison] = {}

    def get_or_create_liaison(self, full_name: str, identifier: str) -> "CckMproLiaison":
        if identifier in self.liaison_by_identifier:
            return self.liaison_by_identifier[identifier]

        liaison = CckMproLiaison(full_name=full_name, identifier=identifier)
        self.liaison_by_identifier[identifier] = liaison
        self.all_liaisons.append(liaison)
        return liaison

    def load_folder(self, folder_full_path: str) -> Self:
        for dirpath, dirnames, filenames in os.walk(folder_full_path):
            for file_name in filenames:
                cck_file = CckMproTraceFile(parent_folder_full_path=dirpath, file_name=file_name, library=self)
                self.all_processed_files.append(cck_file)
                self.all_processed_lines += cck_file.all_processed_lines
                self.all_problem_enchainement_numero_protocolaire += cck_file.all_problem_enchainement_numero_protocolaire
                self.all_changement_etats_liaisons_mpro += cck_file.all_changement_etats_liaisons_mpro

                for key, value in cck_file.lines_per_liaison.items():
                    if key not in self.lines_per_liaison:
                        self.lines_per_liaison[key] = []
                    self.lines_per_liaison[key] += value

                assert self.all_processed_lines
        assert self.all_processed_lines

        with logger_config.stopwatch_with_label("Create all_changement_etats_liaisons_mpro_per_link"):
            for changement_etat_liaison_mpro in self.all_changement_etats_liaisons_mpro:
                if changement_etat_liaison_mpro.liaison not in self.all_changement_etats_liaisons_mpro_per_link:
                    self.all_changement_etats_liaisons_mpro_per_link[changement_etat_liaison_mpro.liaison] = []
                self.all_changement_etats_liaisons_mpro_per_link[changement_etat_liaison_mpro.liaison].append(changement_etat_liaison_mpro)

        with logger_config.stopwatch_with_label("Create all_problem_enchainement_numero_protocolaire_per_link"):
            for problem_enchainement_numero_protocolaire in self.all_problem_enchainement_numero_protocolaire:
                if problem_enchainement_numero_protocolaire.liaison not in self.all_problem_enchainement_numero_protocolaire_per_link:
                    self.all_problem_enchainement_numero_protocolaire_per_link[problem_enchainement_numero_protocolaire.liaison] = []
                self.all_problem_enchainement_numero_protocolaire_per_link[problem_enchainement_numero_protocolaire.liaison].append(problem_enchainement_numero_protocolaire)

        with logger_config.stopwatch_with_label("Create all_temporary_loss_link"):
            for link in self.all_changement_etats_liaisons_mpro_per_link.keys():  # pylint: disable=consider-iterating-dictionary
                last_change_to_nok = None
                for mpro_link_state_change in self.all_changement_etats_liaisons_mpro_per_link[link]:
                    if mpro_link_state_change.new_state == EtatLiaisonMpro.KO:
                        last_change_to_nok = mpro_link_state_change
                    elif mpro_link_state_change.new_state == EtatLiaisonMpro.OK and mpro_link_state_change.previous_state == EtatLiaisonMpro.KO:
                        if last_change_to_nok:
                            self.all_temporary_loss_link.append(CckMproTemporaryLossLink(loss_link_event=last_change_to_nok, link_back_to_normal_event=mpro_link_state_change))
                        else:
                            logger_config.print_and_log_error(f"Cannot finc change to NOK before {mpro_link_state_change}")

        logger_config.print_and_log_info(f"{len(self.all_problem_enchainement_numero_protocolaire)} problems enchainement numero protocolaire")
        logger_config.print_and_log_info(f"{len(self.all_temporary_loss_link)} temporary_loss_link")
        logger_config.print_and_log_info(f"{len(self.all_changement_etats_liaisons_mpro)} changements états liaisons mpro")
        logger_config.print_and_log_info(
            f"{','.join([key.identifier if key is not None else "None" + ':' + str(len(value)) for key, value in self.lines_per_liaison.items()])} changements états liaisons mpro"
        )
        logger_config.print_and_log_info(f"{len(self.all_problem_enchainement_numero_protocolaire)} all_problem_enchainement_numero_protocolaire")
        logger_config.print_and_log_info(
            f"{','.join([key.identifier if key is not None else "None" + ':' + str(len(value)) for key, value in self.all_problem_enchainement_numero_protocolaire_per_link.items()])} all_problem_enchainement_numero_protocolaire_per_link"
        )

        return self


pass


@dataclass
class CckMproLiaison:
    full_name: str
    identifier: str
    all_lines: List["CckMproTraceLine"] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.hash_computed = hash(self.full_name)

    def __hash__(self) -> int:
        return self.hash_computed


@dataclass
class CckMproTraceFile:
    parent_folder_full_path: str
    file_name: str
    library: "CckMproTraceLibrary"
    all_processed_lines: List["CckMproTraceLine"] = field(default_factory=list)
    all_problem_enchainement_numero_protocolaire: List["CckMproProblemEnchainementNumeroProtocolaire"] = field(default_factory=list)
    all_changement_etats_liaisons_mpro: List["CckMproChangementEtatLiaison"] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.file_full_path = self.parent_folder_full_path + "/" + self.file_name

        self.lines_per_liaison: Dict[Optional[CckMproLiaison], List["CckMproTraceLine"]] = {}
        with logger_config.stopwatch_with_label(f"Open and read CCK Mpro trace file lines {self.file_full_path}", inform_beginning=True):
            with open(self.file_full_path, mode="r", encoding="ANSI") as file:
                all_raw_lines = file.readlines()
                logger_config.print_and_log_info(to_print_and_log=f"File {self.file_full_path} has {len(all_raw_lines)} lines", do_not_print=True)
                for line_number, line in enumerate(all_raw_lines):
                    if line_number % 100000 == 0:
                        logger_config.print_and_log_info(f"Handle line {self.file_name}:#{line_number}")
                    processed_line = CckMproTraceLine(parent_file=self, full_raw_line=line, line_number=line_number)
                    if processed_line.changement_etat_liaison:
                        self.all_changement_etats_liaisons_mpro.append(processed_line.changement_etat_liaison)
                    if processed_line.problem_enchainement_numero_protocolaire:
                        self.all_problem_enchainement_numero_protocolaire.append(processed_line.problem_enchainement_numero_protocolaire)
                    if processed_line.liaison not in self.lines_per_liaison:
                        self.lines_per_liaison[processed_line.liaison] = []
                    self.lines_per_liaison[processed_line.liaison].append(processed_line)
                    self.all_processed_lines.append(processed_line)

        logger_config.print_and_log_info(f"{self.file_full_path}: {len(self.all_processed_lines)} lines found")
        assert self.all_processed_lines, f"{self.file_full_path} is empty"


@dataclass
class CckMproTraceLine:
    parent_file: CckMproTraceFile
    full_raw_line: str
    line_number: int

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

        self.liaison = self.parent_file.library.get_or_create_liaison(full_name=self.liaison_full_name, identifier=self.liaison_id) if self.liaison_full_name and self.liaison_id else None
        if self.liaison:
            self.liaison.all_lines.append(self)

        self.problem_enchainement_numero_protocolaire = (
            CckMproProblemEnchainementNumeroProtocolaire(self) if "le msg a un problème de 'enchainement numero protocolaire'" in self.full_raw_line else None
        )
        self.changement_etat_liaison = CckMproChangementEtatLiaison(self) if "- changement d'état : " in self.full_raw_line else None

        # self.liaison_name

        # self./
        self.decoded_timestamp = datetime.datetime(year=self.year, month=self.month, day=self.day, hour=self.hour, minute=self.minute, second=self.second, microsecond=self.millisecond * 1000)
        pass
