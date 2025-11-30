import tkinter as tk
from tkinter import ttk

from controllers import CalendarController






class CalendarView(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, kwargs)






class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gcal")


    def run(self):
        self.mainloop()




if __name__ == "__main__":
    app = App()
    app.run()
