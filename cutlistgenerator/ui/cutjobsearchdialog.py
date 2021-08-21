from cutlistgenerator.appdataclasses.cutjob import CutJob
from cutlistgenerator import database
from PyQt5.QtWidgets import QDialog, QMessageBox, QTableWidgetItem

from cutlistgenerator.ui.cutjobsearchdialog_ui import Ui_cut_job_search_dialog
from cutlistgenerator.database.cutlistdatabase import CutListDatabase
from cutlistgenerator.appdataclasses.product import Product
from cutlistgenerator.appdataclasses.wirecutter import WireCutter
from cutlistgenerator.logging import FileLogger


logger = FileLogger(__name__)

class CutJobSearchDialog(Ui_cut_job_search_dialog, QDialog):
    def __init__(self,
                cut_list_generator_database: CutListDatabase,
                product: Product = None,
                wire_cutter: WireCutter = None,
                parent=None):
        super(Ui_cut_job_search_dialog, self).__init__(parent)
        self.setupUi(self)

        # Object attributes
        self.cut_list_generator_database = cut_list_generator_database
        self.cut_job = None
        # TODO: Is valid names needed?
        self._valid_products = []
        self._valid_wire_cutters = []
        self._valid_product_numbers = []
        self._valid_wire_cutter_names = []

        # Populate combo boxes
        self._populate_product_number_combo_box()
        self._populate_wire_cutter_combo_box()

        # Connect signals
        self.search_push_button.clicked.connect(self.on_search_button_clicked)
        self.select_push_button.clicked.connect(self.on_select_button_clicked)
        self.cut_job_table_widget.doubleClicked.connect(self.on_select_button_clicked)

        # Automatically select product and wire cutter if given.
        if product is not None:
            self.product_number_combo_box.setCurrentText(product.number)
        
        if wire_cutter is not None:
            self.wire_cutter_name_combo_box.setCurrentText(wire_cutter.name)
        
        # Populate table
        self.on_search_button_clicked()

    
    def get_search_data(self):
        """Returns all data needed to search for a cut job."""
        product_number = self.product_number_combo_box.currentText()
        wire_cutter_name = self.wire_cutter_name_combo_box.currentText()
        return (product_number, wire_cutter_name)
    
    def clear_table(self, tableWidget):
        logger.debug("[TABLE] Clearing table.")
        tableWidget.setRowCount(0)

    def on_search_button_clicked(self):
        search_data = self.get_search_data()
        self.clear_table(self.cut_job_table_widget)
        
        table_data = CutJob.get_all_open(self.cut_list_generator_database)
        self.cut_job_table_widget.setRowCount(len(table_data))

        for row, cut_job in enumerate(table_data):
            self.cut_job_table_widget.setItem(row, 0, QTableWidgetItem(str(cut_job.id)))
            self.cut_job_table_widget.setColumnWidth(0, 50)
            self.cut_job_table_widget.setItem(row, 1, QTableWidgetItem(str(cut_job.date_created.date())))
            self.cut_job_table_widget.setItem(row, 2, QTableWidgetItem(str(cut_job.product.number)))
            self.cut_job_table_widget.setItem(row, 3, QTableWidgetItem("Not implemented."))
            self.cut_job_table_widget.setItem(row, 4, QTableWidgetItem(str(cut_job.assigned_wire_cutter.name)))
            self.cut_job_table_widget.setItem(row, 5, QTableWidgetItem(str(cut_job.quantity_cut)))
            self.cut_job_table_widget.setItem(row, 6, QTableWidgetItem(str(cut_job.date_cut_start)))
            self.cut_job_table_widget.setItem(row, 7, QTableWidgetItem(str(cut_job.date_cut_end)))
            self.cut_job_table_widget.setItem(row, 8, QTableWidgetItem(str(cut_job.date_termination_start)))
            self.cut_job_table_widget.setItem(row, 9, QTableWidgetItem(str(cut_job.date_termination_end)))
            self.cut_job_table_widget.setItem(row, 10, QTableWidgetItem(str(cut_job.date_splice_start)))
            self.cut_job_table_widget.setItem(row, 11, QTableWidgetItem(str(cut_job.date_splice_end)))
            self.cut_job_table_widget.setItem(row, 12, QTableWidgetItem(str(cut_job.is_ready_for_build)))

    def validate_form(self):
        """Validates the form data."""
        form_valid = True
        message = []

        row_num = self.cut_job_table_widget.currentRow()
        if row_num == -1:
            message.append("Please select a row.")
            form_valid = False
        return form_valid, message

    def on_select_button_clicked(self):
        # TODO: Implement select button.
        row_num = self.cut_job_table_widget.currentRow()
        form_valid, messages = self.validate_form()
        if not form_valid:
            msg = QMessageBox()
            msg.setWindowTitle("Cut Job Search")
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Please fix the following problems:")
            msg.setInformativeText("\n".join(messages))
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()
            return
        
        cut_job_id = int(self.cut_job_table_widget.item(row_num, 0).text())
        self.cut_job = CutJob.from_id(self.cut_list_generator_database, cut_job_id)
        self.accept()
    
    def _populate_product_number_combo_box(self):
        self.product_number_combo_box.clear()
        self._valid_product_numbers = []
        self._valid_products = []

        self.product_number_combo_box.addItem("")
        for product in Product.get_all(self.cut_list_generator_database):
            self.product_number_combo_box.addItem(product.number)
            self._valid_product_numbers.append(product.number)
            self._valid_products.append(product)
    
    def _populate_wire_cutter_combo_box(self):
        self.wire_cutter_name_combo_box.clear()
        self._valid_wire_cutter_names = []
        self._valid_wire_cutters = []

        self.wire_cutter_name_combo_box.addItem("")
        for wire_cutter in WireCutter.get_all(self.cut_list_generator_database):
            self.wire_cutter_name_combo_box.addItem(wire_cutter.name)
            self._valid_wire_cutter_names.append(wire_cutter.name)
            self._valid_wire_cutters.append(wire_cutter)