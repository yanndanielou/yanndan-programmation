from logger import logger_config

from stsloganalyzis.unisig.s98 import decode_unisig_s98

OUTPUT_DIRECTORY = "output"


@logger_config.stopwatch_decorator(monitor_ram_usage=True)
def handle_directory(directory_full_path: str, filename_pattern: str = "*") -> None:
    unisig_simulation = decode_unisig_s98.UnisigS98Simulation()
    unisig_simulation.build_unisig_s98_packets_from_load_pcap_files_in_directory(directory_full_path, filename_pattern)
    common_actions(unisig_simulation)
    logger_config.print_and_log_error_if(not unisig_simulation.unisig_s98_packets, f"No packet found in {directory_full_path}")


@logger_config.stopwatch_decorator(monitor_ram_usage=True)
def handle_file(file_full_path: str) -> None:
    unisig_simulation = decode_unisig_s98.UnisigS98Simulation()
    unisig_simulation.build_unisig_s98_packets_from_load_pcap_file(file_full_path)
    common_actions(unisig_simulation)
    logger_config.print_and_log_error_if(not unisig_simulation.unisig_s98_packets, f"No packet found in {file_full_path}")


def common_actions(unisig_simulation: decode_unisig_s98.UnisigS98Simulation) -> None:
    unisig_simulation.recompute_all_mac()
    unisig_simulation.dump_packets_as_json(output_directory=OUTPUT_DIRECTORY)
    unisig_simulation.save_all_packets_as_reports()


def main() -> None:
    with logger_config.application_logger():
        handle_directory(r"C:\Users\fr232487\Downloads\2026_10_02_PAS_PAI_2")
        handle_file(r"D:\Github\yanndanielou-programmation\Python\STSLogAnalyzis\test\resources\unisig_s98\small_capture_started_after_connexion.pcapng")
        handle_file(r"C:\Users\fr232487\Downloads\logs_wsk_PAI75_22.09.2026\log_PAS_PAI_22.09_00002_20260922145856.2026.pcap")
        # handle_directory(r"C:\Users\fr232487\Downloads\2026_10_02_PAS_PAI_2\wireshark")
        handle_directory(r"C:\Users\fr232487\Downloads\logs_wsk_PAI75_22.09.2026", "*.pcap")


if __name__ == "__main__":
    main()
