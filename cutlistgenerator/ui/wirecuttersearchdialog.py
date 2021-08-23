from PyQt5.QtWidgets import QDialog, QMessageBox, QTableWidgetItem

from cutlistgenerator.ui.wirecuttersearchdialog_ui import Ui_wire_cutter_search_dialog
from cutlistgenerator.database.cutlistdatabase import CutListDatabase
from cutlistgenerator.appdataclasses.wirecutter import WireCutter
from cutlistgenerator import utilities
from cutlistgenerator.appdataclasses.systemproperty import SystemProperty


class WireCutterSearchDialog(Ui_wire_cutter_search_dialog, QDialog):
    def __init__(self,
                 cut_list_generator_database: CutListDatabase,
                 wire_cutter: WireCutter = None,
                 parent=None):
        super(Ui_wire_cutter_search_dialog, self).__init__(parent)
        self.setupUi(self)
        self.cut_list_generator_database = cut_list_generator_database
        self.wire_cutter = wire_cutter

        self.headers = utilities.get_table_headers(self.wire_cutter_table_widget)
        self.date_formate = SystemProperty.find_by_name(database_connection=cut_list_generator_database, name="date_formate").value

        self.search_push_button.clicked.connect(self.on_search_button_clicked)
        self.select_push_button.clicked.connect(self.on_select_button_clicked)
        self.wire_cutter_table_widget.doubleClicked.connect(self.on_select_button_clicked)

        if self.wire_cutter:
            self.name_line_edit.setText(self.wire_cutter.name)
        
        self.on_search_button_clicked()
            
    def clear_table(self, tableWidget):
        tableWidget.setRowCount(0)
    
    def get_search_data(self):
        """Returns all data needed to search for a wire cutter."""
        wire_cutter_name = self.name_line_edit.text()
        return {
            "wire_cutter_name": wire_cutter_name
        }
    
    def on_search_button_clicked(self):
        search_data = self.get_search_data()
        self.clear_table(self.wire_cutter_table_widget)
        
        table_data = WireCutter.get_all(self.cut_list_generator_database)
        self.wire_cutter_table_widget.setRowCount(len(table_data))

        row = 0
        for wire_cutter in table_data:
            self.wire_cutter_table_widget.setItem(row, self.headers['Id']['index'], QTableWidgetItem(str(wire_cutter.id)))
            self.wire_cutter_table_widget.setItem(row, self.headers['Name']['index'], QTableWidgetItem(wire_cutter.name))
            self.wire_cutter_table_widget.setItem(row, self.headers['Max Wire Size']['index'], QTableWidgetItem(str(wire_cutter.max_wire_gauge_awg)))
            self.wire_cutter_table_widget.setItem(row, self.headers['Processing Speed (ft/min)']['index'], QTableWidgetItem(str(wire_cutter.processing_speed_feet_per_minute)))
            self.wire_cutter_table_widget.setColumnWidth(self.headers['Processing Speed (ft/min)']['index'], 200)
            value = ""
            if wire_cutter.details:
                value = wire_cutter.details
            self.wire_cutter_table_widget.setItem(row, self.headers['Details']['index'], QTableWidgetItem(value))
            row += 1

    
    def on_select_button_clicked(self):
        row_num = self.wire_cutter_table_widget.currentRow()
        if row_num == -1:
            QMessageBox.information(self, "No row selected", "Please select a row to edit.")
            return
        
        wire_cutter_id = self.wire_cutter_table_widget.item(row_num, self.headers['Id']['index']).text()
        self.wire_cutter = WireCutter.from_id(self.cut_list_generator_database, wire_cutter_id)
        self.accept()
