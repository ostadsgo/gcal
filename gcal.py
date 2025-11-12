import os
import datetime
import pickle
import statistics as stats

from pathlib import Path
from dataclasses import dataclass

import icalendar

# TODO: Manipulate calendar to have color field
# TODO: Use json as data cache; remove pickle

BASE_DIR = Path(__file__).resolve().parent
CALENDARS_DIR = BASE_DIR / "calendars"


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
            if line.strip()
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


class Calendar:
    def __init__(self, name):
        self.full_name = name
        self.name = name.replace(".ics", "")
        self.calendar = self._read()
        self.color = self.calendar.get("color", "#FF0000")
        self.events = self._create_events()
        self.areas = set(event.area for event in self.events)
        self.projects = set(event.project for event in self.events)
        self.tags = list(event.tags for event in self.events)
        self.difficulties = Difficulty(self.events)

    def _read(self):
        cal_path = CALENDARS_DIR / self.full_name
        return icalendar.Calendar.from_ical(cal_path.read_text())

    @property
    def duration(self, year=2025, month=10, day=1) -> float:
        SECONDS_PER_HOUR = 3600
        return (
            sum(
                event.duration.total_seconds()
                for event in self.events
                if event.dtstart.year == year
            )
            / SECONDS_PER_HOUR
        )

    def _create_events(self):
        return [
            Event(component)
            for component in self.calendar.walk()
            if component.name == "VEVENT"
        ]

    # get some keywords and modify calendar event and the save it
    def modify(self, keyword):
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

def save_calendars(calendars):
    with open(BASE_DIR / 'calendars.pkl', 'wb') as pkl_file:
        pickle.dump(calendars, pkl_file)

def load_calendars():
    with open(BASE_DIR / "calendars.pkl", 'rb') as pkl_file:
        return pickle.load(pkl_file)

def calendars():
    if not is_calendar_folder_modified():
        return load_calendars()
    cals = [Calendar(name) for name in os.listdir(CALENDARS_DIR)]
    return save_calendars(cals)
    


def main():
    work = Calendar("Work.ics")
    cal = work.calendar

    e = work.events[1]

    print(calendars())

    # print(work.duration)
    # print(work.difficulties.mean)
    # print(calendars_data())




if __name__ == "__main__":
    main()
