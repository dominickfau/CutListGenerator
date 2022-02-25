from __future__ import annotations
import json
from dataclasses import dataclass
from PyQt5 import QtCore, QtGui, QtWidgets


@dataclass
class DateRange:
    text: str
    start: QtCore.QDate = None
    end: QtCore.QDate = None

    @staticmethod
    def all() -> DateRange:
        """Return a DateRange object that represents all dates"""
        return DateRange("All", QtCore.QDate.currentDate(), QtCore.QDate.currentDate())

    @staticmethod
    def today() -> DateRange:
        """Returns a DateRange for today."""
        return DateRange(
            "Today", QtCore.QDate.currentDate(), QtCore.QDate.currentDate()
        )

    @staticmethod
    def yesterday() -> DateRange:
        """Returns a DateRange for yesterday."""
        today = QtCore.QDate.currentDate()
        return DateRange("Yesterday", today.addDays(-1), today.addDays(-1))

    @staticmethod
    def this_week() -> DateRange:
        """Returns a DataRange starting on sunday and ending on saturday for the current week."""
        today = QtCore.QDate.currentDate()
        start = today.addDays(-(today.dayOfWeek()))
        end = start.addDays(6)
        return DateRange("This Week", start, end)

    @staticmethod
    def last_week() -> DateRange:
        """Returns a DataRange starting on sunday and ending on saturday for the last week."""
        today = QtCore.QDate.currentDate()
        begining_of_week = DateRange.today().start.addDays(-(7 + today.dayOfWeek()))
        end_of_week = begining_of_week.addDays(6)
        return DateRange("Last Week", begining_of_week, end_of_week)

    @staticmethod
    def this_month() -> DateRange:
        """Returns a DataRange starting on the first of the month and ending on the last of the month for the current month."""
        today = QtCore.QDate.currentDate()
        begining_of_month = QtCore.QDate(today.year(), today.month(), 1)
        end_of_month = QtCore.QDate(today.year(), today.month(), today.daysInMonth())
        return DateRange("This Month", begining_of_month, end_of_month)

    @staticmethod
    def last_month() -> DateRange:
        """Returns a DataRange starting on the first of the last month and ending on the last of the last month."""
        today = QtCore.QDate.currentDate()
        begining_of_month = QtCore.QDate(today.year(), today.month(), 1)
        end_of_month = QtCore.QDate(today.year(), today.month(), today.daysInMonth())
        begining_of_last_month = begining_of_month.addMonths(-1)
        end_of_last_month = end_of_month.addMonths(-1)
        return DateRange("Last Month", begining_of_last_month, end_of_last_month)

    @staticmethod
    def this_year() -> DateRange:
        """Returns a DataRange starting on the first of january and ending on the last of december for the current year."""
        today = QtCore.QDate.currentDate()
        begining_of_year = QtCore.QDate(today.year(), 1, 1)
        end_of_year = QtCore.QDate(today.year(), 12, 31)
        return DateRange("This Year", begining_of_year, end_of_year)

    @staticmethod
    def last_year() -> DateRange:
        """Returns a DataRange starting on the first of january and ending on the last of december for the current year."""
        today = QtCore.QDate.currentDate()
        begining_of_year = QtCore.QDate(today.year() - 1, 1, 1)
        end_of_year = QtCore.QDate(today.year() - 1, 12, 31)
        return DateRange("Last Year", begining_of_year, end_of_year)

    @staticmethod
    def up_to_month_end() -> DateRange:
        """Returns a DateRange starting on 1-1-2000 ending on the last of the current month."""
        today = QtCore.QDate.currentDate()
        start = QtCore.QDate(2000, 1, 1)
        end_of_month = QtCore.QDate(today.year(), today.month(), today.daysInMonth())
        return DateRange("Up to Month End", start, end_of_month)


class QDateRangeSelection(QtWidgets.QWidget):
    """Widget for selecting a date range."""

    LABEL_END_CHARACTOR = ":"
    DEFAULT_DATA_RANGE = DateRange.all()
    DATE_SELECTION_RANGES = [
        DateRange.all(),
        DateRange.today(),
        DateRange.yesterday(),
        DateRange.this_week(),
        DateRange.this_month(),
        DateRange.this_year(),
        DateRange.last_week(),
        DateRange.last_month(),
        DateRange.last_year(),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)

        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.main_layout)

        self.date_selection_combo_box = QtWidgets.QComboBox()
        self.date_selection_combo_box.addItems(
            [date_range.text for date_range in self.DATE_SELECTION_RANGES]
        )
        self.date_selection_combo_box.setCurrentText(self.DEFAULT_DATA_RANGE.text)

        from_label = QtWidgets.QLabel("From")
        from_label.setAlignment(QtCore.Qt.AlignCenter)
        from_label.setBuddy(self.date_selection_combo_box)
        from_label.setSizePolicy(
            QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Preferred
        )

        self.start_date_edit = QtWidgets.QDateEdit()
        self.start_date_edit.setDate(self.DEFAULT_DATA_RANGE.start)
        self.start_date_edit.setSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred
        )
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDisplayFormat("MM/dd/yyyy")

        to_label = QtWidgets.QLabel("to")
        to_label.setAlignment(QtCore.Qt.AlignCenter)
        to_label.setBuddy(self.date_selection_combo_box)
        to_label.setSizePolicy(
            QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Preferred
        )

        self.end_date_edit = QtWidgets.QDateEdit()
        self.end_date_edit.setDate(self.DEFAULT_DATA_RANGE.end)
        self.end_date_edit.setSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred
        )
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDisplayFormat("MM/dd/yyyy")

        self.date_selection_combo_box.currentIndexChanged.connect(
            self.date_range_combo_box_changed
        )

        self.main_layout.addWidget(self.date_selection_combo_box)
        self.main_layout.addWidget(from_label)
        self.main_layout.addWidget(self.start_date_edit)
        self.main_layout.addWidget(to_label)
        self.main_layout.addWidget(self.end_date_edit)

    def get_date_range_start_date(self) -> QtCore.QDate:
        """Return the start date of the date range."""
        return self.start_date_edit.date()

    def get_date_range_end_date(self) -> QtCore.QDate:
        """Return the end date of the date range."""
        return self.end_date_edit.date()

    def get_selected_date_range(self) -> DateRange:
        """Return the selected date range."""
        text = self.date_selection_combo_box.currentText()
        return DateRange(
            text, start=self.start_date_edit.date(), end=self.end_date_edit.date()
        )

    def date_range_combo_box_changed(self, index: int) -> None:
        """Handle the change of the date range combo box. Set the start and end dates to the appropriate values."""
        date_range = self.DATE_SELECTION_RANGES[index]
        self.start_date_edit.setDate(date_range.start)
        self.end_date_edit.setDate(date_range.end)
