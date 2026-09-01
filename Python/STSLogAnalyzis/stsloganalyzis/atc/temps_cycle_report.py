from logger import logger_config

from stsloganalyzis.next_data import (
    next_ats_data,
)
from stsloganalyzis.atc import atc_logs, perturbo
from stsloganalyzis.common import common_filters

from common import file_utils

import cProfile, pstats, io
from pstats import SortKey
import os

OUTPUT_DIRECTORY = "output"


def build_temps_cycle_report_from_atc_log(atc_test_result: atc_logs.ATCTestResult) -> None:

    atc_test_result.create_report_all_variables()
