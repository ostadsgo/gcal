from views import App
from models import db
from controllers import (
    CalendarController,
    AreaController,
    ProjectController,
    ChartController,
)

class AppContext:
    def __init__(self, app):
        self.app = app
        self.model = db.model
        self.controllers = {}
        self.views = {}
    
    def setup(self):
        # views
        self.views['calendar'] = self.app.mainframe.calendar_view
        self.views['area'] = self.app.mainframe.area_view
        self.views['project'] = self.app.mainframe.project_view
        self.views['chart'] = self.app.mainframe.chart_view
        
        # controllers
        self.controllers['calendar'] = CalendarController(self)
        self.controllers['area'] = AreaController(self)
        self.controllers['project'] = ProjectController(self)
        self.controllers['chart'] = ChartController(self)

        # initialize controllers
        self.controllers['calendar'].initialize()
        self.controllers['area'].initialize()
        self.controllers['project'].initialize()
        self.controllers['chart'].initialize()
        
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
