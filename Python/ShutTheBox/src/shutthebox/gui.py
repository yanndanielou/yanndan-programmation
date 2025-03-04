import tkinter as tk
from tkinter import ttk

from typing import TYPE_CHECKING, List

from logger import logger_config

if TYPE_CHECKING:
    from shutthebox.application import Situation, OneTurn, CompleteSimulationResult, Situation


class TreeViewApp:
    def __init__(self, root: tk.Tk, simulation_result: CompleteSimulationResult) -> None:
        self.root = root
        self.root.title("Simulation Result Viewer")

        self.tree = ttk.Treeview(root)
        self.tree.pack(expand=True, fill=tk.BOTH)

        self.tree.heading("#0", text="Simulation Structure", anchor=tk.W)

        self.populate_tree(simulation_result.initial_situation)

    def populate_tree(self, situation: "Situation", parent: str = "") -> None:
        """Recursively populates the tree view"""
        situation_id = self.tree.insert(parent, "end", text=f"Situation: Opened Hatches {situation.opened_hatches}")

        for dice_step in situation.next_dices_result_steps:
            dice_id = self.tree.insert(situation_id, "end", text=f"DicesResultStep: Sum {dice_step.dices_sum}")

            for close_action in dice_step.next_close_hatches_actions:
                action_text = f"CloseHatchesAction: Closed Hatches {close_action.hatches_closed_during_action}"
                action_id = self.tree.insert(dice_id, "end", text=action_text)

                for next_situation in close_action._next_situations:
                    self.populate_tree(next_situation, action_id)
