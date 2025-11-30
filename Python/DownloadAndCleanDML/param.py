import os


DML_FILE_RHAPS_ID = 79329709


COLUMNS_NAMES_TO_REMOVE = [
    "Unique ID",
    "Code Dico & Code Arborescence",
    "MemoEasy",
    "Niveau Arborescence",
    "Code Arborescence",
    "Nom Arborescence",
    "Code Dico",
    "Type Document",
    "Tranche",
    "Phase",
    "Désignation Phase",
    "Work Package",
    "WorkPackageLeader",
    "Jalon Contractuel",
    "Date Jalon Contractuel",
    "Commentaires Internes",
    "Commentaires MOE",
    "Référentiel",
    "Jalon GUIDE",
    "Work Product",
    "ID Macrotache",
    "% Macro Tache",
    "Montant",
    "Activité Planning",
    "Date Planning",
    "Lien Doc-Planning",
    "Baseline Livraison",
    "Previous Forecast Livraison",
    "À confirmer Livraison",
    "Durée Livraison 1è Version & Acceptation",
    "GCONF",
    "Jalon Fourniture",
    "Nb de commentaires bloquants encore ouverts",
    "Document technique (Yes/No)",
    "Confidentialité Document",
    "Référence SNCF",
    "ATS+/Nexteo",
    "% Avancement DML",
    "Dernier statut Document",
    "Version avec dernier statut",
    "FILTERED OR NOT",
    "IS LAST VERSION",
    "IS FIRST VERSION",
    "IS FIRST ACCEPTATIONTBDLAST REFUSAL",
    "VERSION & REVISION",
    "CHROMATIC DISCRIMINANT",
    "Numeros  SNCF Mobilités \nn°10-5969 632 \nà\nn°10-5970-637",
    "Statut acceptation",
    "Date Acceptation",
    "Baseline FA",
]

DEFAULT_DOWNLOAD_DIRECTORY = os.path.expandvars(r"%userprofile%\downloads")

DML_FILE_DOWNLOADED_PATTERN = "DML_NEXTEO_ATS+_V*.xlsm"

DML_FILE_WITHOUT_USELESS_SHEETS_PATH = f"{DEFAULT_DOWNLOAD_DIRECTORY}\\DML_NEXTEO_ATS+_V14_without_useless_sheets.xlsm"
DML_FILE_CONVERTED_TO_STANDARD_XSLX = f"{DEFAULT_DOWNLOAD_DIRECTORY}\\DML_NEXTEO_ATS+_V14_standard_excel.xlsx"
DML_FILE_WITH_USELESS_RANGES = f"{DEFAULT_DOWNLOAD_DIRECTORY}\\DML_NEXTEO_ATS+_V14_with_useless_ranges_cleaned.xlsm"
DML_FILE_WITH_USELESS_COLUMNS_REMOVED_XLWINGS = f"{DEFAULT_DOWNLOAD_DIRECTORY}\\DML_NEXTEO_ATS+_V14_with_useless_columns_removed_xlwings.xlsm"
DML_FILE_WITH_USELESS_COLUMNS_REMOVED_OPENPYXL = f"{DEFAULT_DOWNLOAD_DIRECTORY}\\DML_NEXTEO_ATS+_V14_with_useless_columns_removed_openpyxl.xlsm"
DML_FILE_WITHOUT_LINKS = f"{DEFAULT_DOWNLOAD_DIRECTORY}\\DML_NEXTEO_ATS+_V14_without_links.xlsm"
DML_FILE_CLEANED_FINAL = f"{DEFAULT_DOWNLOAD_DIRECTORY}\\DML_NEXTEO_ATS+_V14_cleaned_light.xlsm"
DML_RAW_DOWNLOADED_FROM_RHAPSODY_FILE_PATH = f"{DEFAULT_DOWNLOAD_DIRECTORY}\\DML_NEXTEO_ATS+_V14_raw_from_rhapsody.xlsm"
DML_FILE_FINAL_DESTINATION_PATH = f"{DEFAULT_DOWNLOAD_DIRECTORY}\\DML_NEXTEO_ATS+_V14.xlsm"

USEFUL_DML_SHEET_NAME = "Database"
ALLOWED_DML_SHEETS_NAMES = [USEFUL_DML_SHEET_NAME]

FIRST_LINE_TO_REMOVE_RANGES = "1:1"
RANGES_TO_REMOVE = [FIRST_LINE_TO_REMOVE_RANGES]

DOWNLOAD_FROM_RHAPSODY_ENABLED = True
REMOVE_USELESS_SHEETS_ENABLED = True
REMOVE_LINKS_SHEETS_ENABLED = True
REMOVE_USELESS_RANGES_ENABLED = True
CONVERT_EXCEL_TO_STANDARD_XSLX_ENABLED = True
REMOVE_USELESS_COLUMNS_ENABLED = True
