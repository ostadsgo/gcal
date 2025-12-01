import tkinter as tk
from tkinter import ttk


class CalendarView(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.cards = {}
        self.event_handlers = {}

    # designed to called from controller part.
    def register_event_handler(self, event_name, handler):
        self.event_handlers[event_name] = handler

    def create_calendar_cards(self, calendars):
        for i, calendar in enumerate(calendars):
            calendar_name = calendar["calendar_name"]
            card = ttk.Frame(self, relief="solid", padding=(10, 5))

            card.calendar_name = ttk.Label(card, text="Calendar name: ")
            card.calendar_duration = ttk.Label(card, text="Calendar duration: ")
            card.calendar_name.grid(row=0, column=0)
            card.calendar_duration.grid(row=1, column=0)

            card.grid(row=0, column=i, sticky="nsew", padx=10)

            self.cards[calendar_name] = card

    def update_calendar_card(self, calendar):
        calendar_name = calendar.get("calendar_name")
        total_duration = calendar.get("total_duration")

        calendar_card = self.cards.get(calendar_name)
        calendar_card.calendar_name["text"] = calendar_name
        calendar_card.calendar_duration["text"] = total_duration


class MainFrame(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.calendar_view = CalendarView(self, relief="sunken", padding=(5, 10))
        self.calendar_view.grid(row=0, column=0, sticky="nsew")

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
