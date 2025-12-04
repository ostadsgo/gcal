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

        self.update_item_widget()
        self.update_year_widget()
        self.update_month_widget()

        self.update_calendar_card(calendars)

        # must be after (create_cards)
        self.calendar_view.set_card_selection()

    def update_calendar_card(self, calendars):
        for calendar in calendars:
            self.calendar_view.update_card(calendar)

    def update_item_widget(self):
        calendar_id = self.calendar_view.selected_calendar_id
        rows = self.model.distinct_areas(calendar_id)
        items = [row.name for row in rows]
        self.filter_view.item_combo.set(items)
        self.filter_view.item_var.set(items[0])

    def update_year_widget(self):
        calendar_id = self.calendar_view.selected_calendar_id
        rows = self.model.distinct_years(calendar_id)
        years = [row.year for row in rows]
        self.filter_view.year_combo["values"] = years
        self.filter_view.year_var.set(years[0])

    def update_month_widget(self):
        calendar_id = self.calendar_view.selected_calendar_id
        rows = self.model.distinct_months(calendar_id)
        months = [row.month for row in rows]
        self.filter_view.month_combo["values"] = months
        self.filter_view.month_var.set(months[0])

    def handle_calendar_select(self):
        self.update_year_widget()
        self.update_month_widget()
        print(f"Calendar with id {self.calendar_view.selected_calendar_id} selected")


    def handle_filter_select(self): 
        items = []
        calendar_id = self.calendar_view.selected_calendar_id
        filter_value = self.filter_view.filter_var.get()

        if filter_value == "Areas":
            items = self.model.distinct_areas(calendar_id)
        elif filter_value == "Types":
            items = self.model.distinct_types(calendar_id)
        elif filter_value == "Projects":
            items = self.model.distinct_projects(calendar_id)
        else:
            print(f"No query: Unknow filter value {filter_value}")

        values = [item.name for item in items] 
        self.filter_view.update_item_combo_values(values)

    def handle_year_select(self):
        # Update month combo values by year
        calendar_id = self.calendar_view.selected_calendar_id
        year = self.filter_view.year_var.get()
        rows = self.model.distinct_months_by_year(calendar_id, year)
        months = [row.month for row in rows]
        self.filter_view.month_var.set(months[0])
        self.filter_view.month_combo["values"] = months

    def handle_month_select(self):
        pass

    def handle_item_select(self):
        pass
