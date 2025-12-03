"""contoller.py: core part. get data from model and listen to view."""


class Controller:
    def __init__(self, context):
        self.context = context
        self.calendar_view = context.get_view("calendar")
        self.filter_view = context.get_view("filter")
        self.chart_view = context.get_view("chart")
        self.model = context.model

        self.calendar_view.register_event_handler("calendar_select", self.handle_calendar_select)
        self.filter_view.register_event_handler("year_select", self.handle_year_select)
        self.filter_view.register_event_handler("month_select", self.handle_month_select)
        self.filter_view.register_event_handler("filter_select", self.handle_filter_select)
        self.filter_view.register_event_handler("item_select", self.handle_item_select)

    def initialize(self):
        calendars = self.model.get_calendars_by_usage()
        self.calendar_view.create_cards(calendars)
        self.chart_view.update_stack_chart()

        # populate area for selected calendar for item combo
        rows = self.model.distinct_areas(self.calendar_view.selected_calendar_id)
        values = [row.name for row in rows]
        self.filter_view.item_combo.set(values)
        self.filter_view.item_var.set(values[0])

        # set years
        rows = self.model.distinct_years(self.calendar_view.selected_calendar_id)
        year_values = [row.year for row in rows]
        self.filter_view.year_combo["values"] = year_values
        self.filter_view.year_var.set(year_values[0])

        # set months
        rows = self.model.distinct_months(self.calendar_view.selected_calendar_id)
        month_values = [row.month for row in rows]
        self.filter_view.month_combo["values"] = month_values
        self.filter_view.month_var.set(month_values[0])

        # update calendar cards
        for calendar in calendars:
            self.calendar_view.update_card(calendar)

    def handle_calendar_select(self, calendar_id: int):
        # set years
        rows = self.model.distinct_years(self.calendar_view.selected_calendar_id)
        year_values = [row.year for row in rows]
        self.filter_view.year_combo["values"] = year_values
        self.filter_view.year_var.set(year_values[0])

        # set months
        rows = self.model.distinct_months(self.calendar_view.selected_calendar_id)
        month_values = [row.month for row in rows]
        self.filter_view.month_combo["values"] = month_values
        self.filter_view.month_var.set(month_values[0])

        print(f"Calendar id: {calendar_id}")
        print(year_values)
        print(month_values)

    def handle_date_select(self, date_value):
        print(f"You select date_value {date_value}")

    def handle_filter_select(self, filter_value):
        items = []

        if filter_value == "Areas":
            items = self.model.distinct_areas(self.calendar_view.selected_calendar_id)
        elif filter_value == "Types":
            items = self.model.distinct_types(self.calendar_view.selected_calendar_id)
        elif filter_value == "Projects":
            items = self.model.distinct_projects(self.calendar_view.selected_calendar_id)
        else:
            print(f"No query: Unknow filter value {filter_value}")

        values = [item.name for item in items] 
        self.filter_view.update_item_combo_values(values)

    def handle_year_select(self):
        pass

    def handle_month_select(self):
        pass

    def handle_item_select(self):
        pass
