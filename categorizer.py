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
            words.append(splited_word[-1])
        else:
            words.append(word)
    
    words =  Counter(words)
    return words

def extract_sumary(cal):
    cal = read_calendar(cal)
    for event in cal.events:
        print(str(event["summary"]))


def modify(calendar, rows):
    modified_events = 0
    for component in calendar.walk():
        if component.name == "VEVENT":
            for row in rows:
                keyword, summary, area, project, tags, difficulty, detail = row
                description = f"Area: {area}\nProject: {project}\nTags: {tags}\nDifficulty: {difficulty}\nDetail: {detail}\n"
                if "summary" in component:
                    calendar_summary = component["summary"].lower()
                    if keyword.lower() in calendar_summary:
                        component["summary"] = summary
                        component["description"] = description
                        modified_events += 1
                        break
                                                                  
    print("Modified events: ", modified_events)
    return calendar


def main():
    rows = [
        ("farnaz", "Teaching Farnaz", "Teaching", "Teaching Farnaz", "python, datasci", 4, "Teaching Farnaz Shasti."),
        ("arad", "Teaching Arad", "Teaching", "Teaching Arad", "python", 3, "Teaching Arad."),
        ("motlag", "Teaching Motlag", "Teaching", "Teaching Motlag", "python, django", 4, "Teaching Mina Motlag."),
        ("mehrdad", "Teaching Mehrdad", "Teaching", "None", "python, matplotlib", 4,"Working with Mehrdad on varius projects"),
        ("saeed", "Teaching dr Saeed", "Teaching", "None", "python", 4,"Teaching dr Saeed"),
        ("saeid", "Teaching dr Saeed", "Teaching", "None", "python", 4,"Teaching dr Saeed"),
        ("openpose", "Teaching dr Saeed", "Teaching", "None", "python", 4,"Teaching dr Saeed"),

        ("snapp", "Snapp", "Snapp", "None", "None", 4,"Driving snapp for food money."),
        ("dad", "Help dad", "Ourshop", "None", "None", 4,"Help dad on shop or home"),
        ("ourshop", "Help dad", "Ourshop", "None", "None", 4,"Help dad on shop or home"),
        ("jahzieh", "Help dad", "Ourshop", "None", "None", 4,"Help dad on shop or home"),

        ("content", "Make Instagram post", "Content", "None", "instagram, post", 3,"Make instagram post to create networks."),
        ("post", "Make Instagram post", "Content", "None", "instagram, post", 3,"Make instagram post to create networks."),

        ("gcal", "Develop gcal", "Dev", "gcal", "python, datasci", 2, "Google calendar visualizer to get insight."),
        ("pyquiz", "Develop pyquiz", "Dev", "pyquiz", "javascript, web", 3, "Quiz application to determine level of the participent."),
        ("random", "Random projects", "Dev", "Random projects", "python", 2, "Random project just fill the calendar."),
        ("coding signal", "Signal plot", "Dev", "Signal Plot", "python, matplotlib", 4,"Signal visulaizer for Nastran files."),
        ("flet", "Learn Flet", "Dev", "Learn Flet", "learn, flet", 2,"learn the basic of the flet framework"),
        ("felt", "Learn Flet", "Dev", "Learn Flet", "learn, flet", 2,"learn the basic of the flet framework"),

        ("vim", "Modify neovim", "Dev", "Learn vim/neovim", "tools, neovim", 1,"Modifiy or learn vim/neovim"),

        ("codewar", "Codewars", "Dev", "None", "problem-solving, python", 4,"Problem solving on codewars"),
        ("exerci", "Exercisim", "Dev", "None", "problem-solving, python", 4,"Problem solving on exercisim"),
        ("tkinter", "Learn tkinter", "Dev", "Tkinter by example", "tkinter, gui", 2,"Learn to develop desktop app using tkinter"),
        ("tk ", "Learn tkinter", "Dev", "Tkinter by example", "tkinter, gui", 2,"Learn to develop desktop app using tkinter"),
        ("emacs", "Learn Emacs", "Dev", "None", "linux, emacs", 4,"Learn the basics and try out emacs."),
        ("linux", "Linux config", "Dev", "None", "linux, bash", 2,"Doing varius config on Linux."),
        ("tmuxer", "Develop temuxer", "Dev", "Tmux session switcher", "bash, tmux", 4,"Build a shell script with fzf to switch tmux sessions."),
        ("ostadsgo", "Ostadsgo github page", "Dev", "Ostadsgo github page", "python, web", 2,"Develop my portfolio website for github page."),
        ("github", "Ostadsgo github page", "Dev", "Ostadsgo github page", "python, web", 2,"Develop my portfolio website for github page."),
        ("sys", "Learn Systems", "Dev", "Learn systems", "python, web", 2,"Learn about how systems work."),
        ("think", "Read Think Python", "Dev", "Think Python", "python, book", 2,"Read and Learn the book Think Python."),
    ]


    cal = read_calendar("temp.ics")
    modify(cal, rows)
    save_calendar("temp.ics", cal)

    items = counter("temp.ics")

    print(counter('temp.ics'))
    




if __name__ == "__main__":
    main()



