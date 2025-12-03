from views import App
from models import db
from controllers import Controller


class AppContext:
    def __init__(self, app):
        self.app = app
        self.model = db.model
        self.controllers = {}
        self.views = {}

    def setup(self):
        # views
        self.views["calendar"] = self.app.mainframe.calendar_view
        self.views["filter"] = self.app.mainframe.filter_view
        self.views["report"] = self.app.mainframe.report_view
        self.views["chart"] = self.app.mainframe.chart_view

        # controllers
        self.controllers["controller"] = Controller(self)
        self.controllers["controller"].initialize()

        return self

    def get_controller(self, name):
        return self.controllers.get(name)

    def get_view(self, name):
        return self.views.get(name)


def main():
    app = App()

    context = AppContext(app)
    context.setup()

    app.run()
    db.close()


if __name__ == "__main__":
    main()
