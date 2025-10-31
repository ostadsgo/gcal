# ----------------
# [] TODO: Write simple parser for ics file and remove `icalendar` dependency.
# [] TODO: Extract project form event summary.
# [] TODO:
# [] TODO:
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
    "Work": ("Dev", "Content", "SWE"),
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


def calendar_duration(calendar, year=2025, month=10) -> float:
    total_duration = datetime.timedelta()
    for event in calendar.events:
        if (event["dtstart"].dt.year == year) and (event["dtstart"].dt.month == month):
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
def calendar_data(calendar_file):
    calendar = read_calendar(calendar_file)
    calendar_name = calendar_file.replace(".ics", "")
    calendar_type = "calendar"
    return {
        "name": calendar_name,
        "duration": calendar_duration(calendar),
        "type": calendar_type,
        "color": calendar_colors.get(calendar_name),
    }


def category_data(calendar_file: str, category: str):
    main_calendar = read_calendar(calendar_file)
    calendar_name = calendar_file.replace(".ics", "")
    category_calendar = create_category_calendar(main_calendar, category)
    duration = calendar_duration(category_calendar)
    return {
            "name": category.title(),
            "duration": duration,
            "type": "category",
            "calendar": calendar_name,
            "color": calendar_colors.get(calendar_name),
        }


def make_data():
    calendar_files = os.listdir(CALENDARS_DIR)
    data = {}
    for calendar_file in calendar_files:
        calendar_name = calendar_file.replace(".ics", "")
        cal_data = calendar_data(calendar_file)
        categories = calendar_categories[calendar_name]
        data[calendar_name] = cal_data
        for category in categories:
            cat_data = category_data(calendar_file, category)
            data[category] = cat_data
    return data


def save_data(data):
    with open("data.json", "w") as json_file:
        json.dump(data, json_file)


def read_data(filename="data.json"):
    data = None
    with open(filename, "r") as json_file:
        data = json.load(json_file)
    return data


def get_data():
    # if the calendar folder is not modified return already saved data
    if not is_calendar_folder_modified():
        return read_data()

    data = make_data()
    save_data(data)
    return data


def calculate_other_duration(calendar_name):
    data = get_data()
    categories = calendar_categories[calendar_name]
    calendar_duration = data[calendar_name]["duration"]
    other_duration = calendar_duration

    for category in categories:
        other_duration -= data[category]["duration"]

    return other_duration


def main():
    print(calculate_other_duration("Work"))


if __name__ == "__main__":
    main()
