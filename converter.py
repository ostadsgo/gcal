"""
Calendar Sync - Convert between ICS files and SQLite database with normalized schema

Dependencies:
    - icalendar: pip install icalendar
    - pytz: pip install pytz

Usage:
    from converter import IcsToDb, DbToIcs

    # Import ICS to database
    importer = IcsToDb('calendar.db')
    importer.import_calendar('calendar.ics')

    # Export database to ICS
    exporter = DbToIcs('calendar.db')
    exporter.export_calendar('output.ics')
"""

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

        # Calendar table (existing)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS calendars (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                color TEXT DEFAULT '#FF0000'
            )
        """
        )

        # New normalized tables
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS areas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT
            )
        """
        )

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

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS types (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT
            )
        """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS difficulties (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                level INTEGER UNIQUE NOT NULL,
                label TEXT UNIQUE NOT NULL,
                description TEXT
            )
        """
        )

        # Events table with foreign keys
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                calendar_id INTEGER NOT NULL,
                summary TEXT NOT NULL,
                dtstart TEXT NOT NULL,
                dtend TEXT NOT NULL,
                duration REAL NOT NULL,
                area_id INTEGER,
                project_id INTEGER,
                type_id INTEGER,
                difficulty_id INTEGER,
                detail TEXT,
                FOREIGN KEY (calendar_id) REFERENCES calendars(id) ON DELETE CASCADE,
                FOREIGN KEY (area_id) REFERENCES areas(id),
                FOREIGN KEY (project_id) REFERENCES projects(id),
                FOREIGN KEY (type_id) REFERENCES types(id),
                FOREIGN KEY (difficulty_id) REFERENCES difficulties(id)
            )
        """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
        """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS event_tags (
                event_id INTEGER NOT NULL,
                tag_id INTEGER NOT NULL,
                PRIMARY KEY (event_id, tag_id),
                FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
                FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
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
            "CREATE INDEX IF NOT EXISTS idx_events_difficulty_id ON events(difficulty_id)"
        )

        # Insert default difficulty levels
        self._insert_default_difficulties(cursor)

        self.conn.commit()

    def _insert_default_difficulties(self, cursor):
        """Insert default difficulty levels if they don't exist"""
        difficulties = [
            (1, "Very Easy", "Minimal effort required"),
            (2, "Easy", "Straightforward task"),
            (3, "Medium", "Moderate effort required"),
            (4, "Hard", "Challenging task"),
            (5, "Very Hard", "Complex, requires significant effort"),
        ]

        for level, label, description in difficulties:
            cursor.execute(
                """
                INSERT OR IGNORE INTO difficulties (level, label, description)
                VALUES (?, ?, ?)
            """,
                (level, label, description),
            )

    def get_or_create_lookup_id(self, cursor, table_name, field_name, value):
        """Get or create ID in a lookup table"""
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

    def get_difficulty_id(self, cursor, difficulty_value):
        """Get difficulty ID from level number"""
        if not difficulty_value:
            return None

        try:
            difficulty_level = int(difficulty_value)
            cursor.execute(
                "SELECT id FROM difficulties WHERE level = ?", (difficulty_level,)
            )
            row = cursor.fetchone()
            return row[0] if row else None
        except (ValueError, TypeError):
            return None

    def parse_description(self, desc):
        """Parse structured description into fields"""
        fields = {
            "area": None,
            "type": None,
            "project": None,
            "difficulty": None,
            "tags": None,
            "detail": None,
        }

        if not desc:
            return fields

        for line in str(desc).split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip().lower()
                value = value.strip()

                if key in fields:
                    fields[key] = value

        return fields

    def parse_tags(self, tags_str):
        """Parse comma-separated tags into a list"""
        if not tags_str:
            return []

        tags = [tag.strip() for tag in tags_str.split(",")]
        return [tag for tag in tags if tag]

    def get_or_create_tag(self, cursor, tag_name):
        """Get tag_id for a tag, creating it if it doesn't exist"""
        cursor.execute("SELECT id FROM tags WHERE name = ?", (tag_name,))
        row = cursor.fetchone()

        if row:
            return row[0]
        else:
            cursor.execute("INSERT INTO tags (name) VALUES (?)", (tag_name,))
            return cursor.lastrowid

    def insert_tags(self, cursor, event_id, tags_str):
        """Insert tags for an event using many-to-many relationship"""
        tags = self.parse_tags(tags_str)

        for tag_name in tags:
            tag_id = self.get_or_create_tag(cursor, tag_name)

            try:
                cursor.execute(
                    """
                    INSERT INTO event_tags (event_id, tag_id)
                    VALUES (?, ?)
                """,
                    (event_id, tag_id),
                )
            except sqlite3.IntegrityError:
                # Relationship already exists
                pass

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

                # Calculate duration in hours
                duration = 0
                if (
                    dtstart
                    and dtend
                    and hasattr(dtstart.dt, "__sub__")
                    and hasattr(dtend.dt, "__sub__")
                ):
                    duration = (dtend.dt - dtstart.dt).total_seconds() / 3600

                # Get foreign key IDs for normalized fields
                area_id = self.get_or_create_lookup_id(
                    cursor, "areas", "name", desc_fields["area"]
                )
                type_id = self.get_or_create_lookup_id(
                    cursor, "types", "name", desc_fields["type"]
                )
                project_id = self.get_or_create_project_id(
                    cursor, desc_fields["project"], desc_fields["area"]
                )
                difficulty_id = self.get_difficulty_id(
                    cursor, desc_fields["difficulty"]
                )

                try:
                    cursor.execute(
                        """
                        INSERT INTO events (
                            calendar_id, summary, dtstart, dtend, duration,
                            area_id, project_id, type_id, difficulty_id, detail
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            calendar_id,
                            str(component.get("summary", "")),
                            dtstart_str,
                            dtend_str,
                            duration,
                            area_id,
                            project_id,
                            type_id,
                            difficulty_id,
                            desc_fields["detail"],
                        ),
                    )

                    event_id = cursor.lastrowid

                    # Insert tags if present
                    if desc_fields["tags"]:
                        self.insert_tags(cursor, event_id, desc_fields["tags"])

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

    def get_difficulty_label(self, cursor, difficulty_id):
        """Get difficulty label by ID"""
        if not difficulty_id:
            return None

        cursor.execute("SELECT label FROM difficulties WHERE id = ?", (difficulty_id,))
        row = cursor.fetchone()
        return row[0] if row else None

    def get_event_tags(self, cursor, event_id):
        """Get all tags for an event as comma-separated string"""
        cursor.execute(
            """
            SELECT t.name 
            FROM tags t
            JOIN event_tags et ON t.id = et.tag_id
            WHERE et.event_id = ?
            ORDER BY t.name
        """,
            (event_id,),
        )
        tags = cursor.fetchall()
        return ", ".join([tag[0] for tag in tags])

    def format_description(self, event_row, cursor):
        """Format event fields back to description from normalized tables"""
        parts = []

        # Get values from lookup tables
        area_name = self.get_lookup_value(cursor, "areas", event_row["area_id"])
        type_name = self.get_lookup_value(cursor, "types", event_row["type_id"])
        project_name = self.get_lookup_value(
            cursor, "projects", event_row["project_id"]
        )
        difficulty_label = self.get_difficulty_label(cursor, event_row["difficulty_id"])
        tags_str = self.get_event_tags(cursor, event_row["id"])

        if area_name:
            parts.append(f"Area: {area_name}")
        if type_name:
            parts.append(f"Type: {type_name}")
        if project_name:
            parts.append(f"Project: {project_name}")
        if difficulty_label:
            parts.append(f"Difficulty: {difficulty_label}")
        if tags_str:
            parts.append(f"Tags: {tags_str}")
        if event_row["detail"]:
            parts.append(f"Detail: {event_row['detail']}")

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


if __name__ == "__main__":
    colors = {"work": "#489160", "saeed": "#7C7C7C", "study": "#4B99D2", "growth":"#A479B1"}
    # convert all .ics files to db 
    # for ics_file_path in ICS_DIR.glob("*.ics"):
    #     db_file_name = ics_file_path.stem + ".db"
    #     color = colors.get(ics_file_path.stem)
    #     importer = IcsToDb(Path(DB_DIR / db_file_name))
    #     importer.import_calendar(ics_file_path, color)
    #     print(f"Create database file for {db_file_name}")


    for db_file_path in DB_DIR.glob("*.db"):
        ics_file_name = db_file_path.stem + ".ics"
        exporter = DbToIcs(Path(db_file_path))
        exporter.export_calendar(ICS_DIR / ics_file_name)
