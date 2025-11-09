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

def counter(word, words):
    cal = read_calendar("Work.ics")
    words = []
    for event in cal.events:
        word = event["summary"]
        words.append(word)

    

def modify(calendar, keyword, summary, area="", project="", tags="", detail=""):
    cal = Calendar()
    description = ""
    for event in calendar.events:
        event_copy = event.copy()
        if keyword in event.get("summary", "").lower():
            print('true')
            event_copy["summary"] = summary
            description = f"Area: {area}\nProject: {project}\nTags: {tags}\nDetail: {detail}"
            event_copy["description"] = description
        # else:
        #     description = f"Area:\nProject:\nTags:\nDetail:\n"
        #     print('false')
        cal.add_component(event_copy)
    return cal


def main():
    rows = [
        ("gcal", "Develop gcal", "Dev", "gcal", "Python, DataSci", "Google calendar visualizer to get insight."),
        ("pyquiz", "Develop pyquiz", "Dev", "pyquiz", "Javascript, Web", "Quiz application to determine level of the participent."),
        ("farnaz", "Teaching Farnaz", "Teaching", "Teaching Farnaz", "Python, DataSci", "Teaching Farnaz Shasti."),
        ("arad", "Teaching Arad", "Teaching", "Teaching Arad", "Python", "Teaching Arad."),
        ("motlag", "Teaching motlag", "Teaching", "Teaching Motlag", "Python, Django", "Teaching Mina Motlag."),
        ("random", "Random projects", "Dev", "Random projects", "Python", "Random project just fill the calendar."),
        ("coding signal", "Signal plot", "Dev", "Signal Plot", "Python, Matplotlib", "Signal visulaizer for Nastran files."),
        ("flet", "Learn Flet", "Dev", "Learn Flet", "Learn, Flet", "Learn the basic of the flet framework"),
        ("vim", "Modify neovim", "Dev", "Learn vim/neovim", "Tools, neovim", "Modifiy or learn vim/neovim"),
    ]
    for row in rows:
        cal = read_calendar("temp.ics")
        new_cal = modify(cal, *row)
        save_calendar("temp.ics", new_cal)



if __name__ == "__main__":
    main()



