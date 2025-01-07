import tkinter as tk
""" https://www.tresfacile.net/le-widget-panedwindow-tkinter/#3 
Exemple 3 ( Interface utilisateur avec deux panneaux et boutons de redimensionnement) """

root = tk.Tk()
root.geometry("400x300")

paned_window = tk.PanedWindow(root,
    background="cyan",
    bd=4,
    orient=tk.HORIZONTAL,
    sashrelief=tk.RAISED,
    sashwidth=4,
    showhandle=False,
    sashpad=5,
    sashcursor="sb_h_double_arrow")



paned_window.pack(fill="both", expand=True)

left_frame = tk.Frame(paned_window, background="red")
right_frame = tk.Frame(paned_window, background="green")

paned_window.add(left_frame, minsize=100)
paned_window.add(right_frame, minsize=100)

sashframe = tk.Frame(paned_window, background="blue")
sashframe.place(relx=0.5, rely=0.5, relwidth=0.02, relheight=1.0, anchor="center")

sashlabel = tk.Label(sashframe, background="white")
sashlabel.pack(fill="both", expand=True)

def on_dragged(event):
    print(f"on_dragged {event}")
    sash_x = event.x
    if sash_x > 10 and sash_x < root.winfo_width() - 10:
        sashframe.place(x=sash_x, y=0, relwidth=0.02, relheight=1.0, anchor="center")
        paned_window.sash_place(0, sash_x, 0)

root.bind("<B1-Motion>", on_dragged)

root.mainloop()
