from common import json_utils
from logger import logger_config

# Exemple d'utilisation
if __name__ == "__main__":
    with logger_config.application_logger():
        # Chemin du fichier d'entrée
        input_file = r""
        # Chemin où les fichiers seront créés
        output_dir = "output"

        json_utils.split_json_files_containing_list_to_files(
            input_file_path=r"C:\Users\fr232487\Downloads\Extraction_POLARION_User.json",
            output_directory=output_dir,
            output_file_prefix="user_",
            attribute_to_use_in_file_name="id",
            pretty_print=True,
        )
        json_utils.split_json_files_containing_list_to_files(
            input_file_path=r"C:\Users\fr232487\Downloads\Extraction_POLARION_Full.json",
            output_directory=output_dir,
            output_file_prefix="work_item_",
            attribute_to_use_in_file_name="id",
            pretty_print=True,
        )
