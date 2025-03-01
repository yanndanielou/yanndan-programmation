# -*-coding:Utf-8 -*
# import pytest

from shutthebox import combinations_to_reach_sum


class TestUniqueCombinaTionsToReachSum:
    """TestApplicationWithoutHmi"""

    def test_impossible(self) -> None:
        assert not combinations_to_reach_sum.CombinationsToReachSum.get_all_unique_combinations_to_reach_exactly_sum_using_element_no_more_than_once([1], 12)
        assert not combinations_to_reach_sum.CombinationsToReachSum.get_all_unique_combinations_to_reach_exactly_sum_using_element_no_more_than_once([1, 2, 3], 7)
        assert not combinations_to_reach_sum.CombinationsToReachSum.get_all_unique_combinations_to_reach_exactly_sum_using_element_no_more_than_once([1, 5, 7], 4)

    def test_chatgpt(self) -> None:
        liste = [2, 3, 5, 7]
        somme_a_atteindre = 7
        assert combinations_to_reach_sum.CombinationsToReachSum.get_all_unique_combinations_to_reach_exactly_sum_using_element_no_more_than_once(liste, somme_a_atteindre) == [
            [2, 5],
            [7],
        ]

    def test_simple(self) -> None:
        assert combinations_to_reach_sum.CombinationsToReachSum.get_all_unique_combinations_to_reach_exactly_sum_using_element_no_more_than_once([1], 1) == [[1]]
        assert combinations_to_reach_sum.CombinationsToReachSum.get_all_unique_combinations_to_reach_exactly_sum_using_element_no_more_than_once([1, 2, 3], 2) == [[2]]


class TestApplicationMisc:
    """TestApplicationWithoutHmi"""

    def test_get_all_unique_combinaisons_to_attains_exaclty_sum_using_element_no_more_than_once(self) -> None:
        assert combinations_to_reach_sum.CombinationsToReachSum.get_all_unique_combinations_to_reach_exactly_sum_using_element_no_more_than_once([1, 2, 3], 2) == [[2]]
