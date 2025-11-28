from pathlib import Path
import icalendar
import copy
import zipfile
import os

from datetime import datetime
from zoneinfo import ZoneInfo

import json
from icalendar import Calendar

# TODO: add color to each calendar
# unzip calendar folder
# rename calendars 
# set calendar name
# clear span , bar

BASE_DIR = Path(__file__).resolve().parent
CALENDARS_DIR = Path(BASE_DIR / "calendars")
SECONDS_PER_HOUR = 3600


def unzip_to_calendars(zip_path, extract_to=CALENDARS_DIR):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    print("extracted")


def rename_calendars():
    for cal_name in os.listdir(CALENDARS_DIR):
        if '_' in cal_name:
            name, *_ = cal_name.split("_")
            os.rename(CALENDARS_DIR / cal_name, CALENDARS_DIR / f"{name.lower()}.ics")

def read_calendar(filename):
    cal_path = CALENDARS_DIR / filename
    return icalendar.Calendar.from_ical(cal_path.read_bytes())


def save_calendar(name: str, calendar):
    with open(CALENDARS_DIR / name, "wb") as f:
        f.write(calendar.to_ical())


def create_calendar(filename, calendar):
    with open(CALENDARS_DIR / filename, "wb") as f:
        f.write(calendar.to_ical())
    print(f"calendar {filename} created.")

def print_summary(filename):
    summeries = []
    cal = read_calendar(filename)
    for event in cal.events:
        summeries.append(str(event["summary"].lower()))
    for i in set(summeries):
        print(i)

def fix_timezone_in_ics(input_file, output_file):
    # Read the calendar file
    with open(CALENDARS_DIR/input_file, 'rb') as f:
        cal = Calendar.from_ical(f.read())
    
    tehran_tz = ZoneInfo("Asia/Tehran")
    
    # Process each event
    for component in cal.walk('VEVENT'):
        # Convert DTSTART
        if 'DTSTART' in component:
            dt = component['DTSTART'].dt
            if isinstance(dt, datetime) and dt.tzinfo:
                # Convert UTC to Tehran time and make it timezone-naive
                local_dt = dt.astimezone(tehran_tz).replace(tzinfo=None)
                component['DTSTART'].dt = local_dt
        
        # Convert DTEND
        if 'DTEND' in component:
            dt = component['DTEND'].dt
            if isinstance(dt, datetime) and dt.tzinfo:
                local_dt = dt.astimezone(tehran_tz).replace(tzinfo=None)
                component['DTEND'].dt = local_dt
    
    # Write the modified calendar
    with open(CALENDARS_DIR/output_file, 'wb') as f:
        f.write(cal.to_ical())
    
    print(f"Timezone fixed! Saved to {output_file}")

# Usage
def add_calendar_name(calendar, name):
    calendar.calendar_name = name
    save_calendar(f"{name}.ics", calendar)
    print(f"Add calendar name `{calendar.calendar_name}`")


def add_calendar_color(calendar, color):
    calendar.color = color
    save_calendar(f"{calendar.calendar_name}.ics", calendar)
    print(f"Add color name `{calendar.color}`")

def calendar_meta_data(cal, new_cal):
    for prop_name, prop_value in cal.property_items():
        if prop_name not in ['components', 'prodid', 'version']:
            new_cal.add(prop_name, prop_value)
    return new_cal


def calendar_modify(cal, keywords, data, filename):
    new_cal = Calendar()
    count = 0

    for component in cal.walk():
        if component.name == "VEVENT":
            summary = component.get("summary").lower().strip()
            if any(keyword.lower().strip() in summary for keyword in keywords):
                new_event = copy.deepcopy(component)
                for key, value in data.items():
                    new_event[key] = value
                print(summary, "-->", new_event["summary"])
                print(new_event["description"])
                new_cal.add_component(new_event)
                count += 1
            else:
                new_cal.add_component(component)

    print(f"Changed: {count}")
    return new_cal


def delete_span_br(cal_name, filename):
    cal = read_calendar(cal_name)
    new_cal = Calendar()
    count = 0

    for component in cal.walk():
        if component.name == "VEVENT":
            description = component.get("description")
            new_event = copy.deepcopy(component)
            if description:
                clean_description = description.lower().replace("<span>", "").replace("</span>", "").replace("<br>", "\\n").replace("br>", "\\n").replace("none", "").strip()
                new_event["description"] = clean_description
                new_cal.add_component(new_event)
                count += 1
            else:
                new_cal.add_component(component)

    create_calendar(filename, new_cal)
    print("Description Changed:", count)


def print_all_unique_events(cal):
    print("--------- Unique events -------------")
    events = {}

    for component in cal.walk():
        if component.name == "VEVENT":
            summary = component["summary"]
            if summary in events:
                events[summary] += 1
            else:
                events[summary] = 1

    for summary, count in events.items():
        print(summary, count)

def print_description(cal, summary):
    print("--------- Event Description -------------")
    for component in cal.walk():
        if component.name == "VEVENT":
            event_summary = component["summary"]
            if event_summary.lower() == summary.lower():
                print(component.get("description", "no description"))
                break




def modify_description(cal):
    pass


def modify_by_summary(cal):
    description = [
        "Area: Reading",
        "Type: Novel",
        "Project: Brave New World",
        "Difficulty: 2",
        "Tags: sci-fi",
    ]
    data = {
        "summary": "Brave new world",
        "description": "\n".join(description),
    }

    keywords = ["brave new world"]

    new_cal = calendar_modify(cal, keywords, data, "growth.ics")

    print_description(new_cal, data.get("summary"))

    # create_calendar("growth.ics", new_cal)

    print_all_unique_events(cal)



def main():

    # extract to get calendars file --
    # unzip_to_calendars("/home/saeed//dwl/saeed.ghollami@gmail.com.ical.zip") 

    # -- rename calendars file -- 
    rename_calendars()
    #
    #
    # # -- calendars
    growth = read_calendar("growth.ics")
    modify_by_summary(growth)
    # work = read_calendar("work.ics")
    # saeed = read_calendar("saeed.ics")
    # study = read_calendar("study.ics")
    # #
    # # # -- delete span and br *MUST FIRST*
    # delete_span_br("work.ics", "work.ics")
    # delete_span_br("saeed.ics", "saeed.ics")
    # delete_span_br("growth.ics", "growth.ics")
    # delete_span_br("study.ics", "study.ics")
    # #
    # # -- fix time zone --
    # fix_timezone_in_ics("growth.ics", "growth.ics")
    # fix_timezone_in_ics("work.ics", "work.ics")
    # fix_timezone_in_ics("saeed.ics", "saeed.ics")
    # fix_timezone_in_ics("study.ics", "study.ics")
    # #
    # # # -- Add extra fields ---
    # add_calendar_name(growth, "growth")
    # add_calendar_name(work, "work")
    # add_calendar_name(study, "study")
    # add_calendar_name(saeed, "saeed")
    #
    # # # # # -- add colors
    # add_calendar_color(growth, "#A479B1")
    # add_calendar_color(work, "#489160")
    # add_calendar_color(study, "#4B99D2")
    # add_calendar_color(saeed, "#7C7C7C")



if __name__ == "__main__":
    main()
