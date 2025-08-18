import tkinter as tk
from tkinter import ttk
try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

class DashboardTab(ttk.Frame):
    def __init__(self, parent, data):
        super().__init__(parent)
        self.data = data
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self, text="Monthly Dashboard", font=("Arial", 16)).pack(pady=10)
        self.info_label = tk.Label(self, text="")
        self.info_label.pack()
        if HAS_MATPLOTLIB:
            self.plot_frame = tk.Frame(self)
            self.plot_frame.pack(pady=10)
            self.update_plot()

    def update_plot(self):
        categories = list(self.data.get("budgets", {}).keys())
        spent = [sum(t["amount"] for t in self.data.get("transactions", []) if t["category"]==c) for c in categories]
        budget = [self.data["budgets"].get(c, 0) for c in categories]

        fig, ax = plt.subplots(figsize=(6,4))
        ax.bar(categories, budget, alpha=0.3, label="Budget")
        ax.bar(categories, spent, alpha=0.7, label="Spent")
        ax.set_ylabel("Amount")
        ax.legend()
        canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack()
