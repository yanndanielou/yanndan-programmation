from dateutil import parser
from logger import logger_config

from stsloganalyzis.unisig.s98 import decode_unisig_s98

OUTPUT_DIRECTORY = "output"


def main() -> None:
    with logger_config.application_logger():

        unisig_simulation = decode_unisig_s98.UnisigS98Simulation()
        unisig_simulation.build_unisig_s98_packets_from_load_pcap_files_in_directory(r"C:\Users\fr232487\Downloads\2026_10_02_PAS_PAI_2")
        pass


if __name__ == "__main__":
    main()
