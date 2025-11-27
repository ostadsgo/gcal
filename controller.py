""" contoller.py: core part. get data from model and listen to view."""

from pathlib import Path

from model import DatabaseManager
from utils import ICSParser


BASE_DIR = Path(__file__).resolve().parent
CALENDARS_DIR = BASE_DIR / "calendars"

class CalendarController:
    def __init__(self, db):
        self.db = db
        self.parser = ICSParser()

    def populate_calendars(self):
        ics_files = list(CALENDARS_DIR.glob('*.ics'))
        for ics_file in ics_files:
            cal_data = self.parser.parse_file(ics_file)
            if not self.db.calendar.exists(cal_data["name"]):
                calendar_id = self.db.calendar.insert(
                    cal_data["name"],
                    cal_data["color"]
                )
                print(f"Calendar {cal_data['name']} added to db.")
            else:
                print(f"Calendar {cal_data['name']} already exist.")


if __name__ == "__main__":
    db = DatabaseManager()
    cal = CalendarController(db)
    cal.populate_calendars()
