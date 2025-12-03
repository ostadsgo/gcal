"""contoller.py: core part. get data from model and listen to view."""

class CalendarController:
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
        # Update areas
        areas = self.model.get_top_areas(calendar_id, limit=5)
        area_view = self.context.get_view("area")
        for index, area in enumerate(areas):
            area_view.update_card(index, area)

        # Update Projects
        projects = self.model.get_top_projects(calendar_id, limit=5)
        project_view = self.context.get_view("project")
        for index, project in enumerate(projects):
            project_view.update_card(index, project)


class AreaController:
    def __init__(self, context):
        self.model = context.model
        self.view = context.get_view("area")

    def initialize(self):
        areas = self.model.get_top_areas(limit=5)
        self.view.create_cards(areas)

        # update calendar cards
        for index, area in enumerate(areas):
            self.view.update_card(index, area)


class ProjectController:
    def __init__(self, context):
        self.model = context.model
        self.view = context.get_view("project")

    def initialize(self):
        projects = self.model.get_top_projects(limit=5)
        self.view.create_cards(projects)

        # update calendar cards
        for index, project in enumerate(projects):
            self.view.update_card(index, project)


class ChartController:
    def __init__(self, context):
        self.model = context.model
        self.view = context.get_view("chart")

    def initialize(self):
        self.view.setup_ui()
        self.update_calendar_chart()
        self.update_area_chart()
        self.update_project_chart()

    def update_calendar_chart(self):
        calendars = self.model.get_calendars_by_usage()
        self.view.update_calendar_chart(calendars)

    def update_area_chart(self):
        areas = self.model.get_top_areas(limit=5)
        self.view.update_area_chart(areas)

    def update_project_chart(self):
        projects = self.model.get_top_projects(limit=5)
        self.view.update_project_chart(projects)

