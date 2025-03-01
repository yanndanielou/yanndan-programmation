# -*-coding:Utf-8 -*
""" Class that handles dices """

from dataclasses import dataclass, field
from typing import List, Tuple, cast, Dict
import itertools


# from common import singleton


@dataclass
class Dice:
    _sides_values: list[int] = field(default_factory=lambda: list(range(1, 7)))

    @property
    def sides_values(self) -> list[int]:
        return self._sides_values


@dataclass
class DicesThrownCombinationsOfOneSum:
    _sum: int
    _total_number_of_combinations_with_all_sums: int
    _combinations: list[list[int]] = field(default_factory=list)

    def add_combination(self, combination: Tuple[int, ...]) -> None:
        self._combinations.append(list(combination))

    def get_odds(self) -> float:
        return len(self._combinations) / self._total_number_of_combinations_with_all_sums

    @property
    def combinations(self) -> list[list[int]]:
        return self._combinations

    @property
    def sum(self) -> int:
        return self._sum


class DicesThrownCombinationsResults:

    def __init__(self, dices: list[Dice]):
        self._number_of_dices: int = len(dices)
        self._all_raw_combinations: List[Tuple[int, ...]] = Dices.get_dices_all_combinations(dices=dices)

        self._all_combinations_by_sum: dict[int, DicesThrownCombinationsOfOneSum] = dict()
        self._all_combinations_grouped_by_sum: list[DicesThrownCombinationsOfOneSum] = list()

        for combination in self._all_raw_combinations:
            sum_dices: int = sum(combination)

            if sum_dices not in self._all_combinations_by_sum:
                dices_thrown_combinations_of_one_sum = DicesThrownCombinationsOfOneSum(
                    _sum=sum_dices,
                    _total_number_of_combinations_with_all_sums=len(self._all_raw_combinations),
                )

                self._all_combinations_grouped_by_sum.append(dices_thrown_combinations_of_one_sum)
                self._all_combinations_by_sum[sum_dices] = dices_thrown_combinations_of_one_sum

            self._all_combinations_by_sum[sum_dices].add_combination(combination)

    @property
    def all_raw_combinations(self) -> List[Tuple[int, ...]]:
        return self._all_raw_combinations

    @property
    def all_combinations_by_sum(self) -> dict[int, DicesThrownCombinationsOfOneSum]:
        return self._all_combinations_by_sum

    @property
    def all_combinations_grouped_by_sum(self) -> list[DicesThrownCombinationsOfOneSum]:
        return self._all_combinations_grouped_by_sum


# class Dices(metaclass=singleton.Singleton):
class Dices:
    """Dices"""

    @staticmethod
    def get_dices_all_possible_thrown_combinations_results(dices: list[Dice]) -> DicesThrownCombinationsResults:
        dices_thrown_combinations_results = DicesThrownCombinationsResults(dices)
        return dices_thrown_combinations_results

    @staticmethod
    def get_two_dices_all_combinations_by_sum() -> dict[int, list[Tuple[int, int]]]:
        return cast(
            Dict[int, List[Tuple[int, int]]],
            Dices.get_several_dices_all_combinations_by_sum(2),
        )

    @staticmethod
    def get_several_dices_all_combinations_by_sum(
        number_of_dices: int,
    ) -> dict[int, list[Tuple[int, ...]]]:
        several_dices_all_combinations = Dices.get_several_standard_dices_all_combinations(number_of_dices=number_of_dices)
        all_combinations_by_sum: dict[int, list[Tuple[int, ...]]] = dict()

        for combination in several_dices_all_combinations:
            sum_dices: int = sum(combination)

            if sum_dices in all_combinations_by_sum:
                all_combinations_by_sum[sum_dices] += [combination]

            else:
                all_combinations_by_sum[sum_dices] = [combination]

        return all_combinations_by_sum

    @staticmethod
    def get_several_standard_dices_all_combinations(
        number_of_dices: int,
    ) -> List[Tuple[int, ...]]:
        one_dice_combinations = list(range(1, 7))

        all_combinations: List[Tuple[int, ...]] = list(itertools.product(one_dice_combinations, repeat=number_of_dices))

        return all_combinations

    @staticmethod
    def get_dices_all_combinations(dices: list[Dice]) -> List[Tuple[int, ...]]:
        """
        Calculates all possible combinations of the given list of Dice.

        Args:
            dices (list[Dice]): A list of Dice objects.

        Returns:
            list[tuple[int, ...]]: A list of tuples, where each tuple represents a combination of the dice rolls.
        """
        side_values = [dice.sides_values for dice in dices]
        return list(map(tuple, itertools.product(*side_values)))
