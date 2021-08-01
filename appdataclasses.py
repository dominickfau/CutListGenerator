import datetime
from dataclasses import dataclass
from typing import Optional, List
import json
from json import JSONEncoder

class DatabaseEncoder(JSONEncoder):
        def default(self, obj):
            if isinstance(obj, datetime.datetime):
                return obj.strftime("%Y-%m-%d %H:%M:%S")
            else:
                return obj.__dict__


@dataclass
class WireCutter:
    name: str
    max_wire_gauge_awg: int


@dataclass
class CutItem:
    customer_name: str
    sales_order_number: str
    due_date: datetime.datetime
    product_number: str
    product_description: str
    product_uom: str
    quantity_requseted: int
    line_number: int
    product_unit_price_dollars: Optional[float] = None
    assigned_cutter: Optional[WireCutter] = None
    on_cut_list: bool = False
    quantity_cut: Optional[int] = None
    date_cut_start: Optional[datetime.datetime] = None
    date_cut_end: Optional[datetime.datetime] = None
    date_termination_start: Optional[datetime.datetime] = None
    date_termination_end: Optional[datetime.datetime] = None
    date_splice_start: Optional[datetime.datetime] = None
    date_splice_end: Optional[datetime.datetime] = None
    is_cut: bool = False
    is_spliced: bool = False
    is_terminated: bool = False
    is_ready_for_build: bool = False
    kit_flag: bool = False
    parent_kit_part_num: Optional[str] = None
    id: int = 0
    
    @classmethod
    def from_database_row(cls, row):
        cut_item = CutItem(customer_name = row['customerName'],
                                sales_order_number = row['soNum'],
                                due_date = row['dueDate'],
                                product_number = row['productNum'],
                                product_description = row['description'],
                                product_uom = row['uom'],
                                quantity_requseted = row['qtyLeftToCut'],
                                line_number = row['soLineItem'],
                                assigned_cutter = row['assignedCutter'],
                                on_cut_list = row['addedToCutListFlag'],
                                quantity_cut = row['qtyCut'],
                                date_cut_start = row['dateCutStart'],
                                date_cut_end = row['dateCutEnd'],
                                date_termination_start = row['dateTerminationStart'],
                                date_termination_end = row['dateTerminationEnd'],
                                date_splice_start = row['dateSpliceStart'],
                                date_splice_end = row['dateSpliceEnd'],
                                is_cut = row['cutFlag'],
                                is_spliced = row['splicedFlag'],
                                is_terminated = row['terminatedFlag'],
                                is_ready_for_build = row['readyForBuild'],
                                kit_flag = row['kitFlag'],
                                parent_kit_part_num = row['parentKitPartNum'],
                                id = row['id']
                                )
        return cut_item
    
    @classmethod
    def find_all_unfinished_items(cls, cursor):
        cursor.execute("SELECT * FROM cutlist WHERE readyForBuild = 0 ORDER BY dueDate")
        data = cursor.fetchall()
        
        if not data:
            return None

        cut_items = []
        for row in data:
            cut_items.append(cls.from_database_row(row))
        
        return cut_items
    
    @classmethod
    def find_by_sales_order_number_and_product_number(cls, cursor, so_number, line_num, product_number):
        """Returns a cut list item that matches the given sales order number
            and product number and sale order line number."""

        if line_num is None:
            sql = "SELECT * FROM cutlist WHERE soNum = %s AND productNum = %s"
            cursor.execute(sql, (so_number, product_number))
        else:
            sql = "SELECT * FROM cutlist WHERE soNum = %s AND productNum = %s AND soLineItem = %s"
            cursor.execute(sql, (so_number, product_number, line_num))
        data = cursor.fetchall()
        
        if not data:
            return None

        cut_items = []
        for row in data:
            cut_items.append(cls.from_database_row(row))
        
        return cut_items
    
    @staticmethod
    def update_database(cut_item, cursor):
        sql = """UPDATE cutlist SET addedToCutListFlag = %s, assignedCutter = %s, customerName = %s,
                                    cutFlag = %s, dateCutEnd = %s, dateCutStart = %s, dateSpliceEnd = %s,
                                    dateSpliceStart = %s, dateTerminationEnd = %s, dateTerminationStart = %s,
                                    description = %s, dueDate = %s, kitFlag = %s, parentKitPartNum = %s, productNum = %s,
                                    qtyCut = %s, qtyLeftToCut = %s, soLineItem = %s, soNum = %s, splicedFlag = %s, terminatedFlag = %s,
                                    uom = %s, readyForBuild = %s
                    WHERE id = %s"""
        
        cursor.execute(sql, (cut_item.on_cut_list,
                             cut_item.assigned_cutter,
                             cut_item.customer_name,
                             cut_item.is_cut,
                             cut_item.date_cut_end,
                             cut_item.date_cut_start,
                             cut_item.date_splice_end,
                             cut_item.date_splice_start,
                             cut_item.date_termination_end,
                             cut_item.date_termination_start,
                             cut_item.product_description,
                             cut_item.due_date,
                             cut_item.kit_flag,
                             cut_item.parent_kit_part_num,
                             cut_item.product_number,
                             cut_item.quantity_cut,
                             cut_item.quantity_requseted,
                             cut_item.line_number,
                             cut_item.sales_order_number,
                             cut_item.is_spliced,
                             cut_item.is_terminated,
                             cut_item.product_uom,
                             cut_item.is_ready_for_build,
                             cut_item.id
                            ))
    
    @staticmethod
    def insert_into_database_from_cut_item(cut_item, cursor):
        sql = """INSERT INTO cutlist (addedToCutListFlag, assignedCutter, customerName,
                                        cutFlag, dateCutEnd, dateCutStart, dateSpliceEnd,
                                        dateSpliceStart, dateTerminationEnd, dateTerminationStart,
                                        description, dueDate, kitFlag, parentKitPartNum,
                                        productNum, qtyCut, qtyLeftToCut, soLineItem, soNum,
                                        splicedFlag, terminatedFlag, uom, readyForBuild)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

        cursor.execute(sql, (cut_item.on_cut_list,
                             cut_item.assigned_cutter,
                             cut_item.customer_name,
                             cut_item.is_cut,
                             cut_item.date_cut_end,
                             cut_item.date_cut_start,
                             cut_item.date_splice_end,
                             cut_item.date_splice_start,
                             cut_item.date_termination_end,
                             cut_item.date_termination_start,
                             cut_item.product_description,
                             cut_item.due_date,
                             cut_item.kit_flag,
                             cut_item.parent_kit_part_num,
                             cut_item.product_number,
                             cut_item.quantity_cut,
                             cut_item.quantity_requseted,
                             cut_item.line_number,
                             cut_item.sales_order_number,
                             cut_item.is_spliced,
                             cut_item.is_terminated,
                             cut_item.product_uom,
                             cut_item.is_ready_for_build
                            ))
        return cursor.lastrowid
    
    @staticmethod
    def insert_into_database_from_fishbowl_data_row(row, cursor):
        cursor.execute("""INSERT INTO cutlist (soNum, customerName, dueDate, soLineItem, productNum, description, qtyLeftToCut, uom)
                      VALUES (%(soNum)s, %(customerName)s, %(dueDate)s, %(soLineItem)s, %(productNum)s, %(description)s, %(qtyLeftToCut)s, %(uom)s)""",
                      row)
        return cursor.lastrowid


# @dataclass
# class CutList:
#     cut_list_items: List[CutItem]

#     @classmethod
#     def load_all_from_database(cls, cursor):
#         cursor.execute("SELECT * FROM cutlist")
        
#         data = cursor.fetchall()
#         if not data:
#             return None

#         cut_items = []
#         for row in data:
#             cut_item = CutItem.from_database_row(row)
#             cut_items.append(cut_item)
        
#         return cls(cut_items)
    
    

#     def save_to_database(self, cursor):
#         """Saves the cut list items to the database."""

#         for cut_list_item in self.cut_list_items:
#             if len(CutList.find_by_sales_order_number_and_product_number(cut_list_item, cursor)) == 0:
#                 CutList.update_database(cut_list_item, cursor)
#             else:
#                 CutList.insert_into_database(cut_list_item, cursor)
    
#     def save_to_file(self, file_path: str):
#         """Saves the cut list items to a file"""

#         with open(file_path, 'w') as f:
#             json.dump(self, f, cls=DatabaseEncoder, indent=4)