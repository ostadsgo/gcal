"""contoller.py: core part. get data from model and listen to view."""


class Controller:
    def __init__(self, context):
        self.context = context
        self.model = context.model
        self.calendar_view = context.get_view("calendar")
        self.filter_view = context.get_view("filter")
        self.filter_report_view = context.get_view("filter_report")
        self.stack_chart_view = context.get_view("stack_chart")
        self.bar_chart_view = context.get_view("bar_chart")
        self.hbar_chart_view = context.get_view("hbar_chart")
        self.pie_chart_view = context.get_view("pie_chart")
        print(self.pie_chart_view)

        # Register events
        self.calendar_view.register_event_handler(
            "calendar_select", self.handle_calendar_select
        )
        self.filter_view.register_event_handler("year_select", self.handle_year_select)
        self.filter_view.register_event_handler(
            "month_select", self.handle_month_select
        )
        self.filter_view.register_event_handler(
            "filter_select", self.handle_filter_select
        )
        self.filter_view.register_event_handler("item_select", self.handle_item_select)

    def initialize(self):
        """First load +  methods must only run once."""

        # calendars
        self.create_calendars_card()
        self.update_calendars_card()
        self.calendar_set_selection()

        # widgets
        self.update_year_widget()
        self.update_month_widget()
        self.update_item_widget()

        # Charts
        self.update_stack_chart()
        self.update_hbar_chart()
        self.update_bar_chart()
        self.update_pie_chart()

        # Reports
        self.update_filter_report()

    def create_calendars_card(self):
        calendars = self.model.get_calendars_by_usage()
        self.calendar_view.create_cards(calendars)

    def update_calendars_card(self):
        calendars = self.model.get_calendars_by_usage()
        for calendar in calendars:
            self.calendar_view.update_card(calendar)

    def calendar_set_selection(self):
        self.calendar_view.set_card_selection()

    def update_year_widget(self):
        calendar_id = self.calendar_view.selected_calendar_id
        rows = self.model.distinct_years(calendar_id)
        years = [row.year for row in rows]
        self.filter_view.year_combo["values"] = years
        if years:
            self.filter_view.year_var.set(years[0])
        else:
            self.filter_view.year_var.set("")

    def update_month_widget(self):
        calendar_id = self.calendar_view.selected_calendar_id
        rows = self.model.distinct_months(calendar_id)
        months = [row.month for row in rows]
        self.filter_view.month_combo["values"] = months
        if months:
            self.filter_view.month_var.set(months[0])
        else:
            self.filter_view.month_var.set("")

    def update_item_widget(self):
        calendar_id = self.calendar_view.selected_calendar_id
        year = self.filter_view.year_var.get()
        month = self.filter_view.month_var.get()
        filter_val = self.filter_view.filter_var.get()
        if all([year, month, filter_val]):

            if filter_val == "Areas":
                rows = self.model.distinct_areas_by_year_month(calendar_id, year, month)
            elif filter_val == "Types":
                rows = self.model.distinct_types_by_year_month(calendar_id, year, month)
            elif filter_val == "Projects":
                rows = self.model.distinct_projects_by_year_month(
                    calendar_id, year, month
                )
            else:
                print(f"Unknow filter. {filter_val}.")

            items = [row.name for row in rows]
            self.filter_view.item_combo["values"] = items
            if items:
                self.filter_view.item_var.set(items[0])
            else:
                self.filter_view.item_var.set("")
        else:
            self.filter_view.item_var.set("")

    def update_filter_report(self):
        calendar_id = self.calendar_view.selected_calendar_id
        year = self.filter_view.year_var.get()
        month = self.filter_view.month_var.get()
        filter_val = self.filter_view.filter_var.get()
        item = self.filter_view.item_var.get()
        report = None

        if filter_val == "Areas":
            report = self.model.area_report(calendar_id, year, month, item)
        elif filter_val == "Types":
            report = self.model.type_report(calendar_id, year, month, item)
        elif filter_val == "Projects":
            report = self.model.project_report(calendar_id, year, month, item)
        else:
            print("Unkown filter value in update report.")

        self.filter_report_view.update_rows(item, report)

    def update_bar_chart(self):
        calendar_id = self.calendar_view.selected_calendar_id
        top_types = self.model.get_top_types(calendar_id)
        self.bar_chart_view.update_bar_chart(top_types)

    def update_stack_chart(self):
        calendar_id = self.calendar_view.selected_calendar_id
        year = self.filter_view.year_var.get()
        month = self.filter_view.month_var.get()
        filter_val = self.filter_view.filter_var.get()
        item = self.filter_view.item_var.get()
        rows = None
        if item:
            if filter_val == "Areas":
                rows = self.model.area_daily_duration(calendar_id, year, month, item)
            elif filter_val == "Types":
                rows = self.model.type_daily_duration(calendar_id, year, month, item)
            elif filter_val == "Projects":
                rows = self.model.project_daily_duration(calendar_id, year, month, item)
            else:
                print(f"Unknow filter. {filter_val}.")

            # chart
            days = [row.day for row in rows]
            hrs = [row.total_duration for row in rows]
            calendar_id = self.calendar_view.selected_calendar_id
            calendar = self.model.get_calendar_by_usage(calendar_id)
            self.stack_chart_view.update_stack_chart(days, hrs, calendar.calendar_color)

    def update_hbar_chart(self):
        calendar_id = self.calendar_view.selected_calendar_id
        top_areas = self.model.get_top_areas(calendar_id)
        self.hbar_chart_view.update_hbar_chart(top_areas)

    def update_pie_chart(self):
        calendars = self.model.get_calendars_by_usage()
        self.pie_chart_view.update_pie_chart(calendars)

    # --------------
    # Handlers
    # ---------------
    def handle_calendar_select(self):
        self.update_pie_chart()
        self.update_year_widget()
        self.update_month_widget()
        self.update_item_widget()
        self.update_stack_chart()
        self.update_hbar_chart()
        self.update_bar_chart()
        self.update_filter_report()

    def handle_filter_select(self):
        self.update_item_widget()
        self.update_stack_chart()
        self.update_filter_report()

    def handle_year_select(self):
        self.update_item_widget()
        self.update_stack_chart()
        self.update_filter_report()

    def handle_month_select(self):
        self.update_item_widget()
        self.update_stack_chart()
        self.update_filter_report()

    def handle_item_select(self):
        self.update_stack_chart()
        self.update_filter_report()
