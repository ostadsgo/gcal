import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.dialogs import DatePickerDialog



# matplotlib
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.patheffects import withStroke

plt.style.use("dark_background")

# TODO: 

class ChartView(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.current_data = None
        self.chart_type = None
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

    def refresh_chart(self):
        if self.current_data is None or self.chart_type is None:
            return
        
        if self.chart_type == 'pie':
            self.update_pie_chart(self.current_data)
        elif self.chart_type == 'bar':
            self.update_bar_chart(self.current_data)
        elif self.chart_type == 'hbar':
            self.update_hbar_chart(self.current_data)
        elif self.chart_type == 'scatter':
            self.update_scatter_chart(self.current_data)
        elif self.chart_type == 'stack':
            days, hrs, color = self.current_data
            self.update_stack_chart(days, hrs, color)

    def update_pie_chart(self, data):
        self.current_data = data
        self.chart_type = 'pie'

        self.ax.clear()
        self.fig.patch.set_facecolor(plt.rcParams['figure.facecolor'])
        self.ax.set_facecolor(plt.rcParams['axes.facecolor'])

        # data
        names = [
            item.name if len(item.name) < 15 else item.name[:15] + "..."
            for item in data
        ]
        durations = [item.total_hours for item in data]

        explode = []
        if durations:
            max_index = durations.index(max(durations))
            explode = [0] * len(durations)
            explode[max_index] = 0.1

        # wedge styling
        wedgeprops = {"edgecolor": "#121212"}

        # draw pie chart
        self.ax.pie(
            durations,
            labels=names,
            explode=explode,
            autopct=lambda pct: f"{pct:.1f}%" if pct > 5.0 else "",
            startangle=90,
            shadow=True,
            wedgeprops=wedgeprops,
            labeldistance=1.2,
        )
        self.ax.set_title("Projects")
        self.canvas.draw()

    def update_bar_chart(self, data):
        self.current_data = data
        self.chart_type = 'bar'
        self.ax.clear()
        self.fig.patch.set_facecolor(plt.rcParams['figure.facecolor'])
        self.ax.set_facecolor(plt.rcParams['axes.facecolor'])
        
        types = [row.name for row in data]
        durations = [row.total_hours for row in data]
        
        # Create bars with different colors and enhancements
        colors = plt.cm.Set3(np.linspace(0, 1, len(types)))
        bars = self.ax.bar(range(len(types)), durations, color=colors, 
                           alpha=0.8,  # Transparency
                           linewidth=2,  # Border thickness
                           width=0.7)  # Bar width (0.7 adds spacing)
        
        # Add gradient effect to bars
        for bar, color in zip(bars, colors):
            bar.set_capstyle('round')  # Rounded top
        
        # Remove x-axis labels entirely
        self.ax.set_xticks([])
        self.ax.set_xlabel("")
        
        # Remove spines for cleaner look
        self.ax.spines["top"].set_visible(False)
        self.ax.spines["right"].set_visible(False)
        self.ax.spines["bottom"].set_visible(False)
        self.ax.spines["left"].set_visible(False)
        
        # Subtle horizontal grid only
        self.ax.grid(True, axis='y', linestyle="--", alpha=0.2, color="gray", zorder=0)
        
        # Create legend with type names
        self.ax.legend(
            bars, types, title="Types", loc="upper right", 
            bbox_to_anchor=(1.15, 1), framealpha=0.9, 
            edgecolor='gray', fancybox=True, shadow=True
        )
        
        # Enhanced value labels on top of bars
        for bar, duration in zip(bars, durations):
            height = bar.get_height()
            self.ax.text(
                bar.get_x() + bar.get_width() / 2.0,
                height,
                f"{duration:.1f}h",
                ha="center",
                va="bottom",
                fontsize=10,
                fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='#A1BC98', 
                         edgecolor='gray', alpha=0.8)
            )
        
        self.ax.set_ylabel("Hours", fontsize=12, fontweight='bold')
        self.ax.set_title("Types", fontsize=14, fontweight='bold', pad=20)
        
        # Add tick parameters
        self.ax.tick_params(axis='y', which='major', labelsize=10, width=0)
        
        self.fig.tight_layout()
        self.canvas.draw()

    def update_hbar_chart(self, data):
        self.current_data = data
        self.chart_type = 'hbar'

        self.ax.clear()

        self.fig.patch.set_facecolor(plt.rcParams['figure.facecolor'])
        self.ax.set_facecolor(plt.rcParams['axes.facecolor'])

        areas = [row.name for row in data]
        durations = [row.total_hours for row in data]
        colors = plt.cm.Set3(np.linspace(0, 1, len(areas)))

        self.ax.barh(areas, durations, color=colors, height=0.7, alpha=0.8)
        self.ax.grid(True, axis='x', linestyle="--", alpha=0.2, color="gray", zorder=0)
        self.ax.tick_params(axis='both', which='major', labelsize=10, width=0)

        self.ax.spines["top"].set_visible(False)
        self.ax.spines["right"].set_visible(False)
        self.ax.spines["bottom"].set_visible(False)
        self.ax.spines["left"].set_visible(False)


        self.ax.set_title("Areas")
        self.fig.tight_layout()

        self.canvas.draw()

    def update_stack_chart(self, days, hrs, color):
        self.current_data = (days, hrs, color)
        self.chart_type = 'stack'

        self.ax.clear()
        self.fig.patch.set_facecolor(plt.rcParams['figure.facecolor'])
        self.ax.set_facecolor(plt.rcParams['axes.facecolor'])

        self.ax.stackplot(days, hrs, colors=[color], alpha=0.7)
        self.ax.grid(True, axis='y', linestyle="--", alpha=0.3, color="gray")
        line = self.ax.plot(days, hrs, color=color, linewidth=2.5, solid_capstyle='round')[0]
        line.set_path_effects([withStroke(linewidth=5, foreground='white', alpha=0.3)])

        self.ax.spines["top"].set_visible(False)
        self.ax.spines["right"].set_visible(False)
        self.ax.spines["bottom"].set_visible(False)
        self.ax.spines["left"].set_visible(False)

        self.ax.set_ylabel('Hours', fontsize=12, fontweight='bold')
        self.ax.set_xlabel('Days', fontsize=12, fontweight='bold')

        self.ax.tick_params(axis='both', which='major', labelsize=10, width=0)
        self.ax.set_xticks(days)

        # Total text annotation
        total_hours = sum(hrs)
        self.ax.text(
            0.02,
            0.98,
            f"Total: {total_hours:.1f}h",
            transform=self.ax.transAxes,
            fontsize=11,
            verticalalignment="top",
            bbox=dict(boxstyle="round", facecolor="green", alpha=0.8),
        )

        self.canvas.draw()


class DateView(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.start_date_entry = ttk.DateEntry(self)
        self.end_date_entry = ttk.DateEntry(self)
        self.start_date_entry.grid(row=0, column=0)
        self.end_date_entry.grid(row=1, column=0)
        

class FilterReportView(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.vars = {}
        self.style = ttk.Style()
        font = font = ("TkDefaultFont", 10, "bold")

    def create_report_rows(self, report):
        for i, (name, value) in enumerate(report.to_dict().items()):
            fmt_name = name.replace("_", " ").title()
            self.vars[name] = tk.StringVar(value=f"{fmt_name}: {value}")
            var = self.vars[name]
            row_style = "inverse-secondary" if i % 2 else "inverse-light"
            ttk.Label(self, textvariable=var, bootstyle=row_style, padding=5).grid(
                row=i, column=0, sticky="ew"
            )

    # this is a comment
    def update_rows(self, report):
        for name, value in report.to_dict().items():
            fmt_name = name.replace("_", " ").title()
            self.vars[name].set(f"{fmt_name}: {value}")


class FilterView(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.handlers = {}

        # Year
        self.year_var = tk.StringVar()
        ttk.Label(self, text="Year").grid(row=0, column=0)
        self.year_combo = ttk.Combobox(self, textvariable=self.year_var, state="readonly")
        self.year_combo.grid(row=0, column=1)

        # Month
        self.month_var = tk.StringVar()
        ttk.Label(self, text="Month").grid(row=1, column=0)
        self.month_combo = ttk.Combobox(self, textvariable=self.month_var, state="readonly")
        self.month_combo.grid(row=1, column=1)

        # Filters: Area, Type, Project, ...
        filter_values = ["Areas", "Types", "Projects"]
        self.filter_var = tk.StringVar(value=filter_values[0])
        ttk.Label(self, text="Filter").grid(row=2, column=0)
        self.filter_combo = ttk.Combobox(
            self, values=filter_values, textvariable=self.filter_var, state="readonly"
        )
        self.filter_combo.grid(row=2, column=1)

        # Items: items of selected filter
        self.item_var = tk.StringVar()
        ttk.Label(self, text="Items").grid(row=3, column=0)
        self.item_combo = ttk.Combobox(self, textvariable=self.item_var, state="readonly")
        self.item_combo.grid(row=3, column=1)


        # handlers name
        self.year_combo.handler_name = "year_select"
        self.month_combo.handler_name = "month_select"
        self.filter_combo.handler_name = "filter_select"
        self.item_combo.handler_name = "item_select"

        for child in self.winfo_children():
            child.grid_configure(padx=10, pady=2, sticky="nswe")
            # bind event to each combo
            if child.widgetName == "ttk::combobox":
                child.bind("<<ComboboxSelected>>", self.on_combo_select)

        # row/columnconfigure
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)

    def register_event_handler(self, event_name: str, handler):
        self.handlers[event_name] = handler


    def on_combo_select(self, event):
        handler_name = event.widget.handler_name
        handler = self.handlers[handler_name]
        handler()

    def update_combo_values(self, var, combo, values):
        var.set(values[0] if values else "")
        combo["values"] = values

# Top Frame
class CalendarView(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.cards = {}
        self.handlers = {}
        self.selected_calendar_id = 1
        self.prev_card = None
        self.current_card = None

        for child in self.winfo_children():
            child.grid_configure(pady=5)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

    def register_event_handler(self, event_name: str, handler):
        self.handlers[event_name] = handler

    def update_card_style(self):
        # Rest before update
        self.prev_card.config(bootstyle="default")
        for child in self.prev_card.winfo_children():
            child.config(bootstyle="default")

        # Update
        self.current_card.config(bootstyle="secondary")
        for child in self.current_card.winfo_children():
            child.config(bootstyle="inverse-secondary")

    def on_calendar_select(self, event):
        self.prev_card = self.cards[self.selected_calendar_id]
        handler = self.handlers["calendar_select"]
        self.selected_calendar_id = event.widget.calendar_id
        handler()
        self.current_card = self.cards[self.selected_calendar_id]
        self.update_card_style()

    def on_label_select(self, event):
        # Save current card before handling event. 
        self.prev_card = self.cards[self.selected_calendar_id]
        # handlers
        handler = self.handlers["calendar_select"]
        self.selected_calendar_id = event.widget.master.calendar_id
        handler()

        self.current_card = self.cards[self.selected_calendar_id]
        self.update_card_style()

    def create_cards(self, calendars):
        for i, calendar in enumerate(calendars):
            card = ttk.Frame(self, relief="sunken", padding=10)
            # reference to calendar id to use in event
            card.calendar_id = calendar.calendar_id
            card.name_label = ttk.Label(card, text="")
            card.hours_label = ttk.Label(card, text="")
            card.events_label = ttk.Label(card, text="")
            card.areas_label = ttk.Label(card, text="")
            card.types_label = ttk.Label(card, text="")
            card.projects_label = ttk.Label(card, text="")

            # grid
            card.name_label.grid(row=0, column=0, sticky="ew")
            card.hours_label.grid(row=1, column=0, sticky="ew")
            card.events_label.grid(row=2, column=0, sticky="ew")
            card.areas_label.grid(row=3, column=0, sticky="ew")
            card.types_label.grid(row=4, column=0, sticky="ew")
            card.projects_label.grid(row=5, column=0, sticky="ew")

            card.bind("<Button-1>", self.on_calendar_select)
            card.grid(row=0, column=i, sticky="nsew", padx=5)
            self.cards[calendar.calendar_id] = card

            for child in card.winfo_children():
                if child.widgetName == "ttk::label":
                    child.bind("<Button-1>", self.on_label_select)

    def update_card(self, calendar):
        card = self.cards.get(calendar.calendar_id)
        card.name_label.config(text=calendar.calendar_name.title())
        card.hours_label.config(text=f"Hours: {calendar.total_duration}")
        card.events_label.config(text=f"Events: {calendar.total_events}")
        card.areas_label.config(text=f"Areas: {calendar.distinct_areas}")
        card.types_label.config(text=f"Types: {calendar.distinct_types}")
        card.projects_label.config(text=f"Projects: {calendar.distinct_projects}")

        # Set card selection.
        self.prev_card = self.cards[self.selected_calendar_id]
        self.current_card = self.cards[self.selected_calendar_id]
        self.update_card_style()


class ActionView(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.root = self.master.master
        self.theme_check_var = tk.BooleanVar(value=True)
        self.theme_text_var = tk.StringVar(value="Dark Mode")
        theme_checkbutton = ttk.Checkbutton(
            self,
            bootstyle="round-toggle success",
            text="Dark Mode",
            variable=self.theme_check_var,
            textvariable=self.theme_text_var,
            command=self.switch_theme,
        )
        theme_checkbutton.grid(row=0, column=0)

    def switch_theme(self):
        if self.theme_check_var.get():
            self.activate_dark_theme()
        else:
            self.activate_light_theme()
        self.root.update()

    def activate_dark_theme(self):
        global counter
        self.root.style = ttk.Style("darkly")
        plt.style.use("dark_background")
        self.refresh_all_charts()

    def activate_light_theme(self):
        self.root.style = ttk.Style("flatly")
        plt.style.use("seaborn-v0_8-white")
        self.refresh_all_charts()

    def refresh_all_charts(self):
        """ refresh chart to apply the theme(dark or light)."""
        self.master.stack_chart_view.refresh_chart()
        self.master.pie_chart_view.refresh_chart()
        self.master.bar_chart_view.refresh_chart()
        self.master.hbar_chart_view.refresh_chart()

class MainFrame(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # -- row 0 ---
        self.calendar_view = CalendarView(self)
        self.calendar_view.grid(row=0, column=0)

        self.filter_view = FilterView(self)
        self.filter_view.grid(row=0, column=1)

        self.filter_report_view = FilterReportView(self)
        self.filter_report_view.grid(row=0, column=2)

        self.date_view = DateView(self)
        self.date_view.grid(row=0, column=2)

        self.action_view = ActionView(self)
        self.action_view.grid(row=0, column=2)

        # -- row 1 ---
        self.stack_chart_view = ChartView(self)
        self.stack_chart_view.grid(row=1, column=0, columnspan=2)

        self.pie_chart_view = ChartView(self)
        self.pie_chart_view.grid(row=1, column=2)

        # -- row 2 ---
        self.bar_chart_view = ChartView(self)
        self.bar_chart_view.grid(row=2, column=0, columnspan=2)

        self.hbar_chart_view = ChartView(self)
        self.hbar_chart_view.grid(row=2, column=2)

        for child in self.winfo_children():
            child.config(padding=5)
            child.grid_configure(pady=5, padx=5, stick="NSWE")

        self.filter_report_view.grid_configure(sticky="NSW")
        self.action_view.grid_configure(sticky="NSE")

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=10)
        self.columnconfigure(3, weight=1)


class App(ttk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gcal")
        self.minsize(640, 480)
        self.style = ttk.Style("darkly")
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
