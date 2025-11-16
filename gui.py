import tkinter as tk
from tkinter import ttk

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import gcal


# Left frame
class CalendarFrame(ttk.Frame):
    """Calendar insight including calendar color, name and duration."""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.row_index = 0
        self.rowconfigure(0, weight=1) 
        self.rowconfigure(1, weight=1) 
        self.rowconfigure(2, weight=1) 
        self.columnconfigure(0, weight=1)

        self.insight(gcal.data("calendar"))
        self.insight(gcal.data("area"))
        self.insight(gcal.data("project"))

    def insight(self, data):
        frame = ttk.Frame(self, relief="solid", padding=(5, 5))
        frame.grid(row=self.row_index, column=0, pady=5, padx=(0, 5), sticky="wsen")
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        self.row_index += 1

        for index, row in enumerate(data, 1):
            name = row.get("name")
            color = row.get("color")
            duration = row.get("duration")

            row_frame = ttk.Frame(frame, padding=(5, 5))
            square_dict = dict(width=2, height=1, bg=color, relief="solid", anchor="w")

            # Calendar color
            tk.Label(row_frame, **square_dict).grid(
                row=0, column=0, sticky="nw", padx=(0, 10), pady=5
            )
            # Calendar name
            tk.Label(row_frame, text=name, anchor="w", justify="left").grid(
                row=0, column=1, padx=(0, 10), sticky="nw"
            )
            # Calendar duration
            tk.Label(row_frame, text=f"{duration} hrs").grid(
                row=0, column=2, sticky="ne"
            )
            row_frame.grid(row=index, sticky="wsen")

            # color, name, time size
            row_frame.columnconfigure(0, weight=1)
            row_frame.columnconfigure(1, weight=1)
            row_frame.columnconfigure(2, weight=1)
            row_frame.rowconfigure(0, weight=1)

            frame.rowconfigure(index, weight=1)
            frame.columnconfigure(0, weight=1)


# Right frame
class VisualizeFrame(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.draw()

    def pie_chart(self, data):
        fig, ax = plt.subplots(figsize=(6, 4))
        labels = [row.get("name") for row in data]
        colors = [row.get("color") for row in data]
        durations = [row.get("duration") for row in data]

        ax.pie(
            durations,
            labels=labels,
            colors=colors,
            autopct="%1.1f%%",
            startangle=90,
        )
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def pie_chart2(self, cal_data, cat_data):
        fig, ax = plt.subplots(figsize=(8, 4))
        size = 0.4
        ax.pie(
            [v["duration"] for _, v in cal_data.items()],
            labels=list(cal_data.keys()),
            radius=1,
            colors=[v["color"] for _, v in cal_data.items()],
            wedgeprops=dict(width=size, edgecolor="w"),
        )
        values = [
            item["duration"]
            for calendar in cat_data
            for cal_name, data_list in calendar.items()
            for item in data_list
        ]
        colors = [
            item["color"]
            for calendar in cat_data
            for cal_name, data_list in calendar.items()
            for item in data_list
        ]
        labels = [
            item["name"]
            for calendar in cat_data
            for cal_name, data_list in calendar.items()
            for item in data_list
        ]
        ax.pie(
            values,
            labels=labels,
            radius=1 - size,
            colors=colors,
            wedgeprops=dict(width=size, edgecolor="w"),
        )
        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def bar_chart(self, data):
        pass

    def plot_calendar_spent(self):
        data = gcal.calendars_data()
        self.pie_chart(data)

    def plot_category_spent(self):
        data = gcal.categories_data()
        self.pie_chart(data)

    def draw(self):
        self.pie_chart(gcal.data())


class MainFrame(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        cal_frame = CalendarFrame(self)
        vis_frame = VisualizeFrame(self)
        cal_frame.grid(row=0, column=0, sticky="wsen")
        vis_frame.grid(row=0, column=1, sticky="wsen")

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=3)


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
