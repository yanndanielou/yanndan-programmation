import tkinter as tk
from logger import logger_config
from common import date_time_formats, custom_iterator, file_download_with_progress_bar


def main() -> None:
    with logger_config.application_logger():
        root = tk.Tk()
        root.withdraw()
        popup = tk.Toplevel(root)

        file_download_with_progress_bar.MultipleFilesDownloadPopup(
            master=popup,
            downloads=[
                (
                    "http://line.rex1468191.com/xmltv.php?username=029b58d302&password=360a41fadb",
                    r"D:\ott_all",
                ),
                (
                    "http://line.rex1468191.com/get.php?username=029b58d302&password=360a41fadb&type=m3u_plus&output=ts",
                    r"D:\ott_m3u",
                ),
                (
                    "http://line.rex1468191.com/player_api.php?username=029b58d302&password=360a41fadb&action=get_live_categories",
                    r"D:\ott_get_live_categories",
                ),
                (
                    "http://line.rex1468191.com/player_api.php?username=029b58d302&password=360a41fadb&action=get_vod_categories",
                    r"D:\ott_get_vod_categories",
                ),
                (
                    "http://line.rex1468191.com/player_api.php?username=029b58d302&password=360a41fadb&action=get_series_categories",
                    r"D:\ott_get_series_categories",
                ),
                (
                    "http://line.rex1468191.com/player_api.php?username=029b58d302&password=360a41fadb&action=get_live_streams",
                    r"D:\get_live_streams",
                ),
            ],
            parallel=True,
        )
        root.mainloop()


if __name__ == "__main__":
    # sys.argv[1:]
    main()
