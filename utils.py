""" utils.py - Contins helper clasess and function which are outside of MVC."""

from pathlib import Path
from icalendar import Calendar
from model import DatabaseManager

BASE_DIR = Path(__file__).resolve().parent
CALENDARS_DIR = BASE_DIR / "calendars"
SECONDS_PER_HOUR = 3600


def get_ics_files():
    return list(CALENDARS_DIR.glob('*.ics'))

def read_ics_file(file_path):
    try:
        with open(file_path, 'rb') as f:
            cal = Calendar.from_ical(f.read())
        return cal
    except Exception as e:
        raise ValueError(f"Failed to parse ICS file {file_path}: {e}")

def check_file_path(file_path):
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"ICS file not found: {file_path}")
    return file_path


def parse_event_metadata(description):
    keys = ['area', 'project', 'tags', 'difficulty', 'detail']
    values = [None, None, [], None, None]
    metadata = dict(zip(keys, values))

    if not description:
        return metadata
    
    lines = description.lower().strip().split('\n')
    for line in lines:
        line = line.strip()
        
        if ':' not in line:
            continue
        
        key, value = line.split(':', 1)
        key = key.strip()
        value = value.strip()
        
        # Skip empty values
        if not value:
            continue
        
        if key == 'area':
            metadata['area'] = value
        elif key == 'project':
            metadata['project'] = value
        elif key == 'tags':
            metadata['tags'] = [tag.strip() for tag in value.split(',') if tag.strip()]
        elif key == 'difficulty':
            metadata['difficulty'] = value
        elif key == 'detail':
            metadata['detail'] = value
    
    return metadata


class ICSParser:
    """ Parse .ics file using icalendar and extract data."""

    def __init__(self):
        pass

    def parse_file(self, file_path):
        file_path = check_file_path(file_path)

        if not file_path.exists():
            return FileNotFoundError(f"ics file not found {file_path}")

        # read and parse the file; error if couldn't parse
        cal = read_ics_file(file_path)

        # Extract calendar data with defaults
        name = str(cal.get('NAME', 'Unknown'))
        color = str(cal.get('COLOR', '#FF0000'))

        return {
            'name': name,
            'color': color,
            'file_path': file_path
        }
        # Add to ICSParser class in utils.py

    def parse_events(self, file_path):
        file_path = check_file_path(file_path)
        cal = read_ics_file(file_path)
        
        events = []
        
        for component in cal.walk():
            if component.name == "VEVENT":
                # Extract basic event data
                summary = str(component.get('SUMMARY', 'Untitled'))
                dtstart = component.get('DTSTART').dt
                dtend = component.get('DTEND').dt
                description = str(component.get('DESCRIPTION', ''))
                duration = (dtend - dtstart).total_seconds() / SECONDS_PER_HOUR
                
                metadata = parse_event_metadata(description)
                
                event_data = {
                    'summary': summary,
                    'dtstart': dtstart.isoformat(),
                    'dtend': dtend.isoformat(),
                    'duration': duration,
                    'area': metadata['area'],
                    'project': metadata['project'],
                    'tags': metadata['tags'],
                    'difficulty': metadata['difficulty'],
                    'detail': metadata['detail']
                }
                
                events.append(event_data)
        
        return events
    

class ICSImporter:
    """Import .ics files into database - replaces all existing data"""
    
    def __init__(self, db):
        self.db = db
        self.parser = ICSParser()
    
    def import_fresh(self):
        """Clear database and import all .ics files fresh"""
        print("Clearing existing data...")
        self.clear_all_data()
        
        print("Importing calendars...")
        self.populate_calendars()
        
        print("Importing events...")
        self.populate_events()
        
        print("Import complete!")
    
    def clear_all_data(self):
        """Delete all data from database"""
        self.db.execute("DELETE FROM event_tags")
        self.db.execute("DELETE FROM events")
        self.db.execute("DELETE FROM tags")
        self.db.execute("DELETE FROM calendars")
    
    def populate_calendars(self):
        """Import calendars from .ics files"""
        ics_files = get_ics_files()
        
        for ics_file in ics_files:
            cal_data = self.parser.parse_file(ics_file)
            calendar_id = self.db.calendar.insert(
                cal_data["name"],
                cal_data["color"]
            )
            print(f"Calendar '{cal_data['name']}' imported")
    
    def populate_events(self):
        """Import events from .ics files"""
        ics_files = get_ics_files()
        
        for ics_file in ics_files:
            cal_data = self.parser.parse_file(ics_file)
            calendar_id = self.db.calendar.get_id_by_name(cal_data['name'])
            
            if not calendar_id:
                print(f"Calendar '{cal_data['name']}' not found, skipping events")
                continue
            
            events = self.parser.parse_events(ics_file)
            
            for event in events:
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
            
            print(f"{len(events)} events from '{cal_data['name']}' imported")


if __name__ == "__main__":
    print("=" * 50)
    print("Calendar Data Import")
    print("=" * 50)
    
    with DatabaseManager() as db:
        importer = ICSImporter(db)
        importer.import_fresh()
    
    print("=" * 50)
    print("Done! You can now run your app.")

