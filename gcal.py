import os
import datetime
import json
import statistics as stats

from pathlib import Path
from datetime import datetime, timezone, timedelta

import icalendar
from zoneinfo import ZoneInfo


import db

# [] TODO: if calendar folder or .ics files didn't modied not need for make calendars objects
# [] TODO: feat: Find top3 areas, projects, tags by duration


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

    def __repr__(self):
        return f"AreaManager"

    def __iter__(self):
        areas = {event.area for event in self.events if event.area}
        return iter(areas)

    @property
    def names(self):
        return sorted({event.area for event in self.events if event.area})


class ProjectManager:
    def __init__(self, events):
        self.events = events

    def __getitem__(self, name):
        events = [event for event in self.events if event.project == name]
        return Report(events)

    def __iter__(self):
        projects = {event.project for event in self.events if event.project}
        return iter(projects)

    @property
    def names(self):
        return sorted({event.project for event in self.events if event.project})


class TagManager:
    def __init__(self, events):
        self.events = events

    def __getitem__(self, name):
        events = [event for event in self.events if name in event.tags]
        return Report(events)

    def __iter__(self):
        tags = {event.tag for event in self.events if event.tag}
        return iter(tags)

    @property
    def names(self):
        return sorted({event.tag for event in self.events if event.tag})

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
        # date time
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
    def __init__(self, name, year=2025, month=None, days=None):
        self.full_name = name
        self.year = year
        self.month = month
        self.days = days
        self.calendar = self._read()
        self.name = str(self.calendar.calendar_name)
        self.color = str(self.calendar.get("color", "#FF0000"))
        self.events = self._create_events()

    def __repr__(self):
        return f"Calendar({self.name})"

    def _read(self):
        cal_path = CALENDARS_DIR / self.full_name
        return icalendar.Calendar.from_ical(cal_path.read_text())

    def _filter_events(self, events, year=None, month=None, days=None):
        filtered_events = []

        for event in events:
            if event.dtstart.year == self.year and isinstance(event.dtstart, datetime):
                filtered_events.append(event)
        return filtered_events

    def _create_events(self):
        events = [ Event(comp) for comp in self.calendar.walk() if comp.name == "VEVENT" ]
        return self._filter_events(events)



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
    def difficulties(self):
        return DifficultyManager(self.events)

    @property
    def duration(self):
        return sum(event.duration for event in self.events) / SECONDS_PER_HOUR

    @property
    def count(self):
        return len(self.events)


class CalendarManager:
    def __init__(self):
        self._calendar = None


class DataManager:
    def __init__(self):
        pass


def save_data(data):
    with open(BASE_DIR / "data.json", "w") as json_file:
        json.dump(data, json_file)


def load_data():
    with open(BASE_DIR / "data.json") as json_file:
        return json.load(json_file)


def calendar_data(calendar, year, month, days):
    return {
        "calendar": calendar.name,
        "name": calendar.name,
        "duration": calendar.duration,
        "color": calendar.color,
        "type": "calendar",
        "count": calendar.count,
        "year": calendar.year,
    }


def area_data(calendar, area):
    return {
        "calendar": calendar.name,
        "name": area,
        "duration": calendar.areas[area].duration,
        "color": calendar.color,
        "type": "area",
        "count": calendar.areas[area].count,
        "year": calendar.year,
    }


def project_data(calendar, project):
    return {
        "calendar": calendar.name,
        "name": project,
        "duration": calendar.projects[project].duration,
        "color": calendar.color,
        "type": "project",
        "count": calendar.projects[project].count,
        "year": calendar.year,
    }


def make_data(year, month, days):
    data = []

    saeed = Calendar("Saeed.ics", year, month, days)
    work = Calendar("Work.ics", year, month, days)
    growth = Calendar("Growth.ics", year, month, days)
    study = Calendar("Study.ics", year, month, days)

    data.append(calendar_data(saeed, year, month, days))
    data.append(calendar_data(work, year, month, days))
    data.append(calendar_data(growth, year, month, days))
    data.append(calendar_data(study, year, month, days))

    # -- area --
    for area in ["family", "mindless"]:
        data.append(area_data(saeed, area))

    for area in ["dev", "content", "teaching"]:
        data.append(area_data(work, area))

    for area in ["reading"]:
        data.append(area_data(growth, area))

    for area in ["cs"]:
        data.append(area_data(study, area))

    # -- project --
    for project in ["gcal", "pyquiz"]:
        data.append(project_data(work, project))

    for project in ["crime and punishment", "a fraction of the whole"]:
        data.append(project_data(growth, project))
    return data


def data(year=2025, month=None, days=None, field="calendar", force=False):
    rows = make_data(year, month, days)
    return sorted(
        [row for row in rows if row.get("type") == field],
        key=lambda row: row["duration"],
        reverse=True,
    )



class CalendarManager:
    def __init__(self):
        pass

    def read(self, filename):
        calendar = None
        with open(CALENDARS_DIR / filename, "rb") as f:
            calendar = icalendar.Calendar.from_ical(f.read())
        return calendar



    def read_all(self, folder_path):
        ...


class Calendar:
    def __init__(self, filename):
        manager = CalendarManager()
        self.calendar = manager.read(filename)

    



if __name__ == "__main__":
    saeed = Calendar("Saeed.ics")
    work = Calendar("Work.ics")
    growth = Calendar("Growth.ics")
    study = Calendar("Study.ics")
