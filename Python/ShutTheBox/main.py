# -*-coding:Utf-8 -*
""" Main """
import tkinter as tk
from tkinter import ttk

from logger import logger_config

import logging

from shutthebox.application import Application, SimulationRequest
from shutthebox.dices import Dice
from shutthebox.gui import TreeViewApp


def main() -> None:
    """Main function"""

    with logger_config.stopwatch_with_label("Application duration"):
        logger_config.configure_logger_with_random_log_file_suffix("CloseTheBox", log_file_extension="log", logger_level=logging.DEBUG)

        # simulation_request = SimulationRequest([Dice(list(range(1, 6)))], list(range(1, 7)))
        # simulation_request = SimulationRequest([Dice(list(range(1, 5)))], list(range(1, 4)))

        simulation = Application().run(SimulationRequest([Dice()], list(range(1, 7))))
        # simulation = Application().run()

        root = tk.Tk()
        app = TreeViewApp(root, simulation.complete_simulation_result)
        root.mainloop()

        logger_config.print_and_log_info("End. Nominal end of application")


if __name__ == "__main__":
    # sys.argv[1:]
    main()
