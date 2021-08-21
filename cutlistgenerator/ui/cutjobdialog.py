import datetime
from cutlistgenerator import database
from PyQt5.QtWidgets import QDialog, QMessageBox
from PyQt5.QtCore import QDateTime

from cutlistgenerator.ui.cutjobdialog_ui import Ui_cut_job_dialog
from cutlistgenerator.ui.wirecutterdialog import WireCutterDialog
from cutlistgenerator.database.cutlistdatabase import CutListDatabase
from cutlistgenerator.database.fishbowldatabase import FishbowlDatabaseConnection
from cutlistgenerator.appdataclasses.product import Product
from cutlistgenerator.appdataclasses.wirecutter import WireCutter
from cutlistgenerator.appdataclasses.cutjob import CutJob
from cutlistgenerator.appdataclasses.salesorder import SalesOrder, SalesOrderItem
from cutlistgenerator.logging import FileLogger


logger = FileLogger(__name__)

class CutJobDialog(Ui_cut_job_dialog, QDialog):
    def __init__(self,
                 cut_list_generator_database: CutListDatabase,
                 fishbowl_database: FishbowlDatabaseConnection,
                 product: Product = None,
                 linked_so_item_id: int = None,
                 cut_job: CutJob = None,
                 parent=None):
        super(Ui_cut_job_dialog, self).__init__(parent)
        self.setupUi(self)

        # BUG: Fix this.
        # if cut_job is None or not (product is None and linked_so_item_id is None):
        #     # TODO: Create a better Exception.
        #     raise ValueError("Either a cut job or a product and a linked sales order item must be provided.")

        # Object attributes
        self.cut_list_generator_database = cut_list_generator_database
        self.fishbowl_database = fishbowl_database
        self.linked_so_item = None
        self.sales_order = None
        self.cut_job = cut_job
        # TODO: Is valid names needed?
        self._valid_products = []
        self._valid_wire_cutters = []
        self._valid_product_numbers = []
        self._valid_wire_cutter_names = []

        # Populate combo boxes
        self._populate_product_number_combo_box()
        self._populate_wire_cutter_combo_box()
        
        if product:
            self.add_product(product)
            self.product_number_combo_box.setCurrentText(product.number)

        if linked_so_item_id:
            self.link_sales_order_item(linked_so_item_id)
        
        if self.cut_job:
            self.load_cut_job(self.cut_job)
        
        # Connect signals
        self.save_push_button.clicked.connect(self.on_save_button_clicked)
        self.add_product_push_button.clicked.connect(self.on_add_product_clicked)
        self.add_wire_cutter_push_button.clicked.connect(self.on_add_wire_cutter_clicked)
        self.find_so_item_push_button.clicked.connect(self.on_find_so_item_clicked)
        self.remove_linked_so_item_push_button.clicked.connect(self.on_remove_linked_so_item_clicked)

    def load_cut_job(self, cut_job: CutJob):
        """Loads a cut job into the dialog."""
        self.unlink_sales_order_item()
        if cut_job.related_sales_order_item:
            self.link_sales_order_item(cut_job.related_sales_order_item.id)

        self.product_number_combo_box.setCurrentText(cut_job.product.number)
        self.wire_cutter_name_combo_box.setCurrentText(cut_job.assigned_wire_cutter.name)

        current_date_time = QDateTime.fromString(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "yyyy-MM-dd hh:mm:ss")
        
        # Cutting
        # Initial set datetime to current datetime.
        self.cut_start_date_time_edit.setDateTime(current_date_time)
        self.cut_end_date_time_edit.setDateTime(current_date_time)
        self.termination_start_date_time_edit.setDateTime(current_date_time)
        self.termination_end_date_time_edit.setDateTime(current_date_time)
        self.splice_start_date_time_edit.setDateTime(current_date_time)
        self.splice_end_date_time_edit.setDateTime(current_date_time)

        if cut_job.date_cut_start:
            self.cutting_group_box.setChecked(True)
            self.qty_cut_spin_box.setValue(cut_job.quantity_cut)
            date_time = QDateTime.fromString(cut_job.date_cut_start.strftime("%Y-%m-%d %H:%M:%S"), "yyyy-MM-dd hh:mm:ss")
            self.cut_start_date_time_edit.setDateTime(date_time)
        
            if cut_job.date_cut_end:
                self.cutting_finished_group_box.setChecked(True)
                date_time = QDateTime.fromString(cut_job.date_cut_end.strftime("%Y-%m-%d %H:%M:%S"), "yyyy-MM-dd hh:mm:ss")
                self.cut_end_date_time_edit.setDateTime(date_time)
        
        # Termination
        if cut_job.date_termination_start:
            self.termination_group_box.setChecked(True)
            date_time = QDateTime.fromString(cut_job.date_termination_start.strftime("%Y-%m-%d %H:%M:%S"), "yyyy-MM-dd hh:mm:ss")
            self.termination_start_date_time_edit.setDateTime(date_time)
        
            if cut_job.date_termination_end:
                self.termination_finished_group_box.setChecked(True)
                date_time = QDateTime.fromString(cut_job.date_termination_end.strftime("%Y-%m-%d %H:%M:%S"), "yyyy-MM-dd hh:mm:ss")
                self.termination_end_date_time_edit.setDateTime(date_time)
        
        # Splice
        if cut_job.date_splice_start:
            self.splice_group_box.setChecked(True)
            date_time = QDateTime.fromString(cut_job.date_splice_start.strftime("%Y-%m-%d %H:%M:%S"), "yyyy-MM-dd hh:mm:ss")
            self.splice_start_date_time_edit.setDateTime(date_time)
            
            if cut_job.date_splice_end:
                self.splice_finished_group_box.setChecked(True)
                date_time = QDateTime.fromString(cut_job.date_splice_end.strftime("%Y-%m-%d %H:%M:%S"), "yyyy-MM-dd hh:mm:ss")
                self.splice_end_date_time_edit.setDateTime(date_time)

    def link_sales_order_item(self, so_item_id: int):
        """Links a sales order item to the cut job. Takes a sales order item id."""
        logger.debug(f"Attempting to link sales order item id {so_item_id} to cut job.")

        self.linked_so_item = SalesOrderItem.from_id(self.cut_list_generator_database, so_item_id)
        self.sales_order = SalesOrder.from_sales_order_item_id(self.cut_list_generator_database, so_item_id)

        self.linked_sales_order_number_value_label.setText(self.sales_order.number)
        self.linked_sales_order_product_number_value_label.setText(self.linked_so_item.product.number)
        self.linked_sales_order_line_number_value_label.setText(str(self.linked_so_item.line_number))
    
    def unlink_sales_order_item(self):
        """Unlinks the sales order item from the cut job."""
        logger.info(f"[CUT JOB] Unlinking sales order item from cut job.")
        self.linked_so_item = None
        self.sales_order = None
        self.linked_sales_order_number_value_label.setText("")
        self.linked_sales_order_product_number_value_label.setText("")
        self.linked_sales_order_line_number_value_label.setText("")
    
    def on_find_so_item_clicked(self):
        # TODO: Implement. Create a dialog that allows the user to search for a sales order item.
        pass

    def validate_form(self):
        form_valid = True
        message = []

        if self.product_number_combo_box.currentText() == "":
            form_valid = False
            message.append("Select a product number.")
        
        if self.wire_cutter_name_combo_box.currentText() == "":
            form_valid = False
            message.append("Select a wire cutter.")
        
        return form_valid, message

    def on_add_product_clicked(self):
        # TODO: Implement. Create a dialog that allows the user to add a product.
        pass
    
    def on_remove_linked_so_item_clicked(self):
        msg = QMessageBox()
        msg.setWindowTitle("Cut Job")
        msg.setIcon(QMessageBox.Information)
        msg.setText("Are you sure you want to remove the linked sales order item?")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.exec()
        if msg.result() == QMessageBox.No:
            return

        self.unlink_sales_order_item()
    
    def on_add_wire_cutter_clicked(self):
        selected_wire_cutter_name = self.wire_cutter_name_combo_box.currentText()
        wire_cutter = None
        if selected_wire_cutter_name:
            logger.debug(f"Attempting to add wire cutter {selected_wire_cutter_name} to cut job.")
            wire_cutter = WireCutter.from_name(self.cut_list_generator_database, selected_wire_cutter_name)
            if wire_cutter:
                logger.info(f"[CUT JOB] Adding wire cutter {wire_cutter.name} to cut job.")
            else:
                logger.warning(f"[CUT JOB] Could not find wire cutter with name: {selected_wire_cutter_name}.")

        dialog = WireCutterDialog(self.cut_list_generator_database, wire_cutter, parent=self)
        if dialog.exec():
            self.add_wire_cutter(dialog.wire_cutter)
    
    def _populate_wire_cutter_combo_box(self):
        self.wire_cutter_name_combo_box.clear()
        self._valid_wire_cutter_names = []
        self._valid_wire_cutters = []

        self.wire_cutter_name_combo_box.addItem("")
        for wire_cutter in WireCutter.get_all(self.cut_list_generator_database):
            self.wire_cutter_name_combo_box.addItem(wire_cutter.name)
            self._valid_wire_cutter_names.append(wire_cutter.name)
            self._valid_wire_cutters.append(wire_cutter)
    
    def add_wire_cutter(self, wire_cutter: WireCutter):
        """Add a wire cutter to the list of valid wire cutters."""
        if wire_cutter.name in self._valid_wire_cutter_names:
            return
            
        self._valid_wire_cutter_names.append(wire_cutter.name)
        self._valid_wire_cutter_names.sort()
        
        self.wire_cutter_name_combo_box.clear()
        self.wire_cutter_name_combo_box.addItem("")
        for item in self._valid_wire_cutter_names:
            self.wire_cutter_name_combo_box.addItem(item)
        self.wire_cutter_name_combo_box.setCurrentText(wire_cutter.name)

    def _populate_product_number_combo_box(self):
        self.product_number_combo_box.clear()
        self._valid_product_numbers = []
        self._valid_products = []

        self.product_number_combo_box.addItem("")
        for product in Product.get_all(self.cut_list_generator_database):
            self.product_number_combo_box.addItem(product.number)
            self._valid_product_numbers.append(product.number)
            self._valid_products.append(product)
    
    def add_product(self, product: Product):
        """Add a product number to the list of valid products."""
        if product in self._valid_products:
            return
        
        self._valid_product_numbers.append(product.number)
        self._valid_product_numbers.sort()
        
        self.product_number_combo_box.clear()
        self.product_number_combo_box.addItem("")
        for product_number in self._valid_product_numbers:
            self.product_number_combo_box.addItem(product_number)
        self.product_number_combo_box.setCurrentText(product.number)
    
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
        form_valid, messages = self.validate_form()
        if not form_valid:
            msg = QMessageBox()
            msg.setWindowTitle("Cut Job")
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Please fix the following problems:")
            msg.setInformativeText("\n".join(messages))
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()
            return

        # Required Info
        selected_product_number = self.product_number_combo_box.currentText()
        if selected_product_number not in self._valid_product_numbers:
            product_number_data = self.find_fishbowl_product(selected_product_number)
            if not product_number_data:
                self.product_number_combo_box.setCurrentIndex(0)
                return
            product_number = product_number_data['product_number']
        else:
            product_number = selected_product_number
        
        selected_wire_cutter_name = self.wire_cutter_name_combo_box.currentText()
        if selected_wire_cutter_name not in self._valid_wire_cutter_names:
            wire_cutter_data = self.cut_list_generator_database.get_wire_cutter_by_name(selected_wire_cutter_name)
            if not wire_cutter_data:
                self.wire_cutter_name_combo_box.setCurrentIndex(0)
                return
            wire_cutter_name = wire_cutter_data['name']
        else:
            wire_cutter_name = selected_wire_cutter_name

        # Cutting Info
        cut_started_flag = self.cutting_group_box.isChecked()
        cut_finished_flag = self.cutting_finished_group_box.isChecked()

        qty_cut = self.qty_cut_spin_box.value()
        cut_start_date_time = self.cut_start_date_time_edit.dateTime().toString("yyyy-MM-dd hh:mm:ss")
        cut_end_date_time = self.cut_end_date_time_edit.dateTime().toString("yyyy-MM-dd hh:mm:ss")

        # Set dates to None if not checked.
        if not cut_started_flag:
            qty_cut = None
            cut_start_date_time = None
        
        if not cut_finished_flag:
            cut_end_date_time = None

        # Termination Info
        termination_started_flag = self.termination_group_box.isChecked()
        termination_finished_flag = self.termination_finished_group_box.isChecked()
        termination_start_date_time = self.termination_start_date_time_edit.dateTime().toString("yyyy-MM-dd hh:mm:ss")
        termination_end_date_time = self.termination_end_date_time_edit.dateTime().toString("yyyy-MM-dd hh:mm:ss")
        
        # Set dates to None if not checked.
        if not termination_started_flag:
            termination_start_date_time = None
        
        if not termination_finished_flag:
            termination_end_date_time = None

        # Splice Info
        splice_started_flag = self.splice_group_box.isChecked()
        splice_finished_flag = self.splice_finished_group_box.isChecked()
        splice_start_date_time = self.splice_start_date_time_edit.dateTime().toString("yyyy-MM-dd hh:mm:ss")
        splice_end_date_time = self.splice_end_date_time_edit.dateTime().toString("yyyy-MM-dd hh:mm:ss")

        # Set dates to None if not checked.
        if not splice_started_flag:
            splice_start_date_time = None
        
        if not splice_finished_flag:
            splice_end_date_time = None
        
        ready_for_build_flag = cut_finished_flag and termination_finished_flag and splice_finished_flag

        if not self.cut_job:
            self.cut_job = CutJob(database_connection=self.cut_list_generator_database,
                                product=Product.from_number(self.cut_list_generator_database, product_number),
                                assigned_wire_cutter=WireCutter.from_name(self.cut_list_generator_database, wire_cutter_name),
                                related_sales_order_item=self.linked_so_item,
                                quantity_cut=qty_cut,
                                date_cut_start=cut_start_date_time,
                                date_cut_end=cut_end_date_time,
                                date_termination_start=termination_start_date_time,
                                date_termination_end=termination_end_date_time,
                                date_splice_start=splice_start_date_time,
                                date_splice_end=splice_end_date_time,
                                is_cut=cut_finished_flag,
                                is_spliced=splice_finished_flag,
                                is_terminated=termination_finished_flag,
                                is_ready_for_build=ready_for_build_flag)
        else:
            product = Product.from_number(self.cut_list_generator_database, product_number)
            assigned_wire_cutter = WireCutter.from_name(self.cut_list_generator_database, wire_cutter_name)
            related_sales_order_item = self.linked_so_item
            self.cut_job.product = product
            self.cut_job.assigned_wire_cutter = assigned_wire_cutter
            self.cut_job.related_sales_order_item = related_sales_order_item
            self.cut_job.quantity_cut = qty_cut
            self.cut_job.date_cut_start = cut_start_date_time
            self.cut_job.date_cut_end = cut_end_date_time
            self.cut_job.date_termination_start = termination_start_date_time
            self.cut_job.date_termination_end = termination_end_date_time
            self.cut_job.date_splice_start = splice_start_date_time
            self.cut_job.date_splice_end = splice_end_date_time
            self.cut_job.is_cut = cut_finished_flag
            self.cut_job.is_spliced = splice_finished_flag
            self.cut_job.is_terminated = termination_finished_flag
            self.cut_job.is_ready_for_build = ready_for_build_flag

        self.accept()