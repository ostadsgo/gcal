"""contoller.py: core part. get data from model and listen to view."""


class CalendarController:
    def __init__(self, model, view):
        self.model = model
        self.view = view

        # self.view.register_event_handler("button_clicked", None)

    def initialize(self):
        self.calendar_names()
        self.update_calendars_data()

    def calendar_names(self):
        rows = self.model.calendars_total_duration()
        rows.sort(key=lambda row: row["total_duration"], reverse=True)

        # Extract each calendar name which already sorted by duration.
        calendar_names = [row["calendar_name"] for row in rows]
        self.view.create_calendar_cards(calendar_names)

    def update_calendars_data(self):
        rows = self.model.calendars_total_duration()
        rows.sort(key=lambda row: row["total_duration"], reverse=True)

        for calendar in rows:
            self.view.update_calendar_card(calendar) 
