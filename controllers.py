"""contoller.py: core part. get data from model and listen to view."""


class Controller:
    def __init__(self, context):
        self.context = context
        self.calendar_view = context.get_view("calendar")
        self.filter_view = context.get_view("filter")
        self.model = context.model

        self.calendar_view.register_event_handler("calendar_select", self.handle_calendar_select)
        self.filter_view.register_event_handler("date_select", self.handle_date_select)
        self.filter_view.register_event_handler("filter_select", self.handle_filter_select)

    def initialize(self):
        calendars = self.model.get_calendars_by_usage()
        self.calendar_view.create_cards(calendars)

        # update calendar cards
        for calendar in calendars:
            self.calendar_view.update_card(calendar)

    def handle_calendar_select(self, calendar_id: int):
        print(f"calendar_id is : {calendar_id}")

    def handle_date_select(self, date_value):
        print(f"You select date_value {date_value}")

    def handle_filter_select(self, filter_value):
        items = []
        if filter_value == "Areas":
            items = self.model.distinct_area(self.calendar_view.selected_calendar_id)
        elif filter_value == "Types":
            items = self.model.distinct_types(self.calendar_view.selected_calendar_id)
        elif filter_value == "Projects":
            items = self.model.distinct_projects(self.calendar_view.selected_calendar_id)
        else:
            print(f"No query: Unknow filter value {filter_value}")

        values = [item.name for item in items] 
        self.filter_view.update_item_combo_values(values)
