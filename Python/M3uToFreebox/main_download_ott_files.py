import tkinter as tk
import time
import requests

from logger import logger_config
from common import date_time_formats, custom_iterator, file_download_with_progress_bar


@logger_config.stopwatch_decorator(inform_beginning=True)
def telecharger_fichier_basique(url_to_download: str, file_to_create: str) -> None:
    logger_config.print_and_log_info(f"Download:{url_to_download} to {file_to_create}")

    # Effectuer la requête HTTP GET
    response = requests.get(url_to_download)

    # Vérifier si la requête a fonctionné
    response.raise_for_status()

    # Écrire le contenu dans un fichier en mode binaire ('wb')
    with open(file_to_create, "wb") as f:
        f.write(response.content)

    logger_config.print_and_log_info(f"Téléchargement {file_to_create} terminé  depuis {url_to_download}!")


@logger_config.stopwatch_decorator(inform_beginning=True)
def telecharger_fichier_robuste(url_to_download: str, file_to_create: str, max_retries: int = 5) -> bool:
    logger_config.print_and_log_info(f"Download:{url_to_download} to {file_to_create}")

    headers = {}
    mode = "wb"
    bytes_telecharges = 0

    for tentative in range(max_retries):
        try:
            # Si on a déjà téléchargé une partie, on demande la suite (Range)
            if bytes_telecharges > 0:
                headers["Range"] = f"bytes={bytes_telecharges}-"
                mode = "ab"  # Mode 'append' pour ajouter à la fin du fichier

            # Activer stream=True pour ne pas charger tout en mémoire
            with requests.get(url_to_download, headers=headers, stream=True, timeout=(15, 60)) as r:
                # Si le serveur ne supporte pas la reprise (Code 206), on recommence à 0
                if r.status_code == 200 and bytes_telecharges > 0:
                    logger_config.print_and_log_error(f"Le serveur ne supporte pas la reprise. Recommencement...{url_to_download} to {file_to_create}")
                    mode = "wb"
                    bytes_telecharges = 0

                r.raise_for_status()

                # Écriture par blocs de 8 Ko
                with open(file_to_create, mode) as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            bytes_telecharges += len(chunk)

            # logger_config.print_and_log_info("\nTéléchargement réussi ! ")
            logger_config.print_and_log_info(f"Téléchargement {file_to_create} réussi depuis le lien {url_to_download}!")

            return True

        except (
            requests.exceptions.ChunkedEncodingError,
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
        ) as e:
            logger_config.print_and_log_exception(e)
            logger_config.print_and_log_error(f"\nConnexion interrompue ({e}). Tentative {tentative + 1}/{max_retries}...")
            time.sleep(2)  # Pause avant de réessayer

    logger_config.print_and_log_info(f"\nÉchec du téléchargement après plusieurs tentatives.{url_to_download} to {file_to_create}")
    return False


def main() -> None:
    with logger_config.application_logger():

        downloads_link_and_file = [
            (
                "http://line.rex1468191.com/xmltv.php?username=029b58d302&password=360a41fadb",
                r"D:\ott_all.txt",
            ),
            (
                "http://line.rex1468191.com/get.php?username=029b58d302&password=360a41fadb&type=m3u_plus&output=ts",
                r"D:\ott_m3u.m3u",
            ),
            (
                "http://line.rex1468191.com/player_api.php?username=029b58d302&password=360a41fadb&action=get_live_categories",
                r"D:\ott_get_live_categories.json",
            ),
            (
                "http://line.rex1468191.com/player_api.php?username=029b58d302&password=360a41fadb&action=get_vod_categories",
                r"D:\ott_get_vod_categories.json",
            ),
            (
                "http://line.rex1468191.com/player_api.php?username=029b58d302&password=360a41fadb&action=get_series_categories",
                r"D:\ott_get_series_categories.json",
            ),
            (
                "http://line.rex1468191.com/player_api.php?username=029b58d302&password=360a41fadb&action=get_live_streams",
                r"D:\get_live_streams.json",
            ),
        ]

        for link, file_to_create in [(download_link_and_file[0], download_link_and_file[1]) for download_link_and_file in downloads_link_and_file]:

            telecharger_fichier_robuste(link, file_to_create)
            # telecharger_fichier_basique(link, file_to_create)


if __name__ == "__main__":
    # sys.argv[1:]
    main()
