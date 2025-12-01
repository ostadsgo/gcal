from views import App
from models import DatabaseManager
from controllers import CalendarController, AreaController


def main():
    app = App()
    db = DatabaseManager()

    # model objects
    calendar_model = db.calendar_model
    area_model = db.area_model

    # view objects
    calendar_view = app.mainframe.calendar_view
    area_view = app.mainframe.area_view

    # controllers
    calendar_controller = CalendarController(calendar_model, calendar_view)
    area_controller = AreaController(area_model, area_view)

    # initializers
    calendar_controller.initialize()
    area_controller.initialize()

    app.run()
    db.close()


if __name__ == "__main__":
    main()
