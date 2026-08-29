# -*-coding:Utf-8 -*

from application import M3uToFreeboxApplication
from logger import logger_config
from main_view import M3uToFreeboxMainView


def main() -> None:
    """Main function"""

    with logger_config.application_logger():
        main_view = M3uToFreeboxMainView()
        app: M3uToFreeboxApplication = M3uToFreeboxApplication(main_view)
        main_view.m3u_to_freebox_application = app
        main_view.mainloop()


if __name__ == "__main__":
    # sys.argv[1:]
    main()
