from utils import ICSParser

# Create parser instance
parser = ICSParser()

# Parse a single file
try:
    calendar_data = parser.parse_file('calendars/work.ics')
    print(calendar_data)
except (FileNotFoundError, ValueError) as e:
    print(f"Error: {e}")
