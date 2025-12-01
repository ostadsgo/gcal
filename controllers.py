"""contoller.py: core part. get data from model and listen to view."""


class CalendarController:
    def __init__(self, model, view):
        self.model = model
        self.view = view

        # self.view.register_event_handler("button_clicked", None)

    def initialize(self):
        self.create_cards()
        self.update_cards()

    def create_cards(self):
        rows = self.model.get_calendars()
        rows.sort(key=lambda row: row["total_duration"], reverse=True)

        # Extract each calendar name which already sorted by duration.
        calendar_names = [row["calendar_name"] for row in rows]
        self.view.create_cards(calendar_names)

    def update_cards(self):
        rows = self.model.get_calendars()
        rows.sort(key=lambda row: row["total_duration"], reverse=True)

        for calendar in rows:
            self.view.update_card(calendar) 

class AreaController:
    def __init__(self, model, view):
        self.model = model
        self.view = view

    def initialize(self):
        self.create_cards()
        self.update_cards()

    def create_cards(self):
        rows = self.model.get_areas()
        rows.sort(key=lambda row: row["total_hours"], reverse=True)
        area_names = [row["area_name"] for row in rows]
        self.view.create_cards(area_names[:5])

    def update_cards(self):
        areas = self.model.get_areas()
        areas.sort(key=lambda row: row["total_hours"], reverse=True)
        for area in areas[:5]:
            self.view.update_card(area)


class ProjectController:
    def __init__(self, model, view):
        self.model = model
        self.view = view

    def initialize(self):
        self.create_cards()
        self.update_cards()

    def create_cards(self):
        rows = self.model.get_projects()
        rows.sort(key=lambda row: row["total_hours"], reverse=True)
        project_names = [row["project_name"] for row in rows]
        self.view.create_cards(project_names[:5])

    def update_cards(self):
        projects = self.model.get_projects()
        projects.sort(key=lambda row: row["total_hours"], reverse=True)
        for project in projects[:5]:
            self.view.update_card(project)


