import os
import json
import datetime

from pathlib import Path
from dataclasses import dataclass

import icalendar
from icalendar import Calendar


BASE_DIR = Path(__file__).resolve().parent
CALENDARS_DIR = BASE_DIR / "calendars"

class Difficulty:
    VERY_EASY = 1
    EASY = 2
    MEDIUM = 3
    HARD = 4
    VERY_HARD = 5



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
            if keyword in line and ':' in line:
                *_, value = line.partition(':')
                return value.strip() if value.strip() else ""
        return ""

    def extract_tags(self, keyword):
        for line in self._chop_description():
            if keyword in line and ':' in line:
                *_, value = line.partition(":")
                return [tag.strip() for tag in value.split(',') if tag.strip()]
        return []


class Calendar:
    def __init__(self, name):
        self.name = name
        cal_path = CALENDARS_DIR / name
        self.calendar = icalendar.Calendar.from_ical(cal_path.read_text())
        self.events = self.create_events()

    def duration(self, year=2025, month=10, day=1) -> float:
        total_duration = datetime.timedelta()
        for event in self.events:
            if event.dtstart.year == year:
                total_duration += event.duration

        # convert days to second then hours : 3600 = 1 hour
        return total_duration.total_seconds() / 3600

    def create_events(self):
        return [Event(component) for component in self.calendar.walk() if component.name == "VEVENT"]


def main():
    work = Calendar("Work.ics")
    print(work.duration())

    e = work.events[1]
    print(e.tags)


if __name__ == "__main__":
    main()

