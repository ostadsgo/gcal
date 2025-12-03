"""contoller.py: core part. get data from model and listen to view."""


class Controller:
    def __init__(self, context):
        self.context = context
        self.view = context.get_view("calendar")
        self.model = context.model

        self.view.register_event_handler("calendar_select", self.handle_calendar_select)

    def initialize(self):
        calendars = self.model.get_calendars_by_usage()
        self.view.create_cards(calendars)

        # update calendar cards
        for calendar in calendars:
            self.view.update_card(calendar)

    def handle_calendar_select(self, calendar_id: int):
        print(f"calendar_id is : {calendar_id}")
