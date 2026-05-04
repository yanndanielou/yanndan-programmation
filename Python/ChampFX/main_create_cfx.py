from logger import logger_config

import connexion_param
from champfx import create_champfx


def main() -> None:
    """Main function"""

    with logger_config.application_logger():

        application = create_champfx.CreateChampFXApplication(
            champfx_login=connexion_param.champfx_login,
            champfx_password=connexion_param.champfx_password,
        )
        application.run()


if __name__ == "__main__":
    main()
