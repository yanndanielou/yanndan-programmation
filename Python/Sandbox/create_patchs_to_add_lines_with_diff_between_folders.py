import filecmp
import os
from logger import logger_config

from common import file_utils, file_name_utils

import re

# r'D:\NEXT_PCC_FORM_2.0.1\NEXT_AutomaticTrainSupervision_Training_Simulator_2026_07_10_a_22h42 NEXT\Data'
# r'D:\NEXT_PCC_FORM_2.1.0\NEXT_AutomaticTrainSupervision_Training_Simulator_2026_08_07_a_19h09 NEXT\Data'

DEFAULT_RESULT_VALUE = r"D:\temp\patch"
DEFAULT_PATH_1 = r"D:\NEXT_PCC_FORM_2.1.0\NEXT_AutomaticTrainSupervision_Training_Simulator_2026_08_07_a_19h09 NEXT\Data\Csv"
DEFAULT_PATH_2 = r"D:\NEXT_PCC_FORM_2.0.1\NEXT_AutomaticTrainSupervision_Training_Simulator_2026_07_10_a_22h42 NEXT\Data\Csv"
DEFAULT_FOLDER_TO_APPLY_PATCH = r"D:\NEXT\Data\Csv"
BLACK_LISTED_LINES_SUBSTRING = [
    "SYNOPTIC;",
    "_CCK_",
    "PROTECTIONS_",
]

BLACK_LISTED_FILES_SUBSTRING = [
    "NEXT_segment_in_restriction",
]


@logger_config.stopwatch_decorator(inform_beginning=True)
def get_all_files(base_path: str) -> set[str]:
    """Retourne un set de chemins relatifs de tous les fichiers sous base_path."""
    files = set()
    for root, dirs, filenames in os.walk(base_path):
        for f in filenames:
            full = os.path.join(root, f)
            rel = os.path.relpath(full, base_path)
            files.add(rel)
    return files


@logger_config.stopwatch_decorator(inform_beginning=True)
def compare_folders_and_generate_patchs(
    folder_1_path: str,
    folder_2_path: str,
    result_path: str,
    folder_to_apply_patchs_path_instead_of_folder_2: str,
    do_added_files: bool,
    do_deleted_files: bool,
    do_modified_lines: bool,
) -> tuple[dict[str, int], str]:
    """
    Compare path1 (cible) et path2 (source à transformer).
    Génère Apply_patchs.bat dans result_path.
    Le .bat, exécuté depuis path2, rend path2 identique à path1.

    En plus des scripts par fichier, génère un script .bat par sous-répertoire
    enfant contenant l'ensemble des diff du dossier concerné.
    """
    files1 = get_all_files(folder_1_path)
    files2 = get_all_files(folder_2_path)

    added_files = files1 - files2  # fichiers présents dans 1 mais pas dans 2
    deleted_files = files2 - files1  # fichiers présents dans 2 mais pas dans 1
    common_files = files1 & files2  # fichiers communs

    global_bat_lines = [
        "@echo on",
        "chcp 65001 >nul",
        "setlocal EnableDelayedExpansion",
        "",
        "",
    ]

    stats = {"added": 0, "deleted": 0, "modified": 0}

    # ----------------------------------------------------------------
    # 1. AJOUTS : fichiers qui existent dans path1 mais pas dans path2
    # ----------------------------------------------------------------
    if do_added_files:
        global_bat_lines.append("REM ========== FICHIERS À AJOUTER ==========")
        global_bat_lines.append("")
        for rel in sorted(added_files):
            src = os.path.join(folder_1_path, rel)
            dst_rel = rel
            dst_dir = os.path.dirname(dst_rel)
            stats["added"] += 1

            global_bat_lines.append(f"REM --- Ajout : {rel} ---")
            if dst_dir:
                global_bat_lines.append(f'if not exist "{dst_dir}" mkdir "{dst_dir}"')
            global_bat_lines.append(f'copy /Y "{src}" "{dst_rel}"')
            global_bat_lines.append("")

    # ----------------------------------------------------------------
    # 2. SUPPRESSIONS : fichiers dans path2 mais pas dans path1
    # ----------------------------------------------------------------
    if do_deleted_files:
        global_bat_lines.append("REM ========== FICHIERS À SUPPRIMER ==========")
        global_bat_lines.append("")
        for rel in sorted(deleted_files):
            stats["deleted"] += 1
            global_bat_lines.append(f"REM --- Suppression : {rel} ---")
            global_bat_lines.append(f'if exist "{rel}" del /F /Q "{rel}"')
            global_bat_lines.append("")

        # Nettoyage des répertoires vides après suppression
        if deleted_files:
            deleted_dirs = set()
            for rel in deleted_files:
                d = os.path.dirname(rel)
                while d:
                    deleted_dirs.add(d)
                    d = os.path.dirname(d)
            global_bat_lines.append("REM --- Nettoyage des répertoires vides ---")
            for d in sorted(deleted_dirs, key=lambda x: x.count(os.sep), reverse=True):
                global_bat_lines.append(f'if exist "{d}" rd "{d}" 2>nul')
            global_bat_lines.append("")

    # ----------------------------------------------------------------
    # 3. MODIFICATIONS : fichiers communs dont le contenu diffère
    # ----------------------------------------------------------------
    if do_modified_lines:
        global_bat_lines.append("REM ========== FICHIERS À MODIFIER ==========")
        global_bat_lines.append("")
        for rel in sorted(common_files):
            file_1_full_path = os.path.join(folder_1_path, rel)
            file_2_full_path = os.path.join(folder_2_path, rel)

            blacklisted = False
            for blacklist in BLACK_LISTED_FILES_SUBSTRING:
                if blacklist in file_1_full_path:
                    blacklisted = True

            if blacklisted:
                logger_config.print_and_log_info(f"{file_1_full_path} is blacklisted")
                continue

            # Comparaison rapide
            if filecmp.cmp(file_1_full_path, file_2_full_path, shallow=False):
                logger_config.print_and_log_info(f"Files {file_name_utils.get_file_name_with_extension_from_full_path(file_1_full_path)} are identical", do_not_print=True)
                continue  # fichiers identiques

            logger_config.print_and_log_info(f"Files {file_name_utils.get_file_name_with_extension_from_full_path(file_1_full_path)} are different")
            lines_file_1 = file_utils.open_text_file_and_get_read_lines(file_1_full_path)
            lines_file_2 = file_utils.open_text_file_and_get_read_lines(file_2_full_path)

            stats["modified"] += 1

            if lines_file_1 is None or lines_file_2 is None:
                global_bat_lines.append(f"REM --- Modification (binaire) : {rel} ---")
                global_bat_lines.append(f'copy /Y "{file_1_full_path}" "{rel}"')
                global_bat_lines.append("")
                continue

            patch_script_name = rel.replace(os.sep, "_").replace(".", "_") + "_patch.bat"
            patch_script_path = os.path.join(result_path, patch_script_name)

            missing_lines = sorted(set(lines_file_1) - set(lines_file_2))

            logger_config.print_and_log_info(f"{file_1_full_path}: {len(missing_lines)} lines to add")
            if missing_lines:

                global_bat_lines.append(f"REM --- Modification (texte) : {rel} ---")

                file_to_apply_patch = file_2_full_path.replace(folder_2_path, folder_to_apply_patchs_path_instead_of_folder_2) if folder_to_apply_patchs_path_instead_of_folder_2 else file_2_full_path

                with open(patch_script_path, "w", encoding="utf-8") as patch_f:

                    patch_f.write(f"IF EXIST {file_to_apply_patch}_original ECHO DO NOTHING PATCH ALREADY APPLIED & pause & EXIT\n")
                    patch_f.write(f"copy {file_to_apply_patch} {file_to_apply_patch}_original \n")

                    for missing_line in missing_lines:
                        blacklisted = False
                        for blacklist in BLACK_LISTED_LINES_SUBSTRING:
                            if blacklist in missing_line:
                                blacklisted = True

                        if not blacklisted:
                            patch_f.write("echo " + missing_line.strip() + ">> " + file_to_apply_patch + "\n")

                global_bat_lines.append(f'CALL "{file_name_utils.get_file_name_with_extension_from_full_path(patch_script_path)}"')
                global_bat_lines.append("")

    # ----------------------------------------------------------------
    # Résumé
    # ----------------------------------------------------------------
    global_bat_lines.append("REM ========== RÉSUMÉ ==========")
    global_bat_lines.append(f"echo Ajouts     : {stats['added']} fichier(s)")
    global_bat_lines.append(f"echo Suppressions: {stats['deleted']} fichier(s)")
    global_bat_lines.append(f"echo Modifications: {stats['modified']} fichier(s)")
    global_bat_lines.append("echo.")
    global_bat_lines.append("echo Patch appliqué avec succès.")
    global_bat_lines.append("timeout /t 30")

    # Écriture du fichier .bat
    bat_path = os.path.join(result_path, "Apply_patchs.bat")
    with open(bat_path, "w", encoding="utf-8") as f:
        f.write("\n".join(global_bat_lines))

    return stats, bat_path


@logger_config.stopwatch_decorator(inform_beginning=True)
def run_folders_comparison(
    path_folder_comparison_1: str,
    path_folder_comparison_2: str,
    folder_to_apply_patchs_path: str,
    result_path: str,
    do_added_files: bool,
    do_deleted_files: bool,
    do_modified_lines: bool,
) -> None:
    """Callback du bouton GO."""

    logger_config.print_and_log_info(f"run_comparison {path_folder_comparison_1}")

    # Validations
    if not path_folder_comparison_1 or not os.path.isdir(path_folder_comparison_1):
        logger_config.print_and_log_error("Le chemin 1 n'est pas un répertoire valide.")
        return
    if not path_folder_comparison_2 or not os.path.isdir(path_folder_comparison_2):
        logger_config.print_and_log_error("Le chemin 2 n'est pas un répertoire valide.")
        return
    if not result_path or not os.path.isdir(result_path):
        logger_config.print_and_log_error("Le chemin résultats n'est pas un répertoire valide.")
        return

    try:
        stats, bat_path = compare_folders_and_generate_patchs(
            path_folder_comparison_1,
            path_folder_comparison_2,
            result_path,
            folder_to_apply_patchs_path,
            do_added_files,
            do_deleted_files,
            do_modified_lines,
        )
        msg = (
            f"Patch généré avec succès !\n\n"
            f"  Ajouts       : {stats['added']} fichier(s)\n"
            f"  Suppressions : {stats['deleted']} fichier(s)\n"
            f"  Modifications: {stats['modified']} fichier(s)\n\n"
            f"Fichier créé :\n{bat_path}"
        )
        logger_config.print_and_log_info(msg)
    except Exception as e:
        logger_config.print_and_log_error(f"Une erreur est survenue :\n{e}")


if __name__ == "__main__":
    with logger_config.application_logger():
        run_folders_comparison(
            path_folder_comparison_1=DEFAULT_PATH_1,
            path_folder_comparison_2=DEFAULT_PATH_2,
            result_path=DEFAULT_RESULT_VALUE,
            folder_to_apply_patchs_path=DEFAULT_FOLDER_TO_APPLY_PATCH,
            do_added_files=True,
            do_deleted_files=False,
            do_modified_lines=True,
        )
