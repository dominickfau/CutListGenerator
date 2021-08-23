from PyQt5.QtWidgets import QDialog, QMessageBox

from cutlistgenerator.ui.wirecutterdialog_ui import Ui_wire_cutter_dialog
from cutlistgenerator.database.cutlistdatabase import CutListDatabase
from cutlistgenerator.appdataclasses.wirecutter import WireCutter


class WireCutterDialog(Ui_wire_cutter_dialog, QDialog):
    def __init__(self,
                 cut_list_generator_database: CutListDatabase,
                 wire_cutter: WireCutter = None,
                 parent=None):
        super(Ui_wire_cutter_dialog, self).__init__(parent)
        self.setupUi(self)
        self.cut_list_generator_database = cut_list_generator_database
        self.wire_cutter = wire_cutter

        if self.wire_cutter:
            self.name_line_edit.setText(self.wire_cutter.name)

            if self.wire_cutter.max_wire_gauge_awg:
                self.max_wire_size_spin_box.setValue(self.wire_cutter.max_wire_gauge_awg)
            
            if self.wire_cutter.processing_speed_feet_per_minute:
                self.processing_speed_double_spin_box.setValue(self.wire_cutter.processing_speed_feet_per_minute)
            
            if self.wire_cutter.details:
                self.details_text_edit.setPlainText(self.wire_cutter.details)
            

        self.save_push_button.clicked.connect(self.on_save_button_clicked)
    
    def validate_form(self):
        form_valid = True
        message = ""

        if self.name_line_edit.text() == "":
            form_valid = False
            message = "Name cannot be empty."
        
        return form_valid, message

    def on_save_button_clicked(self):
        form_valid, msg = self.validate_form()
        if not form_valid:
            QMessageBox.warning(self, "Warning", msg)
            return
        
        name = self.name_line_edit.text()
        max_wire_gauge_awg = self.max_wire_size_spin_box.value()
        processing_speed_feet_per_minute = self.processing_speed_double_spin_box.value()
        details = self.details_text_edit.toPlainText()

        if not self.wire_cutter:
            self.wire_cutter = WireCutter(self.cut_list_generator_database, name, max_wire_gauge_awg, processing_speed_feet_per_minute, details)
        else:
            self.wire_cutter.name = name
            self.wire_cutter.max_wire_gauge_awg = max_wire_gauge_awg
            self.wire_cutter.processing_speed_feet_per_minute = processing_speed_feet_per_minute
            self.wire_cutter.details = details
        
        self.wire_cutter.save()
        self.accept()
