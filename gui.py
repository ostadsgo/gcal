import tkinter as tk
from tkinter import ttk

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import gcal



# TODO: Use mutlti-tread to not block ui while making and fetching data from gcal.py

class DateFrame(ttk.Frame):
    """ Date selectbox to filter date by specific Year, Month, and daies range. """
    def __init__(self, master, on_year_change, **kwargs):
        super().__init__(master, **kwargs)

        self.on_year_change = on_year_change
        self.year = tk.StringVar()

        self._ui()

    def _ui(self):
        year_combo = ttk.Combobox(self, textvariable=self.year, values=["2023", "2024", "2025"])
        year_combo.pack(expand=True, fill="both")

        # binds
        year_combo.bind("<<ComboboxSelected>>", self.on_year_select)

    def _handle_year_selection(self, event):
        selected_year = int(self.year.get())
        print(selected_year)



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

        self.insight(gcal.data(field="calendar"))
        self.insight(gcal.data(field="area"))
        self.insight(gcal.data(field="project"))

        self.data = []

    def insight(self, data):
        frame = ttk.Frame(self, relief="solid", padding=(5, 5))
        frame.grid(row=self.row_index, column=0, pady=5, padx=(0, 5), sticky="wsen")
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        self.row_index += 1

        for index, row in enumerate(data, 1):
            name = tk.StringVar(value=row.get("name"))
            color = tk.StringVar(value=row.get("color"))
            duration  = tk.StringVar(value=row.get("duration"))

            row_frame = ttk.Frame(frame, padding=(5, 5))
            square_dict = dict(width=2, height=1, bg=color.get(), relief="solid", anchor="w")

            # Calendar color
            tk.Label(row_frame, **square_dict).grid(
                row=0, column=0, sticky="nw", padx=(0, 10), pady=5
            )
            # Calendar name
            tk.Label(row_frame, text=name.get(), anchor="w", justify="left").grid(
                row=0, column=1, padx=(0, 10), sticky="nw"
            )
            # Calendar duration
            tk.Label(row_frame, text=f"{duration.get()} hrs").grid(
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

    def bar_chart(self, data):
        fig, ax = plt.subplots()

        labels = [row.get("name") for row in data]
        colors = [row.get("color") for row in data]
        durations = [row.get("duration") for row in data]

        ax.bar(labels, durations, label=labels, color=colors)
        ax.set_ylabel("Duration in hr")
        ax.set_title("Calendars time spent")

        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def scatter_chart(self, data):
        fig, ax = plt.subplots()

        names = [row["name"] for row in data]
        durations = [row["duration"] for row in data]
        colors = [row["color"] for row in data]
        counts = [row["count"] for row in data]
        scale = [duration * 5 for duration in durations]

        plt.figure(figsize=(10, 6))
        scatter = ax.scatter(durations, counts, c=colors, s=scale, alpha=0.7)

        for i, name in enumerate(names):
            ax.annotate(
                name,
                (durations[i], counts[i]),
                xytext=(5, 5),
                textcoords="offset points",
                fontsize=9,
            )

        plt.title("Calendar Analysis: Duration vs Number of Tasks")
        plt.xlabel("Total Duration (hours)")
        plt.ylabel("Number of Tasks")

        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def draw(self):
        # self.pie_chart(gcal.data())
        self.bar_chart(gcal.data(field="area"))
        # self.scatter_chart(gcal.data("area"))


class MainFrame(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        date_frame = DateFrame(self, relief="solid")
        cal_frame = CalendarFrame(self)
        vis_frame = VisualizeFrame(self)
        date_frame.grid(row=0, column=0, sticky="wsen")
        cal_frame.grid(row=1, column=0, sticky="wsen")
        vis_frame.grid(row=0, column=1, sticky="wsen", rowspan=2)

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=10)
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
