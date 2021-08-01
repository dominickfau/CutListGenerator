import mysql.connector
import sys
import datetime
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QDialog, QApplication, QMessageBox
from mainwindow import Ui_MainWindow
from mysql.connector import errorcode as mysql_errorcode


from settings import load_settings, save_settings
import appdataclasses

SETTINGS_FILE_NAME = "settings.json"
settings = load_settings(SETTINGS_FILE_NAME)

# Exception for when no row is selected
class NoRowSelectedException(Exception):
    def __init__(self, message):
        super().__init__(message)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.fishbowl_connection = None
        self.cutlist_connection = None

        connection_error = False
        try:
            self.connect_to_database()
        except mysql.connector.Error as e:
            connection_error = True
            if e.errno == mysql_errorcode.ER_ACCESS_DENIED_ERROR:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setText("Could notconnect to the database. Please check your settings.")
                msg.setDetailedText(str(e))
                msg.setWindowTitle("Database Error")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec()
                return
    
        self.ui.tableWidget.setHorizontalHeaderLabels(["SO Due Date", "SO Number", "Line Number", "Customer Name", "Product Number", "Description", "Qty Left To Ship", "Qty Cut"])
        self.ui.view_push_button.clicked.connect(self.load_item_data)
        self.ui.save_push_button.clicked.connect(self.save_item_data)
        self.ui.search_push_button.clicked.connect(self.search_item_data)
        self.ui.actionGet_Current_SO_Data_From_Fishbowl.triggered.connect(self.get_current_fishbowl_data)

        if not connection_error:
            self.load_table_data()

    def validate_search_criteria(self, search_so_number, search_part_number):
        """Checkes if the search criteria is valid"""

        if len(search_so_number) == 0 or len(search_part_number) == 0:
            return False
        return True
    
    def search_item_data(self):
        show_finished_parts = self.ui.show_finished_parts_check_box.isChecked()
        search_part_number = self.ui.search_part_number_line_edit.text()
        search_so_number = self.ui.search_so_number_line_edit.text()

        if not self.validate_search_criteria(search_so_number, search_part_number):
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Please enter both SO number and part number to search for.")
            msg.setWindowTitle("Search Error")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()
            return

        # so_number, line_num, product_number
        search_data = (search_so_number, None, search_part_number)
        self.load_table_data(search_criteria=search_data)

    def get_current_fishbowl_data(self):
        rows_inserted, total_fishbowl_rows = self.get_current_so_data_from_fishbowl()

        # show a message box
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(f"{total_fishbowl_rows} rows available to import from Fishbowl.\n{rows_inserted} rows were inserted into the cutlist table.")
        # msg.setInformativeText("{} rows from FishBowl".format(total_fishbowl_rows))
        msg.setWindowTitle("Fishbowl Data")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec()

        self.load_table_data()
    
    def get_current_so_data_from_fishbowl(self):
        fishbowl_cursor = self.get_fishbowl_cursor()
        cut_item_cursor = self.get_cutlist_cursor()

        fishbowl_cursor.execute('''SELECT so.num AS soNum,
                                CASE 
                                    WHEN customer.name = "Brunswick Boat Group, Fort Wayne Operatio" THEN "Brunswick"
                                    WHEN customer.name = "GODFREY MARINE-HURRICANE" THEN "Godfrey"
                                    WHEN customer.name = "MARINE MOORING, INC." THEN "Marine Mooring"
                                    WHEN customer.name = "Bennington Pontoon Boats" THEN "Bennington"
                                    ELSE customer.name
                                END AS customerName,
                                DATE(so.dateFirstShip) AS dueDate,
                                -- DATE_SUB(so.dateFirstShip, INTERVAL 14 DAY) AS cutDate,
                                soitem.soLineItem AS soLineItem,
                                product.num AS productNum,
                                product.description,
                                -- soitem.qtyToFulfill AS qtyToFulfill,
                                (soitem.qtyToFulfill - qtyPicked - qtyFulfilled) AS qtyLeftToCut,
                                productuom.code AS uom

                            FROM so
                            JOIN soitem ON soitem.soId = so.id
                            JOIN customer ON so.customerId = customer.id
                            JOIN product ON soitem.productId = product.id
                            JOIN uom productuom ON product.uomId = productuom.id

                            WHERE soitem.statusId < 50 -- 50 = Finished
                            AND (soitem.qtyToFulfill - qtyPicked - qtyFulfilled) > 0
                            -- AND DATE_SUB(so.dateFirstShip, INTERVAL 14 DAY) < NOW()
                            AND product.num LIKE "50%"
                            AND productuom.code = "ea";
                            ''')

        fishbowl_data = fishbowl_cursor.fetchall()
        # soNum, customerName, dueDate, soLineItem, productNum, description, qtyLeftToCut, uom

        rows_inserted = 0
        total_fishbowl_rows = len(fishbowl_data)

        for row in fishbowl_data:
            cut_item = appdataclasses.CutItem.find_by_sales_order_number_and_product_number(cut_item_cursor, row["soNum"], row['soLineItem'], row["productNum"])[0]
            
            if cut_item:
                continue
            
            appdataclasses.CutItem.insert_into_database_from_fishbowl_data_row(row, cut_item_cursor)
            
            self.cutlist_connection.commit()
            rows_inserted += 1
        
        fishbowl_cursor.close()
        cut_item_cursor.close()
        return rows_inserted, total_fishbowl_rows

    def convert_str_to_time(self, time_str):
        return datetime.datetime.strptime(time_str, "%H:%M:%S").time()
    
    def get_selected_row_data(self):
        row_index = self.ui.tableWidget.currentRow()
        if row_index == -1:
            raise NoRowSelectedException("No row selected.")

        row_count = self.ui.tableWidget.rowCount()
        for x in range(row_count):
            if x != row_index:
                continue
            
            so_num = self.ui.tableWidget.item(x, 1).text()
            line_num = self.ui.tableWidget.item(x, 2).text()
            product_num = self.ui.tableWidget.item(x, 4).text()
            return so_num, line_num, product_num
    
    def get_current_edit_row(self):
        product_num = self.ui.selected_part_number_line_edit.text()
        line_num = self.ui.selected_so_number_line_edit.text()
        so_num = self.ui.selected_so_line_number_line_edit.text()

        if len(product_num) == 0 or len(so_num) == 0 or len(line_num) == 0:
            raise NoRowSelectedException("Please select a row to edit.")
        
        return so_num, line_num, product_num
    
    def get_item_data(self):
        added_to_cut_list_value = self.ui.added_to_cut_list_check_box.isChecked()
        qty_cut_value = self.ui.qty_cut_spin_box.value()
        assigned_cutter_value = self.ui.cutter_combo_box.currentText()

        # Cut data
        is_cut_value = self.ui.is_cut_check_box.isChecked()
        cut_start_date_value = self.ui.cut_start_date_edit.date()
        cut_start_time_value = self.ui.cut_start_time_edit.text()
        cut_start_date_time_value = datetime.datetime.strptime(cut_start_date_value.toString("yyyy-MM-dd") + " " + cut_start_time_value, "%Y-%m-%d %H:%M:%S")
        cut_end_date_value = self.ui.cut_end_date_edit.date()
        cut_end_time_value = self.ui.cut_end_time_edit.text()
        cut_end_date_time_value = datetime.datetime.strptime(cut_end_date_value.toString("yyyy-MM-dd") + " " + cut_end_time_value, "%Y-%m-%d %H:%M:%S")

        # Termination data
        is_terminated_value = self.ui.is_terminated_check_box.isChecked()
        termination_start_date_value = self.ui.termination_start_date_edit.date()
        termination_start_time_value = self.ui.termination_start_time_edit.text()
        termination_start_date_time_value = datetime.datetime.strptime(termination_start_date_value.toString("yyyy-MM-dd") + " " + termination_start_time_value, "%Y-%m-%d %H:%M:%S")
        termination_end_date_value = self.ui.termination_end_date_edit.date()
        termination_end_time_value = self.ui.termination_end_time_edit.text()
        termination_end_date_time_value = datetime.datetime.strptime(termination_end_date_value.toString("yyyy-MM-dd") + " " + termination_end_time_value, "%Y-%m-%d %H:%M:%S")

        # Splice data
        is_spliced_value = self.ui.is_spliced_check_box.isChecked()
        splice_start_date_value = self.ui.splice_start_date_edit.date()
        splice_start_time_value = self.ui.splice_start_time_edit.text()
        splice_start_date_time_value = datetime.datetime.strptime(splice_start_date_value.toString("yyyy-MM-dd") + " " + splice_start_time_value, "%Y-%m-%d %H:%M:%S")
        splice_end_date_value = self.ui.splice_end_date_edit.date()
        splice_end_time_value = self.ui.splice_end_time_edit.text()
        splice_end_date_time_value = datetime.datetime.strptime(splice_end_date_value.toString("yyyy-MM-dd") + " " + splice_end_time_value, "%Y-%m-%d %H:%M:%S")

        # Other data
        is_ready_for_build_value = self.ui.is_ready_for_build_check_box.isChecked()

        return added_to_cut_list_value, qty_cut_value, assigned_cutter_value, \
            is_cut_value, cut_start_date_time_value, cut_end_date_time_value, \
            is_terminated_value, termination_start_date_time_value, termination_end_date_time_value, \
            is_spliced_value, splice_start_date_time_value, splice_end_date_time_value, \
            is_ready_for_build_value
        
    def save_item_data(self):
        try:
            so_num, line_num, product_num = self.get_current_edit_row()
        except NoRowSelectedException as e:
            QtWidgets.QMessageBox.warning(self, "Error", str(e))
            return
        
        cursor = self.get_cutlist_cursor()
        cut_item = appdataclasses.CutItem.find_by_sales_order_number_and_product_number(cursor, so_num, line_num, product_num)[0]


        if cut_item is None:
            return
        
        form_data = self.get_item_data()

        cut_item.on_cut_list = form_data[0]

        if cut_item.on_cut_list:
            cut_item.quantity_cut = form_data[1]
            cut_item.assigned_cutter = form_data[2]

        cut_item.is_cut = form_data[3]
        if cut_item.is_cut:
            cut_item.date_cut_start = form_data[4]
            cut_item.date_cut_end = form_data[5]
        
        cut_item.is_terminated = form_data[6]
        if cut_item.is_terminated:
            cut_item.date_termination_start = form_data[7]
            cut_item.date_termination_end = form_data[8]

        cut_item.is_spliced = form_data[9]
        if cut_item.is_spliced:
            cut_item.date_splice_start = form_data[10]
            cut_item.date_splice_end = form_data[11]

        cut_item.is_ready_for_build = form_data[12]

        appdataclasses.CutItem.update_database(cut_item, cursor)
        self.cutlist_connection.commit()
        self.load_table_data()
        return

    def clear_table_data(self):
        self.ui.tableWidget.setRowCount(0)

    def load_item_data(self):
        try:
            so_num, line_num, product_num = self.get_selected_row_data()
        except NoRowSelectedException as e:
            QtWidgets.QMessageBox.warning(self, "Error", str(e))
            return

        self.ui.selected_so_line_number_line_edit.setText(so_num)
        self.ui.selected_part_number_line_edit.setText(product_num)
        self.ui.selected_so_number_line_edit.setText(line_num)

        cursor = self.get_cutlist_cursor()
        cut_item = appdataclasses.CutItem.find_by_sales_order_number_and_product_number(cursor, so_num, line_num, product_num)[0]

        self.ui.added_to_cut_list_check_box.setChecked(cut_item.on_cut_list)
        self.ui.qty_cut_spin_box.setValue(0)

        if self.ui.added_to_cut_list_check_box.isChecked():
            self.ui.qty_cut_spin_box.setValue(int(cut_item.quantity_cut))
        if cut_item.assigned_cutter is not None:
            self.ui.cutter_combo_box.setCurrentText(cut_item.assigned_cutter)
        
        # Loading cut data
        self.ui.is_cut_check_box.setChecked(cut_item.is_cut)

        if cut_item.date_cut_start is not None:
            date = cut_item.date_cut_start.date()
        else:
            date = datetime.datetime.now().date()
        self.ui.cut_start_date_edit.setDate(date)

        if cut_item.date_cut_end is not None:
            date = cut_item.date_cut_end.date()
        else:
            date = datetime.datetime.now().date()
        self.ui.cut_end_date_edit.setDate(date)

        # Loading termination data
        self.ui.is_terminated_check_box.setChecked(cut_item.is_terminated)

        if cut_item.date_termination_start is not None:
            date = cut_item.date_termination_start.date()
        else:
            date = datetime.datetime.now().date()
        self.ui.termination_start_date_edit.setDate(date)

        if cut_item.date_termination_end is not None:
            date = cut_item.date_termination_end.date()
        else:
            date = datetime.datetime.now().date()
        self.ui.termination_end_date_edit.setDate(date)

        # Loading Splice data
        self.ui.is_spliced_check_box.setChecked(cut_item.is_spliced)

        if cut_item.date_splice_start is not None:
            date = cut_item.date_splice_start.date()
        else:
            date = datetime.datetime.now().date()
        self.ui.splice_start_date_edit.setDate(date)

        if cut_item.date_splice_end is not None:
            date = cut_item.date_splice_end.date()
        else:
            date = datetime.datetime.now().date()
        self.ui.splice_end_date_edit.setDate(date)

        # Loading Other data
        self.ui.is_ready_for_build_check_box.setChecked(cut_item.is_ready_for_build)

    def load_table_data(self, search_criteria: tuple = None):
        self.clear_table_data()
        cursor = self.get_cutlist_cursor()

        if search_criteria is None:
            data = appdataclasses.CutItem.find_all_unfinished_items(cursor)
        else:
            data = appdataclasses.CutItem.find_by_sales_order_number_and_product_number(cursor, search_criteria[0], search_criteria[1], search_criteria[2])
            if data is None:
                return

        self.ui.tableWidget.setRowCount(len(data))

        for row_num, row in enumerate(data):
            self.ui.tableWidget.setItem(row_num, 0, QtWidgets.QTableWidgetItem(str(row.due_date.date())))
            self.ui.tableWidget.setItem(row_num, 1, QtWidgets.QTableWidgetItem(str(row.sales_order_number)))
            self.ui.tableWidget.setItem(row_num, 2, QtWidgets.QTableWidgetItem(str(row.line_number)))
            self.ui.tableWidget.setItem(row_num, 3, QtWidgets.QTableWidgetItem(str(row.customer_name)))
            self.ui.tableWidget.setItem(row_num, 4, QtWidgets.QTableWidgetItem(str(row.product_number)))
            self.ui.tableWidget.setItem(row_num, 5, QtWidgets.QTableWidgetItem(str(row.product_description)))
            self.ui.tableWidget.setItem(row_num, 6, QtWidgets.QTableWidgetItem(str(row.quantity_requseted)))
            self.ui.tableWidget.setItem(row_num, 7, QtWidgets.QTableWidgetItem(str(row.quantity_cut)))

    def connect_to_database(self):
        self.fishbowl_connection = mysql.connector.connect(**settings["Fishbowl_MySQL"]["auth"])
        self.cutlist_connection = mysql.connector.connect(**settings["CutList_MySQL"]["auth"])

    def get_fishbowl_cursor(self):
        if self.fishbowl_connection is None:
            self.connect_to_database()
        return self.fishbowl_connection.cursor(dictionary=True)
    
    def get_cutlist_cursor(self):
        if self.cutlist_connection is None:
            self.connect_to_database()
        return self.cutlist_connection.cursor(dictionary=True)


def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    app.exec_()
    try:
        main_window.fishbowl_connection.close()
        main_window.cutlist_connection.close()
    except Exception:
        pass
    
    exit()


if __name__ == "__main__":
    main()