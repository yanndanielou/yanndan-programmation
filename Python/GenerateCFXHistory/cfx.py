import pandas as pd
import datetime

from logger import logger_config

import utils


class ChampFXEntry:
    def __init__(self, row):
        self.cfx_id = row["CFXID"]
        self.state = row["State"]
        self.submit_date = utils.convert_champfx_extract_date(row["SubmitDate"])
        self.analysis_date = utils.convert_champfx_extract_date(row["HistoryOfLastAction.AnalysisDate"])
        self.solution_date = utils.convert_champfx_extract_date(row["HistoryOfLastAction.SolutionDate"])
        self.verification_date = utils.convert_champfx_extract_date(row["HistoryOfLastAction.VerificationDate"])
        self.validation_date = utils.convert_champfx_extract_date(row["HistoryOfLastAction.ValidationDate"])
        self.closing_date = utils.convert_champfx_extract_date(row["HistoryOfLastAction.ClosingDate"])
        self.year = self.submit_date.year
        self.month = self.submit_date.month
