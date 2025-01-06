""" https://www.tresfacile.net/le-widget-panedwindow-tkinter/#3 
Exemple 2 (Interface avec deux panneaux et une barre de séparation personnalisée) """

import tkinter as tk

root = tk.Tk()
root.geometry("400x300")

paned_window = tk.PanedWindow(root, orient="horizontal")
paned_window.pack(fill="both", expand=True)

left_frame = tk.Frame(paned_window, background="red")
right_frame = tk.Frame(paned_window, background="green")

paned_window.add(left_frame, minsize=100)
paned_window.add(right_frame, minsize=100)

sash_coord = paned_window.sash_coord(0)
sash = tk.Frame(paned_window, height=paned_window.winfo_height(), width=2, background="black")
sash.place(x=sash_coord[0], y=0, height=paned_window.winfo_height())

root.mainloop()
