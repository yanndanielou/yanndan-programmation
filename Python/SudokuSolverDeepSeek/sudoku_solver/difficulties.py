from dataclasses import dataclass
import math


@dataclass
class GameSize:
    allowed_values_in_cells: list[str]
    _name: str  # Renommé en _name pour éviter les conflits

    def get_number_of_cells_per_region(self) -> int:
        return len(self.allowed_values_in_cells)

    def get_region_height(self) -> int:
        return math.isqrt(self.get_number_of_cells_per_region())

    def get_region_width(self) -> int:
        return self.get_region_height()

    @property
    def name(self) -> str:
        return self._name  # Retourne _name au lieu de name


@dataclass
class PuzzleDifficulty:
    _name: str
    _percentage_revealed_cells: int

    @property
    def name(self) -> str:
        return self._name

    @property
    def percentage_revealed_cells(self) -> int:
        return self._percentage_revealed_cells
