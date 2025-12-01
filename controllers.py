"""contoller.py: core part. get data from model and listen to view."""


class CalendarController:
    def __init__(self, model, view):
        self.model = model
        self.view = view

        # self.view.register_event_handler("button_clicked", None)

    def initialize(self):
        data = self.model.calendars_total_duration()
        data.sort(key=lambda row: row["total_duration"], reverse=True)
        self.view.create_calendar_cards(data)
        self.update_calendars_data()

    def update_calendars_data(self):
        data = self.model.calendars_total_duration()
        data.sort(key=lambda row: row["total_duration"], reverse=True)

        for calendar in data:
            self.view.update_calendar_card(calendar)
