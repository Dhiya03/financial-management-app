# gui_helpers.py

import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def populate_tree(tree, data_list, columns):
    """Populate a Treeview with a list of dicts."""
    for row in tree.get_children():
        tree.delete(row)
    for data in data_list:
        values = [data.get(col, "") for col in columns]
        tree.insert("", "end", values=values)

def create_bar_chart(frame, title, x_labels, series_dict, figsize=(6,3)):
    """Create a matplotlib bar chart embedded in a Tkinter frame.
    
    series_dict: {label: values_list}
    """
    fig, ax = plt.subplots(figsize=figsize)
    x = range(len(x_labels))
    width = 0.8 / max(1, len(series_dict))
    
    for i, (label, values) in enumerate(series_dict.items()):
        ax.bar([xi + i*width for xi in x], values, width=width, label=label)
    
    ax.set_xticks([xi + width*(len(series_dict)-1)/2 for xi in x])
    ax.set_xticklabels(x_labels, rotation=45)
    ax.set_title(title)
    ax.legend()
    
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.get_tk_widget().pack()
    canvas.draw()
    return fig, ax, canvas

def alert_if_low(tree, column, threshold=0.1):
    """Highlight rows where remaining budget is below threshold."""
    for iid in tree.get_children():
        remaining = float(tree.item(iid)["values"][column])
        if remaining <= 0:
            tree.item(iid, tags=("overspent",))
        elif remaining / max(1, tree.item(iid)["values"][column-1]) < threshold:
            tree.item(iid, tags=("warning",))
        else:
            tree.item(iid, tags=())
    tree.tag_configure("overspent", background="red")
    tree.tag_configure("warning", background="yellow")

def prompt_top_level(root, title, labels, callback):
    """Create a simple top-level dialog with entries for each label."""
    top = tk.Toplevel(root)
    top.title(title)
    entries = {}
    for i, lbl in enumerate(labels):
        tk.Label(top, text=lbl).grid(row=i, column=0)
        var = tk.StringVar()
        tk.Entry(top, textvariable=var).grid(row=i, column=1)
        entries[lbl] = var
    def on_save():
        values = {lbl: var.get() for lbl, var in entries.items()}
        callback(values)
        top.destroy()
    from tkinter import ttk
    ttk.Button(top, text="Save", command=on_save).grid(row=len(labels), column=0,columnspan=2,pady=5)
    return top
