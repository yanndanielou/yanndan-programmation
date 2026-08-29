import tkinter as tk
import time
import requests

from logger import logger_config
from common import date_time_formats, custom_iterator, file_download_with_progress_bar


def telecharger_fichier_basique(link: str, file_to_create: str) -> None:

    # Effectuer la requête HTTP GET
    response = requests.get(link)

    # Vérifier si la requête a fonctionné
    response.raise_for_status()

    # Écrire le contenu dans un fichier en mode binaire ('wb')
    with open(file_to_create, "wb") as f:
        f.write(response.content)

    print(f"Téléchargement {file_to_create} terminé  depuis {link}!")


def telecharger_fichier_robuste(url: str, nom_fichier: str, max_retries: int = 5) -> bool:
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
            with requests.get(url, headers=headers, stream=True, timeout=15) as r:
                # Si le serveur ne supporte pas la reprise (Code 206), on recommence à 0
                if r.status_code == 200 and bytes_telecharges > 0:
                    print("Le serveur ne supporte pas la reprise. Recommencement...")
                    mode = "wb"
                    bytes_telecharges = 0

                r.raise_for_status()

                # Écriture par blocs de 8 Ko
                with open(nom_fichier, mode) as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            bytes_telecharges += len(chunk)

            print("\nTéléchargement réussi ! ")
            return True

        except (
            requests.exceptions.ChunkedEncodingError,
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
        ) as e:
            print(f"\nConnexion interrompue ({e}). Tentative {tentative + 1}/{max_retries}...")
            time.sleep(2)  # Pause avant de réessayer

    print("\nÉchec du téléchargement après plusieurs tentatives.")
    return False


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
    # main()

    downloads_link_and_file = [
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
    ]

    for link, file_to_create in [(download_link_and_file[0], download_link_and_file[1]) for download_link_and_file in downloads_link_and_file]:

        telecharger_fichier_robuste(link, file_to_create)
        # telecharger_fichier_basique(link, file_to_create)
