"""contoller.py: core part. get data from model and listen to view."""


class CalendarController:
    def __init__(self, model, view):
        self.model = model
        self.view = view

        # self.view.register_event_handler("button_clicked", None)

    def initialize(self):
        calendars = self.model.get_calendars_by_usage()
        self.view.create_cards(calendars)

        # update calendar cards
        for calendar in calendars:
            self.view.update_card(calendar)


class AreaController:
    def __init__(self, model, view):
        self.model = model
        self.view = view

    def initialize(self):
        areas = self.model.get_top_areas(limit=5)
        self.view.create_cards(areas)

        # update calendar cards
        for area in areas:
            self.view.update_card(area)


class ProjectController:
    def __init__(self, model, view):
        self.model = model
        self.view = view

    def initialize(self):
        projects = self.model.get_top_projects(limit=5)
        self.view.create_cards(projects)

        # update calendar cards
        for project in projects:
            self.view.update_card(project)


class ChartController:
    def __init__(self, calendar_model, area_model, project_model, view):
        self.calendar_model = calendar_model
        self.area_model = area_model
        self.project_model = project_model
        self.view = view

    def initialize(self):
        self.view.setup_ui()
        self.update_calendar_chart()
        self.update_area_chart()
        self.update_project_chart()

    def update_calendar_chart(self):
        calendars = self.calendar_model.get_calendars_by_usage()
        self.view.update_calendar_chart(calendars)

    def update_area_chart(self):
        areas = self.area_model.get_top_areas(limit=5)
        self.view.update_area_chart(areas)

    def update_project_chart(self):
        projects = self.project_model.get_top_projects(limit=5)
        self.view.update_project_chart(projects)
