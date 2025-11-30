""" contoller.py: core part. get data from model and listen to view."""

class CalendarController:
    def __init__(self, model, view):
        self.model = model
        self.view = view

        calendars = self.model.get_calendars()
        print(calendars)

