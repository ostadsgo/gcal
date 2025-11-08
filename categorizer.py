import os
# add data

from pathlib import Path

import icalendar
from icalendar import Calendar

BASE_DIR = Path(__file__).resolve().parent
CALENDARS_DIR = BASE_DIR / "calendars"

# read calendar 

def read_calendar(name: str):
    cal_path = CALENDARS_DIR / name
    cal = icalendar.Calendar.from_ical(cal_path.read_text())
    return cal

def save_calendar(name: str, calendar):
    with open(CALENDARS_DIR / name, "wb") as f:
        f.write(calendar.to_ical())

def modify(calendar, keyword, summary, area="", project="", tags="", detail=""):
    cal = Calendar()
    for event in calendar.events:
        event_copy = event.copy()

        print(event["summary"])
        if keyword in event.get("summary", "").lower():
            event_copy["summary"] = summary
            description = f"Area: {area}\nProject: {project}\nTags: {tags}\nDetail: {detail}"
            event_copy["description"] = description
        cal.add_component(event_copy)
    return cal


def main():
    cal = read_calendar("Work.ics")
    data = [
        ("gcal", "Develop gcal", "Dev", "gcal", "Python, DataSci", "Google calendar visualizer to get insight."),
        ("pyquiz", "Develop pyquiz", "Dev", "pyquiz", "Javascript, Web", "Quiz application to determine level of the participent."),
        ("farnaz", "Teaching Farnaz", "Teaching", "Teaching Farnaz", "Python, DataSci", "Teaching Farnaz Shasti."),
        ("arad", "Teaching Arad", "Teaching", "Teaching Arad", "Python", "Teaching Arad."),
        ("motlag", "Teaching motlag", "Teaching", "Teaching Motlag", "Python, Django", "Teaching Mina Motlag."),
        # ("motlag", "Teaching motlag", "Teaching", "Teaching Motlag", "Python, Django", "Teaching Mina Motlag.")
    ]
    new_cal = modify(cal, "pyquiz", "Develop pyquiz", "Dev", "pyquiz", "Javascript, Web", "Quiz application to determine level of the participent")
    # save_calendar("temp.ics", new_cal)



if __name__ == "__main__":
    main()



