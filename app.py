from views import App
from controllers import Controller


class AppContext:
    def __init__(self, app):
        self.app = app
        self.controllers = {}
        self.views = {}

    def setup(self):
        # views
        self.views["action"] = self.app.mainframe.action_view
        self.views["calendar"] = self.app.mainframe.calendar_view
        self.views["filter"] = self.app.mainframe.filter_view
        self.views["report"] = self.app.mainframe.report_view
        self.views["stack_chart"] = self.app.mainframe.stack_chart_view
        self.views["bar_chart"] = self.app.mainframe.bar_chart_view
        self.views["hbar_chart"] = self.app.mainframe.hbar_chart_view
        self.views["pie_chart"] = self.app.mainframe.pie_chart_view

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
    controller = context.controllers["controller"]

    app.run()
    # clean up database right after app closing 
    controller.db.close()


if __name__ == "__main__":
    main()
