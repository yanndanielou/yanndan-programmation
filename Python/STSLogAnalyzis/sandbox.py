import itertools
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import networkx as nx


def roll_dice():
    """Generate all possible sums of two dice."""
    return [sum(roll) for roll in itertools.product(range(1, 7), repeat=2)]


def valid_combinations(target, tiles, current=[]):
    """Find all possible ways to sum to 'target' using 'tiles'."""
    if target == 0:
        return [current]
    if target < 0 or not tiles:
        return []
    return valid_combinations(target - tiles[0], tiles[1:], current + [tiles[0]]) + valid_combinations(target, tiles[1:], current)


def simulate_shut_the_box():
    """Simulates all possible dice rolls and their valid tile flips."""
    tiles = list(range(1, 10))
    roll_outcomes = roll_dice()
    results = {}

    for roll in roll_outcomes:
        results[roll] = valid_combinations(roll, tiles)

    return results


def plot_results(results):
    """Plot the number of valid ways to play each dice roll."""
    rolls = sorted(results.keys())
    counts = [len(results[roll]) for roll in rolls]

    fig, ax = plt.subplots()
    ax.bar(rolls, counts, color="skyblue")
    ax.set_xlabel("Dice Roll")
    ax.set_ylabel("Valid Moves")
    ax.set_title("Valid Shut The Box Moves per Roll")
    return fig


def display_tree_view(frame, results):
    """Display all possible plays in a tree view."""
    tree = ttk.Treeview(frame, columns=("Roll", "Combination"), show="headings")
    tree.heading("Roll", text="Dice Roll")
    tree.heading("Combination", text="Valid Combinations")

    for roll, ways in results.items():
        parent = tree.insert("", "end", values=(roll, ""))
        for way in ways:
            tree.insert(parent, "end", values=("", " + ".join(map(str, way))))

    tree.pack()


def display_results():
    """Creates a GUI to display results."""
    results = simulate_shut_the_box()

    root = tk.Tk()
    root.title("Shut The Box Simulation")

    frame = ttk.Frame(root)
    frame.pack(padx=10, pady=10)

    label = ttk.Label(frame, text="Shut The Box Possible Plays", font=("Arial", 14))
    label.pack()

    display_tree_view(frame, results)

    fig1 = plot_results(results)
    canvas1 = FigureCanvasTkAgg(fig1, master=root)
    canvas1.get_tk_widget().pack()
    canvas1.draw()

    root.mainloop()


if __name__ == "__main__":
    display_results()
