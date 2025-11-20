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
class Insight(ttk.LabelFrame):
    """Calendar insight including calendar color, name and duration."""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.vars = []

    def ui(self, data):
        for index, row in enumerate(data, 1):
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


    def update_data(self, data):
        for i, row in enumerate(data):
            ui_vars = self.vars[i]

            # variables
            name_var = ui_vars.get("name")
            duration_var = ui_vars.get("duration")

            # set values to vars
            name_var.set(row.get("name"))
            duration_var.set(row.get("duration"))



class BarChart(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)

    def draw(self, data):
        labels = [row.get("name", "Uknown") for row in data]
        colors = [row.get("color", "#FF0000") for row in data]
        durations = [row.get("duration", 0) for row in data]
        
        self.ax.bar(labels, durations, label=labels, color=colors)
        self.ax.set_ylabel("Duration in hr")
        self.ax.set_title("Time spent")
        
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)


    def update_chart(self, data):
        if self.ax:
            self.ax.clear()

        self.draw(data)

class PieChart(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)

    def draw(self, data):
        # data
        labels = [row.get("name", "Uknown") for row in data]
        colors = [row.get("color", "#FF0000") for row in data]
        durations = [row.get("duration", 0) for row in data]

        # chart
        self.ax.pie(
            durations,
            colors=colors,
            autopct="%1.1f%%",
            startangle=90,
            pctdistance=0.85,
        )

        # show chart
        self.ax.set_title("Calendar Time Distribution")
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def update_chart(self, data):
        if self.ax:
            self.ax.clear()

        self.draw(data)


class MainFrame(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # -- Date filter --  TODO: could you remove on_year_change add it to some methods.j
        date_continer = ttk.Frame(self)
        date_frame = DateFrame(date_continer, on_year_change=self.handle_year_change)
        date_frame.grid(row=0, column=0, sticky="wsen")
        date_continer.grid(row=0, column=0, sticky="wsen")

        # -- Insight -- 
        # data
        calendars_data = gcal.data(year=2025, field="calendar", force=False)
        areas_data = gcal.data(year=2025, field="area", force=False)
        projects_data = gcal.data(year=2025, field="project", force=False)

        # Insight continer to hold different insights
        insight_container = ttk.Frame(self)
        insight_container.grid(row=1, column=0, sticky="wsen")

        # insights
        self.calendar_insight = Insight(insight_container, text="Calendars")
        self.area_insight = Insight(insight_container, text="Areas")
        self.project_insight = Insight(insight_container, text="Projects")

        # Insight in first look
        self.calendar_insight.ui(calendars_data)
        self.area_insight.ui(areas_data)
        self.project_insight.ui(projects_data)

        # grid insights
        self.calendar_insight.grid(row=0, column=0, sticky="wsen")
        self.area_insight.grid(row=1, column=0, sticky="wsen")
        self.project_insight.grid(row=2, column=0, sticky="wsen")

        # -- Chart --
        chart_container = ttk.Frame(self, relief="solid")
        chart_container.grid(row=0, column=1, rowspan=2, sticky="wsen")

        # pie chart for calendars

        # bar chart for areas
        self.bar_chart = BarChart(chart_container)
        self.bar_chart.grid(row=0, column=0, sticky="wsen")
        self.bar_chart.update_chart(areas_data)

        self.pie_chart = PieChart(chart_container)
        self.pie_chart.grid(row=0, column=1, sticky="wsen")
        self.pie_chart.update_chart(calendars_data)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)


    def handle_year_change(self, year):
        
        calendars_data = gcal.data(year=year, field="calendar", force=True)
        areas_data = gcal.data(year=year, field="area", force=True)
        projects_data = gcal.data(year=year, field="project", force=True)

        # # update insights
        self.calendar_insight.update_data(calendars_data)
        self.area_insight.update_data(areas_data)
        self.project_insight.update_data(projects_data)

        # update charts
        self.bar_chart.update_chart(areas_data)
        self.pie_chart.update_chart(calendars_data)



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
