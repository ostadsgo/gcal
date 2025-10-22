import sys
import tkinter as tk
from tkinter import ttk

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import gcal


class CalendarFrame(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # size of each widget inside the frame
        self.columnconfigure(0, weight=1)
        self.make_calendars()

    def make_calendars(self):
        calendars = gcal.calendars_time_spent()
        colors = gcal.calendar_colors()
        for row_index, (calendar, time_spent) in enumerate(calendars.items()):

            # A calendar detail: color, name, time spent
            frame = ttk.Frame(self)
            tk.Label(
                frame,
                width=5,
                height=1,
                bg=colors.get(calendar, "red"),
                relief="flat",
            ).grid(row=0, column=0, sticky="w", padx=(0, 10), pady=10)
            tk.Label(frame, text=calendar).grid(row=0, column=1, sticky="w")
            tk.Label(frame, text=f"{time_spent} hrs").grid(row=0, column=2, sticky="e")
            frame.grid(row=row_index, column=0, sticky="wsen")

            # color, name, time size
            frame.columnconfigure(0, weight=10)
            frame.columnconfigure(1, weight=45)
            frame.columnconfigure(2, weight=45)


class VisualizeFrame(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.pie_chart()

    def pie_chart(self):
        data = gcal.calendars_time_spent()
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.pie(list(data.values()), labels=list(data.keys()), autopct="%1.1f%%", startangle=90)
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, master=self)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)


class MainFrame(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        cal_frame = CalendarFrame(self, padding=(10, 5), relief="solid")
        vis_frame = VisualizeFrame(self, relief="solid")
        cal_frame.grid(row=0, column=0, sticky="wsen", padx=(0, 20))
        vis_frame.grid(row=0, column=1, sticky="wsen")

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=10)
        self.columnconfigure(1, weight=90)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gcal Vis")
        # self.minsize(1200, 800)

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
