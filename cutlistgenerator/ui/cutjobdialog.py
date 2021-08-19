from PyQt5.QtWidgets import QDialog, QMessageBox

from cutlistgenerator.ui.cutjobdialog_ui import Ui_cut_job_dialog
from cutlistgenerator.ui.wirecutterdialog import WireCutterDialog
from cutlistgenerator.database.cutlistdatabase import CutListDatabase
from cutlistgenerator.database.fishbowldatabase import FishbowlDatabaseConnection
from cutlistgenerator.appdataclasses.product import Product
from cutlistgenerator.appdataclasses.wirecutter import WireCutter
from cutlistgenerator.appdataclasses.cutjob import CutJob


class CutJobDialog(Ui_cut_job_dialog, QDialog):
    def __init__(self,
                 cut_list_generator_database: CutListDatabase,
                 fishbowl_database: FishbowlDatabaseConnection,
                 product: Product = None,
                 parent=None):
        super(CutJobDialog, self).__init__(parent)
        self.setupUi(self)
        self.cut_list_generator_database = cut_list_generator_database
        self.fishbowl_database = fishbowl_database
        self.product = product
        self._valid_product_numbers = []
        self._valid_wire_cutter_names = []
        self._populate_product_number_combo_box()
        self._populate_wire_cutter_combo_box()
        if self.product:
            self.add_product(self.product.number)
        
        self.save_push_button.clicked.connect(self.on_save_button_clicked)
        self.add_product_push_button.clicked.connect(self.on_add_product_clicked)
        self.add_wire_cutter_push_button.clicked.connect(self.on_add_wire_cutter_clicked)
        self.cut_job = None
    
    def on_add_product_clicked(self):
        pass
    
    def on_add_wire_cutter_clicked(self):
        selected_wire_cutter_name = self.wire_cutter_name_combo_box.currentText()
        wire_cutter = None
        if selected_wire_cutter_name:
            wire_cutter = WireCutter.from_name(self.cut_list_generator_database, selected_wire_cutter_name)
        dialog = WireCutterDialog(self.cut_list_generator_database, wire_cutter, parent=self)
        if dialog.exec():
            self.add_wire_cutter(dialog.wire_cutter.name)
    
    def _populate_wire_cutter_combo_box(self):
        self.wire_cutter_name_combo_box.clear()

        self.wire_cutter_name_combo_box.addItem("")
        for row in self.cut_list_generator_database.get_all_wire_cutters():
            self.wire_cutter_name_combo_box.addItem(row['name'])
            self._valid_wire_cutter_names.append(row['name'])
    
    def add_wire_cutter(self, wire_cutter_name):
        """Add a wire cutter to the list of valid wire cutters."""
        if wire_cutter_name not in self._valid_wire_cutter_names:
            self._valid_wire_cutter_names.append(wire_cutter_name)
        
        self._valid_wire_cutter_names.sort()
        
        self.wire_cutter_name_combo_box.clear()
        self.wire_cutter_name_combo_box.addItem("")
        for item in self._valid_wire_cutter_names:
            self.wire_cutter_name_combo_box.addItem(item)
        self.wire_cutter_name_combo_box.setCurrentText(wire_cutter_name)

    def _populate_product_number_combo_box(self):
        self.product_number_combo_box.clear()

        self.product_number_combo_box.addItem("")
        for row in self.cut_list_generator_database.get_all_products():
            self.product_number_combo_box.addItem(row['number'])
            self._valid_product_numbers.append(row['number'])
    
    def add_product(self, product_number):
        """Add a product number to the list of valid products."""
        if product_number not in self._valid_product_numbers:
            self._valid_product_numbers.append(product_number)
        
        self._valid_product_numbers.sort()
        
        self.product_number_combo_box.clear()
        self.product_number_combo_box.addItem("")
        for item in self._valid_product_numbers:
            self.product_number_combo_box.addItem(item)
        self.product_number_combo_box.setCurrentText(product_number)
    
    def find_fishbowl_product(self, product_number, show_message_box=True):
        """Find the product in Fishbowl with the given product number."""
        fishbowl_product = self.fishbowl_database.get_product_data_from_number(product_number)
        if not fishbowl_product:
            if show_message_box:
                msg = QMessageBox()
                msg.setWindowTitle("Cut Job")
                msg.setIcon(QMessageBox.Information)
                msg.setText(f"Could not find product number {product_number}.")
                msg.setInformativeText("An attempt was made to find this product within Fishbowl, but it could not be found. Please check the product number and try again.")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec()
            return None
        return fishbowl_product

    def on_save_button_clicked(self):
        selected_product_number = self.product_number_combo_box.currentText()
        if selected_product_number not in self._valid_product_numbers:
            product_number = self.find_fishbowl_product(selected_product_number)
            if not product_number:
                return
        else:
            product_number = selected_product_number
        



        self.cut_job = product_number
        self.accept()

