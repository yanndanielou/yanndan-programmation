# -*-coding:Utf-8 -*

import pytest

import os
import sys


from typing import List, Tuple

from shutthebox import dices


class TestCombinationsUsingDiceClass:

    class TestThreeSidesDices:
        class TestOneThreeSideDice:
            def test_all_combinations_with_occurrences(self) -> None:
                one_dice = [dices.Dice(_sides_values=[1, 2, 3])]
                all_combinations = dices.Dices.get_dices_all_combinations(one_dice)
                assert len(all_combinations) == 3

    class TestStandardDices:

        class TestOneStandardDices:

            def test_all_combinations_with_occurrences(self) -> None:
                one_dice = [dices.Dice()]
                all_combinations = dices.Dices.get_dices_all_combinations(one_dice)
                assert len(all_combinations) == 6

        class TestTwoStandardDices:

            def test_all_combinations_with_occurrences(self) -> None:
                all_dices = [dices.Dice(), dices.Dice()]
                all_combinations = dices.Dices.get_dices_all_combinations(all_dices)
                assert len(all_combinations) == 36


class TestCombinations:
    """TestApplicationWithoutHmi"""

    class TestTwoDices:

        def test_get_two_dices_all_combinaisons_with_occurences(self) -> None:
            """Number of results"""
            two_dices_all_combinaisons_with_occurences: dict[
                int, list[Tuple[int, int]]
            ] = dices.Dices.get_two_dices_all_combinations_by_sum()

            # assert two_dices_all_combinaisons_with_occurences[1] is None
            assert two_dices_all_combinaisons_with_occurences[2] == [(1, 1)]
            assert len(two_dices_all_combinaisons_with_occurences[2]) == 1
            assert len(two_dices_all_combinaisons_with_occurences[3]) == 2
            assert two_dices_all_combinaisons_with_occurences[12] == [(6, 6)]
            assert len(two_dices_all_combinaisons_with_occurences) == 11

    class TestThreeDices:
        number_of_dices = 3

        def test_get_several_dices_all_combinaisons_by_sum(self) -> None:
            """Number of results"""
            dices_all_combinaisons_with_occurences: dict[int, list[Tuple[int, ...]]] = (
                dices.Dices.get_several_dices_all_combinations_by_sum(
                    self.number_of_dices
                )
            )

            # assert two_dices_all_combinaisons_with_occurences[1] is None
            # assert two_dices_all_combinaisons_with_occurences[2] is None
            assert len(dices_all_combinaisons_with_occurences[3]) == 1
            assert dices_all_combinaisons_with_occurences[3] == [(1, 1, 1)]
