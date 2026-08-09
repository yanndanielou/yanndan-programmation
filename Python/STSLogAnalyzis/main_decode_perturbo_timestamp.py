from logger import logger_config

from stsloganalyzis.next_data import (
    next_ats_data,
)
from dateutil import parser

from stsloganalyzis.archive import archive_analyzis, decode_archive
from stsloganalyzis.atc import atc_logs

OUTPUT_DIRECTORY = "output"

print(atc_logs.pert_variable_to_timestamp(c_heure=51006750, c_decalage=3600000, c_decenie=2, c_jour=2278))
print(atc_logs.pert_variable_to_timestamp(c_heure=59949450, c_decalage=3600000, c_decenie=0, c_jour=0))
