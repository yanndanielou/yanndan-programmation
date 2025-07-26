from typing import List, Dict
from dataclasses import dataclass

import csv

from logger import logger_config


class DecodedActionSet:
    def __init__(self) -> None:
        self.undecoded_bits_by_error: List[int] = []
        self.action_set_id_with_value_true: List[str] = []
        self.action_set_id_with_value: Dict[str, bool] = dict()


@dataclass
class ActionSetContentDecoder:
    csv_file_file_path: str

    def decode_actions_bitfield(self, bitfield: str) -> DecodedActionSet:

        decoded_action_set = DecodedActionSet()
        decoded_bits = set()

        # Read the CSV file
        with open(self.csv_file_file_path, mode="r", encoding="utf-8") as file:
            csv_reader = csv.DictReader(file, delimiter=";")

            # Iterate through each row in the CSV
            for csv_row in csv_reader:

                num_ats_str = csv_row["NUM_ACTION_SET_ATS"] if "NUM_ACTION_SET_ATS" in csv_row else csv_row["NUM_ATS"]
                num_ats = int(num_ats_str)
                # num_ats = int(row["NUM_ATS"])
                decoded_bits.add(num_ats)  # Track decoded bits
                bit_value_str = bitfield[num_ats]
                bit_value_bool = bool(int(bit_value_str))

                action_set_id_str = csv_row["ACTION_SET_ID"] if "ACTION_SET_ID" in csv_row else csv_row["ID"]

                # results.append({"ID": row["ID"], "Value": bit_value})
                decoded_action_set.action_set_id_with_value[action_set_id_str] = bit_value_bool

                if bit_value_str == "1":
                    # results.append(row["ID"])
                    action_set_id_str = csv_row["ACTION_SET_ID"] if "ACTION_SET_ID" in csv_row else csv_row["ID"]
                    decoded_action_set.action_set_id_with_value_true.append(action_set_id_str)

        # Check for any "1" in the bitfield that doesn't have a corresponding entry
        for index, bit in enumerate(bitfield):
            if bit == "1" and index not in decoded_bits:
                decoded_action_set.undecoded_bits_by_error.append(index)
                logger_config.print_and_log_error(f"Warning: Bit at position {index} is '1' but has no corresponding entry in the CSV.")

        return decoded_action_set


def decode_bitfield_returns_only_true(csv_file_file_path: str, bitfield: str) -> List[str]:
    action_set_decoder = ActionSetContentDecoder(csv_file_file_path)
    decoded_action_set = action_set_decoder.decode_actions_bitfield(bitfield)
    return decoded_action_set.action_set_id_with_value_true
