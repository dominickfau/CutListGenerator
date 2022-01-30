from __future__ import annotations
from typing import List
from PyQt5 import QtCore, QtWidgets, QtGui


class CustomQTableWidget(QtWidgets.QTableWidget):
    column_visibility_changed = QtCore.pyqtSignal(int, bool)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.header_context_menu = self.set_header_context_menu()

        self.setAlternatingRowColors(True)
        self.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.setSelectionBehavior(
            QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.horizontalHeader().setStretchLastSection(True)

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.horizontalHeader().setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.horizontalHeader().customContextMenuRequested.connect(
            self.show_header_context_menu
        )
        self.horizontalHeader().setSortIndicatorShown(True)
        self.horizontalHeader().sortIndicatorChanged.connect(self.sort_table)

        font = QtGui.QFont()
        font.setBold(True)
        self.horizontalHeader().setFont(font)

    def set_table_headers(self, headers: List[str]):
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)
        self.header_context_menu = self.set_header_context_menu()

    def sort_table(self, column, order):
        self.sortItems(column, order)

    def toggle_column(self, checked):
        action = self.sender()
        header_text = action.text()

        for column in range(self.columnCount()):
            header = self.horizontalHeaderItem(column)
            if header.text() != header_text:
                continue

            self.setColumnHidden(column, not checked)
            # emit a signal on the column visibility change
            self.column_visibility_changed.emit(column, checked)

    def set_header_context_menu(self) -> QtWidgets.QMenu:
        menu = QtWidgets.QMenu()

        # menu.addAction("Hide This Column.", self.resize_all_columns)
        menu.addSeparator()

        headers = [self.horizontalHeaderItem(i) for i in range(self.columnCount())]
        for header in headers:
            action = QtWidgets.QAction(header.text(), self)
            action.setCheckable(True)
            action.setChecked(True)
            action.toggled.connect(self.toggle_column)
            menu.addAction(action)

        menu.addSeparator()

        # menu.addAction("Auto Resize This Column", self.resize_current_column)
        menu.addAction("Auto Resize All Columns", self.resize_all_columns)
        # TODO: Add ability to set what columns are shown
        return menu

    def show_header_context_menu(self, pos):
        self.header_context_menu.exec_(self.horizontalHeader().mapToGlobal(pos))

    def resize_current_column(self):
        # FIXME: Pass in the current column index
        self.resizeColumnToContents(self.currentColumn())

    def resize_all_columns(self):
        for column in range(self.columnCount()):
            self.resizeColumnToContents(column)

    def show_row_context_menu(self, pos):
        menu = QtWidgets.QMenu()
        menu.addAction("Copy", self.copy_selected_rows)
        menu.exec_(self.mapToGlobal(pos))

    def add_row(self, row_data: List[str]):
        row_count = self.rowCount()
        column_count = self.columnCount()
        assert len(row_data) == column_count

        self.insertRow(row_count)
        for column, data in enumerate(row_data):
            self.setItem(row_count, column, QtWidgets.QTableWidgetItem(data))

    def copy_selected_rows(self):
        rows = self.selectionModel().selectedRows()
        if not rows:
            return
        rows = sorted(rows)
        row_count = len(rows)
        column_count = self.columnCount()
        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.clear()
        for row in rows:
            row_data = []
            for column in range(column_count):
                item = self.item(row.row(), column)
                if item is None:
                    row_data.append("")
                else:
                    row_data.append(item.text())
            clipboard.setText(",".join(row_data))
            if row.row() != row_count - 1:
                clipboard.setText(clipboard.text() + "\n")
