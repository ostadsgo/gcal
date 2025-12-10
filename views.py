import tkinter as tk
from tkinter import ttk

# matplotlib
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# TODO: previous data and selected data compare on stack chart
# TODO: stack chart opacity


class ChartView(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.setup_ui()

    def setup_ui(self):
        """Set up the chart canvas."""
        self.fig = Figure(figsize=(5, 3), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        self.fig.tight_layout()
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

    def update_pie_chart(self, calendars):
        """Create a pie chart."""
        self.ax.clear()

        names = [calendar.calendar_name for calendar in calendars]
        durations = [calendar.total_duration for calendar in calendars]
        colors = [calendar.calendar_color for calendar in calendars]

        self.ax.pie(
            durations, labels=names, colors=colors, autopct="%1.1f%%", startangle=90
        )
        self.ax.set_title("Calendar Time Distribution")
        self.canvas.draw()

    def update_bar_chart(self, data):
        self.ax.clear()
        types = [row.type_name for row in data]
        durations = [row.total_hours for row in data]

        # Create bars with different colors
        colors = plt.cm.Set3(np.linspace(0, 1, len(types)))
        bars = self.ax.bar(range(len(types)), durations, color=colors)

        # Remove x-axis labels entirely
        self.ax.set_xticks([])
        self.ax.set_xlabel("")

        # Create legend with type names
        self.ax.legend(
            bars, types, title="Types", loc="upper right", bbox_to_anchor=(1.15, 1)
        )

        # Add value labels on top of bars
        for bar, duration in zip(bars, durations):
            height = bar.get_height()
            self.ax.text(
                bar.get_x() + bar.get_width() / 2.0,
                height,
                f"{duration:.1f}h",
                ha="center",
                va="bottom",
                fontsize=9,
            )

        self.ax.set_ylabel("Hours")
        self.ax.set_title("Hours by Type")

        self.fig.tight_layout()
        self.canvas.draw()

    def update_hbar_chart(self, data):
        self.ax.clear()

        areas = [row.area_name for row in data]
        durations = [row.total_hours for row in data]

        self.ax.barh(areas, durations)

        self.fig.tight_layout()
        self.canvas.draw()

    def update_stack_chart(self, days, hrs, color):
        self.ax.clear()
        self.ax.stackplot(days, hrs, colors=[color])
        self.ax.grid(True, linestyle="--", alpha=0.3, color="gray")
        self.ax.spines["top"].set_visible(False)
        self.ax.spines["right"].set_visible(False)

        self.ax.spines["left"].set_color("#DDDDDD")
        self.ax.spines["bottom"].set_color("#DDDDDD")

        self.ax.set_xticks(days)
        self.ax.tick_params(axis="both", which="major", labelsize=10)

        self.canvas.draw()


class ReportView(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.is_rows_created = False
        self.vars = {}

    def update_variable(self, name, value=""):
        self.vars.update({name: tk.StringVar(value=value)})

    def create_rows(self):
        """Create label for self.vars dict."""
        if not self.is_rows_created:
            for index, (var_name, var) in enumerate(self.vars.items()):
                ttk.Label(self, textvariable=var).grid(row=index, column=0)
            self.is_rows_created = True

            for child in self.winfo_children():
                child.grid_configure(stick="ew")


class FilterReportView(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.vars = {
            "item_name": tk.StringVar(value="Report for: "),
            "first_date": tk.StringVar(value="Start date: "),
            "last_date": tk.StringVar(value="Last date: "),
            "total_days": tk.StringVar(value="Total Days: "),
            "average_day": tk.StringVar(value="Avg per day:"),
            "total_events": tk.StringVar(value="Events: "),
            "total_hours": tk.StringVar(value="Total hours:"),
            "average_duration": tk.StringVar(value="Average: "),
            "max_duration": tk.StringVar(value="Max: "),
            "min_duration": tk.StringVar(value="Min: "),
        }

        # create rows
        for index, (var_name, var) in enumerate(self.vars.items()):
            ttk.Label(self, textvariable=var).grid(row=index, column=0)

        for child in self.winfo_children():
            child.grid_configure(stick="ew")

    def update_rows(self, name, report):
        self.vars["item_name"].set(f"Report For: {name}")

        for name, value in report.to_dict().items():
            # print(name, value)
            if self.vars.get(name) is not None:
                self.vars[name].set(f"{name.title()}: {value}")


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
        self.filter_combo = ttk.Combobox(
            self, values=filter_values, textvariable=self.filter_var
        )
        self.filter_combo.grid(row=1, column=2)

        # Items: items of selected filter
        self.item_var = tk.StringVar()
        ttk.Label(self, text="Items").grid(row=0, column=3)
        self.item_combo = ttk.Combobox(self, textvariable=self.item_var)
        self.item_combo.grid(row=1, column=3)

        for child in self.winfo_children():
            child.grid_configure(padx=10, pady=2, sticky="nswe")

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
        handler()

    def on_month_select(self, event):
        handler = self.handlers["month_select"]
        handler()

    def on_filter_select(self, event):
        handler = self.handlers["filter_select"]
        handler()

    def on_item_select(self, events):
        handler = self.handlers["item_select"]
        handler()

    def update_year_combo_values(self, values):
        self.year_var.set(values[0])
        self.year_combo["values"] = values

    def update_month_combo_values(self, values):
        self.month_var.set(values[0])
        self.month_combo["values"] = values

    def update_item_combo_values(self, values):
        self.item_var.set(values[0])
        self.item_combo["values"] = values


class CalendarReportView(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        ttk.Label(self, text="Calendar detail").grid()
        self.vars = {}

    def create_rows(self, calendar):
        i = 0
        for i, (name, value) in enumerate(calendar.to_dict().items()):
            self.vars[name] = tk.StringVar(
                value=f"{name.title().replace('_', " ")}: {value}"
            )
            var = self.vars[name]
            ttk.Label(self, textvariable=var, justify="left").grid(
                row=i, column=0, sticky="ew"
            )
            i += 1

    def update_values(self, calendar):
        for name, value in calendar.to_dict().items():
            self.vars[name].set(f"{name.title().replace('_', ' ')}: {value}")


# Top Frame
class CalendarView(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.cards = {}
        self.handlers = {}
        self.selected_calendar_id = 1
        self.previous_card = None
        self.current_card = None

        self.style = ttk.Style()
        self.style.configure("Normal.TFrame", background="lightgray")

        # self.rowconfigure(0, weight=1)
        for child in self.winfo_children():
            child.grid_configure(pady=5)

    def register_event_handler(self, event_name: str, handler):
        self.handlers[event_name] = handler

    def on_calendar_select(self, event):
        handler = self.handlers["calendar_select"]
        self.selected_calendar_id = event.widget.calendar_id
        handler()
        
        # Reset previous card
        if self.current_card:
            self.current_card.config(style="Normal.TFrame")
            for child in self.current_card.winfo_children():
                child.config(style="Normal.TLabel")
        
        # Style new selected card
        self.current_card = self.cards[self.selected_calendar_id]
        
        frame_style_name = f"CalendarColor{self.selected_calendar_id}.TFrame"
        label_style_name = f"CalendarColor{self.selected_calendar_id}.TLabel"
        
        self.current_card.config(style=frame_style_name)
        for child in self.current_card.winfo_children():
            child.config(style=label_style_name)

    def on_label_select(self, event):
        handler = self.handlers["calendar_select"]
        self.selected_calendar_id = event.widget.master.calendar_id
        handler()

        # Reset previous card
        if self.current_card:
            self.current_card.config(style="Normal.TFrame")
            for child in self.current_card.winfo_children():
                child.config(style="Normal.TLabel")
        
        self.current_card = self.cards[self.selected_calendar_id]

        frame_style_name = f"CalendarColor{self.selected_calendar_id}.TFrame"
        label_style_name = f"CalendarColor{self.selected_calendar_id}.TLabel"
        
        self.current_card.config(style=frame_style_name)
        for child in self.current_card.winfo_children():
            child.config(style=label_style_name)


    def set_card_selection(self):
        self.current_card = self.cards[self.selected_calendar_id]

        # Reset previous card
        if self.current_card:
            self.current_card.config(style="Normal.TFrame")
            for child in self.current_card.winfo_children():
                child.config(style="Normal.TLabel")
        
        self.current_card = self.cards[self.selected_calendar_id]

        frame_style_name = f"CalendarColor{self.selected_calendar_id}.TFrame"
        label_style_name = f"CalendarColor{self.selected_calendar_id}.TLabel"
        
        self.current_card.config(style=frame_style_name)
        for child in self.current_card.winfo_children():
            child.config(style=label_style_name)

    def create_cards(self, calendars):
        for i, calendar in enumerate(calendars):
            card = ttk.Frame(self, relief="sunken", padding=10)
            self.style.configure(
                f"CalendarColor{calendar.calendar_id}.TFrame",
                background=f"{calendar.calendar_color}",
            )

            self.style.configure(
                f"CalendarColor{calendar.calendar_id}.TLabel",
                background=f"{calendar.calendar_color}",
            )
            # reference to calendar id to use in event
            card.calendar_id = calendar.calendar_id
            card.name_label = ttk.Label(card, text="")
            card.total_duration_label = ttk.Label(card, text="")

            # grid
            card.name_label.grid(row=0, column=0, sticky="ew")
            card.total_duration_label.grid(row=1, column=0, sticky="ew")

            card.bind("<Button-1>", self.on_calendar_select)
            card.grid(row=0, column=i, sticky="nsew", padx=5)
            self.cards[calendar.calendar_id] = card

            for child in card.winfo_children():
                if child.widgetName == "ttk::label":
                    child.bind("<Button-1>", self.on_label_select)



    def update_card(self, calendar):
        card = self.cards.get(calendar.calendar_id)
        card.name_label.config(text=calendar.calendar_name.title())
        card.total_duration_label.config(
            text=f"Total hours: {calendar.total_duration} hrs"
        )


class MainFrame(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # Top Frame
        self.calendar_view = CalendarView(self)
        self.calendar_view.grid(row=0, column=0, columnspan=2)

        # Filter frame
        self.filter_view = FilterView(self)
        self.filter_view.grid(row=1, column=0, columnspan=2)

        # chart top
        self.top_chart_view = ChartView(self)
        self.top_chart_view.grid(row=2, column=0, columnspan=3)

        # Report for filter
        self.filter_report_view = FilterReportView(self)
        self.filter_report_view.grid(row=2, column=3)

        # chart bottom
        self.bottom_chart_view = ChartView(self)
        self.bottom_chart_view.grid(row=3, column=0, columnspan=3)

        # top_right chart
        self.top_right_chart_view = ChartView(self)
        self.top_right_chart_view.grid(row=3, column=3)


        # Report for calendar
        self.calendar_report_view = CalendarReportView(self)
        self.calendar_report_view.grid(row=0, column=3, rowspan=2)

        for child in self.winfo_children():
            child.config(padding=5, relief="solid")
            child.grid_configure(pady=5, padx=5, sticky="nswe")

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=0)
        self.columnconfigure(2, weight=0)
        self.columnconfigure(3, weight=0)


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
