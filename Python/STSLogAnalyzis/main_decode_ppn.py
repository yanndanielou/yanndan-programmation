from logger import logger_config

from stsloganalyzis.ppn import ppn_log
from stsloganalyzis.unisig import decode_unisig


def main() -> None:

    with logger_config.application_logger():
        library = ppn_log.ProfibusLogLibrary(
            directory_path=r"D:\temp\2026-09-20 logs PPN we mars 26\ppn_cab1_log.tar",
            filename_pattern="profibus.log",
        )
        decode_unisig.SdaErrorsFound().log_stats()

        interesting_stm_ids = [179, 184, 175, 176]
        interesting_stm_messages = library.get_upper_layer_stms_by_stm_ids(interesting_stm_ids)

        pass


# Exemple d'utilisation
if __name__ == "__main__":
    main()
