# ----------------
# [] TODO: Feature: Write simple parser for ics file and remove `icalendar` dependency.
# [] TODO: Extract project form event summary.
# [] TODO: Improvment:  nested data in `calendars_categories_data`
# [] TODO: Feature: How many events happend for a specific project(or area)
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
    "Saeed": ["Sleep", "Burnt"],
    "Work": ["Dev", "Content", "SWE"],
    "Study": ["CS", "School"],
    "Growth": ["Reading", "Workout"],
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
    # [] BUG: there is a bug here .ics doens't added to the calendars name.
    # it works differently if the calendar renamed for the first time or not.
    for cal_name in os.listdir(CALENDARS_DIR):
        if '_' in cal_name:
            name, *_ = cal_name.split("_")
            os.rename(CALENDARS_DIR / cal_name, CALENDARS_DIR / f"{name}.ics")


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
def calendar_data_format(calendar_file: str) -> dict[str, str]:
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
        "name": category,
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
        cal_data = calendar_data_format(calendar_file)
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


def other_duration(calendar_name):
    data = get_data()
    categories = calendar_categories[calendar_name]
    calendar_duration = data[calendar_name]["duration"]
    other_dur = calendar_duration

    for category in categories:
        other_dur -= data[category]["duration"]

    return other_dur


def other_format(calendar_name):
    other_dur = other_duration(calendar_name)
    other = {
        "name": "ohter",
        "duration": other_dur,
        "type": "other",
        "calendar": calendar_name,
        "color": calendar_colors[calendar_name],
    }
    return other


def calendars_data():
    data = get_data()
    cals_data = {}
    for name, calendar_data in data.items():
        if calendar_data["type"] == "calendar":
            cals_data[name] = calendar_data
    return cals_data


def calendar_data(calendar_name: str):
    cals_data = calendars_data()
    return cals_data.get(calendar_name, {})


def all_categories_data():
    data = get_data()
    cals_data = {}
    for name, calendar_data in data.items():
        if calendar_data["type"] == "category":
            cals_data[name] = calendar_data
    return cals_data


def categories_data(calendar_name: str) -> list:
    data = []
    cats_data = all_categories_data()
    for cat, d in cats_data.items():
        if d["calendar"] == calendar_name:
            data.append(d)
    # add other to the categories of the calendar.
    other = other_format(calendar_name)
    data.append(other)
    return data


def calendars_categories_data():
    """Each category with other duration"""
    cals_name = calendars_name()
    data = []
    for cal in cals_name:
        data.append({cal: categories_data(cal)})
    return data


def main():
    rename_calendars()
    # rename_calendars()


if __name__ == "__main__":
    main()
