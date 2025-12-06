import sqlite3
from icalendar import Calendar, Event
from datetime import datetime
import pytz
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
ICS_DIR = BASE_DIR / "ics"
DB_DIR = BASE_DIR / "db"
SECONDS_PER_HOUR = 3600


class IcsToDb:
    """Convert ICS file to SQLite database with normalized schema"""

    def __init__(self, db_file="calendar.db"):
        self.db_file = db_file
        self.conn = None
        self.calendar_timezone = None

    def init_db(self):
        """Initialize database with normalized schema"""
        self.conn = sqlite3.connect(self.db_file)
        cursor = self.conn.cursor()

        # Enable foreign keys
        cursor.execute("PRAGMA foreign_keys = ON")

        # Calendar table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS calendars (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                color TEXT DEFAULT '#FF0000'
            )
        """
        )

        # Areas table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS areas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT
            )
        """
        )

        # Projects table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                area_id INTEGER,
                FOREIGN KEY (area_id) REFERENCES areas(id)
            )
        """
        )

        # Types table with area_id
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS types (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                area_id INTEGER,
                FOREIGN KEY (area_id) REFERENCES areas(id)
            )
        """
        )

        # Events table (added year, month, day, hour, minute, second fields)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                calendar_id INTEGER NOT NULL,
                summary TEXT NOT NULL,
                dtstart TEXT NOT NULL,
                dtend TEXT NOT NULL,
                duration REAL NOT NULL,
                year INTEGER,
                month INTEGER,
                day INTEGER,
                hour INTEGER,
                minute INTEGER,
                second INTEGER,
                area_id INTEGER,
                project_id INTEGER,
                type_id INTEGER,
                is_all_day INTEGER DEFAULT 0,
                FOREIGN KEY (calendar_id) REFERENCES calendars(id) ON DELETE CASCADE,
                FOREIGN KEY (area_id) REFERENCES areas(id),
                FOREIGN KEY (project_id) REFERENCES projects(id),
                FOREIGN KEY (type_id) REFERENCES types(id)
            )
        """
        )

        # Create indexes
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_events_dtstart ON events(dtstart)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_events_calendar_id ON events(calendar_id)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_events_area_id ON events(area_id)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_events_project_id ON events(project_id)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_events_type_id ON events(type_id)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_types_area_id ON types(area_id)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_events_year ON events(year)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_events_year_month ON events(year, month)"
        )

        self.conn.commit()

    def get_or_create_lookup_id(self, cursor, table_name, field_name, value):
        """Get or create ID in a lookup table"""
        if not value:
            return None

        # Normalize value: strip and lowercase
        value = value.strip().lower()
        if not value:
            return None

        cursor.execute(f"SELECT id FROM {table_name} WHERE {field_name} = ?", (value,))
        row = cursor.fetchone()

        if row:
            return row[0]
        else:
            cursor.execute(
                f"INSERT INTO {table_name} ({field_name}) VALUES (?)", (value,)
            )
            return cursor.lastrowid

    def get_or_create_project_id(self, cursor, project_name, area_name=None):
        """Get or create project ID, optionally linked to area"""
        if not project_name:
            return None

        # Normalize project_name: strip and lowercase
        project_name = project_name.strip().lower()
        if not project_name:
            return None

        # First get area_id if provided
        area_id = None
        if area_name:
            area_id = self.get_or_create_lookup_id(cursor, "areas", "name", area_name)

        cursor.execute("SELECT id FROM projects WHERE name = ?", (project_name,))
        row = cursor.fetchone()

        if row:
            return row[0]
        else:
            cursor.execute(
                """
                INSERT INTO projects (name, area_id) VALUES (?, ?)
            """,
                (project_name, area_id),
            )
            return cursor.lastrowid

    def get_or_create_type_id(self, cursor, type_name, area_name=None):
        """Get or create type ID, optionally linked to area"""
        if not type_name:
            return None

        # Normalize type_name: strip and lowercase
        type_name = type_name.strip().lower()
        if not type_name:
            return None

        # First get area_id if provided
        area_id = None
        if area_name:
            area_id = self.get_or_create_lookup_id(cursor, "areas", "name", area_name)

        cursor.execute("SELECT id FROM types WHERE name = ?", (type_name,))
        row = cursor.fetchone()

        if row:
            return row[0]
        else:
            cursor.execute(
                """
                INSERT INTO types (name, area_id) VALUES (?, ?)
            """,
                (type_name, area_id),
            )
            return cursor.lastrowid

    def strip_html_tags(self, text):
        """Remove HTML tags from text, replacing <br> with newlines"""
        import re
        if not text:
            return text
        
        text = str(text)
        # Replace <br> tags with newlines (case-insensitive, with or without /)
        text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
        # Remove all other HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        return text

    def parse_description(self, desc):
        """Parse structured description into fields (only area, type, project)"""
        fields = {
            "area": None,
            "type": None,
            "project": None,
        }

        if not desc:
            return fields

        # Remove HTML tags first
        desc = self.strip_html_tags(desc)

        for line in desc.split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip().lower()
                value = value.strip().lower()  # Convert to lowercase

                if key in fields:
                    fields[key] = value

        return fields

    def extract_datetime_components(self, dt_str):
        """Extract year, month, day, hour, minute, second from datetime string"""
        if not dt_str:
            return None, None, None, None, None, None
        
        try:
            # Parse YYYYMMDD format (all-day events)
            if len(dt_str) == 8:
                year = int(dt_str[0:4])
                month = int(dt_str[4:6])
                day = int(dt_str[6:8])
                return year, month, day, 0, 0, 0
            # Parse YYYYMMDDTHHMMSS format
            elif "T" in dt_str:
                dt_str = dt_str.rstrip("Z")
                year = int(dt_str[0:4])
                month = int(dt_str[4:6])
                day = int(dt_str[6:8])
                hour = int(dt_str[9:11])
                minute = int(dt_str[11:13])
                second = int(dt_str[13:15]) if len(dt_str) >= 15 else 0
                return year, month, day, hour, minute, second
        except (ValueError, IndexError):
            pass
        
        return None, None, None, None, None, None

    def datetime_to_str(self, dt, target_tz=None):
        """Convert datetime object to string in target timezone"""
        if dt is None:
            return None
        if isinstance(dt, str):
            return dt

        if hasattr(dt, "dt"):
            dt = dt.dt

        # Handle date objects (all-day events)
        if not isinstance(dt, datetime):
            return dt.strftime("%Y%m%d")

        # Convert to target timezone if specified
        if target_tz and dt.tzinfo:
            try:
                tz = pytz.timezone(target_tz)
                dt = dt.astimezone(tz)
            except:
                pass
        elif target_tz and not dt.tzinfo:
            # Assume UTC if no timezone info
            try:
                dt = pytz.utc.localize(dt)
                tz = pytz.timezone(target_tz)
                dt = dt.astimezone(tz)
            except:
                pass

        return dt.strftime("%Y%m%dT%H%M%S")

    def import_calendar(self, ics_file, color=None):
        """Import ICS file to SQLite database with normalized schema"""
        with open(ics_file, "rb") as f:
            cal = Calendar.from_ical(f.read())

        self.init_db()
        cursor = self.conn.cursor()

        # Extract calendar timezone
        self.calendar_timezone = str(cal.get("x-wr-timezone", ""))
        calendar_name = Path(ics_file).stem

        print(f"Processing calendar: {calendar_name}")
        print(f"Calendar timezone: {self.calendar_timezone or 'Not specified'}")

        # Get or create calendar
        calendar_id = self.get_or_create_lookup_id(
            cursor, "calendars", "name", calendar_name
        )
        if color and calendar_id:
            cursor.execute(
                "UPDATE calendars SET color = ? WHERE id = ?", (color, calendar_id)
            )

        event_count = 0
        for component in cal.walk():
            if component.name == "VEVENT":
                desc_fields = self.parse_description(component.get("description", ""))

                dtstart = component.get("dtstart")
                dtend = component.get("dtend")
                is_all_day = 0
                if dtstart and not isinstance(dtstart.dt, datetime):
                    is_all_day = 1

                # Convert to calendar timezone if specified
                dtstart_str = self.datetime_to_str(
                    dtstart, self.calendar_timezone if not is_all_day else None
                )
                dtend_str = self.datetime_to_str(
                    component.get("dtend"),
                    self.calendar_timezone if not is_all_day else None,
                )

                # Calculate duration in hours (0 for all-day events)
                duration = 0
                if not is_all_day and dtstart and dtend:
                    duration = (
                        dtend.dt - dtstart.dt
                    ).total_seconds() / SECONDS_PER_HOUR

                # Get foreign key IDs for normalized fields
                area_id = self.get_or_create_lookup_id(
                    cursor, "areas", "name", desc_fields["area"]
                )
                type_id = self.get_or_create_type_id(
                    cursor, desc_fields["type"], desc_fields["area"]
                )
                project_id = self.get_or_create_project_id(
                    cursor, desc_fields["project"], desc_fields["area"]
                )

                # Extract datetime components from dtstart
                year, month, day, hour, minute, second = self.extract_datetime_components(dtstart_str)

                try:
                    cursor.execute(
                        """
                        INSERT INTO events (
                            calendar_id, summary, dtstart, dtend, duration,
                            year, month, day, hour, minute, second,
                            area_id, project_id, type_id, is_all_day
                        ) VALUES  (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            calendar_id,
                            str(component.get("summary", "")),
                            dtstart_str,
                            dtend_str,
                            duration,
                            year,
                            month,
                            day,
                            hour,
                            minute,
                            second,
                            area_id,
                            project_id,
                            type_id,
                            is_all_day,
                        ),
                    )

                    event_count += 1
                except sqlite3.IntegrityError as e:
                    print(f"Skipping event: {e}")

        self.conn.commit()
        self.conn.close()

        print(f"Imported {event_count} events to {self.db_file}")
        return event_count


class DbToIcs:
    """Convert SQLite database to ICS file with normalized schema"""

    def __init__(self, db_file="calendar.db"):
        self.db_file = db_file
        self.conn = None

    def get_lookup_value(self, cursor, table_name, id_value):
        """Get name from lookup table by ID"""
        if not id_value:
            return None

        cursor.execute(f"SELECT name FROM {table_name} WHERE id = ?", (id_value,))
        row = cursor.fetchone()
        return row[0] if row else None

    def format_description(self, event_row, cursor):
        """Format event fields back to description from normalized tables"""
        parts = []

        # Get values from lookup tables
        area_name = self.get_lookup_value(cursor, "areas", event_row["area_id"])
        type_name = self.get_lookup_value(cursor, "types", event_row["type_id"])
        project_name = self.get_lookup_value(
            cursor, "projects", event_row["project_id"]
        )

        if area_name:
            parts.append(f"Area: {area_name}")
        if type_name:
            parts.append(f"Type: {type_name}")
        if project_name:
            parts.append(f"Project: {project_name}")

        return "\n".join(parts)

    def str_to_datetime(self, dt_str):
        """Convert string to datetime/date object for icalendar"""
        if not dt_str:
            return None

        try:
            # Check if it's a date-only string (YYYYMMDD)
            if len(dt_str) == 8:
                return datetime.strptime(dt_str, "%Y%m%d").date()
            # Check if it's a datetime string (YYYYMMDDTHHMMSS)
            elif "T" in dt_str:
                # Remove timezone suffix if present
                dt_str = dt_str.rstrip("Z")
                return datetime.strptime(dt_str, "%Y%m%dT%H%M%S")
            else:
                # Try other formats or return as is
                return datetime.strptime(dt_str, "%Y%m%d")
        except Exception as e:
            print(f"Warning: Could not parse date '{dt_str}': {e}")
            return None

    def export_calendar(self, ics_file, calendar_name=None):
        """Export SQLite database to ICS file"""
        self.conn = sqlite3.connect(self.db_file)
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()

        cal = Calendar()
        cal.add("prodid", "-//Calendar Sync//mxm.dk//")
        cal.add("version", "2.0")

        # Build events query based on calendar filter
        if calendar_name:
            cursor.execute("SELECT id FROM calendars WHERE name = ?", (calendar_name,))
            calendar_row = cursor.fetchone()
            if calendar_row:
                calendar_id = calendar_row["id"]
                cursor.execute(
                    """
                    SELECT e.* FROM events e 
                    WHERE e.calendar_id = ?
                    ORDER BY e.dtstart
                """,
                    (calendar_id,),
                )
            else:
                print(f"Calendar '{calendar_name}' not found")
                return 0
        else:
            # Export all events from all calendars
            cursor.execute("SELECT * FROM events ORDER BY dtstart")

        events = cursor.fetchall()

        for event_row in events:
            event = Event()

            # Convert string dates to proper objects
            dtstart = self.str_to_datetime(event_row["dtstart"])
            dtend = self.str_to_datetime(event_row["dtend"])
            print(dtstart, dtend)

            if not dtstart or not dtend:
                print(f"Skipping event {event_row['id']} due to invalid dates")
                continue

            # Add basic event properties
            event.add("uid", f"event-{event_row['id']}")
            event.add("dtstart", dtstart)
            event.add("dtend", dtend)
            event.add("summary", event_row["summary"])
            event.add("dtstamp", datetime.now())

            # Build description from normalized fields
            description = self.format_description(event_row, cursor)
            if description:
                event.add("description", description)

            cal.add_component(event)

        # Write to file
        with open(ics_file, "wb") as f:
            f.write(cal.to_ical())

        self.conn.close()
        print(f"Exported {len(events)} events to {ics_file}")
        return len(events)


def setup_dirs():
    """Ensure necessary directories exist."""
    ICS_DIR.mkdir(exist_ok=True)
    DB_DIR.mkdir(exist_ok=True)
    print(f"ICS Directory: {ICS_DIR}")
    print(f"DB Directory: {DB_DIR}")


def merge_to_one_db(output_db_file="data.db"):
    """
    Imports all ICS files from the ICS_DIR into a single SQLite database file.
    It deletes the existing output_db_file first to ensure a fresh start.
    """
    setup_dirs()

    output_db_path = DB_DIR / output_db_file

    if output_db_path.exists():
        output_db_path.unlink()
        print(f"Removed existing database: {output_db_file}")

    colors = {
        "work": "#489160",
        "saeed": "#7C7C7C",
        "study": "#4B99D2",
        "growth": "#A479B1",
    }

    importer = IcsToDb(output_db_path)
    importer.init_db()

    total_events_imported = 0
    for ics_file_path in ICS_DIR.glob("*.ics"):
        color = colors.get(ics_file_path.stem)
        print(f"\nImporting {ics_file_path.name} into {output_db_file}...")

        total_events_imported += importer.import_calendar(ics_file_path, color)

    print(f"\nAll ICS files imported successfully.")
    print(f"Total events imported: **{total_events_imported}**")
    print(f"Database created at: **{output_db_path}**")


def to_db():
    colors = {
        "work": "#489160",
        "saeed": "#7C7C7C",
        "study": "#4B99D2",
        "growth": "#A479B1",
    }
    for ics_file_path in ICS_DIR.glob("*.ics"):
        db_file_name = ics_file_path.stem + ".db"
        color = colors.get(ics_file_path.stem)
        importer = IcsToDb(Path(DB_DIR / db_file_name))
        importer.import_calendar(ics_file_path, color)


def to_ics():
    for db_file_path in DB_DIR.glob("*.db"):
        ics_file_name = db_file_path.stem + ".ics"
        exporter = DbToIcs(Path(db_file_path))
        exporter.export_calendar(ICS_DIR / ics_file_name)


if __name__ == "__main__":
    merge_to_one_db()
    # to_db()
