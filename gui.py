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
        year_combo.bind("<<ComboboxSelected>>", self._handle_year_selection)

    def _handle_year_selection(self, event):
        selected_year = int(self.year.get())
        self.on_year_change(selected_year)



# Left frame
class InsightFrame(ttk.LabelFrame):
    """Calendar insight including calendar color, name and duration."""

    def __init__(self, master, data, **kwargs):
        super().__init__(master, **kwargs)
        self.data = data
        self.vars = []
        self.ui()

    def ui(self):
        for index, row in enumerate(self.data, 1):
            # vars
            name = tk.StringVar(value=row.get("name"))
            duration = tk.StringVar(value=str(row.get("duration")) + " hrs")

            # Frame that contain an insight
            row_frame = ttk.Frame(self, padding=(5, 5))

            # Calendar color
            tk.Label(row_frame, width=2, height=1, bg=row["color"], relief="solid", anchor="w").grid(
                row=0, column=0, sticky="nw", padx=(0, 10), pady=5
            )
            # Calendar name
            tk.Label(row_frame, textvariable=name, anchor="w", justify="left").grid(
                row=0, column=1, padx=(0, 10), sticky="nw"
            )
            # Calendar duration
            tk.Label(row_frame, textvariable=duration).grid( row=0, column=2, sticky="ne")

            row_frame.grid(row=index, sticky="wsen")

            self.vars.append({"name": name, "duration": duration})


    def update(self, data):
        self.data = data

        for i, row in enumerate(self.data):
            print(i)
            # get variables or the current row
            ui_vars = self.vars[i]

            # values
            name = row.get("name")
            duration = row.get("duration")

            # variables
            name_var = ui_vars.get("name")
            duration_var = ui_vars.get("duration")

            row.update({
                "name": name_var.set(name),
                "duration": duration_var.set(duration),
        })
        # self.name.set('sdsd')



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

        # -- Date filter -- 
        date_continer = ttk.Frame(self)
        date_frame = DateFrame(date_continer, on_year_change=self.handle_year_change)
        date_frame.grid(row=0, column=0, sticky="wsen")
        date_continer.grid(row=0, column=0, sticky="wsen")

        # -- Insight -- 
        calendars = gcal.data(year=2025, field="calendar", force=False)
        areas = gcal.data(year=2025, field="area", force=False)
        projects = gcal.data(year=2025, field="project", force=False)

        # Insight continer to hold different insights
        insight_container = ttk.Frame(self)
        insight_container.grid(row=1, column=0, sticky="wsen")

        # insights
        self.calendar = InsightFrame(insight_container, data=calendars,text="Calendars")
        self.area = InsightFrame(insight_container, data=areas, text="Areas")
        self.project = InsightFrame(insight_container, data=projects, text="Projects")

        self.calendar.grid(row=0, column=0, sticky="wsen")
        self.area.grid(row=1, column=0, sticky="wsen")
        self.project.grid(row=2, column=0, sticky="wsen")

        # -- Dashboard --

        # self.vis_frame = VisualizeFrame(self)
        # self.date_frame.grid(row=0, column=0, sticky="wsen")
        # self.vis_frame.grid(row=0, column=1, sticky="wsen", rowspan=2)

        # self.rowconfigure(0, weight=1)
        # self.rowconfigure(1, weight=10)
        # self.columnconfigure(0, weight=1)
        # self.columnconfigure(1, weight=3)

    def handle_year_change(self, year):
        calendars = gcal.data(year=year, field="calendar", force=True)
        areas = gcal.data(year=year, field="area", force=True)
        # projects = gcal.data(year=year, field="project", force=True)

        self.calendar.update(calendars)
        self.area.update(areas)
        self.project.update(projects)



class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gcal Vis")

        # MainFrame
        self.main_frame = MainFrame(self,  padding=(5, 5))
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
