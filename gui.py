import sys
import tkinter as tk
from tkinter import ttk

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import gcal


class CalendarFrame(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.calendars_insight_frame = ttk.Frame(self)
        self.categories_insight_frame = ttk.Frame(self)
        ttk.Label(self.calendars_insight_frame, text="Calendars").grid(
            row=0, column=0, sticky="wsen"
        )
        ttk.Label(self.categories_insight_frame, text="Categories").grid(
            row=0, column=0, sticky="wsen"
        )
        self.calendars_insight_frame.grid(row=0, column=0, sticky="wsen")
        self.categories_insight_frame.grid(row=1, column=0, sticky="wsen")

        # size of each widget inside the frame
        self.columnconfigure(0, weight=1)
        self.calendars_insight()
        self.categories_insight()

    def insight(self, section_frame, data: dict[str, int], colors: dict[str, str]):
        for row_index, (calendar, time_spent) in enumerate(data.items(), 1):
            color = colors.get(calendar, "black")
            square_dict = dict(width=5, height=1, bg=color, relief="flat")
            row_frame = ttk.Frame(section_frame)

            # A calendar detail: color, name, time spent
            tk.Label(row_frame, **square_dict).grid(
                row=0, column=0, sticky="w", padx=(0, 10), pady=10
            )
            tk.Label(row_frame, text=calendar).grid(row=0, column=1, sticky="w")
            tk.Label(row_frame, text=f"{time_spent} hrs").grid(
                row=0, column=2, sticky="e"
            )
            row_frame.grid(row=row_index, column=0, sticky="wsen")

            # color, name, time size
            row_frame.columnconfigure(0, weight=10)
            row_frame.columnconfigure(1, weight=45)
            row_frame.columnconfigure(2, weight=45)

    def calendars_insight(self):
        print(self.calendars_insight_frame)
        calendars = gcal.calendars_time_spent()
        colors = gcal.calendars_color()
        self.insight(self.calendars_insight_frame, calendars, colors)

    def categories_insight(self):
        categories = gcal.categories_time_spent()
        colors = gcal.categories_color()
        self.insight(self.categories_insight_frame, categories, colors)


class VisualizeFrame(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.colors = gcal.calendars_color()
        self.plot_pie()
        # self.plot_calendar_spent()
        # self.plot_category_spent()

    def pie_chart(self, data: dict, colors):
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.pie(
            list(data.values()),
            labels=list(data.keys()),
            autopct="%1.1f%%",
            startangle=90,
            colors=[colors.get(label, "red") for label in data.keys()],
        )
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def pie_chart2(self, cal_data, cat_data="", cal_colors="", cat_colors=""):
        fig, ax = plt.subplots(figsize=(8, 4))
        size = 0.3
        ax.pie(
            cal_data.values(),
            radius=1,
            colors=[cal_colors.get(label, "red") for label in cal_data.keys()],
            wedgeprops=dict(width=size, edgecolor="w"),
        )
        ax.pie(
            cat_data.values(),
            radius=1 - size,
            colors=[cat_colors.get(label, "red") for label in cat_data.keys()],
            wedgeprops=dict(width=size, edgecolor="w"),
        )
        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        print(cal_data)
        print(cat_data)

    def plot_pie(self):
        cal_data = gcal.calendars_time_spent()
        cal_colors = gcal.calendars_color()
        cat_data = gcal.categories_time_spent()
        cat_colors = gcal.categories_color()
        self.pie_chart2(cal_data, cat_data, cal_colors, cat_colors)

    def plot_calendar_spent(self):
        data = gcal.calendars_time_spent()
        colors = gcal.calendars_color()
        self.pie_chart(data, colors)

    def plot_category_spent(self):
        data = gcal.categories_time_spent()
        colors = gcal.categories_color()
        self.pie_chart(data, colors)


class MainFrame(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        cal_frame = CalendarFrame(self, padding=(10, 5), relief="solid")
        vis_frame = VisualizeFrame(self, relief="solid")
        cal_frame.grid(row=0, column=0, sticky="wsen", padx=(0, 20))
        vis_frame.grid(row=0, column=1, sticky="wsen")

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=10)
        self.columnconfigure(1, weight=90)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gcal Vis")

        # MainFrame
        self.main_frame = MainFrame(self, padding=(5, 5))
        self.main_frame.grid(row=0, column=0, sticky="wsen")

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.mainloop()

    def on_close(self):
        self.destroy()
        self.quit()


if __name__ == "__main__":
    App()
