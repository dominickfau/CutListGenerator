import sys
import os
import datetime
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QDialog, QApplication, QMessageBox


from cutlistgenerator.ui.mainwindow import Ui_MainWindow
from cutlistgenerator.settings import Settings

DEFAULT_SETTINGS_FILE_NAME = "settings.json"
PROGRAM_NAME = "Cut List Generator"
__version__ = "0.0.3"

# settings = load_settings(DEFAULT_SETTINGS_FILE_NAME)



class Application(QtWidgets.QMainWindow):
    def __init__(self):
        super(Application, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.setWindowTitle(f"{PROGRAM_NAME} v{__version__}")

        self.settings = Settings()

        # Create settings file if it doesn't exist
        if not Settings.validate_file_path(DEFAULT_SETTINGS_FILE_NAME):
            self.settings.save_to_file_path(DEFAULT_SETTINGS_FILE_NAME)


def main():
    app = QApplication(sys.argv)
    main_window = Application()
    main_window.show()
    app.exec_()
    
    exit()


if __name__ == "__main__":
    main()