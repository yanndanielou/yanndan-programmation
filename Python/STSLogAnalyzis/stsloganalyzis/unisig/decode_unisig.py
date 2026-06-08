import binascii
import re
from typing import Dict, Tuple, Union, Optional

from common import bytes_messages

from dataclasses import dataclass


@dataclass
class DecodedFrame:
    time: int
    source: int
    target: int
    sequence: int
    mode: str
    length: int
    bytes_: str


def decode_frame(line: str) -> Optional[DecodedFrame]:

    fields = line.split(" ")
    if len(fields) <= 4:
        print(f"-> bad line format\n{line}")
        return False

    # Extract time: 1970-01-01 02:18:14:652
    time_value = fields[1]
    time_fields = time_value.split(":")
    time = int(time_fields[0]) * 3600 * 1000 + int(time_fields[1]) * 60 * 1000 + int(time_fields[2]) * 1000 + int(time_fields[3])

    print(f"Time: {time}")

    # Extract source and target: [99:37 <= 2:37]
    sap_pattern = re.compile(r"\[(\d+):(\d+) (<=|=>) (\d+):(\d+)\]")
    match = sap_pattern.search(line)
    if match:
        if match.group(3) == "=>":
            source = (int(match.group(1)) << 16) | int(match.group(2))
            target = (int(match.group(4)) << 16) | int(match.group(5))
        else:
            source = (int(match.group(4)) << 16) | int(match.group(5))
            target = (int(match.group(1)) << 16) | int(match.group(2))
    else:
        source = target = 0

    # Extract sequence: [num:43548]
    seq_pattern = re.compile(r"\[num:(\d+)\]")
    match = seq_pattern.search(line)
    if match:
        sequence = int(match.group(1))
    else:
        sequence = 0

    # Extract mode: [mode:SDA]
    mode_pattern = re.compile(r"\[mode:(SDN|SDA)\]")
    match = mode_pattern.search(line)
    if match:
        mode = match.group(1)
    else:
        mode = ""

    # Extract length: [len:51]
    len_pattern = re.compile(r"\[len:(\d+)\]")
    match = len_pattern.search(line)
    if match:
        length = int(match.group(1))
    else:
        length = 0

    # Extract trailing bytes
    bytes_ = line.split("]")[-1].strip()

    if mode in ("SDA", "SDN"):
        return DecodedFrame(time=time,source=source,target=target,sequence=sequence,mode=mode,length=length,bytes_=bytes_)
    else
        return None


class ETCSFrameDecoder:
    def __init__(self) -> None:
        # Initialisation des spécifications des champs (en octets)
        self.field_definitions = {
            "NID_MESSAGE": {"start": 0, "length": 1, "description": "Identifiant du message"},
            "L_MESSAGE": {"start": 1, "length": 2, "description": "Longueur du message"},
            "T_TRAIN": {"start": 3, "length": 4, "description": "Horodatage du train"},
            "M_ACK": {"start": 7, "length": 1, "description": "Confirmation attendue"},
            # Ajouter d'autres champs ici en fonction des spécifications des Subsets
        }

    def decode(self, hex_string: str) -> Dict[str, str | int]:
        # Supprime les espaces et autres caractères inutiles
        hex_string = hex_string.replace(" ", "")

        # Convertit la trame hexadécimale en un tableau d'octets
        try:
            byte_data = binascii.unhexlify(hex_string)
        except binascii.Error:
            raise ValueError("La trame donnée contient des caractères non valides.")

        decoded_fields = {}

        # Décode chaque champ selon les spécifications
        for field, specs in self.field_definitions.items():
            start = specs["start"]
            length = specs["length"]
            assert isinstance(start, int)
            assert isinstance(length, int)
            end = start + length
            if end > len(byte_data):
                raise ValueError(f"Champ {field} dépasse la longueur de la trame.")

            # On extrait les octets du champ
            field_value = byte_data[start:end]

            # Convertit en entier si nécessaire
            if length == 1:
                decoded_value = field_value[0]
            else:
                # Entiers multioctets (big-endian par défaut)
                decoded_value = int.from_bytes(field_value, byteorder="big")

            decoded_fields[field] = {
                "description": specs["description"],
                "value_bytes_str": extract_bits_to_bytes(data=byte_data, start_bit=start, bit_length=length),
                "value_int": decoded_value,
            }

        return decoded_fields


# Exemple d'utilisation
if __name__ == "__main__":

    line = "2026-06-02 17:38:09:961 kppn 1.3.3: [99:33 <= 2:33] Received PROFIBUS message [num:169690][mode:SDA][len:28] 1e 85 01 05 49 64 6c 65 20 63 79 63 6c 65 20 74 69 6d 65 6f 75 74 bc 0b 17 6d 17 78"

    decoded_frame = decode_frame(line)

    print(f"Valid frame: {decoded_frame is not None}")
    if decoded_frame:
        # Affichage des résultats
        print(f"Time: {decoded_frame.time}")
        print(f"Source: {decoded_frame.source}")
        print(f"Target: {decoded_frame.target}")
        print(f"Sequence: {decoded_frame.sequence}")
        print(f"Mode: {decoded_frame.mode}")
        print(f"Length: {decoded_frame.length}")
        print(f"Bytes: {decoded_frame.bytes_}")
    # Trame d'exemple donnée par l'utilisateur
    hex_frame = "2a 85 01 05 49 64 6c 65 20 63 79 63 6c 65 20 74 69 6d 65 6f 75 74 1e ab fe d1 92 5e"

    byte_message_decoded = bytes_messages.DecodedBytesMessage(hex_frame)
    nid_message = byte_message_decoded.get_next_bits_as_single_int_signed_and_unsigned(size_bits=8)[1]
    l_message = byte_message_decoded.get_next_bits_as_single_int_signed_and_unsigned(size_bits=8)[1]
    pass

    decoder = ETCSFrameDecoder()
    try:
        decoded_message = decoder.decode(hex_frame)
        print("Trame décodée :")
        for field, details in decoded_message.items():
            print(f"{field} ({details['description']}): {details['value_int']} : {details['value_bytes_str']}")
    except ValueError as e:
        print(f"Erreur : {e}")
