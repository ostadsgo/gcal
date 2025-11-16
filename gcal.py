import os
import datetime
import json
import statistics as stats

from pathlib import Path
from datetime import timedelta

import icalendar

# [] TODO: feat: Find top3 areas, projects, tags by duration
# [DONE] TODO: feat: limit date range for events don't limit duration


BASE_DIR = Path(__file__).resolve().parent
CALENDARS_DIR = BASE_DIR / "calendars"
SECONDS_PER_HOUR = 3600


class Difficulty:
    VERY_EASY = 1
    EASY = 2
    MEDIUM = 3
    HARD = 4
    VERY_HARD = 5

    def __init__(self, events):
        self.events = events
        self.difficulties = [
            float(event.difficulty) if event.difficulty.isdigit() else 0.0
            for event in events
        ]
        self.mean = stats.mean(self.difficulties)
        self.median = stats.median(self.difficulties)


class Report:
    def __init__(self, events):
        self.events = events
        self._duration = None

    @property
    def duration(self):
        if self._duration is None:
            self._duration = (
                sum(event.duration for event in self.events) // SECONDS_PER_HOUR
            )
        return self._duration

    @property
    def count(self):
        return len(self.events)


class AreaManager:
    def __init__(self, events):
        self.events = events

    def __getitem__(self, name):
        events = [event for event in self.events if event.area == name]
        return Report(events)


class ProjectManager:
    def __init__(self, events):
        self.events = events

    def __getitem__(self, name):
        events = [event for event in self.events if event.project == name]
        return Report(events)


class TagManager:
    def __init__(self, events):
        self.events = events

    def __getitem__(self, name):
        events = [event for event in self.events if name in event.tags]
        return Report(events)


class DifficultyManager:
    def __init__(self, events):
        self.events = events

    def __getitem__(self, name):
        events = [event for event in self.events if event.difficulty == name]
        return Report(events)


class Event:
    def __init__(self, component):
        self.component = component
        self.summary = component.get("summary", "")
        self.description = component.get("description", "")
        self.area = self.extract_value("area")
        self.project = self.extract_value("project")
        self.tags = self.extract_tags("tags")
        self.difficulty = self.extract_value("difficulty")
        self.detail = self.extract_value("detail")
        self.dtstart = component["dtstart"].dt
        self.dtend = component["dtend"].dt
        self.duration = (self.dtend - self.dtstart).total_seconds()

    def _chop_description(self):
        if not self.description:
            return []

        return [
            line.strip().lower()
            for line in self.description.splitlines()
            if line.strip().lower()
        ]

    def extract_value(self, keyword):
        for line in self._chop_description():
            if keyword in line and ":" in line:
                *_, value = line.partition(":")
                return value.strip() if value.strip() else ""
        return ""

    def extract_tags(self, keyword):
        for line in self._chop_description():
            if keyword in line and ":" in line:
                *_, value = line.partition(":")
                return [tag.strip() for tag in value.split(",") if tag.strip()]
        return []

    def __repr__(self):
        return f"Event({self.summary})"


class Calendar:
    def __init__(self, name):
        self.full_name = name
        self.calendar = self._read()
        self.name = str(self.calendar.calendar_name)
        self.color = str(self.calendar.get("color", "#FF0000"))
        self.events = self._create_events()

    def __repr__(self):
        return f"Calendar({self.name})"

    def _read(self):
        cal_path = CALENDARS_DIR / self.full_name
        return icalendar.Calendar.from_ical(cal_path.read_text())

    def _create_events(self, year=2025):
        events = [
            Event(component)
            for component in self.calendar.walk()
            if component.name == "VEVENT"
        ]
        return [event for event in events if event.dtstart.year == year]

    @property
    def areas(self):
        return AreaManager(self.events)

    @property
    def projects(self):
        return ProjectManager(self.events)

    @property
    def tags(self):
        return TagManager(self.events)

    @property
    def difficulty(self):
        return DifficultyManager(self.events)

    def duration(self, year=2025, month=10, day=1) -> float:
        return sum(event.duration for event in self.events) // SECONDS_PER_HOUR


class CalendarManager:
    def __init__(self):
        self._calendar = None


class DataManager:
    def __init__(self):
        pass


def save_last_mtime(current_mtime=""):
    last_mtime = current_mtime or str(CALENDARS_DIR.stat().st_mtime)
    with open("mtime", "w") as text_file:
        text_file.write(str(last_mtime))


def read_last_mtime():
    with open("mtime") as text_file:
        last_mtime = text_file.read()
    return last_mtime


def is_calendar_folder_modified():
    last_mtime = read_last_mtime()
    current_mtime = str(CALENDARS_DIR.stat().st_mtime)
    if current_mtime != last_mtime:
        save_last_mtime(current_mtime)
        return True
    return False


def save_data(data):
    with open(BASE_DIR / "data.json", "w") as json_file:
        json.dump(data, json_file)


def load_data():
    with open(BASE_DIR / "data.json") as json_file:
        return json.load(json_file)


def calendar_data(name):
    cal = Calendar(name)
    return {
        "calendar": cal.name,
        "name": cal.name,
        "duration": cal.duration(),
        "color": cal.color,
        "type": "calendar",
    }


def area_data(calendar_name, area):
    cal = Calendar(calendar_name)
    return {
        "calendar": cal.name,
        "name": area,
        "duration": cal.areas[area].duration,
        "color": cal.color,
        "type": "area",
    }


def project_data(calendar_name, project):
    cal = Calendar(calendar_name)
    return {
        "calendar": cal.name,
        "name": project,
        "duration": cal.projects[project].duration,
        "color": cal.color,
        "type": "project",
    }


def make_data():
    data = []
    # make Calendar
    for name in os.listdir("calendars"):
        row = calendar_data(name)
        data.append(row)

    # -- area --
    for area in ["sleep", "family"]:
        data.append(area_data("Saeed.ics", area))

    for area in ["dev", "content", "teaching"]:
        data.append(area_data("Work.ics", area))

    for area in ["reading"]:
        data.append(area_data("Growth.ics", area))

    for area in ["cs"]:
        data.append(area_data("Study.ics", area))

    # -- project --
    for project in ["gcal", "pyquiz"]:
        data.append(project_data("Work.ics", project))

    return data


def data(field_type="calendar"):
    if is_calendar_folder_modified():
        rows = make_data()
        save_data(rows)
    else:
        rows = load_data()

    return sorted(
        [row for row in rows if row.get("type") == field_type],
        key=lambda row: row["duration"],
        reverse=True
    )


def main():
    work = Calendar("Work.ics")
    print("Calendar duratin: ", work.duration())
    # print(get_data())
    # print(work.projects["gcal"].duration)
    data()


if __name__ == "__main__":
    main()
