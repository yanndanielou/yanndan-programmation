import json
import os


def split_objects_to_files(input_file_path: str, output_directory: str, pretty_print: bool = True) -> None:
    """
    Divise une liste d'objets contenus dans un fichier en fichiers JSON individuels.

    :param input_file_path: Chemin du fichier d'entrée contenant une liste d'objets JSON.
    :param output_directory: Chemin du répertoire où les fichiers doivent être enregistrés.
    :param pretty_print: (bool) Détermine si l'output JSON doit être formaté pour être lisible (True) ou compact (False).
    """
    # Vérifie si le fichier d'entrée existe
    if not os.path.exists(input_file_path):
        print(f"Erreur : Le fichier d'entrée '{input_file_path}' n'existe pas.")
        return

    # Chargement des données depuis le fichier
    try:
        with open(input_file_path, "r", encoding="utf-8") as file:
            input_list = json.load(file)
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier d'entrée : {e}")
        return

    # Vérifie si le chargement a produit une liste
    if not isinstance(input_list, list):
        print("Erreur : Le fichier d'entrée doit contenir une liste JSON.")
        return

    # Crée le répertoire de sortie s'il n'existe pas
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Parcourt chaque objet dans la liste et crée des fichiers individuels
    for index, obj in enumerate(input_list):
        file_name = f"object_{index + 1}.json"
        file_path = os.path.join(output_directory, file_name)

        # Options pour le formatage du JSON
        json_options = {"ensure_ascii": False, "indent": 4 if pretty_print else None, "separators": (",", ":") if not pretty_print else None}

        try:
            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(obj, file, **json_options)
            print(f"Fichier écrit : {file_path}")
        except Exception as e:
            print(f"Erreur lors de l'écriture de l'objet {index + 1}: {e}")


# Exemple d'utilisation
if __name__ == "__main__":
    # Chemin du fichier d'entrée
    input_file = r"C:\Users\fr232487\Downloads\Extraction_POLARION_Full.json"

    # Chemin où les fichiers seront créés
    output_dir = "output"

    # Appel de la fonction avec pretty_print activé
    split_objects_to_files(input_file, output_dir, pretty_print=True)
