import os

from logger import logger_config

from stsloganalyzis.ppn import ppn_profibus_log
from stsloganalyzis.unisig import upper_layer_libraries


def process_directory(root_path: str, child_directory: str) -> None:
    # Tout ce qui est créé ici est local et détruit à la fin de la fonction
    library = ppn_profibus_log.ProfibusLogLibrary.from_directory(
        directory_parent_path=root_path,
        directory_name=child_directory,
        label=child_directory,
    )
    library.save_all_usual_reports()

    # library.save_upper_layer_stms_by_stm_ids([161])
    # library.save_upper_layer_stms_by_stm_ids([178])

    # library.save_upper_layer_stms_by_stm_ids([179, 184, 175, 176, 14, 177, 178])
    # library.save_upper_layer_stms_by_stm_ids([15, 14])
    # library.save_upper_layer_stms_by_stm_ids([161, 177])


def main() -> None:

    with logger_config.application_logger():

        root_path = r"D:\temp\2026-09-20 logs PPN we mars 26"
        all_sub_directories = os.listdir(root_path)

        logger_config.print_and_log_info(f"{len(all_sub_directories)} child directories")
        for child_directory in all_sub_directories:
            process_directory(root_path, child_directory)


# Exemple d'utilisation
if __name__ == "__main__":
    main()
