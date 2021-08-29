from cutlistgenerator.database.cutlistdatabase import CutListDatabase
from cutlistgenerator.appdataclasses.salesorder import SalesOrder, SalesOrderItem
from cutlistgenerator.appdataclasses import product
from cutlistgenerator.appdataclasses.systemproperty import SystemProperty
import sys, os, traceback, datetime, inspect
from typing import List
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMessageBox, QProgressBar, QPushButton
from PyQt5.QtCore import QRunnable, QThreadPool, pyqtSlot, pyqtSignal, QObject, Qt


import cutlistgenerator

# Ui Windows
from cutlistgenerator.ui.mainwindow_ui import Ui_MainWindow
from cutlistgenerator.ui.cutjobdialog import CutJobDialog
from cutlistgenerator.ui.cutjobsearchdialog import CutJobSearchDialog
from cutlistgenerator.ui.wirecutterdialog import WireCutterDialog
from cutlistgenerator.ui.wirecuttersearchdialog import WireCutterSearchDialog


from cutlistgenerator.ui.customwidgets.resizablemessagebox import ResizableMessageBox

from cutlistgenerator.database.mysqldatabase import MySQLDatabaseConnection
from cutlistgenerator.database.fishbowldatabase import FishbowlDatabaseConnection
from cutlistgenerator import utilities
from cutlistgenerator.logging import FileLogger
from cutlistgenerator.appdataclasses.cutjob import CutJob
from cutlistgenerator.appdataclasses.product import Product




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
        self.kwargs['progress_data_signal'] = self.signals.progress_data
        result = self.fn(*self.args, **self.kwargs)
        self.signals.result.emit(result)
        self.signals.finished.emit()

class WorkerSignals(QObject):
    progress = pyqtSignal(int)
    progress_data = pyqtSignal(object)
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)


class MainWindow(Ui_MainWindow, QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(Ui_MainWindow, self).__init__(parent)
        self.setupUi(self)

        self.updating_table = False
        self.updating_fishbowl_data = False

        self.threadpool = QThreadPool()
        self.progressBar = QProgressBar()
        self.progressBar.setAlignment(Qt.AlignCenter)
        self.headers = utilities.get_table_headers(self.sales_order_table_widget)

        self.statusbar.addPermanentWidget(self.progressBar)

        # This is simply to show the bar
        self.progressBar.setGeometry(30, 40, 200, 25)
        self.progressBar.setValue(50)
        self.progressBar.hide()

        # Menubar

        # File
        # TODO: Add file menu functions.
        # self.actionSettings.triggered.connect(self.show_settings_dialog)
        # self.actionSystem_Properties.triggered.connect(self.show_system_properties_dialog)
        # self.actionHelp.triggered.connect(self.show_help_dialog)
        # self.actionAbout.triggered.connect(self.show_about_dialog)

        # Edit
        self.actionAdd_To_Exclude_List.triggered.connect(self.add_to_exclude_list)

        # Fishbowl
        self.action_fishbowl_Get_Sales_Order_Data.triggered.connect(self.thread_get_current_fb_data)

        # Cut Job
        self.action_cut_job_Create_Blank.triggered.connect(lambda: self.create_cut_job())
        self.action_cut_job_Show_All_Open.triggered.connect(lambda: self.show_cut_job_search_dialog(cut_list_generator_database=self.cut_list_generator_database,parent=self))

        # Reports - Export
        # TODO: Add export report functionality
        # self.actionExport_Cut_Job_Summary.triggered.connect(self.export_cut_job_summary)
        # self.actionExport_Cut_Jobs_List.triggered.connect(self.export_cut_jobs_list)
        # self.actionExport_Termination_Job_List.triggered.connect(self.export_termination_jobs_list)
        # self.actionExport_Splice_Jobs_List.triggered.connect(self.export_splice_jobs_list)
        # self.actionExport_Product_List.triggered.connect(self.export_product_list)
        # self.actionExport_Wire_Cutter_List.triggered.connect(self.export_wire_cutter_list)
        # self.actionExport_Wire_Cutter_Options_List.triggered.connect(self.export_wire_cutter_options_list)

        # General Context Menu
        self.addAction(self.action_fishbowl_Get_Sales_Order_Data)
        self.addAction(self.action_cut_job_Show_All_Open)
        self.addAction(self.action_cut_job_Create_Blank)


        # Table Context Menu Items
        # TODO: Rework last 2 items.
        self.sales_order_table_widget.addAction(self.actionAdd_To_Exclude_List)
        self.sales_order_table_widget.addAction(self.action_cut_job_Create_Blank)
        self.sales_order_table_widget.addAction(self.action_cut_job_Show_All_Open)

        # Wire Cutter
        self.actionWire_Cutter_New.triggered.connect(lambda: self.show_wire_cutter_dialog(cut_list_generator_database=self.cut_list_generator_database,
                                                                                             parent=self))
        self.actionWire_Cutter_Edit.triggered.connect(lambda: self.show_wire_cutter_dialog(cut_list_generator_database=self.cut_list_generator_database,
                                                                                                parent=self,
                                                                                                wire_cutter=self.show_wire_cutter_search_dialog(cut_list_generator_database=self.cut_list_generator_database,
                                                                                                     parent=self)))

        # Push buttons
        self.so_search_push_button.clicked.connect(self.thread_get_so_table_data)
        self.so_view_push_button.clicked.connect(self.on_view_button_clicked)
        self.sales_order_table_widget.doubleClicked.connect(self.on_so_table_row_double_clicked)

        # This auto strips the text when the widget looses focus.
        self.so_search_product_number_line_edit.editingFinished.connect(lambda: self.so_search_product_number_line_edit.setText(self.so_search_product_number_line_edit.text().strip()))
        self.so_search_so_number_line_edit.editingFinished.connect(lambda: self.so_search_so_number_line_edit.setText(self.so_search_so_number_line_edit.text().strip()))

        self.fishbowl_database = FishbowlDatabaseConnection(connection_args=cutlistgenerator.program_settings.get_fishbowl_settings()['auth'])
        self.cut_list_generator_database = MySQLDatabaseConnection(connection_args=cutlistgenerator.program_settings.get_cutlist_settings()['auth'])

        # This is to make sure all system properties exist.
        utilities.create_default_system_properties(self.cut_list_generator_database)

        if not cutlistgenerator.program_settings.is_database_setup():
            logger.info("[DATABASE] Setting up database.")
            # TODO: Add a dialog to infrom the user that they need to setup the database.
            # TODO: Create a function to setup the database.
            utilities.create_database(self.cut_list_generator_database)
            cutlistgenerator.program_settings.set_database_setup(True)
            logger.info("[DATABASE] Database setup complete.")

        # BUG: There is an issue with this where the thread is loosing the connection to the database.
        # auto_update_fishbowl_so_data = SystemProperty.find_by_name(self.cut_list_generator_database, "fishbowl_auto_update_sales_orders").value
        # if auto_update_fishbowl_so_data:
        #     logger.info("[AUTO UPDATE] Auto updating sales order data from Fishbowl.")
        #     self.thread_get_current_fb_data()
        
        self.date_formate = SystemProperty.find_by_name(database_connection=self.cut_list_generator_database, name="date_formate").value

    def add_to_exclude_list(self):
        """Finds the selected row in the sales order table and adds it to the exclude list."""
        selected_row = self.sales_order_table_widget.currentRow()
        if selected_row != -1:
            product_number = self.sales_order_table_widget.item(selected_row, self.headers['Product Number']['index']).text()
            product = Product.from_number(self.cut_list_generator_database, product_number)
            if not product:
                lines = "\n".join([str(line) for line in inspect.stack()])
                logger.error(f"[EXCLUDE LIST] Product not found: {product_number}")
                msg = ResizableMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setWindowTitle("Error")
                msg.setText(f"Product not found: {product_number}")
                msg.setDetailedText(f"The product number {product_number} could not be found in the database.\n\nStack:\n{lines}")
                msg.exec()
                return

            msg = QMessageBox()
            msg.setIcon(QMessageBox.Question)
            msg.setWindowTitle("Add to Exclude List")
            msg.setText(f"Are you sure you want to add {product_number} to the exclude list?")
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg.setDefaultButton(QMessageBox.Yes)
            ret = msg.exec()
            if ret == QMessageBox.No:
                return
            
            logger.info(f"Adding {product_number} to exclude list.")
            self.cut_list_generator_database.save_product_number_to_exclude(product_number)
            
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Question)
            msg.setWindowTitle("Update Sales Orders")
            msg.setText(f"{product_number} has been added to the exclude list.")
            msg.setInformativeText("Do you want to remove this product from all sales orders?")
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg.setDefaultButton(QMessageBox.Yes)
            ret = msg.exec()
            if ret == QMessageBox.No:
                return
            
            # Double check that the user is sure.
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Remove Sales Order Items")
            msg.setText(f"Are you sure you want to remove all sales order items for {product_number}?")
            msg.setInformativeText("This action cannot be undone! This action will remove all sales order items for this product from all sales orders.")
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg.setDefaultButton(QMessageBox.No)
            ret = msg.exec()
            if ret == QMessageBox.No:
                return
            
            # Remove all items from all sales orders.
            logger.warning(f"Removing all sales order items for {product_number}.")
            SalesOrder.remove_all_sales_order_items_for_product(database_connection=self.cut_list_generator_database, product=product)
            self.thread_get_so_table_data()

    def get_so_search_data(self):
        include_finished = self.so_search_include_finished_check_box.isChecked()
        product_number = self.so_search_product_number_line_edit.text().strip()
        so_number = self.so_search_so_number_line_edit.text().strip()

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

        return {'product_number': product_number, 'cut_in_full': include_finished, 'so_number': so_number}
    
    def ask_user_direction_for_selected_row(self, sales_order_item: SalesOrderItem):
        """Asks the user if they want to create a cut job for the selected sales order. Returns what the user wants to do."""
        sales_order_number = SalesOrder.get_number_from_sales_order_item_id(self.cut_list_generator_database, sales_order_item.id)
        cut_jobs = CutJob.from_sales_order_item_id(self.cut_list_generator_database, sales_order_item.id)

        msg = QMessageBox()
        msg.setIcon(QMessageBox.Question)
        msg.setInformativeText("What would you like to do?")
        if len(cut_jobs) == 0:
            msg.setText(f"The selected sales order ({sales_order_number}) has no cut jobs.")
            msg.setWindowTitle("Cut Job Creation")
            msg.addButton(QPushButton('Create New'), QMessageBox.YesRole)
            msg.addButton(QPushButton('Cancel'), QMessageBox.RejectRole)
        else:
            msg.setText(f"The selected sales order ({sales_order_number}) has cut jobs.")
            msg.setWindowTitle("Cut Job Selection")
            msg.addButton(QPushButton('Select Existing'), QMessageBox.NoRole)
            msg.addButton(QPushButton('Create New'), QMessageBox.YesRole)
            msg.addButton(QPushButton('Cancel'), QMessageBox.RejectRole)

        msg.exec()
        return msg.buttonRole(msg.clickedButton())

    def on_view_button_clicked(self):
        """Called when the view button is clicked."""
        row_num = self.sales_order_table_widget.currentRow()
        if row_num == -1:
            msg = QMessageBox()
            msg.setWindowTitle("Sales Order")
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Please select a row to view.")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()
            return

        row_data = self.get_row_data_from_so_table(row_num)
        self.check_selected_row_for_cut_jobs(row_data)

    def on_so_table_row_double_clicked(self, row):
        """Callback for when a row is double clicked in the sales order table."""
        row_num = row.row()
        row_data = self.get_row_data_from_so_table(row_num)
        self.check_selected_row_for_cut_jobs(row_data)
    
    def check_selected_row_for_cut_jobs(self, selected_row_data):
        """Checks if the selected row has a cut job already created. Then asks the user what they want to do. Ether create a new cut job or select an existing cut job."""
        sales_order_item = SalesOrderItem.from_id(self.cut_list_generator_database, selected_row_data['so_item_id'])
        reply = self.ask_user_direction_for_selected_row(sales_order_item)
        if reply == QMessageBox.NoRole:
            self.show_cut_job_search_dialog(cut_list_generator_database=self.cut_list_generator_database,
                                            product=sales_order_item.product,
                                            sales_order_item=sales_order_item,
                                            parent=self)
        elif reply == QMessageBox.YesRole:
            self.create_cut_job(product=sales_order_item.product, linked_so_item=sales_order_item)
        else:
            return
        
    def show_cut_job_search_dialog(self, **kwargs):
        """Shows the cut job search dialog. Passes the keyword arguments to the dialog."""
        dialog = CutJobSearchDialog(**kwargs)
        dialog.accepted.connect(lambda: self.load_cut_job(dialog.cut_job))
        dialog.showMaximized()
    
    def show_wire_cutter_dialog(self, **kwargs):
        """Shows the wire cutter dialog. Passes the keyword arguments to the dialog."""
        dialog = WireCutterDialog(**kwargs)
        dialog.exec()
        if dialog.wire_cutter:
            dialog.wire_cutter.save()
    
    def show_wire_cutter_search_dialog(self, **kwargs):
        """Shows the wire cutter search dialog. Passes the keyword arguments to the dialog. Returns the selected wire cutter."""
        dialog = WireCutterSearchDialog(**kwargs)
        dialog.exec()
        return dialog.wire_cutter

    def get_row_data_from_so_table(self, row_num: int) -> dict:
        so_item_id = int(self.sales_order_table_widget.item(row_num, self.headers['Id']['index']).text())
        so_number = self.sales_order_table_widget.item(row_num, self.headers['SO Number']['index']).text()
        product_number = self.sales_order_table_widget.item(row_num, self.headers['Product Number']['index']).text()
        return {
            'so_item_id': so_item_id,
            'so_number': so_number,
            'product_number': product_number
        }
        
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
        self.thread_get_so_table_data()

        
    def create_cut_job(self, product: Product = None, linked_so_item: SalesOrderItem = None):
        logger.info("[CUT JOB] Creating cut job.")
        # Open a dialog to get the cut job data.
        dialog = CutJobDialog(cut_list_generator_database=self.cut_list_generator_database,
                              fishbowl_database=self.fishbowl_database,
                              product=product,
                              linked_so_item=linked_so_item,
                              parent=self)
        if dialog.exec():
            dialog.cut_job.save()
            logger.info(f"[CUT JOB] Cut job data saved. Job ID: {dialog.cut_job.id}")
        self.thread_get_so_table_data()

    def clear_table(self, tableWidget):
        # TODO: Move this to a utility function.
        logger.debug("[TABLE] Clearing table.")
        tableWidget.setRowCount(0)

    def get_so_table_data(self, progress_signal=None, progress_data_signal=None) -> List[dict]:
        # FIXME: Check if items that are not fully cut are being loaded.
        # TODO: Check that Include Finished checkbox is working.
        cut_list_generator_database = MySQLDatabaseConnection(connection_args=cutlistgenerator.program_settings.get_cutlist_settings()['auth'])
        table_data = []
        search_data = self.get_so_search_data()
        _table_data = cut_list_generator_database.get_sales_order_table_data(search_data)
        logger.debug(f"[SEARCH] Found {len(_table_data)} rows of data.")

        self.headers = utilities.get_max_column_widths(_table_data, self.headers)

        if progress_data_signal:
            progress_data_signal.emit("Retreiving SO data...")

        for row_index, row in enumerate(_table_data, 1):
            if progress_signal:
                progress_signal.emit(int(row_index / len(_table_data) * 100))

            is_child_item = row.pop('is_child_item')
            sales_order_item = SalesOrderItem.from_id(cut_list_generator_database, row['Id'])

            data = {
                'is_child_item': is_child_item,
                'sales_order_item': sales_order_item,
                'row': row
            }
            table_data.append(data)
        cut_list_generator_database.disconnect()
        return table_data
    
    def load_so_table_data(self, table_data: list):
        # FIXME: Check if items that are not fully cut are being loaded.
        # TODO: Check that Include Finished checkbox is working.

        total_rows = len(table_data)
        self.set_progress_bar_text("Loading SO data...")
        logger.debug(f"[LOAD TABLE] Loading {total_rows} rows of data.")
        self.clear_table(self.sales_order_table_widget)
        self.sales_order_table_widget.setRowCount(len(table_data))

        self.headers = utilities.get_max_column_widths(table_data, self.headers)

        for row_index, row in enumerate(table_data):
            self.update_progess_bar_value(int(row_index / total_rows * 100))

            sales_order_item = row.pop('sales_order_item')
            table_row = row.pop('row')

            qty_left_to_cut = int(sales_order_item.qty_left_to_cut)
            qty_scheduled_to_cut = int(sales_order_item.qty_scheduled_to_cut)

            column_index = self.headers['Qty Left To Cut']['index']
            width = self.headers['Qty Left To Cut']['width']
            self.sales_order_table_widget.setItem(row_index, column_index, QtWidgets.QTableWidgetItem(str(qty_left_to_cut)))
            self.sales_order_table_widget.setColumnWidth(column_index, width)

            column_index = self.headers['Qty Scheduled To Cut']['index']
            width = self.headers['Qty Scheduled To Cut']['width']
            self.sales_order_table_widget.setItem(row_index, column_index, QtWidgets.QTableWidgetItem(str(qty_scheduled_to_cut)))
            self.sales_order_table_widget.setColumnWidth(column_index, width)

            for key in table_row:
                value = table_row[key]
                if value == None:
                    value = ''
                if key == 'Qty Left To Ship':
                    value = int(value)
                elif key == 'Fully Cut':
                    if value == True:
                        value = "Yes"
                    else:
                        value = "No"
                elif isinstance(value, datetime.datetime):
                    value = value.strftime(self.date_format)

                column_index = self.headers[key]['index']
                # width = self.get_max_width_for_column(table_data, key) * 2
                width = self.headers[key]['width']
                if key == "Description":
                    width = 200
                self.sales_order_table_widget.setItem(row_index, column_index, QtWidgets.QTableWidgetItem(str(value)))
                self.sales_order_table_widget.setColumnWidth(column_index, width)
        self.reset_progress_bar()

    def update_progess_bar_value(self, value):
        self.progressBar.setValue(value)
    
    def set_progress_bar_text(self, text):
        self.progressBar.setFormat(text)

    def reset_progress_bar(self):
        self.progressBar.setValue(0)
        self.progressBar.hide()

    def thread_get_current_fb_data(self):
        def set_updating_fishbowl_data(value: bool):
            self.updating_fishbowl_data = value
        
        if self.updating_fishbowl_data:
            logger.warning("Attempted to get data while fishbowl data was already being updated. Ignoring request.")
            return

        self.updating_fishbowl_data = True

        logger.info("Starting thread to get current sales order data from Fishbowl.")
        self.action_fishbowl_Get_Sales_Order_Data.setEnabled(False)

        fishbowl_database = FishbowlDatabaseConnection(connection_args=cutlistgenerator.program_settings.get_fishbowl_settings()['auth'])

        worker = Worker(fn=self.get_current_fb_data,
                        fishbowl_database=fishbowl_database,
                        cut_list_database=self.cut_list_generator_database
                        )


        worker.signals.finished.connect(self.reset_progress_bar)
        worker.signals.finished.connect(self.thread_get_so_table_data)
        worker.signals.finished.connect(lambda: self.action_fishbowl_Get_Sales_Order_Data.setEnabled(True))
        worker.signals.finished.connect(lambda: logger.info("[FISHBOWL DATA] Finished retreiving data from Fishbowl."))
        worker.signals.finished.connect(lambda: fishbowl_database.disconnect())
        worker.signals.result.connect(lambda: set_updating_fishbowl_data(False))
        worker.signals.result.connect(self.show_fishbowl_update_finished_message_box)
        worker.signals.progress.connect(self.update_progess_bar_value)
        worker.signals.progress_data.connect(self.set_progress_bar_text)

        self.progressBar.show()
        self.progressBar.setValue(0)
        self.threadpool.start(worker)
    
    def thread_get_so_table_data(self):
        def set_updating_table(value: bool):
            self.updating_table = value
        
        if self.updating_table:
            logger.warning("Attempted to get SO data while table was still updating. Ignoring request.")
            return

        self.updating_table = True
        logger.info("Starting thread to reload SO data into table.")

        worker = Worker(fn=self.get_so_table_data)

        worker.signals.finished.connect(self.reset_progress_bar)
        worker.signals.finished.connect(lambda: logger.info("[TABLE RELOAD] Finished reloading data into table."))
        worker.signals.result.connect(lambda: set_updating_table(False))
        worker.signals.result.connect(self.load_so_table_data)
        worker.signals.progress.connect(self.update_progess_bar_value)
        worker.signals.progress_data.connect(self.set_progress_bar_text)
        self.progressBar.show()
        self.progressBar.setValue(0)
        self.threadpool.start(worker)
    
    @staticmethod
    def get_current_fb_data(fishbowl_database: FishbowlDatabaseConnection, cut_list_database: CutListDatabase, progress_signal=None, progress_data_signal=None):
        start_time = datetime.datetime.now()
        total_rows, rows_inserted, rows_updated, total_skipped = utilities.update_sales_order_data_from_fishbowl(fishbowl_database, cut_list_database, progress_signal, progress_data_signal)
        end_time = datetime.datetime.now()
        time_delta = end_time - start_time
        return total_rows, rows_inserted, rows_updated, total_skipped

    def show_fishbowl_update_finished_message_box(self, result):
        total_rows, rows_inserted, rows_updated, total_skipped = result
        msg = QMessageBox()
        msg.setWindowTitle("Fishbowl")
        msg.setIcon(QMessageBox.Information)
        msg.setText(f"Fishbowl data update complete.")
        lines = [
            f"Total Fishbowl SO items open: {total_rows}",
            f"SO items updated: {rows_updated}",
            f"Products skipped: {total_skipped}",
            f"SO items inserted: {rows_inserted}",
            f"Items ignored: {total_rows - rows_inserted - total_skipped}",
            ]
        msg.setInformativeText("\n".join(lines))

        msg.setStandardButtons(QMessageBox.Ok)
        msg.setWindowModality(Qt.NonModal) # This is needed to keep the message box from blocking other code from running.
        msg.exec()