from logger import logger_config

from stsloganalyzis.unisig.s98 import decode_unisig_s98

OUTPUT_DIRECTORY = "output"


def main() -> None:
    with logger_config.application_logger():

        unisig_simulation = decode_unisig_s98.UnisigS98Simulation()
        unisig_simulation.build_unisig_s98_packets_from_load_pcap_file(r"C:\Users\fr232487\Downloads\logs_wsk_PAI75_22.09.2026\log_PAS_PAI_22.09_00002_20260922145856.2026.pcap")
        # unisig_simulation.build_unisig_s98_packets_from_load_pcap_files_in_directory(r"C:\Users\fr232487\Downloads\logs_wsk_PAI75_22.09.2026", "*.pcap")
        unisig_simulation.recompute_all_mac()
        unisig_simulation.save_all_packets()
        assert unisig_simulation.unisig_s98_packets


if __name__ == "__main__":
    main()
