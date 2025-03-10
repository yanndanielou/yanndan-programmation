from datetime import datetime, timezone

from common import json_encoders


import pandas

from logger import logger_config

import time
import re

import os


def parse_section(section):
    section_data = {}
    lines = section.strip().split("\n")
    for line in lines:
        if ":" in line:
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()
            if key == "Time":
                try:
                    section_data[key] = datetime.strptime(value, "%Y-%m-%d %H:%M:%S %z")
                except ValueError:
                    section_data[key] = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
            elif key == "Schema Rev":
                section_data[key] = int(value)
            else:
                section_data[key] = value

    fields_start = lines.index("==Fields==") + 1
    fields_end = lines.index("", fields_start)
    fields = lines[fields_start:fields_end]

    field_data = {}
    for field in fields:
        field_name = field.split("(")[0].strip()
        field_values = field.split("(")[1][:-1].split(":")
        field_data[field_name] = {"Old": field_values[0].strip(), "New": field_values[1].strip()}

    section_data["Fields"] = field_data
    return section_data


def parse_extended_history_text(text):

    data = []
    sections = text.split("====START====")
    for section in sections[1:]:
        data.append(parse_section(section=section))

    return data
