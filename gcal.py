import os
import json
import datetime
import statistics as stats

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
    def __init__(self, name, color):
        self.name = name
        self.color = color
        self.calendar = self._read()
        self.events = self._create_events()
        self.areas = set(event.area for event in self.events)
        self.projects = set(event.project for event in self.events)
        self.tags = list(event.tags for event in self.events)
        self.difficulties = Difficulty(self.events)

    def _read(self):
        cal_path = CALENDARS_DIR / self.name
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
    

def calendars_data():
    pass


def main():
    work = Calendar("Work.ics", "#00ff00")
    e = work.events[1]

    print(work.duration)
    print(work.difficulties.mean)


if __name__ == "__main__":
    main()
