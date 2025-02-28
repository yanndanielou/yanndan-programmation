# -*-coding:Utf-8 -*
# import pytest

from shutthebox import application
from shutthebox.dices import Dice


class TestSimpleSimulations:

    class TestOneDiceAnd6Hatches:

        def test_last_step(self) -> None:
            dices: list[Dice] = [Dice()]
            initial_opened_hatches: list[int] = list(range(1, 7))

            application_test = application.Application(_dices=dices, _initial_opened_hatches=initial_opened_hatches)
            application_test.run()
            complete_simulation = application_test.complete_simulation
            all_flat_games = complete_simulation.all_flat_games
            complete_simulation.dump_in_json_file("TestOneDiceAnd6Hatches.json")

            # assert len(all_flat_games) == 15


class TestOneStep:

    checker: application.Application = application.Application()

    def test_last_step(self) -> None:
        all_possibilities_with_hatches: list[application.OneFlatGame] = self.checker.compute_all_possibilities_with_hatches([1, 2, 3])
        assert all_possibilities_with_hatches is not None


class TestUniqueccombinaisonsToReachExacltySumUsingElementNoMoreThanOnce:
    """TestApplicationWithoutHmi"""

    checker: application.Application = application.Application()

    def test_impossible(self) -> None:
        assert not self.checker.get_all_unique_combinaisons_to_reach_exaclty_sum_using_element_no_more_than_once([1], 12)
        assert not self.checker.get_all_unique_combinaisons_to_reach_exaclty_sum_using_element_no_more_than_once([1, 2, 3], 7)
        assert not self.checker.get_all_unique_combinaisons_to_reach_exaclty_sum_using_element_no_more_than_once([1, 5, 7], 4)

    def test_chatgpt(self) -> None:
        liste = [2, 3, 5, 7]
        somme_a_atteindre = 7
        assert self.checker.get_all_unique_combinaisons_to_reach_exaclty_sum_using_element_no_more_than_once(liste, somme_a_atteindre) == [
            [2, 5],
            [7],
        ]

    def test_simple(self) -> None:
        assert self.checker.get_all_unique_combinaisons_to_reach_exaclty_sum_using_element_no_more_than_once([1], 1) == [[1]]
        assert self.checker.get_all_unique_combinaisons_to_reach_exaclty_sum_using_element_no_more_than_once([1, 2, 3], 2) == [[2]]


class TestApplicationMisc:
    """TestApplicationWithoutHmi"""

    checker: application.Application = application.Application()

    def test_get_all_unique_combinaisons_to_attains_exaclty_sum_using_element_no_more_than_once(self) -> None:
        assert self.checker.get_all_unique_combinaisons_to_reach_exaclty_sum_using_element_no_more_than_once([1, 2, 3], 2) == [[2]]
