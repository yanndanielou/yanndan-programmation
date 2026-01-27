import csv
import datetime
import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional, cast

import re


from logger import logger_config

# CONTENT_OF_FIELD_IN_CASE_OF_DECODING_ERROR = "!!! Decoding Error !!!"

LIAISON_PATTERN_STR = ".*(?P<liaison_full_name>Liaison (?P<liaison_id>\d+A?B?)).*"
LIAISON_PATTERN = re.compile(LIAISON_PATTERN_STR)


@dataclass
class CckMproTraceLine:
    full_line: str

    def __post_init__(self) -> None:
        self.raw_date_str = self.full_line[1:23]
        self.year = int(self.raw_date_str[:4])
        self.month = int(self.raw_date_str[5:7])
        self.day = int(self.raw_date_str[8:10])
        self.hour = int(self.raw_date_str[11:13])
        self.minute = int(self.raw_date_str[14:16])
        self.second = int(self.raw_date_str[17:19])
        self.millisecond = int(self.raw_date_str[20:22]) * 10

        match_liaison_pattern = LIAISON_PATTERN.match(self.full_line)
        assert match_liaison_pattern, f"{self.full_line} does not match {LIAISON_PATTERN_STR}"
        self.liaison_full_name = match_liaison_pattern.group("liaison_full_name")
        self.liaison_id = match_liaison_pattern.group("liaison_id")
        pass
        # self.liaison_name

        # self./

        self.decoded_timestamp = datetime.datetime(year=self.year, month=self.month, day=self.day, hour=self.hour, minute=self.minute, second=self.second, microsecond=self.millisecond * 1000)
        pass
