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
        return DateRange("All")

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


class QDateRangeSelection(QtWidgets.QWidget):
    """Widget for selecting a date range."""

    LABEL_END_CHARACTOR = ":"
    DEFAULT_DATA_RANGE = DateRange.today()
    DATE_SELECTION_RANGES = [
        DateRange.today(),
        DateRange.yesterday(),
        DateRange.this_week(),
        DateRange.this_month(),
        DateRange.this_year(),
        DateRange.last_week(),
        DateRange.last_month(),
        DateRange.last_year(),
    ]

    def __init__(self, *label_text: str, parent=None):
        super().__init__(parent)

        self.main_layout = QtWidgets.QFormLayout()
        self.setLayout(self.main_layout)

        for label_text in label_text:
            widget_name_suffix = self.convert_text_to_widget_name_suffix(label_text)
            h_box_layout = QtWidgets.QHBoxLayout()

            label = QtWidgets.QLabel(f"{label_text}{self.LABEL_END_CHARACTOR}")

            date_selection_combo_box = QtWidgets.QComboBox()
            date_selection_combo_box.setObjectName(
                f"date_selection_combo_box_{widget_name_suffix}"
            )
            date_selection_combo_box.addItems(
                [date_range.text for date_range in self.DATE_SELECTION_RANGES]
            )
            date_selection_combo_box.setCurrentText(self.DEFAULT_DATA_RANGE.text)

            from_label = QtWidgets.QLabel("From")
            from_label.setAlignment(QtCore.Qt.AlignRight)
            from_label.setBuddy(date_selection_combo_box)
            from_label.setSizePolicy(
                QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Preferred
            )

            start_date_edit = QtWidgets.QDateEdit()
            start_date_edit.setDate(self.DEFAULT_DATA_RANGE.start)
            start_date_edit.setObjectName(f"start_date_edit_{widget_name_suffix}")
            start_date_edit.setSizePolicy(
                QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred
            )
            start_date_edit.setCalendarPopup(True)
            start_date_edit.setDisplayFormat("MM/dd/yyyy")

            to_label = QtWidgets.QLabel("to")
            to_label.setAlignment(QtCore.Qt.AlignRight)
            to_label.setBuddy(date_selection_combo_box)
            to_label.setSizePolicy(
                QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Preferred
            )

            end_date_edit = QtWidgets.QDateEdit()
            end_date_edit.setDate(None)
            end_date_edit.setObjectName(f"end_date_edit_{widget_name_suffix}")
            end_date_edit.setSizePolicy(
                QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred
            )
            end_date_edit.setCalendarPopup(True)
            end_date_edit.setDisplayFormat("MM/dd/yyyy")

            date_selection_combo_box.currentIndexChanged.connect(
                lambda index=date_selection_combo_box.currentIndex(), start=start_date_edit, end=end_date_edit: self.date_range_combo_box_changed(
                    index, start, end
                )
            )

            h_box_layout.addWidget(date_selection_combo_box)
            h_box_layout.addWidget(from_label)
            h_box_layout.addWidget(start_date_edit)
            h_box_layout.addWidget(to_label)
            h_box_layout.addWidget(end_date_edit)

            self.main_layout.addRow(label, h_box_layout)

    @staticmethod
    def convert_text_to_widget_name_suffix(text: str) -> str:
        """Convert the text of a label to a widget name suffix."""
        return text.replace(" ", "_").lower()

    def get_date_range_start_date(self, label_text: str) -> QtCore.QDate:
        """Return the start date of the date range."""
        widget_name_suffix = self.convert_text_to_widget_name_suffix(label_text)
        return self.findChild(
            QtWidgets.QDateEdit, f"start_date_edit_{widget_name_suffix}"
        ).date()

    def get_date_range_end_date(self, label_text: str) -> QtCore.QDate:
        """Return the end date of the date range."""
        widget_name_suffix = self.convert_text_to_widget_name_suffix(label_text)
        return self.findChild(
            QtWidgets.QDateEdit, f"end_date_edit_{widget_name_suffix}"
        ).date()

    def get_selected_date_range(self, label_text: str) -> DateRange:
        """Return the selected date range."""
        widget_name_suffix = self.convert_text_to_widget_name_suffix(label_text)
        index = self.findChild(
            QtWidgets.QComboBox, f"date_selection_combo_box_{widget_name_suffix}"
        ).currentIndex()
        start_date = self.get_date_range_start_date(label_text)
        end_date = self.get_date_range_end_date(label_text)
        date_range = self.DATE_SELECTION_RANGES[index]
        date_range.start = start_date
        date_range.end = end_date
        return date_range

    def date_range_combo_box_changed(
        self,
        index: int,
        start_date_edit: QtWidgets.QDateEdit,
        end_date_edit: QtWidgets.QDateEdit,
    ) -> None:
        """Handle the change of the date range combo box. Set the start and end dates to the appropriate values."""
        date_range = self.DATE_SELECTION_RANGES[index]
        start_date_edit.setDate(date_range.start)
        end_date_edit.setDate(date_range.end)


class Window(QtWidgets.QWidget):
    """Main window."""

    DATE_RANGES = [
        "Date Issued",
        "Date Created",
        "Date Modified",
        "Date Scheduled",
        "Date Fulfilled",
    ]

    def __init__(self, parent=None):
        super().__init__(parent)

        self.main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_layout)

        self.date_range_selection = QDateRangeSelection(*self.DATE_RANGES)
        self.main_layout.addWidget(self.date_range_selection)

        self.push_button = QtWidgets.QPushButton("Push Me")
        self.push_button.clicked.connect(self.on_push_button_clicked)
        self.main_layout.addWidget(self.push_button)

    def on_push_button_clicked(self) -> None:
        """Handle the click of the push button."""
        # Get the date range for the last date range selection.
        x = {}
        for text in self.DATE_RANGES:
            x[text] = self.date_range_selection.get_selected_date_range(text)

        print(x)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())
