import sys
import traceback
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMessageBox

import cutlistgenerator
from cutlistgenerator.logging import FileLogger
from cutlistgenerator.settings import Settings
from cutlistgenerator import utilities

from cutlistgenerator.ui.customwidgets.resizablemessagebox import ResizableMessageBox
from cutlistgenerator.gui_mainwindow import MainWindow


DEFAULT_SETTINGS_FILE_NAME = "settings.json"
PROGRAM_NAME = "Cut List Generator"
__version__ = "0.1.5"

# Create settings file if it doesn't exist
if not Settings.validate_file_path(DEFAULT_SETTINGS_FILE_NAME):
    utilities.touch(DEFAULT_SETTINGS_FILE_NAME)
    cutlistgenerator.program_settings.set_file_path(DEFAULT_SETTINGS_FILE_NAME)
    cutlistgenerator.program_settings.save()
else:
    cutlistgenerator.program_settings.set_file_path(DEFAULT_SETTINGS_FILE_NAME)
    cutlistgenerator.program_settings.load()

logger = FileLogger(__name__)


class Application():
    def __init__(self):
        super(Application, self).__init__()
        logger.info(f"Program Version: {__version__}")
        self.app = QApplication(sys.argv)
        self.main_window = MainWindow()
    
    def cleanup(self):
        self.main_window.fishbowl_database.disconnect()
        self.main_window.cut_list_generator_database.disconnect()

    def run(self):
        try:
            self.main_window.showMaximized()
            self.main_window.thread_get_so_table_data()
            self.app.exec_()
        except Exception as e:
            message = traceback.format_exc()
            logger.critical("Fatale exception occurred.")
            logger.exception(message)
            logger.critical("End of exception.")

            msg = ResizableMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Fatale exception occurred.")
            msg.setInformativeText(f"Exception: {e}")
            msg.setDetailedText(message)
            msg.setWindowTitle("Fatale Exception")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()

        logger.info("[END] Closing application.")
        exit()


if __name__ == "__main__":
    logger.info("[START] Starting application.")
    app = Application()
    app.run()