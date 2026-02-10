# -*-coding:Utf-8 -*
import json
import os

from common import string_utils
from typing import Optional
from logger import logger_config


def split_json_files_containing_list_to_files(
    input_file_path: str, output_directory: str, output_file_prefix: str, attribute_to_use_in_file_name: Optional[str] = None, pretty_print: bool = True
) -> None:
    """
    Divise une liste d'objets contenus dans un fichier en fichiers JSON individuels.

    :param input_file_path: Chemin du fichier d'entrée contenant une liste d'objets JSON.
    :param output_directory: Chemin du répertoire où les fichiers doivent être enregistrés.
    :param pretty_print: (bool) Détermine si l'output JSON doit être formaté pour être lisible (True) ou compact (False).
    """
    # Vérifie si le fichier d'entrée existe
    if not os.path.exists(input_file_path):
        logger_config.print_and_log_error(f"Erreur : Le fichier d'entrée '{input_file_path}' n'existe pas.")
        return

    # Chargement des données depuis le fichier
    try:
        with open(input_file_path, "r", encoding="utf-8") as file:
            input_list = json.load(file)
    except Exception as e:
        logger_config.print_and_log_error(f"Erreur lors de la lecture du fichier d'entrée : {e}")
        return

    # Vérifie si le chargement a produit une liste
    if not isinstance(input_list, list):
        logger_config.print_and_log_error("Erreur : Le fichier d'entrée doit contenir une liste JSON.")
        return

    logger_config.print_and_log_info(f"{len(input_list)} objects {output_file_prefix} found")

    # Crée le répertoire de sortie s'il n'existe pas
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Parcourt chaque objet dans la liste et crée des fichiers individuels
    for index, obj in enumerate(input_list):
        identifier = obj[attribute_to_use_in_file_name] if attribute_to_use_in_file_name and attribute_to_use_in_file_name in obj else f"{index + 1}"
        output_file_options_suffix = "_pretty" if pretty_print else ""
        output_file_name = string_utils.format_filename(f"{output_file_prefix}{identifier}_{output_file_options_suffix}.json")
        output_file_path = os.path.join(output_directory, output_file_name)

        # Options pour le formatage du JSON
        json_options = {"ensure_ascii": False, "indent": 4 if pretty_print else None, "separators": (",", ":") if not pretty_print else None}

        try:
            with open(output_file_path, "w", encoding="utf-8") as file:
                json.dump(obj, file, **json_options)

            if index > 1 and index % (round(len(input_list) / 10)) == 0:
                logger_config.print_and_log_info(f"{index+1}th / {len(input_list)} ({round((index+1)/len(input_list)*100,2)}%) file {output_file_prefix} created")
        except Exception as e:
            logger_config.print_and_log_error(f"Erreur lors de l'écriture de l'objet {index + 1}: {e}")
