import tkinter as tk
from tkinter import ttk


class ChartView(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        ttk.Label(self, text="chart Frame").grid(row=0, column=0)

class ProjectView(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.cards = {}
        self.columnconfigure(0, weight=1)

    def create_cards(self, project_names):
        for i, project_name in enumerate(project_names):
            card = ttk.Frame(self, relief="solid", padding=10)

            # widgets
            card.project_name = ttk.Label(card, text="")
            card.total_hours = ttk.Label(card, text="")

            # grid
            card.project_name.grid(row=0, column=1, sticky="ew")
            card.total_hours.grid(row=0, column=2, sticky="ew")

            card.grid(row=i, column=0, sticky="nsew", pady=5)
            self.rowconfigure(i, weight=1)
            self.cards[project_name] = card
    
    def update_card(self, project):
        area_card = self.cards.get(project["project_name"])

        area_card.project_name["text"] = project["project_name"]
        area_card.total_hours["text"] = project["total_hours"]

# Side
class AreaView(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.cards = {}
        self.columnconfigure(0, weight=1)

    def create_cards(self, area_names):
        for i, area_name in enumerate(area_names):
            card = ttk.Frame(self, relief="solid", padding=10)

            # widgets
            card.area_name = ttk.Label(card, text="")
            card.total_hours = ttk.Label(card, text="")

            # grid
            card.area_name.grid(row=0, column=1, sticky="ew")
            card.total_hours.grid(row=0, column=2, sticky="ew")

            card.grid(row=i, column=0, sticky="nsew", pady=5)
            self.rowconfigure(i, weight=1)
            self.cards[area_name] = card
    
    def update_card(self, area):
        area_card = self.cards.get(area["area_name"])

        area_card.area_name["text"] = area["area_name"]
        area_card.total_hours["text"] = area["total_hours"]

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

    def create_cards(self, calendar_names):
        for i, calendar_name in enumerate(calendar_names):
            card = ttk.Frame(self, relief="solid", padding=10)

            # widgets
            card.calendar_name = ttk.Label(card, text="")
            card.total_duration = ttk.Label(card, text="")
            card.total_events = ttk.Label(card, text="")

            # grid
            card.calendar_name.grid(row=0, column=0, sticky="ew")
            card.total_duration.grid(row=1, column=0, sticky="ew")
            card.total_events.grid(row=2, column=0, sticky="ew")

            card.grid(row=0, column=i, sticky="nsew", padx=5)
            self.columnconfigure(i, weight=1)

            self.cards[calendar_name] = card

    def update_card(self, calendar):
        calendar_name = calendar.get("calendar_name")
        total_duration = calendar.get("total_duration")
        total_events = calendar.get("total_events")

        calendar_card = self.cards.get(calendar_name)
        calendar_card.calendar_name["text"] = calendar_name.title()
        calendar_card.total_duration["text"] = f"{total_duration} hrs"
        calendar_card.total_events["text"] = f"{total_events} events"


class MainFrame(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # Top Frame
        self.calendar_view = CalendarView(self)
        self.calendar_view.grid(row=0, column=0, columnspan=2)

        # Right frame
        self.chartView = ProjectView(self)
        self.chartView.grid(row=1, column=1, rowspan=3)

        # Left frame (1)
        self.area_view = AreaView(self)
        self.area_view.grid(row=1, column=0)

        # Left fram (2)
        self.project_view = ProjectView(self)
        self.project_view.grid(row=2, column=0)

        for child in self.winfo_children():
            child.config(padding=5, relief="solid")
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
