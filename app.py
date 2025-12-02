from views import App
from models import DatabaseManager
from controllers import CalendarController, AreaController, ProjectController, ChartController


def main():
    app = App()
    db = DatabaseManager()

    # models
    calendar_model = db.calendar_model
    area_model = db.area_model
    project_model = db.project_model

    # views
    calendar_view = app.mainframe.calendar_view
    area_view = app.mainframe.area_view
    project_view = app.mainframe.project_view
    chart_view = app.mainframe.chart_view

    # controllers
    calendar_controller = CalendarController(calendar_model, calendar_view)
    area_controller = AreaController(area_model, area_view)
    project_controller = ProjectController(project_model, project_view)
    chart_controller = ChartController(
        calendar_model, 
        area_model, 
        project_model, 
        chart_view
    )

    # initializers
    calendar_controller.initialize()
    area_controller.initialize()
    project_controller.initialize()
    chart_controller.initialize()

    app.run()
    db.close()


if __name__ == "__main__":
    main()
