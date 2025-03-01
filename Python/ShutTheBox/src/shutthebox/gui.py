import tkinter as tk
from tkinter import ttk

from typing import TYPE_CHECKING, List

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
        self.populate_tree("Initial Situation", initial_situation.next_turns)

    def populate_tree(self, parent_name: str, turns: List["OneTurn"], parent_id: str = "") -> None:
        """Recursively add turns to the tree"""
        parent_node = self.tree.insert(parent_id, "end", text=parent_name)

        for i, turn in enumerate(turns):
            turn_name = f"Turn {i + 1}"
            turn_node = self.tree.insert(parent_node, "end", text=turn_name)

            # Recursively add next turns
            self.populate_tree(turn_name, turn.next_turns, turn_node)
