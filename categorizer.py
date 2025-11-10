import os
from collections import Counter
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

def counter(calendar_name):
    cal = read_calendar(calendar_name)
    words = []
    for event in cal.events:
        word = str(event["summary"])
        if ':' in word:
            splited_word = word.split(":", 1)
            words.append(splited_word[-1].strip())
        else:
            words.append(word)
    
    words =  Counter(words)
    return words

def move_events_by_keyword(source_cal_path, target_cal_path, keywords):
    """Move events containing specific keywords to another calendar"""
    
    # Read source calendar
    with open(source_cal_path, 'r', encoding='utf-8') as f:
        source_cal = Calendar.from_ical(f.read())
    
    # Create target calendar (or read existing one)
    try:
        with open(target_cal_path, 'r', encoding='utf-8') as f:
            target_cal = Calendar.from_ical(f.read())
    except FileNotFoundError:
        # Create new calendar if target doesn't exist
        target_cal = Calendar()
        target_cal.add('prodid', '-//My Calendar//mxm.dk//')
        target_cal.add('version', '2.0')
    
    moved_count = 0
    
    # Find and move events
    components_to_remove = []
    for component in source_cal.walk():
        if component.name == "VEVENT":
            summary = str(component.get('summary', '')).lower()
            
            # Check if event matches any keyword
            if any(keyword.lower() in summary for keyword in keywords):
                # Copy event to target calendar
                target_cal.add_component(copy.deepcopy(component))
                # Mark for removal from source
                components_to_remove.append(component)
                moved_count += 1
    
    # Remove moved events from source calendar
    for component in components_to_remove:
        source_cal.subcomponents.remove(component)
    
    # Save both calendars
    with open(source_cal_path, 'wb') as f:
        f.write(source_cal.to_ical())
    
    with open(target_cal_path, 'wb') as f:
        f.write(target_cal.to_ical())
    
    print(f"Moved {moved_count} events to {target_cal_path}")
    return moved_count

def extract_sumary(cal):
    cal = read_calendar(cal)
    for event in cal.events:
        print(str(event["summary"]))

def create_description(cal):
    for component in cal.walk():
        description = f"Area:\nProject:\nTags:\nDifficulty:\nDetail:\n"
        component["description"] = description
    return cal

def modify(calendar, rows):
    modified_events = 0
    for component in calendar.walk():
        if component.name == "VEVENT":
            for row in rows:
                keyword, summary, area, project, tags, difficulty, detail = row
                description = f"Area: {area}\nProject: {project}\nTags: {tags}\nDifficulty: {difficulty}\nDetail: {detail}\n"
                if "summary" in component:
                    # description = f"Area:\nProject:\nTags:\nDifficulty:\nDetail:\n"
                    # component["description"] = description
                    calendar_summary = component["summary"].lower()
                    if keyword.lower() in calendar_summary.lower():
                        component["summary"] = summary
                        component["description"] = description
                        modified_events += 1
                        break

                                                                  
    print("Modified events: ", modified_events)
    return calendar


def main():
    rows = [
        # ("sleep", "Sleep", "Sleep", "", "", 1, ""),
        # ("breakfast", "Eat", "", "", "", 1, ""),
        # ("dinner", "Eat", "", "", "", 1, ""),
        # ("lunch", "Eat", "", "", "", 1, ""),
        # ("wake", "Sleep", "Sleep", "", "", 1, ""),
        # ("yt", "Youtube", "Youtbue", "", "", 1, ""),
        # ("youtube", "Youtube", "Youtbue", "", "", 1, ""),
        # ("youtbue", "Youtube", "Youtbue", "", "", 1, ""),
        # ("phone", "Phone", "", "", "", 1, ""),
        #
        # ("kid", "Play with Sofia", "Sofia", "", "", 1, ""),
        #
        # ("walk", "Walk", "Workout", "", "", 1, ""),
        #
        # ("reading", "Reading", "Reading", "", "", 2, ""),
        #
        # ("reading", "Reading", "Reading", "", "", 1, ""),
        # ("read", "Reading", "Reading", "", "", 1, ""),
        #
        # ("mehrdad", "Teaching Mehrdad", "Teaching", "", "", 3, ""),
        # ("shayan", "Teaching Shayan", "Teaching", "", "", 3, ""),
        # ("sajad", "Teaching Sajad", "Teaching", "", "", 3, ""),
        # ("sj", "Teaching Sajad", "Teaching", "", "", 3, ""),
        # ("shahin", "Teaching shahin", "Teaching", "", "", 3, ""),
        # ("zahra", "Teaching zahra", "Teaching", "", "", 3, ""),
        # ("mojgan", "Teaching mojgan", "Teaching", "", "", 3, ""),
        # ("masali", "Teaching Masali", "Teaching", "", "", 3, ""),
        # ("kian", "Teaching Kian", "Teaching", "", "", 3, ""),
        #
        # ("ramin", "Ramin", "Friend", "", "", 3, ""),
        #
        # # dev
        # ("ostad", "Dev ostadsgo", "Dev", "Ostadgso", "python, html, css", 3, "ostadsgo github page"),
        #
        # ("movie", "Watch Movie", "Movie", "", "", 1, ""),
        # ("anime", "Watch anime", "Movie", "", "", 1, ""),
        # ("monster", "Monster", "Movie", "", "anime", 1, ""),

        # ("Arad", "Teaching Arad", "Teaching", "", "", 3, ""),
        # ("zarnegar", "Teaching zarnegar", "Teaching", "", "", 3, ""),
        #
        # ("mehradad", "Teaching Mehrdad", "Teaching", "", "", 3, ""),
        # ("linux", "Learn config", "Dev", "", "linux, bash", 2, ""),

        ("init", "Phone", "Phone", "", "", 1, ""),

        ("commute", "Commute", "Wife", "", "", 1, ""),
        ("wife", "Wife", "Wife", "", "", 1, ""),
        ("family", "Family", "Wife", "", "", 1, ""),
        ("parent", "Parent", "Family", "", "", 1, ""),
        ("mom", "Mom", "Family", "", "", 1, ""),


    ]


    cal = read_calendar("saeed_temp.ics")
    cal = modify(cal, rows)
    save_calendar("saeed_temp.ics", cal)


    print(counter("saeed_temp.ics"))




if __name__ == "__main__":
    main()



