

from views import App, CalendarView
from controllers import CalendarController
from models import DatabaseManager, CalendarModel

def main():
    app = App()

    db = DatabaseManager()
    model = CalendarModel(db)
    
    view = CalendarView()

    controller = CalendarController(model, view)






    db.close()
    app.run()



if __name__ == "__main__":
    main()
