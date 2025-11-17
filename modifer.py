from pathlib import Path
import icalendar
import copy

from icalendar import Calendar

import sqlite3


BASE_DIR = Path(__file__).resolve().parent
CALENDARS_DIR = BASE_DIR / "calendars"
SECONDS_PER_HOUR = 3600


def read_calendar(filename):
    cal_path = CALENDARS_DIR / filename
    return icalendar.Calendar.from_ical(cal_path.read_bytes())


def save_calendar(name: str, calendar):
    with open(CALENDARS_DIR / name, "wb") as f:
        f.write(calendar.to_ical())


def create_calendar(filename, calendar):
    with open(CALENDARS_DIR / filename, "wb") as f:
        f.write(calendar.to_ical())

def print_summary(filename):
    summeries = []
    cal = read_calendar(filename)
    for event in cal.events:
        summeries.append(str(event["summary"].lower()))
    for i in set(summeries):
        print(i)

def add_description(cal_name, filename):
    cal = read_calendar(cal_name)
    new_cal = Calendar()
    description = [
        "Area:",
        "Project:",
        "Tags:",
        "Difficulty:",
        "Detail:",

    ]
    description = "\n".join(description)

    x = []
    for component in cal.walk():
        if component.name == "VEVENT":
            new_event = copy.deepcopy(component)
            if component.get("description") is None:
                print(component.get("summary"))

            # new_event["description"] = description
            # new_cal.add_component(new_event)

    # create_calendar(filename, new_cal)

def calendar_walk(cal_name, keywords, data, filename):
    cal = read_calendar(cal_name)
    new_cal = Calendar()
    count = 0

    for component in cal.walk():
        if component.name == "VEVENT":
            summary = component.get("summary").lower()
            if any(keyword.lower() in summary for keyword in keywords):
                new_event = copy.deepcopy(component)
                for key, value in data.items():
                    new_event[key] = value
                print(summary, "-->", new_event["summary"])
                new_cal.add_component(new_event)
                count += 1
            else:
                new_cal.add_component(component)

    print(f"Changed: {count}")
    # create_calendar(filename, new_cal)


def delete_span_br(cal_name, filename):
    cal = read_calendar(cal_name)
    new_cal = Calendar()
    count = 0

    for component in cal.walk():
        if component.name == "VEVENT":
            description = component.get("description")
            new_event = copy.deepcopy(component)
            if description:
                clean_description = description.replace("<span>", "").replace("</span>", "").replace("<br>", "\n").strip()
                new_event["description"] = clean_description
                new_cal.add_component(new_event)
                count += 1
            else:
                new_cal.add_component(component)

    create_calendar(filename, new_cal)
    print("Description Changed:", count)


def main():
    description = [
        "Area: Reading",
        "Project: Crime and Punishment",
        "Tags: pt10",
        "Difficulty: 1",
        "Detail:",

    ]
    data = {
        "summary": "PT 10",
        "description": "\n".join(description),
    }

    keywords = ["workout"]


    # add_description("Saeed.ics", "temp.ics")
    # calendar_walk("Growth.ics", keywords, data, "temp.ics")
    # print_summary("temp.ics")
    delete_span_br("Study.ics", "Study.ics")


if __name__ == "__main__":
    main()
