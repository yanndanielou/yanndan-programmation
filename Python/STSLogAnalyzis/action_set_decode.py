from typing import List, Dict
import csv


def decode_bitfield_returns_each_field_and_value(csv_file_file_path: str, bitfield: str) -> List[Dict[str, str]]:
    results: List[Dict[str, str]] = []
    decoded_bits = set()

    # Read the CSV file
    with open(csv_file_file_path, mode="r", encoding="utf-8") as file:
        csv_reader = csv.DictReader(file, delimiter=";")

        # Iterate through each row in the CSV
        for csv_row in csv_reader:
            num_ats_str = csv_row["NUM_ACTION_SET_ATS"] if "NUM_ACTION_SET_ATS" in csv_row else csv_row["NUM_ATS"]
            num_ats = int(num_ats_str)
            decoded_bits.add(num_ats)  # Track decoded bits
            bit_value = bitfield[num_ats]

            action_set_id_str = csv_row["ACTION_SET_ID"] if "ACTION_SET_ID" in csv_row else csv_row["ID"]
            # results.append({"ID": row["ID"], "Value": bit_value})
            results.append({"ID": action_set_id_str, "Value": bit_value})

    # Check for any "1" in the bitfield that doesn't have a corresponding entry
    for index, bit in enumerate(bitfield):
        if bit == "1" and index not in decoded_bits:
            print(f"Warning: Bit at position {index} is '1' but has no corresponding entry in the CSV.")

    return results


def decode_bitfield_returns_only_true(csv_file_file_path: str, bitfield: str) -> List[str]:
    results: List[str] = []
    decoded_bits = set()

    # Read the CSV file
    with open(csv_file_file_path, mode="r", encoding="utf-8") as file:
        csv_reader = csv.DictReader(file, delimiter=";")

        # Iterate through each row in the CSV
        for csv_row in csv_reader:

            num_ats_str = csv_row["NUM_ACTION_SET_ATS"] if "NUM_ACTION_SET_ATS" in csv_row else csv_row["NUM_ATS"]
            num_ats = int(num_ats_str)
            # num_ats = int(row["NUM_ATS"])
            decoded_bits.add(num_ats)  # Track decoded bits
            bit_value = bitfield[num_ats]

            if bit_value == "1":
                # results.append(row["ID"])
                action_set_id_str = csv_row["ACTION_SET_ID"] if "ACTION_SET_ID" in csv_row else csv_row["ID"]
                results.append(action_set_id_str)

    # Check for any "1" in the bitfield that doesn't have a corresponding entry
    for index, bit in enumerate(bitfield):
        if bit == "1" and index not in decoded_bits:
            print(f"Warning: Bit at position {index} is '1' but has no corresponding entry in the CSV.")

    return results


# Example usage
CSV_FILE_PATH = "input/ACTION_SET_NEXT_INV_V6_06_BLD.csv"

actions_next_syst_2025_07_11t18h17mn34s = "010010010000010010010010010010010010010010010010010010010010010010010001000100010000001011011000001001000100010010000100010001001000010010001000010001000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000010100101011111111010111101110000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"  # pylint: disable=line-too-long

decoded_results1 = decode_bitfield_returns_each_field_and_value(CSV_FILE_PATH, actions_next_syst_2025_07_11t18h17mn34s)
decoded_results2 = decode_bitfield_returns_only_true(CSV_FILE_PATH, actions_next_syst_2025_07_11t18h17mn34s)
print("\n")

for tru_field in decoded_results2:
    print(tru_field)
pass  # pylint: disable=unnecessary-pass
