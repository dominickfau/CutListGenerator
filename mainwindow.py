# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(972, 599)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.selected_part_number_label = QtWidgets.QLabel(self.centralwidget)
        self.selected_part_number_label.setObjectName("selected_part_number_label")
        self.horizontalLayout_8.addWidget(self.selected_part_number_label)
        self.selected_part_number_line_edit = QtWidgets.QLineEdit(self.centralwidget)
        self.selected_part_number_line_edit.setReadOnly(True)
        self.selected_part_number_line_edit.setObjectName("selected_part_number_line_edit")
        self.horizontalLayout_8.addWidget(self.selected_part_number_line_edit)
        self.selected_so_number_label = QtWidgets.QLabel(self.centralwidget)
        self.selected_so_number_label.setObjectName("selected_so_number_label")
        self.horizontalLayout_8.addWidget(self.selected_so_number_label)
        self.selected_so_number_line_edit = QtWidgets.QLineEdit(self.centralwidget)
        self.selected_so_number_line_edit.setReadOnly(True)
        self.selected_so_number_line_edit.setObjectName("selected_so_number_line_edit")
        self.horizontalLayout_8.addWidget(self.selected_so_number_line_edit)
        self.selected_so_line_number_label = QtWidgets.QLabel(self.centralwidget)
        self.selected_so_line_number_label.setObjectName("selected_so_line_number_label")
        self.horizontalLayout_8.addWidget(self.selected_so_line_number_label)
        self.selected_so_line_number_line_edit = QtWidgets.QLineEdit(self.centralwidget)
        self.selected_so_line_number_line_edit.setReadOnly(True)
        self.selected_so_line_number_line_edit.setObjectName("selected_so_line_number_line_edit")
        self.horizontalLayout_8.addWidget(self.selected_so_line_number_line_edit)
        self.verticalLayout_7.addLayout(self.horizontalLayout_8)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.added_to_cut_list_check_box = QtWidgets.QCheckBox(self.groupBox)
        self.added_to_cut_list_check_box.setObjectName("added_to_cut_list_check_box")
        self.verticalLayout_2.addWidget(self.added_to_cut_list_check_box)
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.qty_cut_label = QtWidgets.QLabel(self.groupBox)
        self.qty_cut_label.setObjectName("qty_cut_label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.qty_cut_label)
        self.qty_cut_spin_box = QtWidgets.QSpinBox(self.groupBox)
        self.qty_cut_spin_box.setMaximum(10000)
        self.qty_cut_spin_box.setObjectName("qty_cut_spin_box")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.qty_cut_spin_box)
        self.cutter_label = QtWidgets.QLabel(self.groupBox)
        self.cutter_label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.cutter_label.setObjectName("cutter_label")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.cutter_label)
        self.cutter_combo_box = QtWidgets.QComboBox(self.groupBox)
        self.cutter_combo_box.setObjectName("cutter_combo_box")
        self.cutter_combo_box.addItem("")
        self.cutter_combo_box.addItem("")
        self.cutter_combo_box.addItem("")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.cutter_combo_box)
        self.verticalLayout_2.addLayout(self.formLayout)
        self.horizontalLayout.addWidget(self.groupBox)
        self.groupBox_2 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_2.setObjectName("groupBox_2")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.groupBox_2)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.is_cut_check_box = QtWidgets.QCheckBox(self.groupBox_2)
        self.is_cut_check_box.setObjectName("is_cut_check_box")
        self.verticalLayout_3.addWidget(self.is_cut_check_box)
        self.formLayout_3 = QtWidgets.QFormLayout()
        self.formLayout_3.setObjectName("formLayout_3")
        self.cut_start_label = QtWidgets.QLabel(self.groupBox_2)
        self.cut_start_label.setObjectName("cut_start_label")
        self.formLayout_3.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.cut_start_label)
        self.cut_end_label = QtWidgets.QLabel(self.groupBox_2)
        self.cut_end_label.setObjectName("cut_end_label")
        self.formLayout_3.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.cut_end_label)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.cut_start_date_edit = QtWidgets.QDateEdit(self.groupBox_2)
        self.cut_start_date_edit.setObjectName("cut_start_date_edit")
        self.horizontalLayout_2.addWidget(self.cut_start_date_edit)
        self.cut_start_time_edit = QtWidgets.QLineEdit(self.groupBox_2)
        self.cut_start_time_edit.setObjectName("cut_start_time_edit")
        self.horizontalLayout_2.addWidget(self.cut_start_time_edit)
        self.formLayout_3.setLayout(0, QtWidgets.QFormLayout.FieldRole, self.horizontalLayout_2)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.cut_end_date_edit = QtWidgets.QDateEdit(self.groupBox_2)
        self.cut_end_date_edit.setObjectName("cut_end_date_edit")
        self.horizontalLayout_3.addWidget(self.cut_end_date_edit)
        self.cut_end_time_edit = QtWidgets.QLineEdit(self.groupBox_2)
        self.cut_end_time_edit.setObjectName("cut_end_time_edit")
        self.horizontalLayout_3.addWidget(self.cut_end_time_edit)
        self.formLayout_3.setLayout(1, QtWidgets.QFormLayout.FieldRole, self.horizontalLayout_3)
        self.verticalLayout_3.addLayout(self.formLayout_3)
        self.horizontalLayout.addWidget(self.groupBox_2)
        self.groupBox_3 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_3.setObjectName("groupBox_3")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.groupBox_3)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.is_terminated_check_box = QtWidgets.QCheckBox(self.groupBox_3)
        self.is_terminated_check_box.setObjectName("is_terminated_check_box")
        self.verticalLayout_4.addWidget(self.is_terminated_check_box)
        self.formLayout_4 = QtWidgets.QFormLayout()
        self.formLayout_4.setObjectName("formLayout_4")
        self.termination_start_label = QtWidgets.QLabel(self.groupBox_3)
        self.termination_start_label.setObjectName("termination_start_label")
        self.formLayout_4.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.termination_start_label)
        self.termination_end_label = QtWidgets.QLabel(self.groupBox_3)
        self.termination_end_label.setObjectName("termination_end_label")
        self.formLayout_4.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.termination_end_label)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.termination_start_date_edit = QtWidgets.QDateEdit(self.groupBox_3)
        self.termination_start_date_edit.setObjectName("termination_start_date_edit")
        self.horizontalLayout_4.addWidget(self.termination_start_date_edit)
        self.termination_start_time_edit = QtWidgets.QLineEdit(self.groupBox_3)
        self.termination_start_time_edit.setObjectName("termination_start_time_edit")
        self.horizontalLayout_4.addWidget(self.termination_start_time_edit)
        self.formLayout_4.setLayout(0, QtWidgets.QFormLayout.FieldRole, self.horizontalLayout_4)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.termination_end_date_edit = QtWidgets.QDateEdit(self.groupBox_3)
        self.termination_end_date_edit.setObjectName("termination_end_date_edit")
        self.horizontalLayout_5.addWidget(self.termination_end_date_edit)
        self.termination_end_time_edit = QtWidgets.QLineEdit(self.groupBox_3)
        self.termination_end_time_edit.setObjectName("termination_end_time_edit")
        self.horizontalLayout_5.addWidget(self.termination_end_time_edit)
        self.formLayout_4.setLayout(1, QtWidgets.QFormLayout.FieldRole, self.horizontalLayout_5)
        self.verticalLayout_4.addLayout(self.formLayout_4)
        self.horizontalLayout.addWidget(self.groupBox_3)
        self.groupBox_4 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_4.setObjectName("groupBox_4")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.groupBox_4)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.is_spliced_check_box = QtWidgets.QCheckBox(self.groupBox_4)
        self.is_spliced_check_box.setObjectName("is_spliced_check_box")
        self.verticalLayout_5.addWidget(self.is_spliced_check_box)
        self.formLayout_5 = QtWidgets.QFormLayout()
        self.formLayout_5.setObjectName("formLayout_5")
        self.splice_start_label = QtWidgets.QLabel(self.groupBox_4)
        self.splice_start_label.setObjectName("splice_start_label")
        self.formLayout_5.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.splice_start_label)
        self.splice_end_label = QtWidgets.QLabel(self.groupBox_4)
        self.splice_end_label.setObjectName("splice_end_label")
        self.formLayout_5.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.splice_end_label)
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.splice_start_date_edit = QtWidgets.QDateEdit(self.groupBox_4)
        self.splice_start_date_edit.setObjectName("splice_start_date_edit")
        self.horizontalLayout_6.addWidget(self.splice_start_date_edit)
        self.splice_start_time_edit = QtWidgets.QLineEdit(self.groupBox_4)
        self.splice_start_time_edit.setObjectName("splice_start_time_edit")
        self.horizontalLayout_6.addWidget(self.splice_start_time_edit)
        self.formLayout_5.setLayout(0, QtWidgets.QFormLayout.FieldRole, self.horizontalLayout_6)
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.splice_end_date_edit = QtWidgets.QDateEdit(self.groupBox_4)
        self.splice_end_date_edit.setObjectName("splice_end_date_edit")
        self.horizontalLayout_7.addWidget(self.splice_end_date_edit)
        self.splice_end_time_edit = QtWidgets.QLineEdit(self.groupBox_4)
        self.splice_end_time_edit.setObjectName("splice_end_time_edit")
        self.horizontalLayout_7.addWidget(self.splice_end_time_edit)
        self.formLayout_5.setLayout(1, QtWidgets.QFormLayout.FieldRole, self.horizontalLayout_7)
        self.verticalLayout_5.addLayout(self.formLayout_5)
        self.horizontalLayout.addWidget(self.groupBox_4)
        self.groupBox_5 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_5.setObjectName("groupBox_5")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.groupBox_5)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.is_ready_for_build_check_box = QtWidgets.QCheckBox(self.groupBox_5)
        self.is_ready_for_build_check_box.setObjectName("is_ready_for_build_check_box")
        self.verticalLayout_6.addWidget(self.is_ready_for_build_check_box)
        self.horizontalLayout.addWidget(self.groupBox_5)
        self.verticalLayout_7.addLayout(self.horizontalLayout)
        self.save_push_button = QtWidgets.QPushButton(self.centralwidget)
        self.save_push_button.setObjectName("save_push_button")
        self.verticalLayout_7.addWidget(self.save_push_button)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.formLayout_2 = QtWidgets.QFormLayout()
        self.formLayout_2.setObjectName("formLayout_2")
        self.so_number_label = QtWidgets.QLabel(self.centralwidget)
        self.so_number_label.setObjectName("so_number_label")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.so_number_label)
        self.search_so_number_line_edit = QtWidgets.QLineEdit(self.centralwidget)
        self.search_so_number_line_edit.setObjectName("search_so_number_line_edit")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.search_so_number_line_edit)
        self.part_number_label = QtWidgets.QLabel(self.centralwidget)
        self.part_number_label.setObjectName("part_number_label")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.part_number_label)
        self.search_part_number_line_edit = QtWidgets.QLineEdit(self.centralwidget)
        self.search_part_number_line_edit.setObjectName("search_part_number_line_edit")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.search_part_number_line_edit)
        self.verticalLayout.addLayout(self.formLayout_2)
        self.show_finished_parts_check_box = QtWidgets.QCheckBox(self.centralwidget)
        self.show_finished_parts_check_box.setObjectName("show_finished_parts_check_box")
        self.verticalLayout.addWidget(self.show_finished_parts_check_box)
        self.search_push_button = QtWidgets.QPushButton(self.centralwidget)
        self.search_push_button.setObjectName("search_push_button")
        self.verticalLayout.addWidget(self.search_push_button)
        self.tableWidget = QtWidgets.QTableWidget(self.centralwidget)
        self.tableWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(7)
        self.tableWidget.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(5, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(6, item)
        self.verticalLayout.addWidget(self.tableWidget)
        self.verticalLayout_7.addLayout(self.verticalLayout)
        self.view_push_button = QtWidgets.QPushButton(self.centralwidget)
        self.view_push_button.setObjectName("view_push_button")
        self.verticalLayout_7.addWidget(self.view_push_button)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 972, 21))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionGet_Current_SO_Data_From_Fishbowl = QtWidgets.QAction(MainWindow)
        self.actionGet_Current_SO_Data_From_Fishbowl.setObjectName("actionGet_Current_SO_Data_From_Fishbowl")
        self.menuFile.addAction(self.actionGet_Current_SO_Data_From_Fishbowl)
        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        MainWindow.setTabOrder(self.added_to_cut_list_check_box, self.qty_cut_spin_box)
        MainWindow.setTabOrder(self.qty_cut_spin_box, self.cutter_combo_box)
        MainWindow.setTabOrder(self.cutter_combo_box, self.is_terminated_check_box)
        MainWindow.setTabOrder(self.is_terminated_check_box, self.is_cut_check_box)
        MainWindow.setTabOrder(self.is_cut_check_box, self.is_spliced_check_box)
        MainWindow.setTabOrder(self.is_spliced_check_box, self.is_ready_for_build_check_box)
        MainWindow.setTabOrder(self.is_ready_for_build_check_box, self.search_so_number_line_edit)
        MainWindow.setTabOrder(self.search_so_number_line_edit, self.search_part_number_line_edit)
        MainWindow.setTabOrder(self.search_part_number_line_edit, self.search_push_button)
        MainWindow.setTabOrder(self.search_push_button, self.tableWidget)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.selected_part_number_label.setText(_translate("MainWindow", "Part Number:"))
        self.selected_so_number_label.setText(_translate("MainWindow", "SO Number:"))
        self.selected_so_line_number_label.setText(_translate("MainWindow", "SO Line Number:"))
        self.groupBox.setTitle(_translate("MainWindow", "1: Add To Cut List"))
        self.added_to_cut_list_check_box.setText(_translate("MainWindow", "Added To Cut List"))
        self.qty_cut_label.setText(_translate("MainWindow", "Qty Cut:"))
        self.cutter_label.setText(_translate("MainWindow", "Cutter:"))
        self.cutter_combo_box.setItemText(0, _translate("MainWindow", "Jim"))
        self.cutter_combo_box.setItemText(1, _translate("MainWindow", "Brandon"))
        self.cutter_combo_box.setItemText(2, _translate("MainWindow", "Dom"))
        self.groupBox_2.setTitle(_translate("MainWindow", "2: Cut Data"))
        self.is_cut_check_box.setText(_translate("MainWindow", "Is Cut"))
        self.cut_start_label.setText(_translate("MainWindow", "Cut Start:"))
        self.cut_end_label.setText(_translate("MainWindow", "Cut End:"))
        self.cut_start_time_edit.setInputMask(_translate("MainWindow", "00:00:00"))
        self.cut_start_time_edit.setText(_translate("MainWindow", "00:00:00"))
        self.cut_end_time_edit.setInputMask(_translate("MainWindow", "00:00:00"))
        self.cut_end_time_edit.setText(_translate("MainWindow", "00:00:00"))
        self.groupBox_3.setTitle(_translate("MainWindow", "3: Termination Data"))
        self.is_terminated_check_box.setText(_translate("MainWindow", "Is Terminated"))
        self.termination_start_label.setText(_translate("MainWindow", "Term Start:"))
        self.termination_end_label.setText(_translate("MainWindow", "Term End:"))
        self.termination_start_time_edit.setInputMask(_translate("MainWindow", "00:00:00"))
        self.termination_start_time_edit.setText(_translate("MainWindow", "00:00:00"))
        self.termination_end_time_edit.setInputMask(_translate("MainWindow", "00:00:00"))
        self.termination_end_time_edit.setText(_translate("MainWindow", "00:00:00"))
        self.groupBox_4.setTitle(_translate("MainWindow", "4: Splice Data"))
        self.is_spliced_check_box.setText(_translate("MainWindow", "Is Spliced"))
        self.splice_start_label.setText(_translate("MainWindow", "Splice Start:"))
        self.splice_end_label.setText(_translate("MainWindow", "Splice End:"))
        self.splice_start_time_edit.setInputMask(_translate("MainWindow", "00:00:00"))
        self.splice_start_time_edit.setText(_translate("MainWindow", "00:00:00"))
        self.splice_end_time_edit.setInputMask(_translate("MainWindow", "00:00:00"))
        self.splice_end_time_edit.setText(_translate("MainWindow", "00:00:00"))
        self.groupBox_5.setTitle(_translate("MainWindow", "5: Other"))
        self.is_ready_for_build_check_box.setText(_translate("MainWindow", "Ready For Build"))
        self.save_push_button.setText(_translate("MainWindow", "Save"))
        self.so_number_label.setText(_translate("MainWindow", "SO Number:"))
        self.part_number_label.setText(_translate("MainWindow", "Part Number:"))
        self.show_finished_parts_check_box.setText(_translate("MainWindow", "Show Finished Parts"))
        self.search_push_button.setText(_translate("MainWindow", "Search"))
        item = self.tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "Sales Order"))
        item = self.tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "Line Number"))
        item = self.tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "Customer Name"))
        item = self.tableWidget.horizontalHeaderItem(3)
        item.setText(_translate("MainWindow", "Product Number"))
        item = self.tableWidget.horizontalHeaderItem(4)
        item.setText(_translate("MainWindow", "Description"))
        item = self.tableWidget.horizontalHeaderItem(5)
        item.setText(_translate("MainWindow", "Qty Left To Ship"))
        item = self.tableWidget.horizontalHeaderItem(6)
        item.setText(_translate("MainWindow", "Qty On Cut List"))
        self.view_push_button.setText(_translate("MainWindow", "View"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.actionGet_Current_SO_Data_From_Fishbowl.setText(_translate("MainWindow", "Get Current SO Data From Fishbowl"))
