"""contoller.py: core part. get data from model and listen to view."""


class Controller:
    def __init__(self, context):
        self.context = context
        self.calendar_view = context.get_view("calendar")
        self.filter_view = context.get_view("filter")
        self.chart_view = context.get_view("chart")
        self.report_view = context.get_view("report")
        self.model = context.model

        self.calendar_view.register_event_handler("calendar_select", self.handle_calendar_select)
        self.filter_view.register_event_handler("year_select", self.handle_year_select)
        self.filter_view.register_event_handler("month_select", self.handle_month_select)
        self.filter_view.register_event_handler("filter_select", self.handle_filter_select)
        self.filter_view.register_event_handler("item_select", self.handle_item_select)

    def initialize(self):
        calendars = self.model.get_calendars_by_usage()
        self.calendar_view.create_cards(calendars)
        self.update_calendar_card(calendars)
        self.calendar_view.set_card_selection()

        self.update_year_widget()
        self.update_month_widget()
        self.update_item_widget()

        self.update_chart()
        self.update_report()
    
    def update_calendar_card(self, calendars):
        for calendar in calendars:
            self.calendar_view.update_card(calendar)
    

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
                rows = self.model.distinct_projects_by_year_month(calendar_id, year, month)
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


    def update_report(self):
        calendar_id = self.calendar_view.selected_calendar_id
        filter_val = self.filter_view.filter_var.get()
        item = self.filter_view.item_var.get()
        report = None

        if filter_val == "Areas":
            report = self.model.area_report(calendar_id, item)
        elif filter_val == "Types":
            pass
        elif filter_val == "Projects":
            pass
        else:
            pass

        self.report_view.vars["item_name"].set(f"Report for: {item}")
        self.report_view.vars["first_date"].set(f"First date: {report.first_date}")
        self.report_view.vars["last_date"].set(f"Last date: {report.last_date}")
        self.report_view.vars["total_days"].set(f"Total days: {report.total_days}")
        self.report_view.vars["average_day"].set(f"Avg per day: {report.average_day}")
        self.report_view.vars["total_events"].set(f"Events count: {report.total_events}")
        self.report_view.vars["total_hours"].set(f"Total hrs: {report.total_hours}")
        self.report_view.vars["average_duration"].set(f"Average: {report.average_duration}")
        self.report_view.vars["max_duration"].set(f"Average: {report.max_duration}")
        self.report_view.vars["min_duration"].set(f"Average: {report.min_duration}")



    # --------------
    # Handlers
    # ---------------
    def handle_calendar_select(self):
        self.update_year_widget()
        self.update_month_widget()
        self.update_item_widget()
        self.update_chart()
        self.update_report()

    def handle_filter_select(self): 
        self.update_item_widget()
        self.update_chart()
        self.update_report()

    
    def handle_year_select(self):
        self.update_item_widget()
        self.update_chart()
        self.update_report()
    
    def handle_month_select(self):
        self.update_item_widget()
        self.update_chart()
        self.update_report()

    def handle_item_select(self):
        self.update_chart()
        self.update_report()
    
    def update_chart(self):
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
            self.chart_view.update_stack_chart(days, hrs)
