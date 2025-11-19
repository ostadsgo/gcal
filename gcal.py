import os
import datetime
import json
import statistics as stats

from pathlib import Path
from datetime import datetime, timezone, timedelta

import icalendar
from zoneinfo import ZoneInfo

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


def calendar_data(name, year, month, days):
    cal = Calendar(name, year, month, days)
    return {
        "calendar": cal.name,
        "name": cal.name,
        "duration": cal.duration,
        "color": cal.color,
        "type": "calendar",
        "count": cal.count,
    }


def area_data(calendar_name, area):
    cal = Calendar(calendar_name)
    return {
        "calendar": cal.name,
        "name": area,
        "duration": cal.areas[area].duration,
        "color": cal.color,
        "type": "area",
        "count": cal.areas[area].count,
    }


def project_data(calendar_name, project):
    cal = Calendar(calendar_name)
    return {
        "calendar": cal.name,
        "name": project,
        "duration": cal.projects[project].duration,
        "color": cal.color,
        "type": "project",
        "count": cal.projects[project].count,
    }


def make_data(year, month, days):
    data = []
    # make Calendar
    for name in os.listdir("calendars"):
        row = calendar_data(name, year, month, days)
        data.append(row)

    # -- area --
    for area in ["family", "mindless"]:
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

    for project in ["crime and punishment", "a fraction of the whole"]:
        data.append(project_data("Growth.ics", project))
    return data


def data(year=2025, month=None, days=None, field="calendar", force=False):
    if force:
        rows = make_data(year, month, days)
        save_data(rows)
    else:
        rows = load_data()

    return sorted(
        [row for row in rows if row.get("type") == field],
        key=lambda row: row["duration"],
        reverse=True,
    )


def main():
    # d = data()
    # sample
    # growth = Calendar("Growth.ics")
    saeed = Calendar("Saeed.ics", year=2024)
    # work = Calendar("Work.ics")
    # study = Calendar("Study.ics")
    # print(study.name)

    # x  = 0
    # for event in saeed.events:
    #     # print(event.summary, ":", "start:", event.dtstart, "end:", event.dtend, "duration:", event.duration / SECONDS_PER_HOUR)
    #
    #     print(event.summary, ":", event.duration / 3600)
    #     x += event.duration
    #
    # print(x / SECONDS_PER_HOUR)

    # saeed.debug_duration()
    x = []
    for e in saeed.events:
        x.append(e.dtstart.year)
    print(set(x))
    



if __name__ == "__main__":
    main()
