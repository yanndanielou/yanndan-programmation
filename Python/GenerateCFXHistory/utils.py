import math
from logger import logger_config


from typing import Optional

from datetime import datetime
import pytz


def convert_champfx_extract_date(raw_champfx_date: str | float):  # -> Optional(datetime):

    if type(raw_champfx_date) is not str:

        if math.isnan(raw_champfx_date):
            return None

    if raw_champfx_date == "nan":
        return None
    try:
        # Dictionnaire pour la conversion des mois en français vers des chiffres
        mois_francais = {
            "janvier": "01",
            "février": "02",
            "mars": "03",
            "avril": "04",
            "mai": "05",
            "juin": "06",
            "juillet": "07",
            "août": "08",
            "septembre": "09",
            "octobre": "10",
            "novembre": "11",
            "décembre": "12",
        }

        # Séparer la date et l'heure
        date_part, time_part = raw_champfx_date.split(" à ")

        # Séparer la date en ses composants (jour, mois, année)
        jour, mois_texte, annee = date_part.split(" ")
        mois = mois_francais[mois_texte.lower()]

        # Extraire l'heure et le fuseau horaire
        temps, fuseau = time_part.split(" UTC")
        heure, minute, seconde = temps.split(":")

        # Créer un objet datetime sans information de fuseau horaire
        dt_naif = datetime(int(annee), int(mois), int(jour), int(heure), int(minute), int(seconde))

        # Ajuster pour le fuseau horaire
        utc_offset = int(fuseau)
        timezone = pytz.FixedOffset(utc_offset * 60)
        dt_aware = dt_naif.replace(tzinfo=timezone)

        return dt_naif
    except:
        logger_config.print_and_log_error(f"Could not parse date {raw_champfx_date}.")
        raise ValueError()
