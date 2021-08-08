import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMessageBox


from cutlistgenerator.ui.mainwindow import Ui_MainWindow
from cutlistgenerator.settings import Settings
from cutlistgenerator.database.mysqldatabase import MySQLDatabaseConnection
from cutlistgenerator.database.fishbowldatabase import FishbowlDatabaseConnection
from cutlistgenerator import utilities

DEFAULT_SETTINGS_FILE_NAME = "settings.json"
PROGRAM_NAME = "Cut List Generator"
__version__ = "0.1.0"


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
        else:
            self.settings.set_file_path(DEFAULT_SETTINGS_FILE_NAME)
            self.settings.load()

        self.fishbowl_database = FishbowlDatabaseConnection(connection_args=self.settings.fishbowl_settings['auth'])
        self.cut_list_generator_database = MySQLDatabaseConnection(connection_args=self.settings.cutlist_settings['auth'])

        self.ui.actionGet_Current_SO_Data_From_Fishbowl.triggered.connect(self.get_current_fb_data)

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
    app = QApplication(sys.argv)
    main_window = Application()
    main_window.show()
    app.exec_()

    main_window.fishbowl_database.disconnect()
    main_window.cut_list_generator_database.disconnect()
    
    exit()


if __name__ == "__main__":
    main()