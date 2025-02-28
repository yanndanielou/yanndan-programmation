# -*-coding:Utf-8 -*
""" Main """

from dataclasses import dataclass, field
from typing import List, Tuple, Optional

from shutthebox.dices import Dices, Dice, DicesThrownCombinationsResults

from logger import logger_config

from common import json_encoders


@dataclass
class CompleteSimulation:

    _all_flat_games: list["OneFlatGame"] = field(default_factory=list)

    @property
    def all_flat_games(self) -> list["OneFlatGame"]:
        return self._all_flat_games

    def add_flat_games(self, flat_games_to_add: list["OneFlatGame"]) -> None:
        self._all_flat_games = self._all_flat_games + flat_games_to_add

    def dump_in_json_file(self, json_file_full_path: str) -> None:

        json_encoders.JsonEncodersUtils.serialize_list_objects_in_json(self._all_flat_games, json_file_full_path)

        """  print(
            f"{len(res_all_possibilities_with_hatches)} possibilities found: \n\n"
            + "\n\n".join([str(game) for game in res_all_possibilities_with_hatches])
        ) """
        # for game in all_possibilities_with_hatches:
        #    print(f"Game :\n {str(game)}")


@dataclass
class OneStandaloneTurn:
    dices_sum: int
    dices_sum_chances: int
    opened_hatches_before_turn: list[int]
    closed_hatches_during_turn: Optional[list[int]]
    previously_already_closed_hatches: list[int] = field(default_factory=list)

    def __str__(self) -> str:
        return f"Dices thrown, sum:{self.dices_sum}, opened_hatches_before_turn:{self.opened_hatches_before_turn}, closed_hatches_during_turns:{self.closed_hatches_during_turn}"


@dataclass
class OneFlatGame:
    turns: list[OneStandaloneTurn]
    final_opened_hatches: list[int]

    def __str__(self) -> str:
        return f"Final opened hatches: {self.final_opened_hatches} \n" + "\tTurns: \n\t\t" + "\n\t\t ".join([str(turn) for turn in self.turns])


@dataclass
class Application:
    """Close the box application"""

    _dices: list[Dice] = field(default_factory=lambda: [Dice(), Dice()])
    _initial_opened_hatches: list[int] = field(default_factory=lambda: list(range(1, 10)))
    _complete_simulation: CompleteSimulation = field(default_factory=lambda: CompleteSimulation())

    @property
    def dices(self) -> list[Dice]:
        return self._dices

    @property
    def initial_opened_hatches(self) -> list[int]:
        return self._initial_opened_hatches

    @property
    def complete_simulation(self) -> CompleteSimulation:
        return self._complete_simulation

    def run(self) -> None:
        """Run"""
        self.compute_all_possibilities_from_beginning()

    def compute_all_possibilities_from_beginning(self) -> list[OneFlatGame]:
        self._complete_simulation.add_flat_games(self.compute_all_possibilities_with_hatches(self._initial_opened_hatches))
        return self._complete_simulation.all_flat_games

    def play_dices_with_all_combinations_with_same_sum(
        self,
        dices_sum: int,
        dices_results: list[Tuple[int, ...]],
        opened_hatches: list[int],
        previous_turns: list[OneStandaloneTurn] | None = None,
    ) -> list[OneFlatGame]:
        if previous_turns is None:  # to avoid https://pylint.pycqa.org/en/latest/user_guide/messages/warning/dangerous-default-value.html
            previous_turns = []

        all_possibilities_with_hatches: list[OneFlatGame] = []

        for dices_results in dices_results:

            all_hatches_combinaisons = self.get_all_unique_combinaisons_to_reach_exaclty_sum_using_element_no_more_than_once(
                opened_hatches, dices_sum
            )

            if not all_hatches_combinaisons:

                current_turn_with_combination = OneStandaloneTurn(
                    dices_sum=dices_sum,
                    dices_sum_chances=0,
                    closed_hatches_during_turn=None,
                    opened_hatches_before_turn=opened_hatches.copy(),
                )
                all_possibilities_with_hatches += [
                    OneFlatGame(
                        final_opened_hatches=opened_hatches.copy(),
                        turns=previous_turns.copy() + [current_turn_with_combination],
                    )
                ]

            for hatches_combination in all_hatches_combinaisons:

                new_opened_hatches: list[int] = list(set(opened_hatches) - set(hatches_combination))
                current_turn_with_combination = OneStandaloneTurn(
                    dices_sum=dices_sum,
                    dices_sum_chances=0,
                    closed_hatches_during_turn=hatches_combination,
                    opened_hatches_before_turn=opened_hatches.copy(),
                )

                all_possibilities_with_hatches += self.compute_all_possibilities_with_hatches(
                    new_opened_hatches,
                    previous_turns + [current_turn_with_combination],
                )

        return all_possibilities_with_hatches

    def compute_all_possibilities_with_hatches(
        self, opened_hatches: list[int], previous_turns: list[OneStandaloneTurn] | None = None
    ) -> list[OneFlatGame]:

        if previous_turns is None:  # to avoid https://pylint.pycqa.org/en/latest/user_guide/messages/warning/dangerous-default-value.html
            previous_turns = []

        all_possibilities_with_hatches: list[OneFlatGame] = []

        dices_all_possible_thrown_combinations_results: DicesThrownCombinationsResults = Dices.get_dices_all_possible_thrown_combinations_results(
            self._dices
        )

        for dices_sum, dices_thrown_combinations_result in dices_all_possible_thrown_combinations_results.all_combinations_by_sum.items():
            for combination in dices_thrown_combinations_result.combinations:
                all_possibilities_with_hatches += self.play_dices_with_all_combinations_with_same_sum(
                    dices_sum, combination, opened_hatches, previous_turns
                )

        return all_possibilities_with_hatches + [OneFlatGame(final_opened_hatches=opened_hatches.copy(), turns=previous_turns.copy())]

    def get_all_unique_combinaisons_to_reach_exaclty_sum_using_element_no_more_than_once(
        self, elements: list[int], sum_to_attain: int
    ) -> list[list[int]]:

        def backtrack(reste: int, index: int, chemin: list) -> None:
            # Si la somme restante est atteinte, ajouter la combinaison
            if reste == 0:
                results.append(list(chemin))
                return
            # Si la somme restante est négative ou plus d'éléments, arrêter
            if reste < 0:
                return

            for i in range(index, len(elements)):
                # Ajouter le nombre actuel au chemin
                chemin.append(elements[i])
                # Appel récursif avec la somme restante mise à jour et index + 1 (pour éviter les répétitions)
                backtrack(reste - elements[i], i + 1, chemin)  # Réutiliser l'élément actuel (index = i)
                # Retirer l'élément ajouté (backtracking)
                chemin.pop()

        results: list[list[int]] = list()

        backtrack(sum_to_attain, 0, [])

        return results
