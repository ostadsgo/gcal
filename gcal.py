import datetime
from pathlib import Path
import os

import icalendar
from icalendar import Calendar, Event


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


def save_calendar(name: str, calendar):
    with open(CAL_DIR / name, "wb") as f:
        f.write(calendar.to_ical())


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


def calendars_color():
    return {
        "Work": "#489160",
        "Study": "#4B99D2",
        "Growth": "#A479B1",
        "Saeed": "#7C7C7C",
    }


def categorizer(summary):
    new_summary = ""
    keys = ["breakfast", "lunch", "dinner"]
    for key in keys:
        if key in summary.lower():
            new_summary = f"Eat: {key}"
            return new_summary
    return summary


def fix_summary():
    cal = read_calendar("Saeed_updated.ics")

    # Modify summaries of all events
    for component in cal.walk():
        if component.name == "VEVENT":
            summary = component.get("summary", "no summary")
            component["summary"] = categorizer(summary)
            print(component["summary"])

    save_calendar("Saeed_updated.ics", cal)


# -- Sub category (tag) --
def category_time_spent(cal_name: str, category: str):
    # colors, category, timespent
    category_cal = Calendar()
    cal = read_calendar(cal_name)
    for event in cal.events:
        summary = event["summary"]
        item, *_ = summary.split(":")
        if item.lower() == category.lower():
            category_cal.add_component(event)

    calendar = cal_name.replace(".ics", "")
    spent = time_spent(category_cal)
    # color = calendar_colors().get(calendar)
    # return {
    #     # "calendar": calendar,
    #     # "color": color,
    #     # "name": category.title(),
    #     "spent": spent,
    # }
    return spent


def categories_time_spent():
    return {
        "Sleep": category_time_spent("Saeed.ics", "sleep"),
        "Burnt": category_time_spent("Saeed.ics", "burnt"),
        "Dev": category_time_spent("Work.ics", "dev"),
        "Content": category_time_spent("Work.ics", "content"),
        "Design": category_time_spent("Work.ics", "Learn"),
        "SWE": category_time_spent("Work.ics", "SWE"),
        "CS": category_time_spent("Study.ics", "cs"),
        "School": category_time_spent("Study.ics", "school"),
        "Reading": category_time_spent("Growth.ics", "reading"),
        "Workout": category_time_spent("Growth.ics", "workout"),
    }


def categories_color():
    cats = {
        "Saeed": ("Sleep", "Burnt"),
        "Work": ("Dev", "Content", "Design", "SWE"),
        "Study": ("CS", "School"),
        "Growth": ("Reading", "Workout"),
    }
    cals_color = calendars_color()
    cats_color = {}
    for cal, tags in cats.items():
        for tag in tags:
            color = cals_color.get(cal)
            cats_color[tag] = color
    return cats_color



def main():
    x = category_time_spent("Saeed.ics", "sleep")
    y = category_time_spent("Saeed.ics", "burnt")
    print(x, y)


if __name__ == "__main__":
    main()
