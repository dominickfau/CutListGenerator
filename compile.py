import subprocess
import os
from typing import List

CURRENT_DIR = os.path.abspath(os.getcwd())

print("Starting...")
commands = {
    "cutjobdialog_ui": ["pyuic5", "./cutlistgenerator/ui/cutjobdialog_ui.ui", "-o", "./cutlistgenerator/ui/cutjobdialog_ui.py"],
    "cutjobsearchdialog_ui": ["pyuic5", "./cutlistgenerator/ui/cutjobsearchdialog_ui.ui", "-o", "./cutlistgenerator/ui/cutjobsearchdialog_ui.py"],
    "mainwindow_ui": ["pyuic5", "./cutlistgenerator/ui/mainwindow_ui.ui", "-o", "./cutlistgenerator/ui/mainwindow_ui.py"],
    "productdialog_ui": ["pyuic5", "./cutlistgenerator/ui/productdialog_ui.ui", "-o", "./cutlistgenerator/ui/productdialog_ui.py"],
    "wirecutterdialog_ui": ["pyuic5", "./cutlistgenerator/ui/wirecutterdialog_ui.ui", "-o", "./cutlistgenerator/ui/wirecutterdialog_ui.py"],
    "wirecuttersearchdialog_ui": ["pyuic5", "./cutlistgenerator/ui/wirecuttersearchdialog_ui.ui", "-o", "./cutlistgenerator/ui/wirecuttersearchdialog_ui.py"],
    "helpdialog_ui": ["pyuic5", "./cutlistgenerator/ui/helpdialog_ui.ui", "-o", "./cutlistgenerator/ui/helpdialog_ui.py"]
}

def execute_command(command: List[str]):
    subprocess.run(command)

def create_executable():
    print("Creating executable...")
    command = []


for key in commands:
    command = commands[key]
    print(f"Running {key}")
    execute_command(command)



"""
pyinstaller
--noconfirm
--onedir
--console
--add-data
"C:/Users/Nick Gamming/Documents/Python/Cut_List/settings.json;."
--add-data
"C:/Users/Nick Gamming/Documents/Python/Cut_List/Files For New Release/SCHEMA_CREATE_cutlistgenerator.sql;sql/" 
"C:/Users/Nick Gamming/Documents/Python/Cut_List/Cut_List_Generator.py"
"""

print("Finished")