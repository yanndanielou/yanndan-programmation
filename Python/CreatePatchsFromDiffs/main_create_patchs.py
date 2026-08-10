import pandas
from logger import logger_config

import os
import difflib
import filecmp
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path


def browse_directory(entry_var):
    """Ouvre un sélecteur de répertoire et met à jour le champ."""
    path = filedialog.askdirectory()
    if path:
        entry_var.set(path)


def get_all_files(base_path):
    """Retourne un set de chemins relatifs de tous les fichiers sous base_path."""
    files = set()
    for root, dirs, filenames in os.walk(base_path):
        for f in filenames:
            full = os.path.join(root, f)
            rel = os.path.relpath(full, base_path)
            files.add(rel)
    return files


def generate_patch(path1, path2, result_path, do_adds, do_deletes, do_modifications):
    """
    Compare path1 (cible) et path2 (source à transformer).
    Génère Apply_patchs.bat dans result_path.
    Le .bat, exécuté depuis path2, rend path2 identique à path1.
    """
    files1 = get_all_files(path1)
    files2 = get_all_files(path2)

    added_files = files1 - files2  # fichiers présents dans 1 mais pas dans 2
    deleted_files = files2 - files1  # fichiers présents dans 2 mais pas dans 1
    common_files = files1 & files2  # fichiers communs

    bat_lines = [
        "@echo off",
        "chcp 65001 >nul",
        "setlocal EnableDelayedExpansion",
        "",
        f"REM ============================================================",
        f"REM  Apply_patchs.bat",
        f'REM  Transforme le contenu de "{path2}"',
        f'REM  pour le rendre identique à "{path1}"',
        f"REM ============================================================",
        "",
        "REM Ce script doit être exécuté depuis le répertoire cible (chemin 2)",
        f'cd /d "{path2}"',
        "",
    ]

    stats = {"added": 0, "deleted": 0, "modified": 0}

    # ----------------------------------------------------------------
    # 1. AJOUTS : fichiers qui existent dans path1 mais pas dans path2
    # ----------------------------------------------------------------
    if do_adds:
        bat_lines.append("REM ========== FICHIERS À AJOUTER ==========")
        bat_lines.append("")
        for rel in sorted(added_files):
            src = os.path.join(path1, rel)
            dst_rel = rel
            dst_dir = os.path.dirname(dst_rel)
            stats["added"] += 1

            bat_lines.append(f"REM --- Ajout : {rel} ---")
            if dst_dir:
                bat_lines.append(f'if not exist "{dst_dir}" mkdir "{dst_dir}"')
            bat_lines.append(f'copy /Y "{src}" "{dst_rel}"')
            bat_lines.append("")

    # ----------------------------------------------------------------
    # 2. SUPPRESSIONS : fichiers dans path2 mais pas dans path1
    # ----------------------------------------------------------------
    if do_deletes:
        bat_lines.append("REM ========== FICHIERS À SUPPRIMER ==========")
        bat_lines.append("")
        for rel in sorted(deleted_files):
            stats["deleted"] += 1
            bat_lines.append(f"REM --- Suppression : {rel} ---")
            bat_lines.append(f'if exist "{rel}" del /F /Q "{rel}"')
            bat_lines.append("")

        # Nettoyage des répertoires vides après suppression
        if deleted_files:
            deleted_dirs = set()
            for rel in deleted_files:
                d = os.path.dirname(rel)
                while d:
                    deleted_dirs.add(d)
                    d = os.path.dirname(d)
            bat_lines.append("REM --- Nettoyage des répertoires vides ---")
            for d in sorted(deleted_dirs, key=lambda x: x.count(os.sep), reverse=True):
                bat_lines.append(f'if exist "{d}" rd "{d}" 2>nul')
            bat_lines.append("")

    # ----------------------------------------------------------------
    # 3. MODIFICATIONS : fichiers communs dont le contenu diffère
    # ----------------------------------------------------------------
    if do_modifications:
        bat_lines.append("REM ========== FICHIERS À MODIFIER ==========")
        bat_lines.append("")
        for rel in sorted(common_files):
            file1 = os.path.join(path1, rel)
            file2 = os.path.join(path2, rel)

            # Comparaison rapide
            if filecmp.cmp(file1, file2, shallow=False):
                continue  # fichiers identiques

            # Tenter une comparaison texte ligne par ligne
            is_text = True
            try:
                with open(file1, "r", encoding="utf-8", errors="strict") as f:
                    lines1 = f.readlines()
                with open(file2, "r", encoding="utf-8", errors="strict") as f:
                    lines2 = f.readlines()
            except (UnicodeDecodeError, ValueError):
                is_text = False

            stats["modified"] += 1

            if not is_text:
                # Fichier binaire : on copie simplement
                bat_lines.append(f"REM --- Modification (binaire) : {rel} ---")
                bat_lines.append(f'copy /Y "{file1}" "{rel}"')
                bat_lines.append("")
                continue

            # ---- Fichier texte : générer un patch granulaire ----
            bat_lines.append(f"REM --- Modification (texte) : {rel} ---")

            # On utilise un fichier temporaire PowerShell pour appliquer
            # les modifications ligne par ligne de manière fiable
            ps_script_name = rel.replace(os.sep, "_").replace(".", "_") + "_patch.ps1"
            ps_script_path = os.path.join(result_path, ps_script_name)

            # Générer le script PowerShell de patch
            ps_lines = generate_powershell_patch(file1, file2, rel, lines1, lines2)
            with open(ps_script_path, "w", encoding="utf-8") as ps_f:
                ps_f.write("\n".join(ps_lines))

            bat_lines.append(f'powershell -ExecutionPolicy Bypass -File "{ps_script_path}" "{rel}"')
            bat_lines.append("")

    # ----------------------------------------------------------------
    # Résumé
    # ----------------------------------------------------------------
    bat_lines.append("REM ========== RÉSUMÉ ==========")
    bat_lines.append(f"echo Ajouts     : {stats['added']} fichier(s)")
    bat_lines.append(f"echo Suppressions: {stats['deleted']} fichier(s)")
    bat_lines.append(f"echo Modifications: {stats['modified']} fichier(s)")
    bat_lines.append("echo.")
    bat_lines.append("echo Patch appliqué avec succès.")
    bat_lines.append("pause")

    # Écriture du fichier .bat
    bat_path = os.path.join(result_path, "Apply_patchs.bat")
    with open(bat_path, "w", encoding="utf-8") as f:
        f.write("\n".join(bat_lines))

    return stats, bat_path


def generate_powershell_patch(file1, file2, rel_path, lines1, lines2):
    """
    Génère un script PowerShell qui transforme le fichier file2
    pour qu'il devienne identique à file1, en appliquant les diffs.
    """
    ps = [
        "param([string]$TargetFile)",
        "",
        "# Ce script remplace le contenu du fichier cible",
        "# par le contenu attendu (issu de chemin 1).",
        "",
        "# Contenu final attendu :",
        "$newContent = @'",
    ]

    # Lire le contenu final attendu (celui de path1)
    with open(file1, "r", encoding="utf-8") as f:
        content = f.read()

    ps.append(content)
    ps.append("'@")
    ps.append("")
    ps.append("# Écriture du contenu dans le fichier cible")
    ps.append("[System.IO.File]::WriteAllText($TargetFile, $newContent, " "[System.Text.Encoding]::UTF8)")
    ps.append('Write-Host "Patché : $TargetFile"')

    return ps


def run_comparison(path1_var, path2_var, result_var, add_var, del_var, mod_var):
    """Callback du bouton GO."""
    path1 = path1_var.get().strip()
    path2 = path2_var.get().strip()
    result_path = result_var.get().strip()

    # Validations
    if not path1 or not os.path.isdir(path1):
        messagebox.showerror("Erreur", "Le chemin 1 n'est pas un répertoire valide.")
        return
    if not path2 or not os.path.isdir(path2):
        messagebox.showerror("Erreur", "Le chemin 2 n'est pas un répertoire valide.")
        return
    if not result_path or not os.path.isdir(result_path):
        messagebox.showerror("Erreur", "Le chemin résultats n'est pas un répertoire valide.")
        return

    do_adds = add_var.get()
    do_deletes = del_var.get()
    do_mods = mod_var.get()

    if not do_adds and not do_deletes and not do_mods:
        messagebox.showwarning("Attention", "Veuillez cocher au moins une option " "(Ajouts, Suppressions ou Modifications).")
        return

    try:
        stats, bat_path = generate_patch(path1, path2, result_path, do_adds, do_deletes, do_mods)
        msg = (
            f"Patch généré avec succès !\n\n"
            f"  Ajouts       : {stats['added']} fichier(s)\n"
            f"  Suppressions : {stats['deleted']} fichier(s)\n"
            f"  Modifications: {stats['modified']} fichier(s)\n\n"
            f"Fichier créé :\n{bat_path}"
        )
        messagebox.showinfo("Succès", msg)
    except Exception as e:
        messagebox.showerror("Erreur", f"Une erreur est survenue :\n{e}")


def create_gui():
    """Crée la fenêtre principale."""
    root = tk.Tk()
    root.title("Comparateur de répertoires – Générateur de Patch")
    root.resizable(False, False)

    # Variables
    path1_var = tk.StringVar()
    path2_var = tk.StringVar()
    result_var = tk.StringVar()
    add_var = tk.BooleanVar(value=True)
    del_var = tk.BooleanVar(value=True)
    mod_var = tk.BooleanVar(value=True)

    # Style
    pad = {"padx": 10, "pady": 5}
    entry_width = 60

    # ---- Chemin 1 ----
    frame1 = tk.LabelFrame(root, text="Chemin 1 (référence / cible)", padx=10, pady=5)
    frame1.pack(fill="x", **pad)

    tk.Entry(frame1, textvariable=path1_var, width=entry_width).pack(side="left", padx=(0, 5))
    tk.Button(frame1, text="Parcourir…", command=lambda: browse_directory(path1_var)).pack(side="left")

    # ---- Chemin 2 ----
    frame2 = tk.LabelFrame(root, text="Chemin 2 (source à transformer)", padx=10, pady=5)
    frame2.pack(fill="x", **pad)

    tk.Entry(frame2, textvariable=path2_var, width=entry_width).pack(side="left", padx=(0, 5))
    tk.Button(frame2, text="Parcourir…", command=lambda: browse_directory(path2_var)).pack(side="left")

    # ---- Chemin résultats ----
    frame3 = tk.LabelFrame(root, text="Chemin résultats", padx=10, pady=5)
    frame3.pack(fill="x", **pad)

    tk.Entry(frame3, textvariable=result_var, width=entry_width).pack(side="left", padx=(0, 5))
    tk.Button(frame3, text="Parcourir…", command=lambda: browse_directory(result_var)).pack(side="left")

    # ---- Options ----
    frame_opts = tk.LabelFrame(root, text="Options", padx=10, pady=5)
    frame_opts.pack(fill="x", **pad)

    tk.Checkbutton(frame_opts, text="Ajouts", variable=add_var).pack(side="left", padx=10)
    tk.Checkbutton(frame_opts, text="Suppressions", variable=del_var).pack(side="left", padx=10)
    tk.Checkbutton(frame_opts, text="Modifications", variable=mod_var).pack(side="left", padx=10)

    # ---- Bouton GO ----
    tk.Button(
        root, text="GO", font=("Arial", 14, "bold"), bg="#009999", fg="white", width=20, height=2, command=lambda: run_comparison(path1_var, path2_var, result_var, add_var, del_var, mod_var)
    ).pack(pady=15)

    root.mainloop()


if __name__ == "__main__":
    create_gui()
