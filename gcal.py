import os
import datetime
import json
import statistics as stats

from pathlib import Path
from dataclasses import dataclass

import icalendar

# TODO: Manipulate calendar to have color field
# TODO: Use json as data cache; remove pickle

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


# I am not sure how can i use this class but it will be used i guess
class Color:
    def __init__(self, hex_color):
        self.hex_color = color


# I am not sure how can i use this class but it will be used i guess
class Duration:
    # event.area.duration
    pass


class AreaManager:
    def __init__(self, events):
        self.events = events


    def __getitem__(self, name):
        areas = [event for event in self.events if event.area == name]
        print(areas)




class Project:
    def __init__(text: str):
        self.text = text

    def duration(self, events, year=2025, month=1, day=1):
        return (
            sum(
                event.duration.total_seconds()
                for event in events
                if event.project.text == self.text and event.dtstart.year == year
            )
            / SECONDS_PER_HOUR
        )

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
        self.duration = self.dtend - self.dtstart

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
        self.name = self.calendar.calendar_name
        self.color = str(self.calendar.get("color", "#FF0000"))
        self.events = self._create_events()
        # self.areas = {event.area for event in self.events}
        self.projects = {event.project for event in self.events if event.project}
        self.tags = {tag for event in self.events for tag in event.tags}
        self.difficulties = [int(event.difficulty) for event in self.events if event.difficulty]

    def __repr__(self):
        return f"Calendar({self.name})"

    def _read(self):
        cal_path = CALENDARS_DIR / self.full_name
        return icalendar.Calendar.from_ical(cal_path.read_text())

    def _create_events(self):
        return [
            Event(component)
            for component in self.calendar.walk()
            if component.name == "VEVENT"
        ]

    @property
    def areas(self):
        return AreaManager(self.events)


    def duration(self, year=2025, month=10, day=1) -> float:
        return (
            sum(
                event.duration.total_seconds()
                for event in self.events
                if event.dtstart.year == year
            )
            / SECONDS_PER_HOUR
        )

    def area_duration(self, area, year=2025, month=1, day=1):
        return (
            sum(
                event.duration.total_seconds()
                for event in self.events
                if event.area == area and event.dtstart.year == year
            )
            / SECONDS_PER_HOUR
        )

    def projects_duration(self, projects, year=2025, month=1, day=1):
        d = dict.fromkeys(projects, 0)
        for project in projects:
            duration = (
                sum(
                    event.duration.total_seconds()
                    for event in self.events
                    if event.project == project and event.dtstart.year == year
                )
                / SECONDS_PER_HOUR
            )
            d[project] = duration
        return d

    # get some keywords and modify calendar event and the save it
    def modify(self, keyword):
        pass


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


def calendars_data():
    calendars = [Calendar(name) for name in os.listdir(CALENDARS_DIR)]
    d = [
        {"name": calendar.name, "duration": calendar.duration, "color": calendar.color}
        for calendar in calendars
    ]
    return d


def get_calendar(name):
    if not name in os.listdir(CALENDARS_DIR):
        print(f"Calendar `{name}` not found in `{CALENDARS_DIR}`")
        return
    return Calendar(name)


def get_shade_color(hex_color, darkness=0.3):
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)

    # Make it darker
    r = int(r * (1 - darkness))
    g = int(g * (1 - darkness))
    b = int(b * (1 - darkness))

    return f"#{r:02x}{g:02x}{b:02x}"


def areas_data(calendar_name, areas: list[str]):
    d = {}
    color_darkness = 0.3
    calendar = get_calendar(calendar_name)
    for area in areas:
        if area in calendar.areas:
            name = calendar.name
            color = get_shade_color(calendar.color, color_darkness)
            duration = calendar.area_duration(area)
            d[area] = {"name": name, "color": color, "duration": duration}
            color_darkness += 0.1
    return d


def projects_data(calendar_name, projects: list[str]):
    d = {}
    color_darkness = 0.3
    calendar = get_calendar(calendar_name)
    for project in projects:
        if project in calendar.projects:
            name = calendar.name
            color = get_shade_color(calendar.color, color_darkness)
            duration = calendar.projects_duration(project)
            d[project] = {"name": name, "color": color, "duration": duration}
            color_darkness += 0.1
    return d


def tags_data(tags: list[str]):
    pass


def data():
    """ Data = calendars + areas + project + tags """
    # if not is_calendar_folder_modified():
    #     return load_data()
    # return save_data(d)
    d =   areas_data("Work.ics", ["dev", "content"]) | projects_data("Work.ics", ["pyquiz", "gcal"])
    print(d)


def main():
    work = Calendar("Work.ics")
    work.areas['dev']






if __name__ == "__main__":
    main()
