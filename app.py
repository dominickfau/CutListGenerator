from __future__ import annotations
from re import S
import sys
import logging
from dataclasses import dataclass
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QRunnable, QThreadPool, pyqtSlot, pyqtSignal, QObject, Qt
from PyQt5.QtWidgets import QApplication, QMessageBox, QProgressBar, QPushButton
import fishbowlorm
from cutlistgenerator import (
    FISHBOWL_DATABASE_USER,
    FISHBOWL_DATABASE_PASSWORD,
    FISHBOWL_DATABASE_HOST,
    FISHBOWL_DATABASE_PORT,
    FISHBOWL_DATABASE_SCHEMA,
)
from cutlistgenerator.database import global_session
from cutlistgenerator.database.models.salesorder import SalesOrder, SalesOrderItem
from cutlistgenerator.settings import *
from cutlistgenerator import utilities
from cutlistgenerator.customwidgets.qtable import CustomQTableWidget
from cutlistgenerator.ui.dialogs import CustomerNameConverterDialog, CutJobEditorDialog


frontend_logger = logging.getLogger("frontend")
root_logger = logging.getLogger("root")

# db_name = "qes"
# host = "192.168.1.107"
# port = "3306"
# username = "gone"
# password = "fishing"


fishbowl_orm = fishbowlorm.FishbowlORM(
    db_name=FISHBOWL_DATABASE_SCHEMA,
    host=FISHBOWL_DATABASE_HOST,
    port=FISHBOWL_DATABASE_PORT,
    username=FISHBOWL_DATABASE_USER,
    password=FISHBOWL_DATABASE_PASSWORD,
)


COLUMNS = [
    "Due Date",
    "Customer",
    "SO Number",
    "Line Number",
    "Part Number",
    "Description",
    "Qty Left To Ship",
    "Fully Cut",
    "Parent Number",
    "Parent Description",
]


@dataclass
class SalesOrderSearchCriteria:
    """The search criteria for the sales order table."""

    number: str = ""
    customer_name: str = ""
    status: str = ""
    show_fully_cut: bool = False


class Worker(QRunnable):
    """
    Worker thread
    """

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):
        """
        Initialise the runner function with passed args, kwargs.
        """

        self.kwargs["progress_signal"] = self.signals.progress
        self.kwargs["progress_data_signal"] = self.signals.progress_data
        result = self.fn(*self.args, **self.kwargs)
        self.signals.result.emit(result)
        self.signals.finished.emit()


class WorkerSignals(QObject):
    progress = pyqtSignal(int)
    progress_data = pyqtSignal(object)
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(PROGRAM_NAME)
        self.resize(800, 600)
        self.setup_ui()
        self.connect_signals()

        root_logger.info("Starting {} version {}".format(PROGRAM_NAME, PROGRAM_VERSION))

        self.updating_table = False
        self.updating_fishbowl_data = False
        self.table_data = []  # type: list[SalesOrder]

        self.threadpool = QThreadPool()
        self.progressBar = QProgressBar()

        self.statusbar.addPermanentWidget(self.progressbar)

        self.reload_so_table()

    def setup_ui(self):
        """Setup the UI."""

        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(5, 5, 5, 5)

        self.main_widget = QtWidgets.QWidget()
        self.main_widget.setLayout(self.main_layout)

        self.setCentralWidget(self.main_widget)

        self.setup_menubar()

        self.progressbar = QProgressBar()
        self.progressbar.setMaximum(100)
        self.progressbar.setMinimum(0)
        self.progressbar.setAlignment(Qt.AlignCenter)
        self.progressbar.setGeometry(30, 40, 200, 25)
        self.progressbar.setValue(50)
        self.progressbar.hide()

        self.setup_statusbar()

        self.so_search_groupbox = QtWidgets.QGroupBox("SO Search")
        self.so_search_layout = QtWidgets.QVBoxLayout()
        self.so_search_groupbox.setLayout(self.so_search_layout)
        self.main_layout.addWidget(self.so_search_groupbox)

        self.so_search_number_lineedit = QtWidgets.QLineEdit()
        self.so_search_customer_name_lineedit = QtWidgets.QLineEdit()
        self.so_search_part_number_lineedit = QtWidgets.QLineEdit()
        self.include_fully_cut_checkbox = QtWidgets.QCheckBox("Include Fully Cut")
        self.so_search_button = QtWidgets.QPushButton("Search")

        search_form_layout = QtWidgets.QFormLayout()
        search_form_layout.addRow("Number", self.so_search_number_lineedit)
        search_form_layout.addRow("Customer", self.so_search_customer_name_lineedit)
        search_form_layout.addRow("Part Number", self.so_search_part_number_lineedit)

        self.so_search_layout.addLayout(search_form_layout)
        self.so_search_layout.addWidget(self.include_fully_cut_checkbox)
        self.so_search_layout.addWidget(self.so_search_button)

        self.so_table_widget = CustomQTableWidget()
        self.so_table_widget.set_table_headers(COLUMNS)

        self.view_selected_so_button = QtWidgets.QPushButton("View")
        self.view_selected_so_button.setEnabled(False)

        self.so_search_layout.addWidget(self.so_table_widget, stretch=1)
        self.so_search_layout.addWidget(self.view_selected_so_button)

    def setup_menubar(self):
        self.menubar = QtWidgets.QMenuBar(self)

        self.file_menu = QtWidgets.QMenu(self.menubar)
        self.file_menu.setTitle("File")

        self.open_customer_name_converter_action = QtWidgets.QAction(self)
        self.open_customer_name_converter_action.setText("Customer Name Converter")
        self.open_customer_name_converter_action.triggered.connect(
            self.open_customer_name_converter_dialog
        )
        self.file_menu.addAction(self.open_customer_name_converter_action)

        self.exit_action = QtWidgets.QAction(self)
        self.exit_action.setText("Exit")
        self.exit_action.triggered.connect(self.close)
        self.file_menu.addAction(self.exit_action)

        self.menubar.addAction(self.file_menu.menuAction())

        self.fishbowl_menu = QtWidgets.QMenu(self.menubar)
        self.fishbowl_menu.setTitle("Fishbowl")

        self.update_fishbowl_data_action = QtWidgets.QAction(self)
        self.update_fishbowl_data_action.setText("Update Fishbowl Data")
        self.update_fishbowl_data_action.triggered.connect(self.update_fishbowl_data)
        self.fishbowl_menu.addAction(self.update_fishbowl_data_action)

        self.menubar.addAction(self.fishbowl_menu.menuAction())

        self.wire_cutter_menu = QtWidgets.QMenu(self.menubar)
        self.wire_cutter_menu.setTitle("Wire Cutter")

        self.new_wire_cutter_action = QtWidgets.QAction(self)
        self.new_wire_cutter_action.setText("New Wire Cutter")
        # self.new_wire_cutter_action.triggered.connect(self.new_wire_cutter)
        self.wire_cutter_menu.addAction(self.new_wire_cutter_action)

        self.edit_wire_cutter_action = QtWidgets.QAction(self)
        self.edit_wire_cutter_action.setText("Edit Wire Cutter")
        # self.edit_wire_cutter_action.triggered.connect(self.edit_wire_cutter)
        self.wire_cutter_menu.addAction(self.edit_wire_cutter_action)

        self.menubar.addAction(self.wire_cutter_menu.menuAction())

        self.setMenuBar(self.menubar)

    def setup_statusbar(self):
        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)

        self.statusbar.addPermanentWidget(self.progressbar)

    def dissable(self):
        self.so_search_groupbox.setEnabled(False)
        self.view_selected_so_button.setEnabled(False)
        self.so_search_button.setEnabled(False)

    def enable(self):
        self.so_search_groupbox.setEnabled(True)
        self.so_search_button.setEnabled(True)

    def open_customer_name_converter_dialog(self):
        dialog = CustomerNameConverterDialog(self)
        dialog.exec()

    def on_so_table_row_double_clicked(self, row: QtWidgets.QTableWidgetItem):
        index = row.row()
        so_number = self.so_table_widget.item(index, 2).text()
        line_number = self.so_table_widget.item(index, 3).text()
        sales_order_item = SalesOrderItem.find_by_so_number_line_number(
            so_number=so_number, line_number=line_number
        )
        dialog = CutJobEditorDialog(sales_order_item=sales_order_item, parent=self)
        dialog.exec()
        self.reload_so_table()

    def on_so_table_selection_changed(self):
        self.view_selected_so_button.setEnabled(True)

    def connect_signals(self):
        self.so_search_number_lineedit.editingFinished.connect(
            lambda x=self.so_search_number_lineedit: utilities.clean_text_input(x)
        )
        self.so_search_customer_name_lineedit.editingFinished.connect(
            lambda x=self.so_search_customer_name_lineedit: utilities.clean_text_input(
                x
            )
        )
        self.so_search_part_number_lineedit.editingFinished.connect(
            lambda x=self.so_search_part_number_lineedit: utilities.clean_text_input(x)
        )

        self.so_search_button.clicked.connect(self.reload_so_table)
        self.so_table_widget.doubleClicked.connect(self.on_so_table_row_double_clicked)
        self.so_table_widget.selectionModel().selectionChanged.connect(
            self.on_so_table_selection_changed
        )
        # self.view_selected_so_button.clicked.connect(self.view_selected_so)

    def reset_progress_bar(self):
        self.progressbar.setValue(0)
        self.progressbar.setFormat("")
        self.progressbar.hide()

    def update_fishbowl_data(self):
        def set_updating_table(value: bool):
            self.updating_table = value

        if self.updating_table:
            frontend_logger.warning(
                "Attempted to update Fishbowl data, but an update thread is already running. Ignoring request."
            )
            return

        self.updating_table = True
        frontend_logger.info("Starting thread to update Fishbowl data.")

        fb_open_sales_orders = fishbowlorm.models.FBSalesOrder.find_all_open(
            fishbowl_orm
        )

        worker = Worker(
            fn=utilities.create_sales_orders_from_fishbowl_data,
            session=global_session,
            fishbowl_orm=fishbowl_orm,
            fb_open_sales_orders=fb_open_sales_orders,
        )

        worker.signals.finished.connect(self.reset_progress_bar)
        worker.signals.finished.connect(self.enable)
        worker.signals.finished.connect(
            lambda: frontend_logger.debug(
                "[TABLE RELOAD] Finished reloading data into table."
            )
        )
        worker.signals.result.connect(lambda: set_updating_table(False))
        worker.signals.result.connect(self.reload_so_table)
        worker.signals.progress.connect(self.progressbar.setValue)
        worker.signals.progress_data.connect(self.progressbar.setFormat)

        self.progressbar.show()
        self.progressbar.setValue(0)
        self.dissable()
        self.threadpool.start(worker)

    def reload_so_table(self, search_criteria: SalesOrderSearchCriteria = None):
        self.so_table_widget.setRowCount(0)
        self.table_data = SalesOrder.find_all_unfinished()

        # "Due Date",
        # "Customer",
        # "SO Number",
        # "Line Number",
        # "Part Number",
        # "Description",
        # "Qty Left To Ship",
        # "Fully Cut",
        # "Parent Number",
        # "Parent Description",

        data = []
        for so in self.table_data:
            for item in so.items:
                if item.quantity_left_to_fulfill == 0 or item.is_cut:
                    continue
                data.append(
                    [
                        item.date_scheduled_fulfillment.strftime(DATE_FORMAT),
                        so.customer.name_converted,
                        so.number,
                        item.line_number,
                        item.part.number,
                        item.description,
                        str(int(item.quantity_left_to_fulfill)),
                        item.fully_cut,
                        item.parent_item.part.number if item.parent_item else "",
                        item.parent_item.part.description if item.parent_item else "",
                    ]
                )

        for row in data:
            self.so_table_widget.insert_row_data(row)

        self.so_table_widget.resizeColumnsToContents()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
