import json
import os
from logger import logger_config


def split_objects_to_files(input_file_path: str, output_directory: str, pretty_print: bool = True) -> None:
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

    logger_config.print_and_log_info(f"{len(input_list)} objects found")

    # Crée le répertoire de sortie s'il n'existe pas
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Parcourt chaque objet dans la liste et crée des fichiers individuels
    for index, obj in enumerate(input_list):
        output_file_options_suffix = "_pretty" if pretty_print else ""
        output_file_name = f"object_{index + 1}_{output_file_options_suffix}.json"
        output_file_path = os.path.join(output_directory, output_file_name)

        # Options pour le formatage du JSON
        json_options = {"ensure_ascii": False, "indent": 4 if pretty_print else None, "separators": (",", ":") if not pretty_print else None}

        try:
            with open(output_file_path, "w", encoding="utf-8") as file:
                json.dump(obj, file, **json_options)

            if index % 500 == 0:
                logger_config.print_and_log_info(f"{index+1}th file created : {output_file_path}")
        except Exception as e:
            logger_config.print_and_log_error(f"Erreur lors de l'écriture de l'objet {index + 1}: {e}")


# Exemple d'utilisation
if __name__ == "__main__":
    with logger_config.application_logger():
        # Chemin du fichier d'entrée
        input_file = r"C:\Users\fr232487\Downloads\Extraction_POLARION_Full.json"

        # Chemin où les fichiers seront créés
        output_dir = "output"

        # Appel de la fonction avec pretty_print activé
        split_objects_to_files(input_file, output_dir, pretty_print=True)
