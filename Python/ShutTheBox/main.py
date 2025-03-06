# -*-coding:Utf-8 -*
""" Main """
import tkinter as tk
from tkinter import ttk

from logger import logger_config

import logging

from shutthebox.application import Application, SimulationRequest
from shutthebox.dices import Dice
from shutthebox.gui import TreeViewApp

import numpy


def main() -> None:
    """Main function"""

    with logger_config.stopwatch_with_label("Application duration"):
        logger_config.configure_logger_with_random_log_file_suffix("CloseTheBox", log_file_extension="log", logger_level=logging.DEBUG)

        # simulation_request = SimulationRequest([Dice(list(range(1, 6)))], list(range(1, 7)))
        # simulation_request = SimulationRequest([Dice(list(range(1, 5)))], list(range(1, 4)))

        # simulation = Application().run(SimulationRequest([Dice()], list(range(1, 7))))

        # simulation = Application().run(SimulationRequest([Dice(range(1, 3))], list(range(1, 4))))
        simulation = Application().run(SimulationRequest([Dice(range(1, 3))], [1, 1, 2]))
        # simulation = Application().run()
        simulation_result = simulation.complete_simulation_result
        all_flat_games = simulation_result.all_games
        all_flat_games_odds = [game.final_situation.get_odds_to_happen_from_initial_situation_taking_into_account_dices_and_hatches() for game in all_flat_games]
        print(all_flat_games_odds)

        all_flat_games_odds_str = [f"{game.final_situation.get_odds_to_happen_from_initial_situation_taking_into_account_dices_and_hatches()*100:.1f}" for game in all_flat_games]
        print(all_flat_games_odds_str)

        final_games_cumulated_odds = sum(game.final_situation.get_odds_to_happen_from_initial_situation_taking_into_account_dices_and_hatches() for game in all_flat_games)
        print(final_games_cumulated_odds)

        root = tk.Tk()
        app = TreeViewApp(root, simulation.complete_simulation_result)
        root.mainloop()

        logger_config.print_and_log_info("End. Nominal end of application")


if __name__ == "__main__":
    # sys.argv[1:]
    main()
