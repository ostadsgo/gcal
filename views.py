import tkinter as tk
from tkinter import ttk

# matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# BUG: calendar click triggered only only frame not when clicked on widgets in the frame


class ChartView(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.axes = {}
        self.setup_ui()

    def setup_ui(self):
        """Set up the chart canvas."""
        self.figure = Figure(figsize=(8, 4), dpi=100)
        gs = self.figure.add_gridspec(2, 2, width_ratios=[1, 1.5], height_ratios=[1, 1])

        self.axes["stack"] = self.figure.add_subplot(gs[0, :])
        # self.axes["pie"] = self.figure.add_subplot(gs[1, 0])
        # self.axes["bar"] = self.figure.add_subplot(gs[1, 1])

        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

    def update_calendar_chart(self, calendars):
        """Create a pie chart."""
        self.axes["calendars_chart"].clear()

        names = [calendar.calendar_name for calendar in calendars]
        durations = [calendar.total_duration for calendar in calendars]
        colors = [calendar.calendar_color for calendar in calendars]

        self.axes["calendars_chart"].pie(
            durations, labels=names, colors=colors, autopct="%1.1f%%", startangle=90
        )
        self.axes["calendars_chart"].set_title("Calendar Time Distribution")

        self.canvas.draw()

    def update_area_chart(self, areas):
        names = [area.area_name for area in areas]
        durations = [area.total_hours for area in areas]
        self.axes["areas_chart"].bar(names, durations)
        self.canvas.draw()

    def update_project_chart(self, projects):
        names = [project.project_name for project in projects]
        durations = [project.total_hours for project in projects]
        self.axes["projects_chart"].bar(names, durations)
        self.canvas.draw()

    def update_stack_chart(self, data=None):
        x = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        y = [10, 5, 10, 5, 10, 5, 10, 5, 10]
        self.axes["stack"].stackplot(x, y)
        # self.axes["stack"].set(xlim=(0, 8), xticks=np.arange(1, 8), ylim=(0, 8), yticks=np.arange(1, 8))
        self.canvas.draw()


class ReportView(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        ttk.Label(self, text="Report view")


class FilterView(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.handlers = {}

        # Year
        self.year_var = tk.StringVar()
        ttk.Label(self, text="Year").grid(row=0, column=0)
        self.year_combo = ttk.Combobox(self, textvariable=self.year_var)
        self.year_combo.grid(row=1, column=0)

        # Month
        self.month_var = tk.StringVar()
        ttk.Label(self, text="Month").grid(row=0, column=1)
        self.month_combo = ttk.Combobox(self, textvariable=self.month_var)
        self.month_combo.grid(row=1, column=1)

        # Filters: Area, Type, Project, ...
        filter_values = ["Areas", "Types", "Projects"]
        self.filter_var = tk.StringVar(value=filter_values[0])
        ttk.Label(self, text="Filter").grid(row=0, column=2)
        self.filter_combo = ttk.Combobox(self, values=filter_values, textvariable=self.filter_var)
        self.filter_combo.grid(row=1, column=2)
        
        # Items: items of selected filter
        self.item_var = tk.StringVar()
        ttk.Label(self, text="Items").grid(row=0, column=3)
        self.item_combo = ttk.Combobox(self, textvariable=self.item_var)
        self.item_combo.grid(row=1, column=3)

        for child in self.winfo_children():
            child.grid_configure(padx=10, sticky="nswe")

        # Bind
        self.year_combo.bind("<<ComboboxSelected>>", self.on_year_select)
        self.month_combo.bind("<<ComboboxSelected>>", self.on_month_select)
        self.filter_combo.bind("<<ComboboxSelected>>", self.on_filter_select)
        self.item_combo.bind("<<ComboboxSelected>>", self.on_item_select)

        # row/columnconfigure
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)

    def register_event_handler(self, event_name: str, handler):
        self.handlers[event_name] = handler

    def on_year_select(self, event):
        handler = self.handlers["year_select"]
        selected_year = self.year_var.get()
        handler(selected_year)

    def on_month_select(self, event):
        handler = self.handlers["month_select"]
        selected_month = self.month_var.get()
        handler(selected_month)

    def on_filter_select(self, event):
        handler = self.handlers["filter_select"]
        selected_filter = self.filter_var.get()
        handler(selected_filter)

    def on_item_select(self):
        pass

    def update_year_combo_values(self, values):
        self.year_var.set(values[0])
        self.year_combo["values"] = values

    def update_month_combo_values(self, values):
        self.month_var.set(values[0])
        self.month_combo["values"] = values

    def update_item_combo_values(self, values):
        self.item_var.set(values[0])
        self.item_combo["values"] = values

# Top Frame
class CalendarView(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.cards = {}
        self.handlers = {}
        self.selected_calendar_id = 1

        self.rowconfigure(0, weight=1)

    def register_event_handler(self, event_name: str, handler):
        self.handlers[event_name] = handler

    def on_calendar_hover(self, event):
        pass

    def on_calendar_select(self, event):
        handler = self.handlers["calendar_select"]
        self.selected_calendar_id = event.widget.calendar_id
        handler(event.widget.calendar_id)

    def create_cards(self, calendars):
        for i, calendar in enumerate(calendars):
            card = ttk.Frame(self, relief="solid", padding=10)

            # reference to calendar id to use in event
            card.calendar_id = calendar.calendar_id

            # widgets
            card.calendar_name_label = ttk.Label(card, text="")
            card.duration_label = ttk.Label(card, text="n hrs")
            card.events_label = ttk.Label(card, text="n events")
            card.areas_label = ttk.Label(card, text="n areas")
            card.projects_label = ttk.Label(card, text="n types")

            # grid
            card.calendar_name_label.grid(row=0, column=0, sticky="ew")
            card.duration_label.grid(row=1, column=0, sticky="ew")
            card.events_label.grid(row=2, column=0, sticky="ew")
            card.areas_label.grid(row=3, column=0, sticky="ew")
            card.projects_label.grid(row=4, column=0, sticky="ew")

            card.bind("<Button-1>", self.on_calendar_select)
            card.grid(row=0, column=i, sticky="nsew", padx=5)
            self.columnconfigure(i, weight=1)

            self.cards[calendar.calendar_name] = card

    def update_card(self, calendar):
        card = self.cards.get(calendar.calendar_name)
        card.calendar_name_label.config(text=calendar.calendar_name.title())
        card.duration_label.config(text=f"{calendar.total_duration} hrs")
        card.events_label.config(text=f"{calendar.total_events} events")
        card.areas_label.config(text=f"{calendar.distinct_areas} areas")
        card.projects_label.config(text=f"{calendar.distinct_projects} projects")


class MainFrame(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # Top Frame
        self.calendar_view = CalendarView(self)
        self.calendar_view.grid(row=0, column=0)

        # Filter frame
        self.filter_view = FilterView(self)
        self.filter_view.grid(row=1, column=0)

        # Chart and insight
        self.chart_view = ChartView(self)
        self.chart_view.grid(row=2, column=0)

        # Chart and insight
        self.report_view = ReportView(self)
        self.chart_view.grid(row=3, column=0)

        for child in self.winfo_children():
            child.config(padding=5, relief="solid")
            child.grid_configure(pady=5, padx=5, sticky="nswe")

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=10)
        self.columnconfigure(0, weight=1)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gcal")
        self.minsize(640, 480)
        self.update_idletasks()

        self.mainframe = MainFrame(self)
        self.mainframe.grid(row=0, column=0, sticky="nsew")

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

    def run(self):
        self.mainloop()


if __name__ == "__main__":
    app = App()
    app.run()
