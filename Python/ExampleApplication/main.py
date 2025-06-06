"""Example module that performs addition"""

from logger import logger_config
from exampleapplication import exponentiation, tetration


def main() -> None:
    """Main function"""
    logger_config.configure_logger_with_random_log_file_suffix("exampleapplication")
    logger_config.print_and_log_info("Start application")

    exponentiation_result = exponentiation.exponentiation_custom(2, 2)
    logger_config.print_and_log_info(f"exponentiation_result:{exponentiation_result}")

    tetration_result = tetration.tetration_custom(2, 2)
    logger_config.print_and_log_info(f"tetration_result:{tetration_result}")

    logger_config.print_and_log_info("End. Nominal end of application")


if __name__ == "__main__":
    # sys.argv[1:]
    main()
