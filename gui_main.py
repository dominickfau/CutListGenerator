from cutlistgenerator.appdataclasses.systemproperty import SystemProperty
import sys, os, traceback, datetime
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMessageBox


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

class Application(QtWidgets.QMainWindow):
    def __init__(self):
        super(Application, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.setWindowTitle(f"{PROGRAM_NAME} v{__version__}")

        self.settings = cutlistgenerator.program_settings


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
        

        # self.cut_list_generator_database.create()

        # self.ui.actionGet_Sales_Order_Data.triggered.connect(self.get_current_fb_data)


    def get_current_fb_data(self):
        start_time = datetime.datetime.now()
        total_rows, rows_inserted = utilities.update_sales_order_data_from_fishbowl(fishbowl_database=self.fishbowl_database,
                                                        cut_list_database=self.cut_list_generator_database)
        end_time = datetime.datetime.now()
        time_delta = end_time - start_time
        logger.info(f"[EXECUTION TIME]: {time_delta.total_seconds() *1000} ms")
        
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(f"{total_rows} rows available to import from Fishbowl.\n{rows_inserted} rows were inserted into the cutlist table.")

        # TODO: Change detailed text to something more meaningful.
        # msg.setDetailedText(f"{total_rows} rows available to import from Fishbowl.\n{rows_inserted} rows were inserted into the cutlist table.\n\nExecution time: {time_delta.total_seconds() *1000} ms")
        msg.setWindowTitle("Fishbowl Data")
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