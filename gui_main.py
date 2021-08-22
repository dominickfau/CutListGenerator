from cutlistgenerator.appdataclasses.salesorder import SalesOrderItem
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
from cutlistgenerator.ui.cutjobsearchdialog import CutJobSearchDialog


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
        self.headers = self._get_table_headers(self.ui.sales_order_table_widget)

        self.ui.statusbar.addPermanentWidget(self.progressBar)

        # This is simply to show the bar
        self.progressBar.setGeometry(30, 40, 200, 25)
        self.progressBar.setValue(50)
        self.progressBar.hide()

        # Menubar
        self.ui.action_fishbowl_Get_Sales_Order_Data.triggered.connect(self.thread_get_current_fb_data)
        self.ui.action_cut_job_Create_Blank.triggered.connect(lambda: self.create_cut_job())
        self.ui.action_cut_job_Show_All_Open.triggered.connect(lambda: self.show_cut_job_search_dialog(cut_list_generator_database=self.cut_list_generator_database,parent=self))

        # Push buttons
        self.ui.so_search_push_button.clicked.connect(self.load_so_table_data)
        self.ui.so_view_push_button.clicked.connect(self.on_view_button_clicked)
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

        auto_update_fishbowl_so_data = SystemProperty.find_by_name(self.cut_list_generator_database, "fishbowl_auto_update_sales_orders").value
        if auto_update_fishbowl_so_data:
            logger.info("[AUTO UPDATE] Auto updating sales order data from Fishbowl.")
            self.thread_get_current_fb_data()
        
        self.load_so_table_data()
    
    def _get_table_headers(self, table_widget) -> dict:
        # TODO: Move this to a utility function.
        """Returns a dict of the headers for the given table widget."""
        headers = {}
        for index in range(table_widget.columnCount()):
            header = table_widget.horizontalHeaderItem(index)
            if header is not None:
                width = len(header.text()) * 10
                headers[header.text()] = {'index': index, 'width': width}
        return headers

    def get_so_search_data(self):
        include_finished = self.ui.so_search_include_finished_check_box.isChecked()
        product_number = self.ui.so_search_product_number_line_edit.text().strip()
        so_number = self.ui.so_search_so_number_line_edit.text().strip()

        if include_finished:
            include_finished = "%"
        else:
            include_finished = 0
        
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
    
    def on_view_button_clicked(self):
        row_num = self.ui.sales_order_table_widget.currentRow()
        if row_num == -1:
            msg = QMessageBox()
            msg.setWindowTitle("Sales Order")
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Please select a row to view.")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()
            return

        data = self.get_row_data_from_so_table(row_num)
        sales_order_item = SalesOrderItem.from_id(self.cut_list_generator_database, data['so_item_id'])
        product = Product.from_number(self.cut_list_generator_database, data['product_number'])
        cut_jobs = CutJob.from_sales_order_item_id(self.cut_list_generator_database, sales_order_item.id)
        if len(cut_jobs) == 0:
            self.load_cut_job_data()
        else:
            self.show_cut_job_search_dialog(cut_list_generator_database=self.cut_list_generator_database, product=product, sales_order_item=sales_order_item, parent=self)

    def on_so_table_row_double_clicked(self, row):
        row_num = row.row()
        data = self.get_row_data_from_so_table(row_num)
        sales_order_item = SalesOrderItem.from_id(self.cut_list_generator_database, data['so_item_id'])
        product = Product.from_number(self.cut_list_generator_database, data['product_number'])
        cut_jobs = CutJob.from_sales_order_item_id(self.cut_list_generator_database, sales_order_item.id)
        if len(cut_jobs) == 0:
            self.load_cut_job_data()
        else:
            self.show_cut_job_search_dialog(cut_list_generator_database=self.cut_list_generator_database, product=product, sales_order_item=sales_order_item)
        
    def show_cut_job_search_dialog(self, **kwargs):
        dialog = CutJobSearchDialog(**kwargs)
        # dialog.rejected.connect(lambda: self.load_cut_job_data())
        dialog.accepted.connect(lambda: self.load_cut_job(dialog.cut_job))
        dialog.exec()

    def get_row_data_from_so_table(self, row_num: int) -> dict:
        so_item_id = int(self.ui.sales_order_table_widget.item(row_num, self.headers['Id']['index']).text())
        so_number = self.ui.sales_order_table_widget.item(row_num, self.headers['SO Number']['index']).text()
        product_number = self.ui.sales_order_table_widget.item(row_num, self.headers['Product Number']['index']).text()
        return {
            'so_item_id': so_item_id,
            'so_number': so_number,
            'product_number': product_number
        }
    
    def load_cut_job_data(self, cut_job: CutJob = None):
        row_num = self.ui.sales_order_table_widget.currentRow()
        if row_num == -1:
            self.create_cut_job()
            return

        row_data = self.get_row_data_from_so_table(row_num)
        product = Product.from_number(self.cut_list_generator_database, row_data['product_number'])
        so_item_id = row_data['so_item_id']
        # TODO: Change this it use the cut job id instead of the so item id.
        # logger.debug(f"[CUT JOB] Loading cut job data for sales order item ID: {so_item_id}'")
        if not cut_job:
            # logger.info(f"[CUT JOB] No cut job data found for sales order item ID: {so_item_id}")
            msg = QMessageBox()
            msg.setWindowTitle("Cut Job")
            msg.setIcon(QMessageBox.Information)
            msg.setText("Would you like to create a cut job for the selected item?")
            msg.setInformativeText("Click No to create a blank cut job.")
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg.exec()
            if msg.result() == QMessageBox.Yes:
                self.create_cut_job(product, so_item_id)
            else:
                self.create_cut_job()
            return
        self.load_cut_job(cut_job)
        
    def load_cut_job(self, cut_job: CutJob):
        logger.info(f"[CUT JOB] Loading cut job ID: {cut_job.id}")
        # Open a dialog to get the cut job data.
        dialog = CutJobDialog(cut_list_generator_database=self.cut_list_generator_database,
                              fishbowl_database=self.fishbowl_database,
                              cut_job=cut_job,
                              parent=self)
        if dialog.exec():
            dialog.cut_job.save()
            logger.info(f"[CUT JOB] Cut job data saved. Job ID: {dialog.cut_job.id}")
            if dialog.cut_job.is_cut and dialog.cut_job.related_sales_order_item:
                logger.info(f"[CUT JOB] Checking if sales order item ID {dialog.cut_job.related_sales_order_item.id} is fully cut.")
                sales_order_item = dialog.cut_job.related_sales_order_item
                if sales_order_item.cut_in_full:
                    logger.info(f"Sales order item ID {sales_order_item.id} is fully cut.")
                    sales_order_item.save()
                else:
                    logger.info(f"Sales order item ID {sales_order_item.id} is not fully cut.")
        self.load_so_table_data()

        
    def create_cut_job(self, product: Product = None, linked_so_item_id: int = None):
        logger.info("[CUT JOB] Creating cut job.")
        # Open a dialog to get the cut job data.
        dialog = CutJobDialog(cut_list_generator_database=self.cut_list_generator_database,
                              fishbowl_database=self.fishbowl_database,
                              product=product,
                              linked_so_item_id=linked_so_item_id,
                              parent=self)
        if dialog.exec():
            dialog.cut_job.save()
            logger.info(f"[CUT JOB] Cut job data saved. Job ID: {dialog.cut_job.id}")
        self.load_so_table_data()

    def clear_table(self, tableWidget):
        # TODO: Move this to a utility function.
        logger.debug("[TABLE] Clearing table.")
        tableWidget.setRowCount(0)
    
    def get_max_width_for_column(self, data: dict, column_key: str) -> int:
        """Returns the maximum width for a given column."""
        # TODO: Move this to a utility function.
        max_width = 0
        for row in data:
            value = str(row[column_key])
            if len(value) > max_width:
                max_width = len(value)
        return max_width

    def load_so_table_data(self):
        # TODO: Move this to a thread.
        logger.debug("[LOAD TABLE] Loading SO data into table.")
        search_data = self.get_so_search_data()
        self.clear_table(self.ui.sales_order_table_widget)

        # TODO: Remove this when we have a better way of getting the data.
        # FIXME: Check if items that are not fully cut are being loaded.
        # TODO: Check that Include Finished checkbox is working.
        table_data = self.cut_list_generator_database.get_sales_order_table_data(search_data)
        self.ui.sales_order_table_widget.setRowCount(len(table_data))
        logger.debug(f"[SEARCH] Found {len(table_data)} rows of data.")

        for row_index, row in enumerate(table_data):
            is_child_item = row.pop('is_child_item')
            sales_order_item = SalesOrderItem.from_id(self.cut_list_generator_database, row['Id'])
            qty_left_to_cut = int(sales_order_item.qty_left_to_cut)
            qty_scheduled_to_cut = int(sales_order_item.qty_scheduled_to_cut)

            column_index = self.headers['Qty Left To Cut']['index']
            width = self.headers['Qty Left To Cut']['width']
            self.ui.sales_order_table_widget.setItem(row_index, column_index, QtWidgets.QTableWidgetItem(str(qty_left_to_cut)))
            self.ui.sales_order_table_widget.setColumnWidth(column_index, width)

            column_index = self.headers['Qty Scheduled To Cut']['index']
            width = self.headers['Qty Scheduled To Cut']['width']
            self.ui.sales_order_table_widget.setItem(row_index, column_index, QtWidgets.QTableWidgetItem(str(qty_scheduled_to_cut)))
            self.ui.sales_order_table_widget.setColumnWidth(column_index, width)

            for key in row:
                # Id, Due Date, Customer Name, SO Number, Product Number, Description, Qty Left To Ship, Line Number, Fully Cut, Parent Number, Parent Description
                value = row[key]
                if value == None:
                    value = ''
                if key == 'Qty Left To Ship':
                    value = int(value)
                elif key == 'Fully Cut':
                    if value == True:
                        value = "Yes"
                    else:
                        value = "No"

                column_index = self.headers[key]['index']
                # width = self.get_max_width_for_column(table_data, key) * 2
                width = self.headers[key]['width']
                self.ui.sales_order_table_widget.setItem(row_index, column_index, QtWidgets.QTableWidgetItem(str(value)))
                self.ui.sales_order_table_widget.setColumnWidth(column_index, width)


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