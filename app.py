from views import App
from models import DatabaseManager
from controllers import CalendarController


def main():
    app = App()
    db = DatabaseManager()

    calendar_model = db.calendar_model
    calendar_view = app.mainframe.calendar_view

    calendar_controller = CalendarController(calendar_model, calendar_view)
    calendar_controller.initialize()

    app.run()
    db.close()


if __name__ == "__main__":
    main()
