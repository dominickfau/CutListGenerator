import json
import mysql.connector

import querys

SETTINGS_FILE_NAME = "settings.json"

def get_current_so_data_from_fishbowl(cursor):
    cursor.execute(querys.CURRENT_FISHBOWL_SO_DATA)

    data = cursor.fetchall()
    return data

def find_cut_list_data(cursor, row):
    required_keys = ["soNum", "productNum"]
    if not isinstance(row, dict): raise TypeError("row must be of type dict")

    missing_keys = []
    for key in required_keys:
        if key not in row:
            missing_keys.append(key)

    if len(missing_keys) > 0: raise KeyError(f"Missing required key(s): {missing_keys}")
    
    cursor.execute("SELECT * FROM fishbowlsodata WHERE soNum = %(soNum)s AND productNum = %(productNum)s", row)
    data = cursor.fetchall()
    return data

def read_settings_file(file_path):
    with open(file_path, "r") as f:
        settings = json.loads(f.read())

    return settings

def insert_cut_list_data(cursor, row):
    cursor.execute("""INSERT INTO fishbowlsodata (soNum, customerName, dueDate, soLineItem, productNum, description, qtyLeftToCut, uom)
                      VALUES (%(soNum)s, %(customerName)s, %(dueDate)s, %(soLineItem)s, %(productNum)s, %(description)s, %(qtyLeftToCut)s, %(uom)s)""",
                      row)


settings = read_settings_file(SETTINGS_FILE_NAME)
fishbowl_connection = mysql.connector.connect(**settings["Fishbowl_MySQL"]["auth"])
cutlist_connection = mysql.connector.connect(**settings["CutList_MySQL"]["auth"])

fishbowl_cursor = fishbowl_connection.cursor(dictionary=True)
cutlist_cursor = cutlist_connection.cursor(dictionary=True)


fishbowl_data = get_current_so_data_from_fishbowl(fishbowl_cursor)

rows_inserted = 0
for row in fishbowl_data:
    cutlist_data = find_cut_list_data(cutlist_cursor, row)
    
    if cutlist_data:
        continue
    
    insert_cut_list_data(cutlist_cursor, row)
    
    cutlist_connection.commit()
    rows_inserted += 1


fishbowl_connection.close()
cutlist_connection.close()

print(f"{len(fishbowl_data)} rows from open SO's.")
print(f"{rows_inserted} rows inserted.")
