from __future__ import annotations
import logging
from datetime import datetime
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QCloseEvent, QKeyEvent
from cutlistgenerator import errors
from cutlistgenerator import LAST_USERNAME
from cutlistgenerator.settings import DATE_FORMAT
from cutlistgenerator.customwidgets.qtable import CustomQTableWidget
from cutlistgenerator.utilities import clean_text_input
from cutlistgenerator.database import Session, global_session
from cutlistgenerator.database.models.part import Part
from cutlistgenerator.database.models.customer import Customer, CustomerNameConversion
from cutlistgenerator.database.models.user import User
from cutlistgenerator.database.models.salesorder import SalesOrderItem
from cutlistgenerator.database.models.cutjob import (
    CutJob,
    CutJobItem,
    CutJobStatus,
    CutJobItemStatus,
)
from cutlistgenerator.database.models.wirecutter import WireCutter


backend_logger = logging.getLogger("backend")


class UserEditorDialog(QtWidgets.QDialog):
    """A dialog for creating and editing users."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("User Editor")

        self.session = Session()

    def closeEvent(self, event: QCloseEvent) -> None:
        """Clean up resources before closing the window."""
        self.session.close()
        event.accept()


class ChangePasswordDialog(QtWidgets.QDialog):
    """A dialog for changing the password."""

    def __init__(self, user: User, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Change Password")
        self.keyPressEvent = self.key_pressed_event

        self.session = Session()

        self.user = user

        self.main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_layout)

        self.current_password_label = QtWidgets.QLabel("Current Password:")
        self.current_password_edit = QtWidgets.QLineEdit()
        self.current_password_edit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.current_password_edit.editingFinished.connect(
            lambda widget=self.current_password_edit: clean_text_input(widget)
        )

        self.new_password_label = QtWidgets.QLabel("New Password:")
        self.new_password_edit = QtWidgets.QLineEdit()
        self.new_password_edit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.new_password_edit.editingFinished.connect(
            lambda widget=self.new_password_edit: clean_text_input(widget)
        )

        self.confirm_password_label = QtWidgets.QLabel("Confirm Password:")
        self.confirm_password_edit = QtWidgets.QLineEdit()
        self.confirm_password_edit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.confirm_password_edit.editingFinished.connect(
            lambda widget=self.confirm_password_edit: clean_text_input(widget)
        )

        self.change_password_button = QtWidgets.QPushButton("Change Password")
        self.change_password_button.clicked.connect(self.change_password)

        self.form_layout = QtWidgets.QFormLayout()
        self.form_layout.addRow(self.current_password_label, self.current_password_edit)
        self.form_layout.addRow(self.new_password_label, self.new_password_edit)
        self.form_layout.addRow(self.confirm_password_label, self.confirm_password_edit)

        self.main_layout.addLayout(self.form_layout)
        self.main_layout.addStretch()
        self.main_layout.addWidget(self.change_password_button)

    def key_pressed_event(self, event: QKeyEvent) -> None:
        """Handle the key press event."""
        if event.key() == Qt.Key_Escape:
            self.reject()
            self.close()

        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.change_password()

    def change_password(self) -> None:
        """Change the password."""
        current_password = self.current_password_edit.text()
        new_password = self.new_password_edit.text()
        confirm_password = self.confirm_password_edit.text()

        if not current_password or not new_password or not confirm_password:
            QtWidgets.QMessageBox.warning(self, "Error", "Please fill in all fields.")
            return

        if new_password != confirm_password:
            QtWidgets.QMessageBox.warning(self, "Error", "New passwords do not match.")
            self.new_password_edit.setText("")
            self.confirm_password_edit.setText("")
            self.new_password_edit.setFocus()
            return

        if not self.user.verify_password(current_password):
            QtWidgets.QMessageBox.warning(
                self, "Error", "Current password is incorrect."
            )
            self.current_password_edit.selectAll()
            self.current_password_edit.setFocus()
            return

        self.user.password = new_password
        self.session.commit()
        self.session.close()
        self.accept()
        self.close()


class LoginDialog(QtWidgets.QDialog):
    def __init__(self, parent):
        super().__init__(parent)

        self.setWindowTitle("Login")
        self.keyPressEvent = self.key_pressed_event

        self.user = None  # type: User

        self.username_label = QtWidgets.QLabel("Username:")
        self.username_edit = QtWidgets.QLineEdit()
        self.username_edit.editingFinished.connect(
            lambda widget=self.username_edit: clean_text_input(widget)
        )

        self.password_label = QtWidgets.QLabel("Password:")
        self.password_edit = QtWidgets.QLineEdit()
        self.password_edit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.password_edit.editingFinished.connect(
            lambda widget=self.password_edit: clean_text_input(widget)
        )

        self.login_button = QtWidgets.QPushButton("Login")
        self.login_button.clicked.connect(self.on_login_button_clicked)

        self.exit_button = QtWidgets.QPushButton("Cancel")
        self.exit_button.clicked.connect(self.close_event)

        self.exit_button = QtWidgets.QPushButton("Exit")
        self.exit_button.clicked.connect(QtWidgets.qApp.quit)

        if LAST_USERNAME.value != "":
            self.username_edit.setText(LAST_USERNAME.value)
            self.password_edit.selectAll()
            self.password_edit.setFocus()

        self.main_layout = QtWidgets.QVBoxLayout()

        self.form_layout = QtWidgets.QFormLayout()
        self.form_layout.addRow(self.username_label, self.username_edit)
        self.form_layout.addRow(self.password_label, self.password_edit)

        self.button_layout = QtWidgets.QHBoxLayout()
        self.button_layout.addStretch()
        self.button_layout.addWidget(self.login_button)
        self.button_layout.addWidget(self.exit_button)
        self.button_layout.addWidget(self.exit_button)

        self.main_layout.addLayout(self.form_layout)
        self.main_layout.addLayout(self.button_layout)

        self.setLayout(self.main_layout)

    def close_event(self, event=None):
        self.reject()
        self.close()

    def key_pressed_event(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.on_login_button_clicked()

    def on_login_button_clicked(self):
        username = self.username_edit.text()
        password = self.password_edit.text()

        if len(username) == 0 or len(password) == 0:
            QtWidgets.QMessageBox.warning(
                self, "Login Error", "Username and password are required."
            )
            self.password_edit.selectAll()
            self.password_edit.setFocus()
            return

        try:
            self.user = User.authenticate(username, password)
        except errors.AuthenticationError as e:
            QtWidgets.QMessageBox.warning(self, "Login Error", str(e))
            self.password_edit.selectAll()
            self.password_edit.setFocus()
            return

        LAST_USERNAME.value = username
        LAST_USERNAME.save()

        self.accept()


class CustomerNameConverterDialog(QtWidgets.QDialog):
    def __init__(self, parent):
        super().__init__(parent)

        self.setWindowTitle("Customer Name Converter")
        self.setMinimumSize(300, 100)
        self.keyPressEvent = self.key_pressed_event

        self.session = Session()
        self.modified = (
            False  # Used to determine if the user has modified the customer name
        )
        self.loading_data = False
        self.previous_customer = None  # type: Customer

        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        self.message_label = QtWidgets.QLabel(
            "Add or change what customer name you want to use.\nThis window will stay open until you close it."
        )

        self.customer_label = QtWidgets.QLabel("Customer:")
        self.customer_edit = QtWidgets.QComboBox()

        self.loading_data = True
        customers = (
            self.session.query(Customer).order_by(Customer.name).all()
        )  # type: list[Customer]
        for customer in customers:
            self.customer_edit.addItem(customer.name, customer)

        self.loading_data = False

        self.customer_edit.setEditable(False)
        self.customer_edit.setInsertPolicy(QtWidgets.QComboBox.NoInsert)
        self.customer_edit.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)

        self.customer_name_label = QtWidgets.QLabel("Customer Name:")
        self.customer_name_edit = QtWidgets.QLineEdit()

        self.save_button = QtWidgets.QPushButton("Save")
        self.exit_button = QtWidgets.QPushButton("Exit")

        self.on_customer_changed()

    def create_layout(self):
        self.main_layout = QtWidgets.QVBoxLayout()

        self.form_layout = QtWidgets.QFormLayout()
        self.form_layout.addRow(self.customer_label, self.customer_edit)
        self.form_layout.addRow(self.customer_name_label, self.customer_name_edit)

        self.button_layout = QtWidgets.QHBoxLayout()
        self.button_layout.addStretch()
        self.button_layout.addWidget(self.save_button)
        self.button_layout.addWidget(self.exit_button)

        self.main_layout.addWidget(self.message_label)
        self.main_layout.addStretch()
        self.main_layout.addLayout(self.form_layout)
        self.main_layout.addLayout(self.button_layout)

        self.setLayout(self.main_layout)

    def create_connections(self):
        self.customer_edit.currentIndexChanged.connect(self.on_customer_changed)
        self.customer_name_edit.editingFinished.connect(
            lambda widget=self.customer_name_edit: clean_text_input(widget)
        )
        self.customer_name_edit.textEdited.connect(self.on_customer_name_changed)

        self.save_button.clicked.connect(self.on_save_button_clicked)
        self.exit_button.clicked.connect(self.close_event)

    def close_event(self, event=None):
        if self.check_pending_changes():
            return
        self.close()

    def on_customer_name_changed(self, text=None):
        if self.loading_data:
            return
        self.modified = True
        self.setWindowTitle("Customer Name Converter - *")

    def key_pressed_event(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.save()

    def check_pending_changes(self):
        if self.loading_data:
            return False
        if self.modified:
            message_box = QtWidgets.QMessageBox(self)
            message_box.setWindowTitle("Save Changes?")
            message_box.setText(
                "You have made changes to the customer name. Would you like to save them?"
            )
            message_box.setStandardButtons(
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
            )
            message_box.setDefaultButton(QtWidgets.QMessageBox.Yes)
            message_box.setEscapeButton(QtWidgets.QMessageBox.Cancel)
            message_box.setIcon(QtWidgets.QMessageBox.Question)
            response = message_box.exec()
            if response == QtWidgets.QMessageBox.Yes:
                self.save(self.previous_customer)
                return True
            elif response == QtWidgets.QMessageBox.No:
                self.modified = False

        return False

    def on_customer_changed(self, index=None):
        if self.check_pending_changes():
            return

        customer = self.customer_edit.currentData()
        self.previous_customer = customer
        conversion = (
            self.session.query(CustomerNameConversion)
            .filter(CustomerNameConversion.customer_id == customer.id)
            .first()
        )  # type: CustomerNameConversion

        if conversion is None:
            self.customer_name_edit.setText("")
            return
        self.customer_name_edit.setText(conversion.name)

    def on_save_button_clicked(self):
        self.save()

    def save(self, previous_customer: Customer = None):
        customer = self.customer_edit.currentData()
        if previous_customer:
            customer = previous_customer

        new_name = self.customer_name_edit.text()

        conversion = (
            self.session.query(CustomerNameConversion)
            .filter(CustomerNameConversion.customer_id == customer.id)
            .first()
        )  # type: CustomerNameConversion
        if conversion is None:
            conversion = CustomerNameConversion(customer_id=customer.id, name=new_name)
            self.session.add(conversion)

        conversion.date_modified = datetime.now()
        conversion.name = new_name
        if new_name == "":
            self.session.delete(conversion)
        self.session.commit()
        self.modified = False
        self.setWindowTitle("Customer Name Converter")


class CutJobEditorDialog(QtWidgets.QDialog):

    COLUMNS = [
        "Part Number",
        "Description",
        "Qty To Cut",
        "Qty Cut",
        "Qty Remaining",
        "Status",
    ]

    def __init__(
        self,
        sales_order_item: SalesOrderItem,
        cut_job: CutJob = None,
        sales_order_items: list[SalesOrderItem] = None,
        parent=None,
    ):
        super().__init__(parent)

        self.resize(600, 400)

        self.setWindowTitle("Cut Job Editor")
        self.keyPressEvent = self.key_pressed_event

        self.sales_order_item = sales_order_item
        self.cut_job = cut_job
        if self.cut_job is None and self.sales_order_item.cut_job_item:
            self.cut_job = self.sales_order_item.cut_job_item.cut_job

        self.create_widgets()
        self.create_layout()
        self.create_connections()

        if not self.cut_job:
            status = CutJobItemStatus.find_by_name("Entered")
            wire_cutter = self.wire_cutter_combo_box.currentData()
            self.cut_job = CutJob.create(wire_cutter)
            cut_job_item = CutJobItem(
                cut_job_id=self.cut_job.id,
                status_id=status.id,
                part_id=self.sales_order_item.part_id,
            )
            if self.sales_order_item:
                cut_job_item.add_sales_order_item(self.sales_order_item)

            if sales_order_items:
                for sales_order_item in sales_order_items:
                    cut_job_item.add_sales_order_item(sales_order_item)

        self.reload_table()

    def key_pressed_event(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()

    def create_widgets(self):
        self.wire_cutter_combo_box = QtWidgets.QComboBox()
        self.wire_cutter_combo_box.setSizeAdjustPolicy(
            QtWidgets.QComboBox.AdjustToContents
        )

        wire_cutters = WireCutter.find_all()
        for wire_cutter in wire_cutters:
            self.wire_cutter_combo_box.addItem(wire_cutter.name, wire_cutter)

        if self.cut_job:
            self.wire_cutter_combo_box.setCurrentIndex(
                self.wire_cutter_combo_box.findData(self.cut_job.wire_cutter)
            )

        self.cut_job_status_combo_box = QtWidgets.QComboBox()
        self.cut_job_status_combo_box.setSizeAdjustPolicy(
            QtWidgets.QComboBox.AdjustToContents
        )

        cut_job_statuses = CutJobStatus.find_all()
        for cut_job_status in cut_job_statuses:
            self.cut_job_status_combo_box.addItem(cut_job_status.name, cut_job_status)

        if self.cut_job:
            self.cut_job_status_combo_box.setCurrentIndex(
                self.cut_job_status_combo_box.findData(self.cut_job.status)
            )

        self.table_widget = CustomQTableWidget()

        self.table_widget.set_table_headers(self.COLUMNS)

        self.add_item_button = QtWidgets.QPushButton("Add Item")
        self.remove_item_button = QtWidgets.QPushButton("Remove Item")
        self.remove_item_button.setEnabled(False)

        self.save_button = QtWidgets.QPushButton("Save")

    def create_layout(self):
        layout = QtWidgets.QVBoxLayout()

        form_layout = QtWidgets.QFormLayout()
        form_layout.addRow("Wire Cutter", self.wire_cutter_combo_box)
        form_layout.addRow("Status", self.cut_job_status_combo_box)

        table_layout = QtWidgets.QHBoxLayout()
        table_button_layout = QtWidgets.QVBoxLayout()
        table_layout.addWidget(self.table_widget, 1)
        table_layout.addLayout(table_button_layout)

        # table_button_layout.addWidget(self.add_item_button)
        # table_button_layout.addWidget(self.remove_item_button)
        table_button_layout.addStretch(1)

        layout.addLayout(form_layout)
        layout.addLayout(table_layout)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

    def create_connections(self):
        self.table_widget.selectionModel().selectionChanged.connect(
            self.on_table_selection_changed
        )
        self.table_widget.itemDoubleClicked.connect(self.on_table_item_double_clicked)
        self.save_button.clicked.connect(self.on_save_button_clicked)
        self.add_item_button.clicked.connect(self.on_add_item_button_clicked)
        self.remove_item_button.clicked.connect(self.on_remove_item_button_clicked)

    def on_table_selection_changed(self):
        self.remove_item_button.setEnabled(True)

    def on_add_item_button_clicked(self):
        dialog = CutJobItemEditorDialog(self.cut_job, parent=self)
        dialog.exec()
        self.reload_table()

    def on_table_item_double_clicked(self, row: QtWidgets.QTableWidgetItem):
        index = row.row()
        if index == -1:
            return
        cut_job_item = self.cut_job.items[index]
        dialog = CutJobItemEditorDialog(
            self.cut_job, cut_job_item=cut_job_item, parent=self
        )
        dialog.exec()
        self.reload_table()
        self.cut_job_status_combo_box.setCurrentIndex(
            self.cut_job_status_combo_box.findData(self.cut_job.status)
        )

    def on_remove_item_button_clicked(self):
        selected_row = self.table_widget.currentRow()
        if selected_row == -1:
            self.remove_item_button.setEnabled(False)

        cut_job_item = self.table_widget.item(selected_row, 0).data(
            Qt.UserRole
        )  # type: CutJobItem
        cut_job_item.delete()
        self.table_widget.removeRow(selected_row)

    def reload_table(self):
        self.table_widget.setRowCount(0)

        data = {}  # type: dict[CutJobItem, list[str]]
        if self.cut_job:
            for cut_job_item in self.cut_job.items:
                data[cut_job_item] = [
                    cut_job_item.part.number,
                    cut_job_item.part.description,
                    str(cut_job_item.quantity_to_cut),
                    str(cut_job_item.quantity_cut),
                    str(cut_job_item.left_to_cut),
                    cut_job_item.status.name,
                ]

        for cut_job_item, row_data in data.items():
            self.table_widget.insert_row_data(row_data, user_data=cut_job_item)

        self.table_widget.resizeColumnsToContents()

    def on_save_button_clicked(self):
        if self.table_widget.rowCount() == 0:
            QtWidgets.QMessageBox.warning(
                self,
                "No items",
                "No items have been added to the cut job.\n"
                "Please add at least one item.",
            )
            return
        self.cut_job.wire_cutter = self.wire_cutter_combo_box.currentData()
        self.cut_job.status = self.cut_job_status_combo_box.currentData()

        self.cut_job.save()
        self.close()


class CutJobItemEditorDialog(QtWidgets.QDialog):
    def __init__(
        self,
        cut_job: CutJob,
        cut_job_item: CutJobItem = None,
        parent=None,
    ):
        super().__init__(parent)

        self.resize(300, 100)

        self.setWindowTitle("Cut Job Item Editor")
        self.keyPressEvent = self.key_pressed_event

        self.cut_job = cut_job
        self.cut_job_item = cut_job_item

        self.create_widgets()
        self.create_layout()
        self.create_connections()
        if self.cut_job_item:
            self.part_combo_box.setEnabled(False)

    def key_pressed_event(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()

    def create_widgets(self):
        self.part_combo_box = QtWidgets.QComboBox()
        self.part_combo_box.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
        self.part_combo_box.setEditable(True)

        self.item_status_combo_box = QtWidgets.QComboBox()
        self.item_status_combo_box.setSizeAdjustPolicy(
            QtWidgets.QComboBox.AdjustToContents
        )

        item_statuses = CutJobItemStatus.find_all()
        parts = Part.find_all()

        for part in parts:
            self.part_combo_box.addItem(part.number, part)

        for item_status in item_statuses:
            self.item_status_combo_box.addItem(item_status.name, item_status)

        self.quantity_to_cut_spin_box = QtWidgets.QSpinBox()
        self.quantity_to_cut_spin_box.setMinimum(0)
        self.quantity_to_cut_spin_box.setMaximum(1000000)
        self.quantity_to_cut_spin_box.setButtonSymbols(
            QtWidgets.QAbstractSpinBox.NoButtons
        )

        self.quantity_cut_spin_box = QtWidgets.QSpinBox()
        self.quantity_cut_spin_box.setMinimum(0)
        self.quantity_cut_spin_box.setMaximum(1000000)
        self.quantity_cut_spin_box.setButtonSymbols(
            QtWidgets.QAbstractSpinBox.NoButtons
        )

        if self.cut_job_item:
            self.quantity_to_cut_spin_box.setValue(self.cut_job_item.quantity_to_cut)
            self.quantity_cut_spin_box.setValue(self.cut_job_item.quantity_cut)

            self.part_combo_box.setCurrentText(self.cut_job_item.part.number)

            self.item_status_combo_box.setCurrentIndex(
                self.item_status_combo_box.findData(self.cut_job_item.status)
            )

        self.save_button = QtWidgets.QPushButton("Save")

    def create_layout(self):
        layout = QtWidgets.QVBoxLayout()

        form_layout = QtWidgets.QFormLayout()
        form_layout.addRow("Part", self.part_combo_box)
        form_layout.addRow("Status", self.item_status_combo_box)
        form_layout.addRow("Quantity to cut", self.quantity_to_cut_spin_box)
        form_layout.addRow("Quantity cut", self.quantity_cut_spin_box)

        layout.addLayout(form_layout)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

    def create_connections(self):
        self.save_button.clicked.connect(self.on_save_button_clicked)
        self.quantity_to_cut_spin_box.editingFinished.connect(
            lambda: self.quantity_cut_spin_box.setMaximum(
                self.quantity_to_cut_spin_box.value()
            )
        )
        self.quantity_to_cut_spin_box.valueChanged.connect(
            self.on_quantity_cut_spin_box_value_changed
        )
        self.quantity_cut_spin_box.valueChanged.connect(
            self.on_quantity_cut_spin_box_value_changed
        )

    def on_quantity_cut_spin_box_value_changed(self):
        qty_cut = self.quantity_cut_spin_box.value()
        qty_to_cut = self.quantity_to_cut_spin_box.value()
        if qty_cut == qty_to_cut:
            self.item_status_combo_box.setCurrentIndex(
                self.item_status_combo_box.findData(
                    CutJobItemStatus.find_by_name("Fulfilled")
                )
            )
        else:
            self.item_status_combo_box.setCurrentIndex(
                self.item_status_combo_box.findData(
                    CutJobItemStatus.find_by_name("In Progress")
                )
            )

        if qty_cut == 0:
            self.item_status_combo_box.setCurrentIndex(
                self.item_status_combo_box.findData(
                    CutJobItemStatus.find_by_name("Entered")
                )
            )

    def on_save_button_clicked(self):
        part = self.part_combo_box.currentData()

        if self.cut_job_item:
            self.cut_job_item.part = part
            self.cut_job_item.quantity_to_cut = self.quantity_to_cut_spin_box.value()
            self.cut_job_item.quantity_cut = self.quantity_cut_spin_box.value()
            self.cut_job_item.status = self.item_status_combo_box.currentData()
            self.cut_job_item.save()
        else:
            self.cut_job_item = CutJobItem(
                cut_job_id=self.cut_job.id,
                part_id=part.id,
                quantity_to_cut=self.quantity_to_cut_spin_box.value(),
                quantity_cut=self.quantity_cut_spin_box.value(),
                status_id=self.item_status_combo_box.currentData().id,
            )
            self.cut_job_item.save()

        self.close()
