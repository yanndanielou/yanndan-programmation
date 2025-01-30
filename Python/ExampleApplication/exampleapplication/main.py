""" Example module that performs addition """

from logger import logger_config
from exponentiation import exponentiation_custom
from tetration import tetration_custom


def main() -> None:
    """Main function"""
    logger = logger_config.get_logger("exampleapplication")
    logger.info("Start application")

    exponentiation_result = exponentiation_custom(2, 2)
    logger.info(f"exponentiation_result:{exponentiation_result}")

    tetration_result = tetration_custom(2, 2)
    logger.info(f"tetration_result:{tetration_result}")

    logger.info("End. Nominal end of application")


if __name__ == "__main__":
    # sys.argv[1:]
    main()
