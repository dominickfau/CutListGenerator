from cutlistgenerator.appdataclasses.systemproperty import SystemProperty
import sys, os, traceback, datetime
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import QRunnable, QThreadPool, pyqtSlot, pyqtSignal, QObject


import cutlistgenerator
from cutlistgenerator.ui.mainwindow import Ui_MainWindow
from cutlistgenerator.ui.customwidgets.resizablemessagebox import ResizableMessageBox
from cutlistgenerator.settings import Settings
from cutlistgenerator.database.mysqldatabase import MySQLDatabaseConnection
from cutlistgenerator.database.fishbowldatabase import FishbowlDatabaseConnection
from cutlistgenerator import utilities
from cutlistgenerator.logging import FileLogger


DEFAULT_SETTINGS_FILE_NAME = "settings.json"
PROGRAM_NAME = "Cut List Generator"
__version__ = "0.1.0"

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

        self.settings = cutlistgenerator.program_settings
        self.threadpool = QThreadPool()


        # Create settings file if it doesn't exist
        if not Settings.validate_file_path(DEFAULT_SETTINGS_FILE_NAME):
            logger.info(f"Creating settings file: {DEFAULT_SETTINGS_FILE_NAME}")
            utilities.touch(DEFAULT_SETTINGS_FILE_NAME)
            self.settings.set_file_path(DEFAULT_SETTINGS_FILE_NAME)
            self.settings.save()
        else:
            logger.info(f"Loading settings from file: {DEFAULT_SETTINGS_FILE_NAME}")
            self.settings.set_file_path(DEFAULT_SETTINGS_FILE_NAME)
            self.settings.load()

        self.fishbowl_database = FishbowlDatabaseConnection(connection_args=self.settings.get_fishbowl_settings()['auth'])
        self.cut_list_generator_database = MySQLDatabaseConnection(connection_args=self.settings.get_cutlist_settings()['auth'])

        if not self.settings.is_database_setup():
            logger.info("[DATABASE] Setting up database.")
            # TODO: Add a dialog to infrom the user that they need to setup the database.
            # TODO: Create a function to setup the database.
            utilities.create_database(self.cut_list_generator_database)
            self.settings.set_database_setup(True)
            logger.info("[DATABASE] Database setup complete.")

        self.ui.actionGet_Current_SO_Data_From_Fishbowl.triggered.connect(self.thread_get_current_fb_data)
        auto_update_fishbowl_so_data = SystemProperty.find_by_name(self.cut_list_generator_database, "fishbowl_auto_update_sales_orders")
        # if auto_update_fishbowl_so_data.value:
        #     logger.info("[AUTO UPDATE] Auto updating sales order data from Fishbowl.")
        #     self.get_current_fb_data()

    def thread_get_current_fb_data(self):
        logger.info("[TREAD] Starting thread to get current sales order data from Fishbowl.")
        self.ui.statusbar.showMessage("Pulling current sales order data from Fishbowl.")
        self.ui.actionGet_Current_SO_Data_From_Fishbowl.setEnabled(False)
        worker = Worker(fn=self.get_current_fb_data, fishbowl_database=self.fishbowl_database, cut_list_database=self.cut_list_generator_database)
        worker.signals.finished.connect(lambda: self.ui.statusbar.showMessage("Finished pulling sales order data from Fishbowl."))
        worker.signals.finished.connect(lambda: self.ui.actionGet_Current_SO_Data_From_Fishbowl.setEnabled(True))
        worker.signals.finished.connect(self.show_fishbowl_update_finished_message_box)
        self.threadpool.start(worker)
    
    @staticmethod
    def get_current_fb_data(fishbowl_database, cut_list_database):
        # TODO: Rework this to enable pySignals to be used.
        start_time = datetime.datetime.now()
        total_rows, rows_inserted = utilities.update_sales_order_data_from_fishbowl(fishbowl_database, cut_list_database)
        end_time = datetime.datetime.now()
        time_delta = end_time - start_time
        logger.info(f"[EXECUTION TIME]: {time_delta.total_seconds() *1000} ms")

    def show_fishbowl_update_finished_message_box(self):
        msg = QMessageBox()
        msg.setWindowTitle("Fishbowl")
        msg.setIcon(QMessageBox.Information)
        msg.setText("Fishbowl data update complete.")

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