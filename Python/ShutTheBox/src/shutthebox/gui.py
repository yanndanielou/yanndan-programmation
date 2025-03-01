import tkinter as tk
from tkinter import ttk

from typing import TYPE_CHECKING, List

from logger import logger_config

if TYPE_CHECKING:
    from shutthebox.application import InitialSituation, OneTurn


class TreeViewApp:
    def __init__(self, root: tk.Tk, initial_situation: "InitialSituation") -> None:
        self.root = root
        self.root.title("Tree View Representation")

        self.tree = ttk.Treeview(root)
        self.tree.pack(expand=True, fill=tk.BOTH)

        # Adding column
        self.tree.heading("#0", text="Game Turns")

        # Populate tree
        self.populate_tree(f"Initial Situation: Opened Hatches={initial_situation._initial_opened_hatches}", initial_situation.next_turns)

    def populate_tree(self, parent_name: str, turns: List["OneTurn"], parent_id: str = "") -> None:
        """Recursively add turns to the tree"""
        parent_node = self.tree.insert(parent_id, "end", text=parent_name)

        for i, turn in enumerate(turns):
            dices_step_text = f"Dices: Sum={turn._dices_result_action.dices_sum}, Odds={turn._dices_result_action._dices_sum_odds * 100:.2f}%"
            dices_step_node = self.tree.insert(parent_node, "end", text=dices_step_text)

            close_hatches_text = f"Close Hatches: Opened={turn._close_hatches_action._opened_hatches_before_turn}, Closed={turn._close_hatches_action._closed_hatches_during_turn}"
            close_hatches_node = self.tree.insert(dices_step_node, "end", text=close_hatches_text)

            # Recursively add next turns
            self.populate_tree(close_hatches_text, turn.next_turns, close_hatches_node)
