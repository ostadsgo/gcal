""" utils.py - Contins helper clasess and function which are outside of MVC."""

from pathlib import Path
from icalendar import Calendar

class ICSParser:
    """ Parse .ics file using icalendar and extract data."""

    def __init__(self):
        pass

    def parse_file(self, file_path):
        file_path = Path(file_path)

        if not file_path.exists():
            return FileNotFoundError(f"ics file not found {file_path}")

        # read and parse the file; error if couldn't parse
        try:
            with open(file_path, 'rb') as f:
                cal = Calendar.from_ical(f.read())
        except Exception as e:
            raise ValueError(f"Failed to parse ICS file {file_path}: {e}")

        # Extract calendar data with defaults
        name = str(cal.get('NAME', 'Unknown'))
        color = str(cal.get('COLOR', '#FF0000'))

        return {
            'name': name,
            'color': color,
            'file_path': file_path
        }
    
