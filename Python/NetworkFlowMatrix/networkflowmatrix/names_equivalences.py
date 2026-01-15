from typing import Dict


class NamesEquivalences:
    def __init__(self, names_equivalences_data: Dict[str, str]) -> None:
        self.names_equivalences_data = names_equivalences_data
        # self.reversed = {v: k for k, v in names_equivalences_data.items()}
