from cutlistgenerator.appdataclasses import product
from cutlistgenerator.appdataclasses.systemproperty import SystemProperty
import sys, os, traceback, datetime
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMessageBox, QProgressBar
from PyQt5.QtCore import QRunnable, QThreadPool, pyqtSlot, pyqtSignal, QObject


import cutlistgenerator

# Ui Windows
from cutlistgenerator.ui.mainwindow_ui import Ui_MainWindow
from cutlistgenerator.ui.cutjobdialog import CutJobDialog


from cutlistgenerator.ui.customwidgets.resizablemessagebox import ResizableMessageBox
from cutlistgenerator.settings import Settings
from cutlistgenerator.database.mysqldatabase import MySQLDatabaseConnection
from cutlistgenerator.database.fishbowldatabase import FishbowlDatabaseConnection
from cutlistgenerator import utilities
from cutlistgenerator.logging import FileLogger
from cutlistgenerator.appdataclasses.cutjob import CutJob
from cutlistgenerator.appdataclasses.product import Product


DEFAULT_SETTINGS_FILE_NAME = "settings.json"
PROGRAM_NAME = "Cut List Generator"
__version__ = "0.1.0"

# Create settings file if it doesn't exist
if not Settings.validate_file_path(DEFAULT_SETTINGS_FILE_NAME):
    utilities.touch(DEFAULT_SETTINGS_FILE_NAME)
    cutlistgenerator.program_settings.set_file_path(DEFAULT_SETTINGS_FILE_NAME)
    cutlistgenerator.program_settings.save()
else:
    cutlistgenerator.program_settings.set_file_path(DEFAULT_SETTINGS_FILE_NAME)
    cutlistgenerator.program_settings.load()

logger = FileLogger(__name__)

class Worker(QRunnable):
    '''
    Worker thread
    '''

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):
        '''
        Initialise the runner function with passed args, kwargs.
        '''

        self.kwargs['progress_signal'] = self.signals.progress
        result = self.fn(*self.args, **self.kwargs)
        self.signals.result.emit(result)
        self.signals.finished.emit()

class WorkerSignals(QObject):
    progress = pyqtSignal(int)
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)


class Application(QtWidgets.QMainWindow):
    def __init__(self):
        super(Application, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.setWindowTitle(f"{PROGRAM_NAME} v{__version__}")

        self.threadpool = QThreadPool()
        self.progressBar = QProgressBar()

        self.ui.statusbar.addPermanentWidget(self.progressBar)

        # This is simply to show the bar
        self.progressBar.setGeometry(30, 40, 200, 25)
        self.progressBar.setValue(50)
        self.progressBar.hide()

        self.ui.so_search_push_button.clicked.connect(self.load_so_table_data)
        self.ui.sales_order_table_widget.doubleClicked.connect(self.on_so_table_row_double_clicked)

        # This auto strips the text when the widget looses focus.
        self.ui.so_search_product_number_line_edit.editingFinished.connect(lambda: self.ui.so_search_product_number_line_edit.setText(self.ui.so_search_product_number_line_edit.text().strip()))
        self.ui.so_search_so_number_line_edit.editingFinished.connect(lambda: self.ui.so_search_so_number_line_edit.setText(self.ui.so_search_so_number_line_edit.text().strip()))

        self.fishbowl_database = FishbowlDatabaseConnection(connection_args=cutlistgenerator.program_settings.get_fishbowl_settings()['auth'])
        self.cut_list_generator_database = MySQLDatabaseConnection(connection_args=cutlistgenerator.program_settings.get_cutlist_settings()['auth'])

        if not cutlistgenerator.program_settings.is_database_setup():
            logger.info("[DATABASE] Setting up database.")
            # TODO: Add a dialog to infrom the user that they need to setup the database.
            # TODO: Create a function to setup the database.
            utilities.create_database(self.cut_list_generator_database)
            cutlistgenerator.program_settings.set_database_setup(True)
            logger.info("[DATABASE] Database setup complete.")

        self.ui.actionGet_Sales_Order_Data.triggered.connect(self.thread_get_current_fb_data)
        auto_update_fishbowl_so_data = SystemProperty.find_by_name(self.cut_list_generator_database, "fishbowl_auto_update_sales_orders").value
        if auto_update_fishbowl_so_data:
            logger.info("[AUTO UPDATE] Auto updating sales order data from Fishbowl.")
            self.thread_get_current_fb_data()
        
        self.load_so_table_data()

    def get_so_search_data(self):
        include_finished = self.ui.so_search_include_finished_check_box.isChecked()
        product_number = self.ui.so_search_product_number_line_edit.text().strip()
        so_number = self.ui.so_search_so_number_line_edit.text().strip()

        if include_finished:
            include_finished = "%"
        
        if len(product_number) == 0:
            product_number = "%"
        else:
            product_number = f"%{product_number}%"

        if len(so_number) == 0:
            so_number = "%"
        else:
            so_number = f"%{so_number}%"
        
        logger.debug(f"[SEARCH] Current search parameters. Product Number: '{product_number}' SO Number: '{so_number}'' Show Finished: '{include_finished}'")

        return {'product_number': product_number, 'cut_in_full': include_finished, 'so_number': so_number}
    
    def on_so_table_row_double_clicked(self, row):
        row_num = row.row()
        so_item_id = int(self.ui.sales_order_table_widget.item(row_num, 0).text())
        product_number = self.ui.sales_order_table_widget.item(row_num, 4).text()
        product = Product.from_number(self.cut_list_generator_database, product_number)
        self.load_cut_job_data(so_item_id, product)
    
    def load_cut_job_data(self, so_item_id, product: Product):
        logger.debug(f"[CUT JOB] Loading cut job data for sales order item ID: {so_item_id}'")
        data = self.cut_list_generator_database.get_cut_job_by_so_item_id(so_item_id)
        if not data:
            logger.info(f"[CUT JOB] No cut job data found for sales order item ID: {so_item_id}")
            msg = QMessageBox()
            msg.setWindowTitle("Cut Job")
            msg.setIcon(QMessageBox.Information)
            msg.setText("The selected sales order item does not have a cut job associated with it. Would you like to create one?")
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg.exec()
            if msg.result() == QMessageBox.Yes:
                self.create_cut_job(product)
            return
    
    def create_cut_job(self, product: Product):
        logger.info(f"[CUT JOB] Creating cut job for product: {product.number}")
        # Open a dialog to get the cut job data.
        dialog = CutJobDialog(cut_list_generator_database=self.cut_list_generator_database,
                              fishbowl_database=self.fishbowl_database,
                              product=product,
                              parent=self)
        if dialog.exec():
            print(dialog.cut_job)

    def clear_table(self, tableWidget):
        logger.debug("[TABLE] Clearing table.")
        tableWidget.setRowCount(0)

    def load_so_table_data(self):
        logger.debug("[SEARCH] Loading SO data into table.")
        search_data = self.get_so_search_data()
        self.clear_table(self.ui.sales_order_table_widget)

        table_data = self.cut_list_generator_database.get_sales_order_table_data(search_data)
        self.ui.sales_order_table_widget.setRowCount(len(table_data))
        logger.debug(f"[SEARCH] Found {len(table_data)} rows of data.")

        for row_index, row in enumerate(table_data):
            for column_index, key in enumerate(row):
                self.ui.sales_order_table_widget.setItem(row_index, column_index, QtWidgets.QTableWidgetItem(str(row[key])))
                if key == "due_date":
                    self.ui.sales_order_table_widget.setColumnWidth(column_index, 100)
                elif key == "customer_name":
                    self.ui.sales_order_table_widget.setColumnWidth(column_index, 200)
                elif key == "product_description":
                    self.ui.sales_order_table_widget.setColumnWidth(column_index, 250)

    def update_progess_bar(self, value):
        self.progressBar.setValue(value)

    def reset_progress_bar(self):
        self.progressBar.setValue(0)
        self.progressBar.hide()

    def thread_get_current_fb_data(self):
        logger.info("[TREAD] Starting thread to get current sales order data from Fishbowl.")
        self.ui.actionGet_Sales_Order_Data.setEnabled(False)
        worker = Worker(fn=self.get_current_fb_data, fishbowl_database=self.fishbowl_database, cut_list_database=self.cut_list_generator_database)
        worker.signals.finished.connect(lambda: self.ui.actionGet_Sales_Order_Data.setEnabled(True))
        worker.signals.result.connect(self.show_fishbowl_update_finished_message_box)
        worker.signals.finished.connect(self.reset_progress_bar)
        worker.signals.progress.connect(self.update_progess_bar)
        self.progressBar.show()
        self.progressBar.setValue(0)
        self.threadpool.start(worker)
    
    @staticmethod
    def get_current_fb_data(fishbowl_database, cut_list_database, progress_signal):
        # TODO: Rework this to enable pySignals to be used.
        start_time = datetime.datetime.now()
        total_rows, rows_inserted = utilities.update_sales_order_data_from_fishbowl(fishbowl_database, cut_list_database, progress_signal)
        end_time = datetime.datetime.now()
        time_delta = end_time - start_time
        logger.info(f"[EXECUTION TIME]: {time_delta.total_seconds() *1000} ms")
        return total_rows, rows_inserted

    def show_fishbowl_update_finished_message_box(self, result):
        msg = QMessageBox()
        msg.setWindowTitle("Fishbowl")
        msg.setIcon(QMessageBox.Information)
        msg.setText(f"Fishbowl data update complete.")
        msg.setInformativeText(f"Total rows available: {result[0]}\nRows inserted: {result[1]}")

        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec()


def main():
    logger.info("[START] Starting application.")
    logger.info(f"Program Version: {__version__}")
    try:
        app = QApplication(sys.argv)
        main_window = Application()
        main_window.show()
        app.exec_()

        main_window.fishbowl_database.disconnect()
        main_window.cut_list_generator_database.disconnect()
    except Exception as e:
        logger.critical("Fatale exception occurred.", exc_info=True)
        logger.critical("End of exception.")

        msg = ResizableMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText("Fatale exception occurred.")
        msg.setInformativeText(f"Exception: {e}")
        msg.setDetailedText(traceback.format_exc())
        msg.setWindowTitle("Fatale Exception")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec()

    logger.info("[END] Closing application.")
    exit()


if __name__ == "__main__":
    main()