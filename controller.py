""" contoller.py: core part. get data from model and listen to view."""

from model import DatabaseManager
from utils import ICSParser, get_ics_files



class CalendarController:
    def __init__(self, db):
        self.db = db
        self.parser = ICSParser()

    def populate_calendars(self):
        ics_files = get_ics_files()
        print(ics_files)

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

    def populate_events(self):
        ics_files = get_ics_files()

        for ics_file in ics_files:
            cal_data = self.parser.parse_file(ics_file)
            calendar_id = self.db.calendar.get_id_by_name(cal_data['name'])
            
            if not calendar_id:
                print(f"Calendar {cal_data['name']} not found. Skipping events.")
                continue
            
            # Get events from file
            events = self.parser.parse_events(ics_file)
            
            for event in events:
                # Insert event
                event_id = self.db.event.insert(
                    calendar_id=calendar_id,
                    summary=event['summary'],
                    dtstart=event['dtstart'],
                    dtend=event['dtend'],
                    duration=event['duration'],
                    area=event['area'],
                    project=event['project'],
                    difficulty=event['difficulty'],
                    detail=event['detail']
                )
                
                for tag_name in event['tags']:
                    tag_id = self.db.tag.get_or_create(tag_name)
                    self.db.tag.link_event_tag(event_id, tag_id)
                
                print(f"Event '{event['summary']}' added.")

if __name__ == "__main__":
    with DatabaseManager() as db:
        controller = CalendarController(db)
        controller.populate_calendars()
        controller.populate_events()
