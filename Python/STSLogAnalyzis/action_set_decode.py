from typing import List, Dict
import csv


def decode_bitfield_returns_each_field_and_value(csv_file_file_path: str, bitfield: str) -> List[Dict[str, str]]:
    results: List[Dict[str, str]] = []

    # Read the CSV file
    with open(csv_file_file_path, mode="r") as file:
        csv_reader = csv.DictReader(file, delimiter=";")

        # Iterate through each row in the CSV
        for row in csv_reader:
            num_ats = int(row["NUM_ATS"])
            bit_value = bitfield[num_ats]

            results.append({"ID": row["ID"], "Value": bit_value})

    return results


def decode_bitfield_returns_only_true(csv_file_file_path: str, bitfield: str) -> List[str]:
    results: List[str] = []

    # Read the CSV file
    with open(csv_file_file_path, mode="r") as file:
        csv_reader = csv.DictReader(file, delimiter=";")

        # Iterate through each row in the CSV
        for row in csv_reader:
            num_ats = int(row["NUM_ATS"])
            bit_value = bitfield[num_ats]

            if bit_value == "1":
                results.append(row["ID"])

    return results


# Example usage
csv_file_path = "input/NEXT_tsActionSet.csv"
bitfield_string = "010010010000010010010010010010010010010010010010010010010010010010010001000100010000001011011000001001000100010010000100010001001000010010001000010001000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000010100101011111111010111101110000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"

decoded_results = decode_bitfield_returns_each_field_and_value(csv_file_path, bitfield_string)
decoded_results = decode_bitfield_returns_only_true(csv_file_path, bitfield_string)
print(decoded_results)
