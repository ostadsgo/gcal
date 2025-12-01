import tkinter as tk
from tkinter import ttk


class ProjectView(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

# Side
class AreaView(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        # members area area
        # every area is frame with color 

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

    def create_calendar_cards(self, calendar_names):
        for i, calendar_name in enumerate(calendar_names):
            card = ttk.Frame(self, relief="solid", padding=(10, 5))

            card.calendar_name = ttk.Label(card, text="")
            card.total_duration = ttk.Label(card, text="")
            card.total_events = ttk.Label(card, text="")
            card.calendar_name.grid(row=0, column=0, sticky="ew")
            card.total_duration.grid(row=1, column=0, sticky="ew")
            card.total_events.grid(row=2, column=0, sticky="ew")

            card.grid(row=0, column=i, sticky="ew", padx=10)
            self.columnconfigure(i, weight=1)

            self.cards[calendar_name] = card

    def update_calendar_card(self, calendar):
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

        self.calendar_view = CalendarView(self, relief="solid", padding=(5, 10))
        self.calendar_view.grid(row=0, column=0, sticky="ew")

        self.rowconfigure(0, weight=1)
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
