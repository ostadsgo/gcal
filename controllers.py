"""contoller.py: core part. get data from model and listen to view."""

import os
import glob
import zipfile
from pathlib import Path

import converter
from models import DatabaseManager

BASE_DIR = Path(__file__).resolve().parent
ICS_DIR = BASE_DIR / "ics"
DB_DIR = BASE_DIR / "db"
DB_FILE = DB_DIR / "data.db"
SECONDS_PER_HOUR = 3600

class Controller:
    def __init__(self, context):
        self.context = context
        self.db = DatabaseManager()
        self.model = self.db.model
        self.action_view = context.get_view("action")
        self.calendar_view = context.get_view("calendar")
        self.filter_view = context.get_view("filter")
        self.report_view = context.get_view("report")
        self.stack_chart_view = context.get_view("stack_chart")
        self.bar_chart_view = context.get_view("bar_chart")
        self.hbar_chart_view = context.get_view("hbar_chart")
        self.pie_chart_view = context.get_view("pie_chart")

        # Register events
        self.action_view.register_event_handler("read_calendars", self.handle_read_calendars)
        self.calendar_view.register_event_handler(
            "calendar_select", self.handle_calendar_select
        )
        self.filter_view.register_event_handler(
            "start_date_selected", self.handle_start_date_selected
        )
        self.filter_view.register_event_handler(
            "end_date_selected", self.handle_end_date_selected
        )
        self.filter_view.register_event_handler(
            "filter_select", self.handle_filter_select
        )
        self.filter_view.register_event_handler("item_select", self.handle_item_select)

    def initialize(self):
        """First load +  methods must only run once."""

        # calendars
        self.create_calendars_card()
        self.update_calendars_card()

        # widgets
        self.update_item_widget()

        # # Charts
        self.update_stack_chart()
        self.update_hbar_chart()
        self.update_bar_chart()
        self.update_pie_chart()
        #
        # # Reports
        self.create_report_rows()
        self.update_filter_report()

    def create_calendars_card(self):
        calendars = self.model.get_calendars_by_usage()
        self.calendar_view.create_cards(calendars)

    def create_report_rows(self):
        calendar_id = self.calendar_view.selected_calendar_id
        start_date = self.filter_view.start_date
        end_date = self.filter_view.end_date
        filter_val = self.filter_view.filter_var.get()
        item = self.filter_view.item_var.get()
        report = self.model.report_by_filter(
            calendar_id, start_date, end_date, filter_val, item
        )
        self.report_view.create_report_rows(report)

    def update_calendars_card(self):
        calendars = self.model.get_calendars_by_usage()
        for calendar in calendars:
            self.calendar_view.update_card(calendar)

    def update_item_widget(self):
        calendar_id = self.calendar_view.selected_calendar_id
        start_date = self.filter_view.start_date
        end_date = self.filter_view.end_date
        filter_val = self.filter_view.filter_var.get()
        rows = self.model.distinct_values_by_filter(
            calendar_id, start_date, end_date, filter_val
        )
        values = [row.name for row in rows]
        self.filter_view.update_item_values(values)

    def update_filter_report(self):
        calendar_id = self.calendar_view.selected_calendar_id
        start_date = self.filter_view.start_date
        end_date = self.filter_view.end_date
        filter_val = self.filter_view.filter_var.get()
        item = self.filter_view.item_var.get()
        report = self.model.report_by_filter(
            calendar_id, start_date, end_date, filter_val, item
        )
        self.report_view.update_rows(report)

    # -- update charts --
    def update_bar_chart(self):
        calendar_id = self.calendar_view.selected_calendar_id
        start_date = str(self.filter_view.start_date)
        end_date = str(self.filter_view.end_date)
        types = self.model.distinct_types_by_date_range(
            calendar_id, start_date, end_date
        )
        self.bar_chart_view.update_bar_chart(types)

    def update_stack_chart(self):
        calendar_id = self.calendar_view.selected_calendar_id
        start_date = self.filter_view.start_date
        end_date = self.filter_view.end_date
        filter_val = self.filter_view.filter_var.get()
        item = self.filter_view.item_var.get()
        rows = self.model.daily_duration_by_filter(
            calendar_id, start_date, end_date, filter_val, item
        )
        if item:
            # chart
            days = range(1, len(rows) + 1)
            hrs = [row.total_duration for row in rows]
            calendar = self.model.get_calendar_by_usage(calendar_id)
            self.stack_chart_view.update_stack_chart(days, hrs, calendar.calendar_color)

    def update_hbar_chart(self):
        calendar_id = self.calendar_view.selected_calendar_id
        start_date = str(self.filter_view.start_date)
        end_date = str(self.filter_view.end_date)
        areas = self.model.distinct_areas_by_date_range(
            calendar_id, start_date, end_date
        )
        self.hbar_chart_view.update_hbar_chart(areas)

    def update_pie_chart(self):
        calendar_id = self.calendar_view.selected_calendar_id
        start_date = str(self.filter_view.start_date)
        end_date = str(self.filter_view.end_date)
        projects = self.model.distinct_projects_by_date_range(
            calendar_id, start_date, end_date
        )
        self.pie_chart_view.update_pie_chart(projects)

    # --------------
    # Handlers
    # ---------------
    def handle_calendar_select(self):
        self.update_item_widget()
        self.update_stack_chart()
        self.update_pie_chart()
        self.update_hbar_chart()
        self.update_bar_chart()
        self.update_filter_report()

    def handle_filter_select(self):
        self.update_item_widget()
        self.update_stack_chart()
        self.update_filter_report()

    def handle_start_date_selected(self):
        # update the item widget
        self.update_item_widget()
        # update charts
        self.update_stack_chart()
        self.update_bar_chart()
        self.update_pie_chart()
        self.update_hbar_chart()
        # update report
        self.update_filter_report()

    def handle_end_date_selected(self):
        # update the item widget
        self.update_item_widget()
        # charts
        self.update_stack_chart()
        self.update_bar_chart()
        self.update_pie_chart()
        self.update_hbar_chart()
        # # reports
        self.update_filter_report()

    def handle_item_select(self):
        self.update_stack_chart()
        self.update_filter_report()

    def handle_read_calendars(self, file_path):
        # 0. Remove old ics files
        os.makedirs(ICS_DIR, exist_ok=True)

        for ics_file in ICS_DIR.glob("*.ics"):
            ics_file.unlink() # remove the file
            print(f"File {ics_file} removed.")

        # Remove db
        DB_FILE.unlink()
        print(f"Remove db file {DB_FILE}")

        with zipfile.ZipFile(file_path, 'r') as zip_file:
            zip_file.extractall(ICS_DIR)

        print(f"ICS files extracted to: {ICS_DIR}")
        
        # Rename ics_files to clean name
        for ics_file in ICS_DIR.glob("*.ics"):
            if "Birthday" in str(ics_file):
                ics_file.unlink()
                print("Birthday calendar removed.")
                continue
            filename = ics_file.name.split("_")[0] + ".ics"
            ics_file.rename(ICS_DIR / filename.lower())
            print("Files renamed.")


        # 3. create db file from ics files
        converter.merge_to_one_db()

        # Reopen database after creating new database
        self.db.close()
        self.db = DatabaseManager()
        self.model = self.db.model

        # 4. refresh the UI. calendars chart everything.
        self.update_calendars_card()

        # widgets
        self.update_item_widget()

        # # Charts
        self.update_stack_chart()
        self.update_hbar_chart()
        self.update_bar_chart()
        self.update_pie_chart()
        
        # # Reports
        self.update_filter_report()

