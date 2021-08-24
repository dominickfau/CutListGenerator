from cutlistgenerator.appdataclasses.cutjob import CutJob
from cutlistgenerator import database
from PyQt5.QtWidgets import QDialog, QMessageBox, QTableWidgetItem

from cutlistgenerator.ui.cutjobsearchdialog_ui import Ui_cut_job_search_dialog
from cutlistgenerator.database.cutlistdatabase import CutListDatabase
from cutlistgenerator.appdataclasses.product import Product
from cutlistgenerator.appdataclasses.wirecutter import WireCutter
from cutlistgenerator.appdataclasses.salesorder import SalesOrder, SalesOrderItem
from cutlistgenerator.logging import FileLogger
from cutlistgenerator import utilities
from cutlistgenerator.appdataclasses.systemproperty import SystemProperty


logger = FileLogger(__name__)

class CutJobSearchDialog(Ui_cut_job_search_dialog, QDialog):
    # TODO: Convert into a persistant dialog.
    def __init__(self,
                cut_list_generator_database: CutListDatabase,
                product: Product = None,
                wire_cutter: WireCutter = None,
                sales_order_item: SalesOrderItem = None,
                parent=None):
        super(Ui_cut_job_search_dialog, self).__init__(parent)
        self.setupUi(self)

        # Object attributes
        self.cut_list_generator_database = cut_list_generator_database
        self.cut_job = None
        self.linked_so_item = None
        self.sales_order_number = None
        # TODO: Is valid names needed?
        self._valid_products = []
        self._valid_wire_cutters = []
        self._valid_product_numbers = []
        self._valid_wire_cutter_names = []
        self.headers = utilities.get_table_headers(self.cut_job_table_widget)
        self.date_formate = SystemProperty.find_by_name(database_connection=cut_list_generator_database, name="date_formate").value

        # Populate combo boxes
        self._populate_product_number_combo_box()
        self._populate_wire_cutter_combo_box()

        # Connect signals
        self.search_push_button.clicked.connect(self.on_search_button_clicked)
        self.select_push_button.clicked.connect(self.on_select_button_clicked)
        self.cut_job_table_widget.doubleClicked.connect(self.on_select_button_clicked)
        self.find_so_item_push_button.clicked.connect(self.on_find_so_item_clicked)
        self.remove_linked_so_item_push_button.clicked.connect(self.unset_sales_order_item)

        # Automatically select product and wire cutter if given.
        if product is not None:
            self.product_number_combo_box.setCurrentText(product.number)
        
        if wire_cutter is not None:
            self.wire_cutter_name_combo_box.setCurrentText(wire_cutter.name)

        if sales_order_item:
            self.linked_so_item = sales_order_item
            self.set_sales_order_item(sales_order_item.id)
        
        # Populate table
        self.on_search_button_clicked()

        if self.cut_job_table_widget.rowCount() == 0:
            self.reject()
    
    def on_find_so_item_clicked(self):
        # TODO: Implement. Create a dialog that allows the user to search for a sales order item.
        pass

    def set_sales_order_item(self, so_item_id: int):
        self.sales_order_number = SalesOrder.get_number_from_sales_order_item_id(self.cut_list_generator_database, so_item_id)

        self.linked_sales_order_number_value_label.setText(self.sales_order_number)
        self.linked_sales_order_product_number_value_label.setText(self.linked_so_item.product.number)
        self.linked_sales_order_line_number_value_label.setText(str(self.linked_so_item.line_number))
    
    def unset_sales_order_item(self):
        self.linked_so_item = None
        self.sales_order_number = None
        self.linked_sales_order_number_value_label.setText("")
        self.linked_sales_order_product_number_value_label.setText("")
        self.linked_sales_order_line_number_value_label.setText("")

    def get_search_data(self):
        """Returns all data needed to search for a cut job."""
        product_number = self.product_number_combo_box.currentText()
        wire_cutter_name = self.wire_cutter_name_combo_box.currentText()
        sales_order_item = self.linked_so_item
        sales_order_number = self.sales_order_number
        return {
            "product_number": product_number,
            "wire_cutter_name": wire_cutter_name,
            "sales_order_item": sales_order_item,
            "sales_order_number": sales_order_number
        }
    
    def clear_table(self, tableWidget):
        logger.debug("[TABLE] Clearing table.")
        tableWidget.setRowCount(0)

    def on_search_button_clicked(self):
        search_data = self.get_search_data()
        self.clear_table(self.cut_job_table_widget)
        
        table_data = CutJob.get_all_open(self.cut_list_generator_database)
        self.cut_job_table_widget.setRowCount(len(table_data))

        row = 0
        for cut_job in table_data:
            so_number = "N/A"
            if cut_job.related_sales_order_item:
                so_number_value = SalesOrder.get_number_from_sales_order_item_id(self.cut_list_generator_database, cut_job.related_sales_order_item.id)
                so_number = f"{so_number_value} Line: {cut_job.related_sales_order_item.line_number}"
            
            if search_data["product_number"] != "" and search_data["product_number"] != cut_job.product.number:
                continue
            if search_data["wire_cutter_name"] != "" and search_data["wire_cutter_name"] != cut_job.assigned_wire_cutter.name:
                continue
            if search_data["sales_order_item"] != None and search_data["sales_order_item"].id != cut_job.related_sales_order_item.id:
                continue
            if search_data["sales_order_number"] != None and search_data["sales_order_number"] != so_number_value:
                continue

            column_index = self.headers['Id']['index']
            width = self.headers['Id']['width']
            self.cut_job_table_widget.setItem(row, column_index, QTableWidgetItem(str(cut_job.id)))
            self.cut_job_table_widget.setColumnWidth(column_index, width)

            column_index = self.headers['Date Created']['index']
            width = self.headers['Date Created']['width']
            value = cut_job.date_created.strftime(self.date_formate)
            self.cut_job_table_widget.setItem(row, column_index, QTableWidgetItem(value))
            self.cut_job_table_widget.setColumnWidth(column_index, width)

            column_index = self.headers['Product Number']['index']
            width = self.headers['Product Number']['width']
            self.cut_job_table_widget.setItem(row, column_index, QTableWidgetItem(str(cut_job.product.number)))
            self.cut_job_table_widget.setColumnWidth(column_index, width)

            column_index = self.headers['SO Number']['index']
            width = self.headers['SO Number']['width']
            self.cut_job_table_widget.setItem(row, column_index, QTableWidgetItem(so_number))
            self.cut_job_table_widget.setColumnWidth(column_index, width)

            column_index = self.headers['Assigned Cutter']['index']
            width = self.headers['Assigned Cutter']['width']
            self.cut_job_table_widget.setItem(row, column_index, QTableWidgetItem(str(cut_job.assigned_wire_cutter.name)))
            self.cut_job_table_widget.setColumnWidth(column_index, width)

            column_index = self.headers['Quantity Cut']['index']
            width = self.headers['Quantity Cut']['width']
            self.cut_job_table_widget.setItem(row, column_index, QTableWidgetItem(str(int(cut_job.quantity_cut))))
            self.cut_job_table_widget.setColumnWidth(column_index, width)

            column_index = self.headers['Cut Start Date']['index']
            width = self.headers['Cut Start Date']['width']
            value = ""
            if cut_job.date_cut_start:
                value = cut_job.date_cut_start.strftime(self.date_formate)
            self.cut_job_table_widget.setItem(row, column_index, QTableWidgetItem(value))
            self.cut_job_table_widget.setColumnWidth(column_index, width)

            column_index = self.headers["Cut End Date"]['index']
            width = self.headers["Cut End Date"]['width']
            value = ""
            if cut_job.date_cut_end:
                value = cut_job.date_cut_end.strftime(self.date_formate)
            self.cut_job_table_widget.setItem(row, column_index, QTableWidgetItem(value))
            self.cut_job_table_widget.setColumnWidth(column_index, width)

            column_index = self.headers['Term Start Date']['index']
            width = self.headers['Term Start Date']['width']
            value = ""
            if cut_job.date_termination_start:
                value = cut_job.date_termination_start.strftime(self.date_formate)
            self.cut_job_table_widget.setItem(row, column_index, QTableWidgetItem(value))
            self.cut_job_table_widget.setColumnWidth(column_index, width)

            column_index = self.headers['Term End Date']['index']
            width = self.headers['Term End Date']['width']
            value = ""
            if cut_job.date_termination_end:
                value = cut_job.date_termination_end.strftime(self.date_formate)
            self.cut_job_table_widget.setItem(row, column_index, QTableWidgetItem(value))
            self.cut_job_table_widget.setColumnWidth(column_index, width)

            column_index = self.headers['Splice Start Date']['index']
            width = self.headers['Splice Start Date']['width']
            value = ""
            if cut_job.date_splice_start:
                value = cut_job.date_splice_start.strftime(self.date_formate)
            self.cut_job_table_widget.setItem(row, column_index, QTableWidgetItem(value))
            self.cut_job_table_widget.setColumnWidth(column_index, width)

            column_index = self.headers['Splice End Date']['index']
            width = self.headers['Splice End Date']['width']
            value = ""
            if cut_job.date_splice_end:
                value = cut_job.date_splice_end.strftime(self.date_formate)
            self.cut_job_table_widget.setItem(row, column_index, QTableWidgetItem(value))
            self.cut_job_table_widget.setColumnWidth(column_index, width)

            column_index = self.headers['Ready For Build']['index']
            width = self.headers['Ready For Build']['width']
            self.cut_job_table_widget.setItem(row, column_index, QTableWidgetItem(str(cut_job.is_ready_for_build_as_string)))
            self.cut_job_table_widget.setColumnWidth(column_index, width)

            row += 1
        
        # This removes any blank rows at the end of the table.
        self.cut_job_table_widget.setRowCount(row)

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