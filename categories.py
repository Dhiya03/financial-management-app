import tkinter as tk
from tkinter import ttk
try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

class CategoryAnalysisTab(ttk.Frame):
    def __init__(self, parent, data):
        super().__init__(parent)
        self.data = data
        tk.Label(self, text="Category Analysis", font=("Arial", 16)).pack(pady=10)
        if HAS_MATPLOTLIB:
            self.plot_frame = tk.Frame(self)
            self.plot_frame.pack(pady=10)
            self.update_plot()

    def update_plot(self):
        categories = list(set(t["category"] for t in self.data.get("transactions", [])))
        spent = [sum(t["amount"] for t in self.data.get("transactions", []) if t["category"]==c) for c in categories]

        fig, ax = plt.subplots(figsize=(6,4))
        ax.pie(spent, labels=categories, autopct='%1.1f%%')
        canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack()
