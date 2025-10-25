# ----------------
# [DONE] TODO: Store claculated data in file to use it for faster char render.
# -----------------

import datetime
from pathlib import Path
import os
import json

import icalendar
from icalendar import Calendar


BASE_DIR = Path(__file__).resolve().parent
CALENDARS_DIR = BASE_DIR / "calendars"
RENAME_CALS = False
RESAVE_CALENDARS_DATA = True
calendar_colors = {
    "Work": "#489160",
    "Study": "#4B99D2",
    "Growth": "#A479B1",
    "Saeed": "#7C7C7C",
}

calendar_categories = {
    "Saeed": ("Sleep", "Burnt"),
    "Work": ("Dev", "Content", "Design", "SWE"),
    "Study": ("CS", "School"),
    "Growth": ("Reading", "Workout"),
}


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


def rename_calendars():
    cals_name = os.listdir(CALENDARS_DIR)
    for cal_name in cals_name:
        new_cal_name, *_ = cal_name.split("_")
        os.rename(CALENDARS_DIR / cal_name, CALENDARS_DIR / f"{new_cal_name}.ics")


def read_calendar(name: str):
    cal_path = CALENDARS_DIR / name
    cal = icalendar.Calendar.from_ical(cal_path.read_text())
    return cal


def save_calendar(name: str, calendar):
    with open(CALENDARS_DIR / name, "wb") as f:
        f.write(calendar.to_ical())


def save_calendars_data(data, filename):
    with open(BASE_DIR / filename) as json_file:
        json.dump(data, json_file)


def read_calendars():
    if RENAME_CALS:
        rename_calendars()

    calendars = []
    cals_name = os.listdir(CALENDARS_DIR)
    for cal_name in cals_name:
        calendars.append(read_calendar(cal_name))
    return calendars


def calendars_name():
    if RENAME_CALS:
        rename_calendars()

    return [calendar.replace(".ics", "") for calendar in os.listdir(CALENDARS_DIR)]


def calendar_duration(calendar, year=2025) -> float:
    total_duration = datetime.timedelta()
    for event in calendar.events:
        if event["dtstart"].dt.year == year:
            total_duration += event.duration

    # convert days to second then hours : 3600 = 1 hour
    return total_duration.total_seconds() // 3600


def create_category_calendar(calendar, category: str):
    category_calendar = Calendar()
    for event in calendar.events:
        summary = event["summary"]
        item, *_ = summary.split(":")
        if item.lower() == category.lower():
            category_calendar.add_component(event)
    return category_calendar


# -- Sub category (tag) --
def category_duration(calendar_file: str, category: str):
    main_calendar = read_calendar(calendar_file)
    category_calendar = create_category_calendar(main_calendar, category)
    return calendar_duration(category_calendar)


def calendar_data(calendar_file):
    calendar = read_calendar(calendar_file)
    calendar_name = calendar_file.replace(".ics", "")
    calendar_type = "calendar"
    return {
        "name": calendar_name,
        "duration": calendar_duration(calendar.name),
        "type": calendar_type,
        "color": calendar_colors.get(calendar_name),
    }


def calendars_data(calendar_files):
    for calendar_file in calendar_files:
        calendar_name = calendar_file.replace(".ics", "")
        data = calendar_data(calendar_file)


def calculate_data():
    data = []
    calendars = calendars_name()
    calendar_type = ""
    for calendar_name in calendars:
        calendar_type = "calendar"
        calendar_data = {}

        calendar_file = f"{calendar_name}.ics"
        calendar = read_calendar(calendar_file)
        calendar_dur = calendar_duration(calendar)

        calendar_data["name"] = calendar_name
        calendar_data["duration"] = calendar_dur
        calendar_data["color"] = calendar_colors.get(calendar_name)
        calendar_data["type"] = calendar_type
        data.append(calendar_data)

        # -- categories --
        categories = calendar_categories.get(calendar_name, [])
        calendar_type = "category"
        other_duration = calendar_dur
        for category_name in categories:
            calendar_data = {}
            category_dur = category_duration(calendar_file, category_name)
            other_duration -= category_dur
            data.append(
                {
                    "name": category_name,
                    "duration": category_dur,
                    "type": calendar_type,
                    "calendar": calendar_name,
                }
            )

        data.append(
            {
                "name": "other",
                "duration": other_duration,
                "type": calendar_type,
                "calendar": calendar_name,
            }
        )
        data.append(calendar_data)

    return data


def save_data(data):
    with open("data.json", "w") as json_file:
        json.dump(data, json_file)


def read_data():
    data = None
    with open("data.json", "r") as json_file:
        data = json.load(json_file)
    return data


def get_data():
    # if the calendar folder is not modified return already saved data
    if not is_calendar_folder_modified():
        return read_data()

    data = calculate_data()
    save_data(data)
    return data


def main():
    calendar_data("Work.ics")


if __name__ == "__main__":
    main()
