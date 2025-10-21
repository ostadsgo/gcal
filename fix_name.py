from pathlib import Path
import icalendar
from icalendar import Calendar


BASE_DIR = Path(__file__).resolve().parent
CAL_DIR = BASE_DIR / "cal"
JSON_DIR = BASE_DIR / "json"
SAEED_CAL_PATH = CAL_DIR / "saeed.ics"


saeed_cal = icalendar.Calendar.from_ical(SAEED_CAL_PATH.read_text())


def tofile(filename, content):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)


def categorize(summary):

    category = {
        "Basic": (
            "lunch",
            "breakfast",
            "dinner",
            "sleep",
            "rest",
            "nap",
            "dinner!",
            "wifi",
            "shit",
            "sick",
            "wake",
            "wake",
            "wakeup",
            "hair",
            "shower",
            "bed",
            "routine",
            "terapist",
            "pc",
            "free",
            "balcon",
            "bank",
            "supper",
            "music",
            "doctor",
            "internet",
            "chill",
            "daydreaming",
            "md",
            "me",
            "scheduled",
            "brunch",
            "off",
            "meal",
            "podcast",
            "calender",
        ),
        "Brunt": (
            "phone",
            "init",
            "youtube",
            "idk",
            "know",
            "wasted",
            "bullshit",
            "yt",
            "ocd",
            "insta",
            "phone",
            "scroll",
            "scrolling",
            "__init__",
            "pintrest",
        ),
        "Friend": ("ramin", "nil", "behzad", "nilofar's"),
        "Wife": ("commute", "driving", "kid", "sofia", "guest"),
        "Teacing": (
            "teaching",
            "mojgan",
            "masali",
            "shahin",
            "mehdi",
            "sami",
            "marsli",
            "std",
            "bahar",
            "msali",
            "dabiri,",
            "amin",
            "exam",
            "mehrdad",
            "yones",
            "raeisi",
            "rox",
            "roxana",
            "arshia",
            "zahra",
            "kian",
            "afshari",
            "maşayex",
            "shayan",
            "rashti",
            "sj",
            "sajad",
            "rezaei",
            "abolfaz",
            "ghahremani",
            "malah",
            "shahla",
            "shahla",
            "zarnegar",
            "zarneger",
            "ali",
            "sm",
        ),
        "Movie": ("movie", "anime", "heist", "watch", "planet", "spy", "peaky"),
        "Family": ("sama", "funeral", "marrage", "fam", "mom"),
        "Reading": ("reading", "book", "audio", "read"),
        "Python": ("python", "cory", "flask"),
        "Web": ("html", "css", "javascript", "js", "web"),
        "Trip": ("village",),
        "Journal": (
            "journaling",
            "goal",
            "plan",
            "planning",
            "click",
            "notion",
            "syllabus",
            "goals",
            "journal",
            "thinking",
            "productivity",
        ),
        "Content": ("blogging"),
        "Dev": (
            "samanabrah",
            "pysimplegui",
            "pcc",
            "saeixgholami.github.io",
            "tkinter",
            "github",
            "programming",
            "dev",
            "saeidx",
            "brain",
            "coding",
            "pmo",
            "vis",
        ),
        "Work": ("work", "shop", "ourshop"),
        "house": (
            "housekeeping",
            "home",
            "chores",
            "bread",
            "buy",
            "clean",
            "room",
            "house",
            "cleaing",
        ),
        "workout": (
            "walk",
            "gym",
            "yoga",
            "walking",
            "exercise",
            "dojo",
            "workout",
            "out",
        ),
        "Study": (
            "computer",
            "learn",
            "math",
            "education",
            "tut",
            "cs",
            "english",
            "cb",
            "lang",
            "dj4e",
            "git",
            "ebook",
            "linux",
        ),
    }

    summary = summary.strip()
    if ":" in summary:
        return summary
    words = [word.strip() for word in summary.split()]

    # --- Categorization ---
    found = False
    val = ""
    for word in words:
        for main_cat, items in category.items():
            if word in items:
                return f"{main_cat}: {summary}"
    return f"NO CAT: {summary}"


def main():
    from icalendar import Calendar, Event
    from datetime import datetime

    # Read an existing calendar file
    with open("cal/saeed.ics", "r") as f:
        cal = Calendar.from_ical(f.read())

    # Modify summaries of all events
    for component in cal.walk():
        if component.name == "VEVENT":
            summary = component.get("summary", "no summary").lower()
            new_summary = categorize(summary)
            component["summary"] = new_summary

    # Save the modified calendar
    with open("modified_calendar.ics", "wb") as f:
        f.write(cal.to_ical())


main()
