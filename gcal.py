# TODO: Calculate time spent on each calendar
#   TODO: On Yearly, Montly and weekly and daily basis
# TODO: Calculate time spent on each sub category
#   TODO: On Yearly, Montly and weekly and daily basis
# TODO: Calculate time spent on each project(task)

import datetime
from pathlib import Path
import os

import icalendar


BASE_DIR = Path(__file__).resolve().parent
CAL_DIR = BASE_DIR / "cal"
RENAME_CALS = False


def rename_calendars():
    cals_name = os.listdir(CAL_DIR)
    for cal_name in cals_name:
        new_cal_name, *_ = cal_name.split("_")
        os.rename(CAL_DIR / cal_name, CAL_DIR / f"{new_cal_name}.ics")


def read_calendar(name: str):
    cal_path = CAL_DIR / name
    cal = icalendar.Calendar.from_ical(cal_path.read_text())
    return cal


def read_calendars():
    if RENAME_CALS:
        rename_calendars()

    calendars = []
    cals_name = os.listdir(CAL_DIR)
    for cal_name in cals_name:
        calendars.append(read_calendar(cal_name))

    return calendars


def time_spent(calendar, year=2025):
    total_duration = datetime.timedelta()
    for event in calendar.events:
        if event["dtstart"].dt.year == year:
            total_duration += event.duration

    # convert days to second then hours : 3600 = 1 hour
    return total_duration.total_seconds() // 3600


def calendars_time_spent():
    """calendar name and timespent on each calendar."""
    times = {
        str(calendar.calendar_name): int(time_spent(calendar))
        for calendar in read_calendars()
    }
    return dict(sorted(times.items(), key=lambda item: item[1], reverse=True))


def calendar_colors():
    return {"Work": "#489160", "Study": "#4B99D2", "Growth": "#A479B1", "Saeed": "Gray"}


def main():
    read_calendars()


if __name__ == "__main__":
    main()
