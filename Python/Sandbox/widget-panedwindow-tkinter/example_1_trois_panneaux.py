""" https://www.tresfacile.net/le-widget-panedwindow-tkinter/#3 
Exemple 1 (Interface utilisateur avec trois panneaux)
 """

import tkinter as tk

root = tk.Tk()
root.geometry("400x300")

paned_window = tk.PanedWindow(root, orient="vertical")
paned_window.pack(fill="both", expand=True)

top_frame = tk.Frame(paned_window, background="red")
middle_frame = tk.Frame(paned_window, background="green")
bottom_frame = tk.Frame(paned_window, background="blue")

paned_window.add(top_frame, minsize=50)
paned_window.add(middle_frame, minsize=50)
paned_window.add(bottom_frame, minsize=50)

root.mainloop()