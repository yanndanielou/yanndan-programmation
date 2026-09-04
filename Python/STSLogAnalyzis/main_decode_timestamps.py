from logger import logger_config

from stsloganalyzis.next_data import (
    next_ats_data,
)
from dateutil import parser

from stsloganalyzis.archive import archive_analyzis, decode_archive
from stsloganalyzis.atc import atc_logs
from stsloganalyzis.common import hlf

OUTPUT_DIRECTORY = "output"

for c_heure in [
    412920,
    414620,
    419670,
]:
    print(str(c_heure) + " = " + str(atc_logs.pert_variable_to_timestamp(c_heure=c_heure, c_decalage=7200000, c_decenie=0, c_jour=0)))

print(hlf.decode_hlf_to_datetime(time_field_value=586360, day_on_decade_field_value=2437, decade_field_value=2, time_offset_value=72000))
