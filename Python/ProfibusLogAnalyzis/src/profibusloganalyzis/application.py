# -*-coding:Utf-8 -*
""" Main """

from dataclasses import dataclass, field
from typing import List, Optional  # , TYPE_CHECKING

from logger import logger_config

from shutthebox.dices import Dices, Dice, DicesThrownCombinationsResults
from shutthebox.combinations_to_reach_sum import CombinationsToReachSum
from shutthebox import param

# if TYPE_CHECKING:
#    from shutthebox.dices import DicesThrownCombinationsOfOneSum


class CompleteSimulationResult:

    def __init__(self, initial_situation: "Situation") -> None:
        self._all_games: list["OneGame"] = []
        self._initial_situation = initial_situation

    @property
    def all_games(self) -> list["OneGame"]:
        return self._all_games

    @property
    def initial_situation(self) -> "Situation":
        return self._initial_situation

    def add_game(self, flat_game_to_add: "OneGame") -> None:
        self._all_games.append(flat_game_to_add)
        if len(self._all_games) % 1000 == 0:
            logger_config.print_and_log_info(f"Games computed so far:{len(self._all_games)}")


@dataclass
class CloseHatchesAction:
    _dices_result_step: "DicesResultStep"
    _hatches_closed_during_action: list[int]
    _next_situations: list["Situation"] = field(default_factory=list)

    def add_next_situation(self, next_situation: "Situation") -> None:
        self._next_situations.append(next_situation)

    @property
    def hatches_closed_during_action(self) -> List[int]:
        return self._hatches_closed_during_action

    @property
    def next_situations(self) -> List["Situation"]:
        return self._next_situations

    @property
    def dices_result_step(self) -> "DicesResultStep":
        return self._dices_result_step

    def get_ratio_among_all_alternatives(self) -> float:
        return 1 / len(self._dices_result_step.next_close_hatches_actions)


@dataclass
class Situation:
    _opened_hatches: list[int]
    _next_dices_result_steps: List["DicesResultStep"] = field(default_factory=list)
    _previous_close_hatches_action: Optional[CloseHatchesAction] = None

    def add_next_dices_result_step(self, new_dices_result_step: "DicesResultStep") -> None:
        self._next_dices_result_steps.append(new_dices_result_step)

    @property
    def next_dices_result_steps(self) -> List["DicesResultStep"]:
        return self._next_dices_result_steps

    @property
    def opened_hatches(self) -> List[int]:
        return self._opened_hatches

    def get_previous_situation(self) -> Optional["Situation"]:
        previous_action = self._previous_close_hatches_action
        if previous_action is None:
            return None
        else:
            return previous_action.dices_result_step.previous_situation

    def get_initial_situation(self) -> "Situation":
        previous_situation = self.get_previous_situation()
        if previous_situation is None:
            return self
        return previous_situation.get_initial_situation()

    def get_odds_to_happen_from_initial_situation_taking_into_account_dices_and_hatches(self) -> float:
        initial_situation = self.get_initial_situation()
        if initial_situation == self:
            return 1.0
        return self.get_odds_to_happen_from_reference_situation_taking_into_account_dices_and_hatches(initial_situation)

    def get_odds_to_happen_from_reference_situation_taking_into_account_dices_and_hatches(self, reference_situation: "Situation") -> float:

        previous_action = self._previous_close_hatches_action

        previous_action_ratio_among_alternatives = previous_action.get_ratio_among_all_alternatives()

        # Probability of reaching this situation from the previous action
        probability_to_get_dice_roll = previous_action.dices_result_step.dices_sum_odds
        previous_situation = self._previous_close_hatches_action.dices_result_step.previous_situation

        if previous_situation == reference_situation:
            return probability_to_get_dice_roll * previous_action_ratio_among_alternatives

        probability_to_reach_previous_situation = previous_situation.get_odds_to_happen_from_reference_situation_taking_into_account_dices_and_hatches(reference_situation)

        return probability_to_get_dice_roll * previous_action_ratio_among_alternatives * probability_to_reach_previous_situation


@dataclass
class DicesResultStep:
    _previous_situation: Situation
    _dices_sum: int
    _dices_sum_odds: float
    _next_close_hatches_actions: list["CloseHatchesAction"] = field(default_factory=list)

    def add_next_close_hatches_action(self, next_close_hatches_action: "CloseHatchesAction") -> None:
        self._next_close_hatches_actions.append(next_close_hatches_action)

    @property
    def dices_sum(self) -> int:
        return self._dices_sum

    @property
    def dices_sum_odds(self) -> float:
        return self._dices_sum_odds

    @property
    def previous_situation(self) -> Situation:
        return self._previous_situation

    @property
    def next_close_hatches_actions(self) -> list["CloseHatchesAction"]:
        return self._next_close_hatches_actions


@dataclass
class OneGame:
    _final_situation: Situation

    @property
    def final_situation(self) -> Situation:
        return self._final_situation


@dataclass
class SimulationRequest:
    _dices: list[Dice] = field(default_factory=lambda: [Dice(), Dice()])
    _initial_opened_hatches: list[int] = field(default_factory=lambda: param.DEFAULT_INITIAL_OPENED_HATCHES)

    @property
    def dices(self) -> list[Dice]:
        return self._dices

    @property
    def initial_opened_hatches(self) -> list[int]:
        return self._initial_opened_hatches


class Simulation:

    def __init__(self, simulation_request: SimulationRequest) -> None:
        self._simulation_request: SimulationRequest = simulation_request
        self._initial_situation = Situation(simulation_request.initial_opened_hatches)
        self._complete_simulation_result: CompleteSimulationResult = CompleteSimulationResult(self._initial_situation)

    def _create_new_game(self, final_situation: Situation) -> OneGame:
        new_game = OneGame(final_situation)
        self._complete_simulation_result.add_game(new_game)
        return new_game

    @property
    def simulation_request(self) -> SimulationRequest:
        return self._simulation_request

    @property
    def complete_simulation_result(self) -> CompleteSimulationResult:
        return self._complete_simulation_result

    def start(self) -> None:
        self.play_situation(self._initial_situation)

    def play_situation(self, previous_situation: Situation) -> None:
        self.throw_dices(previous_situation)

    def _create_close_hatches_action_and_situation(self, dices_result_step: DicesResultStep, hatches_closed_during_action: list[int], new_opened_hatches: list[int]) -> Situation:
        close_hatches_action = CloseHatchesAction(_dices_result_step=dices_result_step, _hatches_closed_during_action=hatches_closed_during_action)
        dices_result_step.add_next_close_hatches_action(close_hatches_action)
        new_situation = Situation(_opened_hatches=new_opened_hatches, _previous_close_hatches_action=close_hatches_action)
        close_hatches_action.add_next_situation(new_situation)
        return new_situation

    def throw_dices(self, previous_situation: Situation) -> None:
        # logger_config.print_and_log_info(f"throw_dices, opened_hatches:{opened_hatches}")

        dices_all_possible_thrown_combinations_results: DicesThrownCombinationsResults = Dices.get_dices_all_possible_thrown_combinations_results(self._simulation_request.dices)

        for combinations_grouped_by_sum in dices_all_possible_thrown_combinations_results.all_combinations_grouped_by_sum:
            dices_sum_odds = combinations_grouped_by_sum.get_odds()
            dices_result_step = DicesResultStep(_dices_sum=combinations_grouped_by_sum.sum, _dices_sum_odds=dices_sum_odds, _previous_situation=previous_situation)
            previous_situation.add_next_dices_result_step(dices_result_step)

            self.play_dices_result_step(dices_result_step, previous_situation.opened_hatches)

    def play_dices_result_step(self, dices_result_step: DicesResultStep, opened_hatches_before_step: list[int]) -> None:

        # logger_config.print_and_log_info(f"play_dices_result_step, dices_result_step:{dices_result_step}, opened_hatches:{opened_hatches_before_step}, previous_turn:{previous_turn}")

        all_hatches_combinations = CombinationsToReachSum.get_all_unique_combinations_to_reach_exactly_sum_using_element_no_more_than_once(
            elements=opened_hatches_before_step, sum_to_reach=dices_result_step.dices_sum
        )

        if not all_hatches_combinations:
            # logger_config.print_and_log_info(f"Game is lost, no possible hatch combination to reach {dices_result_step.dices_sum} from {opened_hatches_before_step}")
            new_situation: Situation = self._create_close_hatches_action_and_situation(
                dices_result_step=dices_result_step, hatches_closed_during_action=[], new_opened_hatches=opened_hatches_before_step
            )
            self._create_new_game(new_situation)

        for hatches_combination in all_hatches_combinations:

            new_opened_hatches: list[int] = list(set(opened_hatches_before_step) - set(hatches_combination))
            # logger_config.print_and_log_info(f"hatches_combination {hatches_combination}, new_opened_hatches:{new_opened_hatches}")

            new_situation: Situation = self._create_close_hatches_action_and_situation(
                dices_result_step=dices_result_step, hatches_closed_during_action=hatches_combination, new_opened_hatches=new_opened_hatches
            )

            if not new_opened_hatches:
                # logger_config.print_and_log_info("Game is won, all hatches closed")
                self._create_new_game(new_situation)

            else:
                self.play_situation(new_situation)


@dataclass
class Application:
    """Close the box application"""

    def run(self, simulation_request: SimulationRequest = SimulationRequest()) -> Simulation:
        """Run"""
        simulation = Simulation(simulation_request)
        logger_config.print_and_log_info("Run")
        simulation.start()
        logger_config.print_and_log_info(f"Simulation ended. Games computer {len(simulation.complete_simulation_result.all_games)}")

        return simulation
