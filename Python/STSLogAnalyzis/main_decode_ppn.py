from logger import logger_config

from stsloganalyzis.next_data import (
    next_ats_data,
)
from stsloganalyzis.ppn import ppn_log


def main() -> None:

    line = "2026-06-02 17:38:09:961 kppn 1.3.3: [99:33 <= 2:33] Received PROFIBUS message [num:169690][mode:SDA][len:28] 1e 85 01 05 49 64 6c 65 20 63 79 63 6c 65 20 74 69 6d 65 6f 75 74 bc 0b 17 6d 17 78"

    decoded_frame = ppn_log.ProfibusLogLine.decode_raw_log_line(line)

    print(f"Valid frame: {decoded_frame is not None}")
    if decoded_frame:
        # Affichage des résultats
        print(f"Time: {decoded_frame.timestamp}")
        print(f"Source: {decoded_frame.source}")
        print(f"Target: {decoded_frame.target}")
        print(f"Sequence: {decoded_frame.sequence}")
        print(f"Mode: {decoded_frame.mode}")
        print(f"Length: {decoded_frame.length}")
        print(f"Bytes: {decoded_frame.bytes_hexa}")
        # Trame d'exemple donnée par l'utilisateur

        decoded_frame.decode_sdn_or_sna()


# Exemple d'utilisation
if __name__ == "__main__":
    main()
