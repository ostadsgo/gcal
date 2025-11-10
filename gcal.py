
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
        self.duration = self.calculate_duration()

    def _chop_description(self):
        lines = []

        if not self.description:
            return lines

        lines = self.description.splitlines()
        lines = [line.lower().strip() for line in lines]
        return lines

    def extract_value(self, keyword):
        value = ""
        lines = self._chop_description()

        for line in lines:
            if keyword in line and ':' in line:
                _, value = line.split(':', 1)
                break
        return value

    def extract_tags(self, keyword):
        tags = []
        lines = self._chop_description()

        for line in lines:
            if keyword in line and ':' in line:
                _, value = line.split(':', 1)
                tags = value.split(',')
                break
        return tags

    def calculate_duration(self):
        duration = datetime.timedelta()
        if self.component.name == "VEVENT":
            start = self.component.get('dtstart').dt
            end = self.component.get('dtend').dt
            duration = end - start
        return duration


def calendar_duration(calendar, year=2025, month=10) -> float:
    total_duration = datetime.timedelta()
    for event in calendar.events:
        if (event["dtstart"].dt.year == year):
            total_duration += event.duration

    # convert days to second then hours : 3600 = 1 hour
    return total_duration.total_seconds() // 3600


def create_events(calendar):
    return [Event(component) for component in calendar.walk()]


def main():
    calendar_name = "Work.ics"
    cal_path = CALENDARS_DIR / calendar_name
    calendar = icalendar.Calendar.from_ical(cal_path.read_text())
    events = create_events(calendar)

    for event in events:
        print(event.summary, event.duration)

    print("Calendar duration is:", calendar_duration(calendar))



if __name__ == "__main__":
    main()

