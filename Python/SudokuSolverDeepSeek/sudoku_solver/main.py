from gui import SudokuGUI
import tkinter as tk


def main() -> None:
    root = tk.Tk()
    app = SudokuGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
