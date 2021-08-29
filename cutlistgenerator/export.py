import pandas
import os
from typing import List
from PyQt5.QtWidgets import QMessageBox, QFileDialog

from cutlistgenerator.database.cutlistdatabase import CutListDatabase

def show_not_implemented_message() -> None:
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setWindowTitle("Data Export")
    msg.setText("This export function has not been implemented.")
    msg.exec()

def ask_save_file_dialog(name: str) -> str:
    """Ask user where to save a file. Retruns None if no file is specified."""
    response = QFileDialog.getSaveFileName(
        caption="Save File",
        directory=name,
        filter="Excel (*.xlsx);;CSV (*.csv);;Chrome html (*.html)",
        initialFilter="Excel (*.xlsx)"
    )
    file_path = response[0]
    return file_path if len(file_path) > 0 else None

def ask_open_file(file_path: str) -> None:
    """Ask user if they would like to open the file after exporting finished."""
    response = QMessageBox.question(
        None,
        "Open File",
        "Do you want to open the file?",
        QMessageBox.Yes | QMessageBox.No,
        QMessageBox.Yes
    )
    if response == QMessageBox.Yes:
        os.startfile(file_path)

def save_to_file(file_path: str, dataframe: pandas.DataFrame) -> None:
    """Saves data to the file."""
    if file_path.endswith(".csv"):
        save_to_csv(file_path, dataframe)
    elif file_path.endswith(".xlsx"):
        save_to_excel(file_path, dataframe)
    elif file_path.endswith(".html"):
        save_to_html(file_path, dataframe)

def save_to_csv(file_path: str, dataframe: pandas.DataFrame) -> None:
    """Saves data to the CSV file."""
    with open(file_path, "w", newline="") as file:
        dataframe.to_csv(file, index=False)

def save_to_html(file_path: str, dataframe: pandas.DataFrame) -> None:
    """Saves data to the HTML file."""
    formatters = {
        'Qty Left To Cut': lambda x: str(int(x))
    }

    with open(file_path, "w", newline="") as file:
        dataframe.to_html(file, index=False, escape=True, formatters=formatters, justify="center")

def save_to_excel(file_path: str, dataframe: pandas.DataFrame) -> None:
    """Saves data to the Excel file."""
    with pandas.ExcelWriter(file_path) as writer:
        dataframe.to_excel(writer, sheet_name="Sheet1", index=False)

def create_dataframe(headers: list, data: List[dict]) -> pandas.DataFrame:
    """Creates a Pandas DataFrame from the data."""
    return pandas.DataFrame(data, columns=headers)

def export_cut_job_summary(database_connection: CutListDatabase):
    """Exports a summary of all unfinished cut jobs."""
    cursor = database_connection.get_cursor()

    cursor.execute("""SELECT cut_job.date_created AS "Date Created",
                        product.number AS "Product Number",
                        product.description AS "Description",
                        wire_cutter.name AS "Wire Cutter",
                        TRIM(cut_job.quantity_cut)+0 AS "Qty Cut",
                        DATE_FORMAT(cut_job.date_cut_end, '%c/%e/%Y %l:%i %p') AS "Cutting End Date",
                        DATE_FORMAT(cut_job.date_termination_end, '%c/%e/%Y %l:%i %p') AS "Termination End Date",
                        DATE_FORMAT(cut_job.date_splice_end, '%c/%e/%Y %l:%i %p') AS "Splice End Date",
                        sales_orders.customer_name AS "Customer Name",
                        sales_orders.sales_order_number AS "SO Number",
                        DATE_FORMAT(sales_orders.due_date, '%c/%e/%Y') AS "SO Due Date",
                        TRIM(sales_orders.qty_left_to_ship)+0 AS "Qty Left To Ship"
                    FROM cut_job
                    JOIN product ON cut_job.product_id = product.id
                    JOIN wire_cutter ON cut_job.assigned_wire_cutter_id = wire_cutter.id
                    LEFT JOIN sales_orders ON sales_orders.sales_order_item_id = cut_job.related_sales_order_item_id""")
    
    headers = [description[0] for description in cursor.description]
    data = cursor.fetchall()
    cursor.close()
    file_path = ask_save_file_dialog("Cut List Summary")
    if not file_path:
        return
    dataframe = create_dataframe(headers, data)
    save_to_file(file_path, dataframe)
    ask_open_file(file_path)

def export_cut_jobs_list(database_connection: CutListDatabase):
    """Exports all cut jobs awaiting to be cut."""
    cursor = database_connection.get_cursor()

    cursor.execute("""SELECT DATE_FORMAT(sales_order_item.due_date, '%c/%e/%Y') AS 'Due Date',
                        sales_order.customer_name AS 'Customer Name',
                        product.number AS 'Product Number',
                        product.description AS 'Description',
                        -- product.unit_price_dollars AS 'Unit Price',
                        SUM(TRIM((sales_order_item.qty_to_fulfill - sales_order_item.qty_fulfilled - sales_order_item.qty_picked))+0) AS 'Qty Left To Cut',
                        product.uom AS 'UOM'
                    FROM sales_order
                    JOIN sales_order_item ON sales_order_item.sales_order_id = sales_order.id
                    JOIN product ON sales_order_item.product_id = product.id
                    LEFT JOIN parent_to_child_product ON parent_to_child_product.child_product_id = product.id
                    LEFT JOIN product parent_product ON parent_to_child_product.parent_product_id = parent_product.id
                    WHERE sales_order_item.cut_in_full = 0
                    GROUP BY product.number, WEEK(sales_order_item.due_date)
                    ORDER BY product.number, sales_order_item.due_date""")
    
    headers = [description[0] for description in cursor.description]
    data = cursor.fetchall()
    cursor.close()
    file_path = ask_save_file_dialog("Cut List")
    if not file_path:
        return
    dataframe = create_dataframe(headers, data)
    save_to_file(file_path, dataframe)
    ask_open_file(file_path)

def export_termination_jobs_list(database_connection: CutListDatabase):
    """Exports all cut jobs that are awaiting to be terminated."""
    show_not_implemented_message()
    return

def export_splice_jobs_list(database_connection: CutListDatabase):
    """Exports all cut jobs awaiting to be spliced."""
    show_not_implemented_message()
    return

def export_product_list(database_connection: CutListDatabase):
    """Export all products."""
    show_not_implemented_message()
    return

def export_wire_cutter_list(database_connection: CutListDatabase):
    """Exports all wire cutters along with any assigned options."""
    show_not_implemented_message()
    return

def export_wire_cutter_options_list(database_connection: CutListDatabase):
    """Exports all options that can be assigned to wire cutters."""
    show_not_implemented_message()
    return