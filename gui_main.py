import sys, os, traceback
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



class Application(QtWidgets.QMainWindow):
    def __init__(self, logger):
        super(Application, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.logger = logger

        self.setWindowTitle(f"{PROGRAM_NAME} v{__version__}")

        self.settings = cutlistgenerator.program_settings


        # Create settings file if it doesn't exist
        if not Settings.validate_file_path(DEFAULT_SETTINGS_FILE_NAME):
            self.logger.info(f"Creating settings file: {DEFAULT_SETTINGS_FILE_NAME}")
            utilities.touch(DEFAULT_SETTINGS_FILE_NAME)
            self.settings.set_file_path(DEFAULT_SETTINGS_FILE_NAME)
            self.settings.save()
        else:
            self.logger.info(f"Loading settings from file: {DEFAULT_SETTINGS_FILE_NAME}")
            self.settings.set_file_path(DEFAULT_SETTINGS_FILE_NAME)
            self.settings.load()

        # Set logging level
        self.logger.set_level(self.settings.get_logging_level())

        self.fishbowl_database = FishbowlDatabaseConnection(connection_args=self.settings.get_fishbowl_settings()['auth'])
        self.cut_list_generator_database = MySQLDatabaseConnection(connection_args=self.settings.get_cutlist_settings()['auth'])

        # self.cut_list_generator_database.create()

        # self.ui.actionGet_Sales_Order_Data.triggered.connect(self.get_current_fb_data)


    def get_current_fb_data(self):
        total_rows, rows_inserted = utilities.update_sales_order_data_from_fishbowl(fishbowl_database=self.fishbowl_database,
                                                        cut_list_database=self.cut_list_generator_database)
        
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(f"{total_rows} rows available to import from Fishbowl.\n{rows_inserted} rows were inserted into the cutlist table.")
        # msg.setInformativeText("{} rows from FishBowl".format(total_fishbowl_rows))
        msg.setWindowTitle("Fishbowl Data")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec()



def main():
    import os
    logger = FileLogger(__name__)
    logger.info("[START] Starting application.")
    try:
        app = QApplication(sys.argv)
        main_window = Application(logger)
        main_window.show()
        app.exec_()

        main_window.fishbowl_database.disconnect()
        main_window.cut_list_generator_database.disconnect()
    except Exception as e:
        logger.critical("Fatale exception occurred.", exc_info=True)
        logger.critical("End of exception.")

        msg = ResizableMessageBox()
        msg.setIcon(QMessageBox.Information)
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