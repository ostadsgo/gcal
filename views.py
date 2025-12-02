import tkinter as tk
from tkinter import ttk

# matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class ChartView(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the chart canvas."""
        self.figure = Figure(figsize=(8, 4), dpi=100)
        self.ax = self.figure.add_subplot(111)
        
        # Create canvas to display the figure in tkinter
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        
        # Configure grid
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

    def update_chart(self, data):
        """Update chart with calendar data."""
        # Clear previous chart
        self.ax.clear()
        
        # Extract data
        names = [item["name"] for item in data]
        durations = [item["duration"] for item in data]
        
        # Create bar chart
        self.ax.bar(names, durations, color='skyblue')
        self.ax.set_xlabel('Calendar')
        self.ax.set_ylabel('Duration (hours)')
        self.ax.set_title('Calendar Durations')
        
        # Rotate labels if many calendars
        self.ax.tick_params(axis='x', rotation=45)
        
        # Adjust layout to prevent label cutoff
        self.figure.tight_layout()
        
        # Redraw canvas
        self.canvas.draw()
    
    def update_pie_chart(self, data):
        """Create a pie chart."""
        self.ax.clear()
        
        names = [item.name for item in data]
        durations = [item.total_duration for item in data]
        colors = [item.color for item in data]
        
        self.ax.pie(durations, labels=names, colors=colors, autopct='%1.1f%%', startangle=90)
        self.ax.set_title('Calendar Time Distribution')
        
        self.canvas.draw()

class ProjectView(ttk.Labelframe):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.cards = {}
        self.columnconfigure(0, weight=1)

    def create_cards(self, projects):
        for i, project in enumerate(projects):
            card = ttk.Frame(self, relief="solid", padding=10)

            # widgets
            card.name_label = ttk.Label(card, text="")
            card.total_hours_label = ttk.Label(card, text="")

            # grid
            card.name_label.grid(row=0, column=1, sticky="ew")
            card.total_hours_label.grid(row=0, column=2, sticky="ew")

            card.grid(row=i, column=0, sticky="nsew", pady=5)
            self.rowconfigure(i, weight=1)
            self.cards[project.name] = card
    
    def update_card(self, project):
        area_card = self.cards.get(project.name)

        area_card.name_label.config(text=project.name)
        area_card.total_hours_label.config(text=project.total_hours)

# Side
class AreaView(ttk.Labelframe):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.cards = {}
        self.columnconfigure(0, weight=1)

    def create_cards(self, areas):
        """ Create frame to update with area's data."""
        for i, area in enumerate(areas):
            card = ttk.Frame(self, relief="solid", padding=10)

            # widgets
            card.name_label = ttk.Label(card, text="")
            card.total_hours_label = ttk.Label(card, text="")

            # grid
            card.name_label.grid(row=0, column=1, sticky="ew")
            card.total_hours_label.grid(row=0, column=2, sticky="ew")

            card.grid(row=i, column=0, sticky="nsew", pady=5)
            self.rowconfigure(i, weight=1)
            self.cards[area.name] = card
    
    def update_card(self, area):
        """ Update area frame with the area data. """
        area_card = self.cards.get(area.name)

        area_card.name_label.config(text=area.name)
        area_card.total_hours_label.config(text=area.total_hours)

# Top Frame
class CalendarView(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.cards = {}
        self.event_handlers = {}
        self.rowconfigure(0, weight=1)

    # designed to called from controller part.
    def register_event_handler(self, event_name, handler):
        self.event_handlers[event_name] = handler

    def create_cards(self, calendars):
        for i, calendar in enumerate(calendars):
            card = ttk.Frame(self, relief="solid", padding=10)

            # widgets
            card.name_label = ttk.Label(card, text="")
            card.duration_label = ttk.Label(card, text="")
            card.events_label = ttk.Label(card, text="")

            # grid
            card.name_label.grid(row=0, column=0, sticky="ew")
            card.duration_label.grid(row=1, column=0, sticky="ew")
            card.events_label.grid(row=2, column=0, sticky="ew")

            card.grid(row=0, column=i, sticky="nsew", padx=5)
            self.columnconfigure(i, weight=1)

            self.cards[calendar.name] = card

    def update_card(self, calendar):
        card = self.cards.get(calendar.name)
        card.name_label.config(text=calendar.name.title())
        card.duration_label.config(text=f"{calendar.total_duration} hrs")
        card.events_label.config(text=f"{calendar.total_events} events")


class MainFrame(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # Top Frame
        self.calendar_view = CalendarView(self)
        self.calendar_view.grid(row=0, column=0, columnspan=2)

        # Right frame
        self.chart_view = ChartView(self)
        self.chart_view.grid(row=1, column=1, rowspan=3)

        # Left frame (1)
        self.area_view = AreaView(self, text="Areas")
        self.area_view.grid(row=1, column=0)

        # Left fram (2)
        self.project_view = ProjectView(self, text="Projects")
        self.project_view.grid(row=2, column=0)

        for child in self.winfo_children():
            child.config(padding=5)
            child.grid_configure(pady=5, padx=5, sticky="nswe")
        
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=10)
        self.rowconfigure(2, weight=10)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=10)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gcal")
        self.minsize(640//2, 480)
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
