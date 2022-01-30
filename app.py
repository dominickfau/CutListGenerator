from __future__ import annotations
import sys
import threading
from datetime import datetime
from dataclasses import dataclass
from PyQt5 import QtCore, QtGui, QtWidgets
import cutlistgenerator
import fishbowlorm
from fishbowlorm import models as fb_models
from cutlistgenerator import frontend_logger, errors
from cutlistgenerator import (
    PROGRAM_NAME,
    PROGRAM_VERSION,
    DEBUG,
    LAST_USERNAME,
)
from cutlistgenerator import (
    FISHBOWL_DATABASE_USER,
    FISHBOWL_DATABASE_PASSWORD,
    FISHBOWL_DATABASE_HOST,
    FISHBOWL_DATABASE_PORT,
    FISHBOWL_DATABASE_SCHEMA,
)
from cutlistgenerator import FORCE_REBUILD_DATABASE, utilities
from cutlistgenerator.customwidgets.customqtable import CustomQTableWidget
from cutlistgenerator.database import Session
from cutlistgenerator.database.models import (
    WireCutter,
    WireSize,
    Customer,
    CustomerNameConversion,
    SalesOrder,
    SalesOrderStatus,
    SalesOrderItem,
    CutJobStatus,
    CutJob,
    CutJobItem,
    CutJobItemStatus,
    User,
    Part,
)

cutlistgenerator.database.create(force_recreate=FORCE_REBUILD_DATABASE)

# db_name = "qes"
# host = "192.168.1.107"
# port = "3306"
# username = "gone"
# password = "fishing"

fishbowl_orm = fishbowlorm.FishbowlORM(
    db_name=FISHBOWL_DATABASE_SCHEMA,
    host=FISHBOWL_DATABASE_HOST,
    port=FISHBOWL_DATABASE_PORT,
    username=FISHBOWL_DATABASE_USER,
    password=FISHBOWL_DATABASE_PASSWORD,
)


@dataclass
class SalesOrderSearchCriteria:
    """The search criteria for the sales order table."""

    number: str = ""
    customer_name: str = ""
    status: str = ""
    show_fully_cut: bool = False


class UserEditor(QtWidgets.QDialog):
    """A dialog for creating and editing users."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("User Editor")

        self.session = Session()

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
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
            lambda widget=self.current_password_edit: utilities.clean_text_input(widget)
        )

        self.new_password_label = QtWidgets.QLabel("New Password:")
        self.new_password_edit = QtWidgets.QLineEdit()
        self.new_password_edit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.new_password_edit.editingFinished.connect(
            lambda widget=self.new_password_edit: utilities.clean_text_input(widget)
        )

        self.confirm_password_label = QtWidgets.QLabel("Confirm Password:")
        self.confirm_password_edit = QtWidgets.QLineEdit()
        self.confirm_password_edit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.confirm_password_edit.editingFinished.connect(
            lambda widget=self.confirm_password_edit: utilities.clean_text_input(widget)
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

    def key_pressed_event(self, event: QtGui.QKeyEvent) -> None:
        """Handle the key press event."""
        if event.key() == QtCore.Qt.Key_Escape:
            self.reject()
            self.close()

        if event.key() == QtCore.Qt.Key_Return or event.key() == QtCore.Qt.Key_Enter:
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
            lambda widget=self.username_edit: utilities.clean_text_input(widget)
        )

        self.password_label = QtWidgets.QLabel("Password:")
        self.password_edit = QtWidgets.QLineEdit()
        self.password_edit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.password_edit.editingFinished.connect(
            lambda widget=self.password_edit: utilities.clean_text_input(widget)
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
        if event.key() == QtCore.Qt.Key_Escape:
            self.close()
        if event.key() == QtCore.Qt.Key_Return or event.key() == QtCore.Qt.Key_Enter:
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


class CustomerNameConverter(QtWidgets.QDialog):
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
            lambda widget=self.customer_name_edit: utilities.clean_text_input(widget)
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
        if event.key() == QtCore.Qt.Key_Escape:
            self.close()
        if event.key() == QtCore.Qt.Key_Return or event.key() == QtCore.Qt.Key_Enter:
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


class MainWindow(QtWidgets.QMainWindow):
    """The main window of the application."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.refreshing_data = False

        self.session = Session()

        self.SALES_ORDER_TABLE_HEADERS = [
            "SO Number",
            "Customer",
            "Due Date",
            "Status",
            "Part Number",
            "Description",
            "Quantity Ordered",
            "Quantity Fulfilled",
            "Quantity Left To Cut",
            "Fully Cut",
            "Line Number",
            "Item Status",
        ]

        self.CUT_JOB_TABLE_HEADERS = [
            "Number",
            "Status",
            "Part Number",
            "Description",
            "Quantity To Cut",
            "Quantity Cut",
            "Quantity Left To Cut",
            "Item Status",
        ]

        self.setWindowTitle(f"{PROGRAM_NAME}")

        self.create_widgets()
        self.create_layout()
        self.create_connections()
        self.create_actions()
        self.create_menus()
        # self.create_toolbars()
        self.create_status_bar()

        self.set_default_values()
        self.status_bar.showMessage("Ready")
        self.centralWidget().setDisabled(True)

    def login(self):
        login_dialog = LoginDialog(self)
        login_dialog.exec_()
        if login_dialog.result() == QtWidgets.QDialog.Accepted:
            self.centralWidget().setDisabled(False)
            self.action_login.setEnabled(False)
            self.action_logout.setEnabled(True)
            self.setWindowTitle(f"{PROGRAM_NAME} ({User.current_user.username})")
            self.action_refresh_so_data.trigger()
            self.action_refresh_cut_job_data.trigger()

    def logout(self):
        self.centralWidget().setDisabled(True)
        self.action_login.setEnabled(True)
        self.action_logout.setEnabled(False)
        self.setWindowTitle(f"{PROGRAM_NAME}")
        User.logout()
        self.reset_widgets()
        self.action_login.trigger()

    def change_password(self):
        change_password_dialog = ChangePasswordDialog(User.current_user, parent=self)
        change_password_dialog.exec_()
        if change_password_dialog.result() == QtWidgets.QDialog.Accepted:
            self.status_bar.showMessage("Password changed successfully")

    def open_user_editor(self):
        user_editor = UserEditor(parent=self)
        user_editor.exec_()
        if user_editor.result() == QtWidgets.QDialog.Accepted:
            self.status_bar.showMessage("User edited successfully")

    def open_customer_name_converter(self):
        customer_name_converter = CustomerNameConverter(self)
        customer_name_converter.exec()
        self.refresh_so_search_customer_combo_box()

    def reset_widgets(self):
        """Clears and resets all widgets."""
        self.sales_order_table.setRowCount(0)

    def create_widgets(self):
        """Create the widgets of the main window."""
        self.main_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.main_widget)

        self.tab_widget = QtWidgets.QTabWidget()

        self.sales_orders_tab = QtWidgets.QWidget()
        self.tab_widget.addTab(self.sales_orders_tab, "Sales Orders")

        self.so_search_number_label = QtWidgets.QLabel("Number:")
        self.so_search_number_edit = QtWidgets.QLineEdit()

        self.so_search_status_label = QtWidgets.QLabel("Status:")
        self.so_search_status_combo_box = QtWidgets.QComboBox()
        self.so_search_status_combo_box.addItem("")
        items = (
            self.session.query(SalesOrderStatus).order_by(SalesOrderStatus.id).all()
        )  # type: list[SalesOrderStatus]
        for item in items:
            self.so_search_status_combo_box.addItem(item.name, item)

        self.so_search_customer_label = QtWidgets.QLabel("Customer:")
        self.so_search_customer_combo_box = QtWidgets.QComboBox()
        self.refresh_so_search_customer_combo_box()

        self.so_search_include_fully_cut_check_box = QtWidgets.QCheckBox(
            "Show fully cut SOs"
        )
        self.so_search_include_fully_cut_check_box.setChecked(False)

        self.so_search_button = QtWidgets.QPushButton("Search")

        self.sales_order_table = CustomQTableWidget()
        self.sales_order_table.customContextMenuRequested.connect(
            self.on_sales_order_table_custom_context_menu_requested
        )
        self.sales_order_table.setSelectionMode(
            QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection
        )
        self.sales_order_table.set_table_headers(self.SALES_ORDER_TABLE_HEADERS)

        self.cut_jobs_tab = QtWidgets.QWidget()
        self.tab_widget.addTab(self.cut_jobs_tab, "Cut Jobs")

        self.cut_job_table = CustomQTableWidget()
        self.cut_job_table.setSelectionMode(
            QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection
        )
        self.cut_job_table.set_table_headers(self.CUT_JOB_TABLE_HEADERS)

    def on_sales_order_table_custom_context_menu_requested(self, pos):
        """Called when the user right-clicks on the sales order table."""
        self.sales_order_table.show_row_context_menu(pos)
        return
        # TODO: Implement
        menu = QtWidgets.QMenu()
        menu.addAction("Create Cut Job", self.create_cut_job_from_selected_sales_orders)
        menu.exec_(self.sales_order_table.viewport().mapToGlobal(pos))

    def refresh_so_search_customer_combo_box(self):
        self.so_search_customer_combo_box.clear()

        self.so_search_customer_combo_box.addItem("")
        items = (
            self.session.query(Customer).order_by(Customer.id).all()
        )  # type: list[Customer]
        for item in items:
            self.so_search_customer_combo_box.addItem(item.name_converted, item)

    def create_layout(self):
        """Create the layout of the main window."""
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_widget.setLayout(self.main_layout)

        self.main_layout.addWidget(self.tab_widget)

        v_layout = QtWidgets.QVBoxLayout()
        form_layout = QtWidgets.QFormLayout()

        form_layout.addRow(self.so_search_number_label, self.so_search_number_edit)
        form_layout.addRow(
            self.so_search_customer_label, self.so_search_customer_combo_box
        )
        form_layout.addRow(self.so_search_status_label, self.so_search_status_combo_box)

        v_layout.addLayout(form_layout)
        v_layout.addWidget(self.so_search_include_fully_cut_check_box)
        v_layout.addWidget(self.so_search_button)
        v_layout.addWidget(self.sales_order_table)
        self.sales_orders_tab.setLayout(v_layout)

        v_layout = QtWidgets.QVBoxLayout()
        v_layout.addWidget(self.cut_job_table)
        self.cut_jobs_tab.setLayout(v_layout)

    def create_connections(self):
        """Create the connections of the main window."""
        pass

    def create_actions(self):
        """Create the actions of the main window."""

        # File Menu
        self.action_exit = QtWidgets.QAction("E&xit", self)
        self.action_exit.setShortcut("Ctrl+Q")
        self.action_exit.setStatusTip("Exit the application")
        self.action_exit.triggered.connect(self.close)

        self.action_login = QtWidgets.QAction("&Login", self)
        self.action_login.setShortcut("Ctrl+L")
        self.action_login.setStatusTip("Login to the application")
        self.action_login.triggered.connect(self.login)

        self.action_logout = QtWidgets.QAction("&Logout", self)
        self.action_logout.setShortcut("Ctrl+O")
        self.action_logout.setStatusTip("Logout from the application")
        self.action_logout.triggered.connect(self.logout)

        self.action_open_customer_name_converter = QtWidgets.QAction(
            "&Customer Name Converter", self
        )
        self.action_open_customer_name_converter.setShortcut("Ctrl+Shift+C")
        self.action_open_customer_name_converter.setStatusTip(
            "Open the customer name converter"
        )
        self.action_open_customer_name_converter.triggered.connect(
            self.open_customer_name_converter
        )

        self.action_refresh_fb_data = QtWidgets.QAction("&Refresh Fishbowl Data", self)
        self.action_refresh_fb_data.setStatusTip("Refresh Fishbowl data")
        self.action_refresh_fb_data.triggered.connect(self.refresh_fb_data)

        self.action_refresh_so_data = QtWidgets.QAction(
            "&Refresh Sales Order Data", self
        )
        self.action_refresh_so_data.setShortcut("Ctrl+R")
        self.action_refresh_so_data.setStatusTip("Refresh the sales order data")
        self.action_refresh_so_data.triggered.connect(lambda: self.load_so_table_data())

        self.action_refresh_cut_job_data = QtWidgets.QAction(
            "&Refresh Cut Job Data", self
        )
        self.action_refresh_cut_job_data.setShortcut("Ctrl+Shift+R")
        self.action_refresh_cut_job_data.setStatusTip("Refresh the cut job data")
        self.action_refresh_cut_job_data.triggered.connect(self.load_cut_job_table_data)

        # User Menu
        self.action_change_password = QtWidgets.QAction("&Change Password", self)
        self.action_change_password.setShortcut("Ctrl+Shift+P")
        self.action_change_password.setStatusTip("Change the password")
        self.action_change_password.triggered.connect(self.change_password)

        self.action_open_user_editor = QtWidgets.QAction("&User Editor", self)
        self.action_open_user_editor.setShortcut("Ctrl+Shift+U")
        self.action_open_user_editor.setStatusTip("Open the user editor")
        self.action_open_user_editor.triggered.connect(self.open_user_editor)

        self.so_search_button.clicked.connect(self.on_so_search_button_clicked)

    def refresh_fb_data(self):
        """Refresh the fishbowl data."""
        self.status_bar.showMessage("Refreshing Fishbowl data...")
        with Session() as session:
            fb_open_sales_orders = fb_models.FBSalesOrder.find_all_open(fishbowl_orm)
            utilities.create_sales_orders_from_fishbowl_data(
                session, fishbowl_orm, fb_open_sales_orders
            )

        self.status_bar.showMessage("Fishbowl data refreshed.")
        self.action_refresh_so_data.trigger()

    def create_menus(self):
        """Create the menus of the main window."""
        self.menubar = self.menuBar()

        self.file_menu = self.menubar.addMenu("File")
        self.file_menu.addAction(self.action_login)
        self.file_menu.addAction(self.action_logout)
        self.file_menu.addSeparator()

        self.file_menu.addAction(self.action_open_customer_name_converter)
        self.file_menu.addAction(self.action_refresh_fb_data)
        self.file_menu.addAction(self.action_refresh_so_data)
        self.file_menu.addAction(self.action_refresh_cut_job_data)
        self.file_menu.addSeparator()

        self.file_menu.addAction(self.action_exit)

        self.action_logout.setEnabled(False)

        self.user_menu = self.menubar.addMenu("User")
        self.user_menu.addAction(self.action_change_password)
        self.user_menu.addAction(self.action_open_user_editor)

    # def create_toolbars(self):
    #     """Create the toolbars of the main window."""
    #     self.tool_bar = self.addToolBar("Tools")
    #     self.refresh_so_data_action = self.tool_bar.addAction("Refresh Sales Order Data", self.load_table_data)

    def create_status_bar(self):
        """Create the status bar of the main window."""
        self.status_bar = QtWidgets.QStatusBar()
        self.setStatusBar(self.status_bar)

    def set_default_values(self):
        """Set the default values of the main window."""
        pass

    def on_so_search_button_clicked(self):
        """Handle the search button being clicked."""
        search_criteria = SalesOrderSearchCriteria(
            number=self.so_search_number_edit.text(),
            customer_name=self.so_search_customer_combo_box.currentText(),
            status=self.so_search_status_combo_box.currentText(),
            show_fully_cut=self.so_search_include_fully_cut_check_box.isChecked(),
        )
        self.load_so_table_data(search_criteria)

    def load_so_table_data(self, search_criteria: SalesOrderSearchCriteria = None):
        """Load the table data."""
        with Session() as session:
            query = (
                session.query(SalesOrder)
                .filter(
                    SalesOrder.status_id
                    <= SalesOrderStatus.find_by_name("In Progress").id
                )
                .order_by(SalesOrder.number)
            )

            if search_criteria is not None:
                if len(search_criteria.number) > 0:
                    query = query.filter(
                        SalesOrder.number.contains(search_criteria.number)
                    )

                if search_criteria.customer_name != "":
                    query = query.join(Customer).filter(
                        Customer.name.contains(search_criteria.customer_name)
                    )

                if search_criteria.status != "":
                    query = query.filter(
                        SalesOrder.status_id
                        == SalesOrderStatus.find_by_name(search_criteria.status).id
                    )

            open_orders = query.all()  # type: list[SalesOrder]
            self.sales_order_table.setRowCount(0)

            for so in open_orders:
                for item in so.items:
                    if item.is_cut and (
                        search_criteria and not search_criteria.show_fully_cut
                    ):
                        continue

                    self.sales_order_table.add_row(
                        [
                            so.number,
                            so.customer.name_converted,
                            so.date_scheduled_fulfillment.strftime("%m/%d/%Y"),
                            so.status.name,
                            item.part.number,
                            item.part.description,
                            str(round(item.quantity_ordered, 0)),
                            str(round(item.quantity_fulfilled, 0)),
                            str(round(item.quantity_left_to_fulfill, 0)),
                            item.fully_cut,
                            item.line_number,
                            item.status.name,
                        ]
                    )

    def load_cut_job_table_data(self):
        """Load the table data."""
        with Session() as session:
            cut_job_status = CutJobStatus.find_by_name("In Progress")
            cut_jobs = (
                session.query(CutJob)
                .filter(CutJob.status_id <= cut_job_status.id)
                .order_by(CutJob.number)
                .all()
            )  # type: list[CutJob]
            self.cut_job_table.setRowCount(0)

            for cut_job in cut_jobs:
                for item in cut_job.items:
                    if item.sales_order_items:
                        for _ in item.sales_order_items:
                            self.cut_job_table.add_row(
                                [
                                    cut_job.number,
                                    cut_job.status.name,
                                    item.part.number,
                                    item.part.description,
                                    str(round(item.quantity_to_cut, 0)),
                                    str(round(item.quantity_cut, 0)),
                                    str(round(item.left_to_cut, 0)),
                                    item.status.name,
                                ]
                            )
                        continue

                    self.cut_job_table.add_row(
                        [
                            cut_job.number,
                            cut_job.status.name,
                            item.part.number,
                            item.part.description,
                            str(round(item.quantity_to_cut, 0)),
                            str(round(item.quantity_cut, 0)),
                            str(round(item.left_to_cut, 0)),
                            item.status.name,
                        ]
                    )


def create_test_data():
    """Create the test cut job data."""
    frontend_logger.info("Creating test data...")

    with Session() as session:
        frontend_logger.warning("Deleting all Sales Orders...")
        session.query(SalesOrderItem).delete()
        session.query(SalesOrder).delete()

        frontend_logger.warning("Deleting all Cut Jobs...")
        session.query(CutJobItem).delete()
        session.query(CutJob).delete()
        session.commit()

        frontend_logger.info("Creating sales order data...")
        fb_open_sales_orders = fb_models.FBSalesOrder.find_all_open(fishbowl_orm)
        utilities.create_sales_orders_from_fishbowl_data(
            session, fishbowl_orm, fb_open_sales_orders
        )

        frontend_logger.info("Creating cut job data...")

        open_sales_orders = (
            session.query(SalesOrder)
            .filter(
                SalesOrder.status_id <= SalesOrderStatus.find_by_name("In Progress").id
            )
            .order_by(SalesOrder.number)
            .all()
        )  # type: list[SalesOrder]
        cut_job_entered_status = CutJobStatus.find_by_name("Entered")
        cut_job_item_entered_status = CutJobItemStatus.find_by_name("Entered")
        wire_cutter = WireCutter.find_by_name("Test Cutter")
        if not wire_cutter:
            frontend_logger.info("Creating wire cutter...")
            wire_cutter = WireCutter(
                name="Test Cutter",
                description="Test Cutter",
                max_wire_size_id=WireSize.find_by_name("10 AWG").id,
            )
            session.add(wire_cutter)
            session.commit()

        so_items = {}  # type: dict[Part, list[SalesOrderItem]]
        for so in open_sales_orders:
            for item in so.items:
                if item.part not in so_items:
                    so_items[item.part] = []
                so_items[item.part].append(item)

        for part, items in so_items.items():
            frontend_logger.info(f"Creating cut job for part {part.number}...")
            cut_job = CutJob(
                number=part.number,
                status_id=cut_job_entered_status.id,
                wire_cutter_id=wire_cutter.id,
            )
            session.add(cut_job)
            session.commit()

            frontend_logger.info(f"Adding items to cut job...")
            for item in items:
                cut_job_item = CutJobItem(
                    cut_job_id=cut_job.id,
                    part_id=item.part.id,
                    quantity_to_cut=0,
                    status_id=cut_job_item_entered_status.id,
                )
                session.add(cut_job_item)
                cut_job_item.add_sales_order_item(item)
            session.commit()

    frontend_logger.info("Test data created.")


class Application(QtWidgets.QApplication):
    """The application of the application."""

    def __init__(self, args):
        super().__init__(args)

        self.aboutToQuit.connect(self.close_event)

        self.main_window = MainWindow()
        self.main_window.setMinimumSize(800, 600)
        self.main_window.show()
        self.main_window.action_login.trigger()

    def close_event(self, event=None) -> None:
        """Close the application."""
        if User.current_user is not None:
            User.logout()


def main():
    """The main function of the application."""
    # create_test_data()
    app = Application(sys.argv)
    app.exec_()
    # with Session() as session:
    #     cut_job = session.query(CutJob).filter(CutJob.number == "5001753").first() # type: CutJob
    #     for item in cut_job.items:
    #         qty = item.quantity_to_cut
    #         item.quantity_cut = qty

    #     session.commit()


if __name__ == "__main__":
    main()
