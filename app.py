from views import App
from models import DatabaseManager
from controllers import CalendarController, AreaController, ProjectController


def main():
    app = App()
    db = DatabaseManager()

    # model objects
    calendar_model = db.calendar_model
    area_model = db.area_model
    project_model = db.project_model

    # view objects
    calendar_view = app.mainframe.calendar_view
    area_view = app.mainframe.area_view
    project_view = app.mainframe.project_view

    # controllers
    calendar_controller = CalendarController(calendar_model, calendar_view)
    area_controller = AreaController(area_model, area_view)
    project_controller = ProjectController(project_model, project_view)

    # initializers
    calendar_controller.initialize()
    area_controller.initialize()
    project_controller.initialize()

    app.run()
    db.close()


if __name__ == "__main__":
    main()
