# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\cutlistgenerator\ui\mainwindow_ui.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1157, 837)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName("verticalLayout")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.label_2 = QtWidgets.QLabel(self.groupBox)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.so_search_so_number_line_edit = QtWidgets.QLineEdit(self.groupBox)
        self.so_search_so_number_line_edit.setObjectName("so_search_so_number_line_edit")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.so_search_so_number_line_edit)
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setObjectName("label")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label)
        self.so_search_product_number_line_edit = QtWidgets.QLineEdit(self.groupBox)
        self.so_search_product_number_line_edit.setObjectName("so_search_product_number_line_edit")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.so_search_product_number_line_edit)
        self.verticalLayout.addLayout(self.formLayout)
        self.so_search_include_finished_check_box = QtWidgets.QCheckBox(self.groupBox)
        self.so_search_include_finished_check_box.setObjectName("so_search_include_finished_check_box")
        self.verticalLayout.addWidget(self.so_search_include_finished_check_box)
        self.so_search_push_button = QtWidgets.QPushButton(self.groupBox)
        self.so_search_push_button.setObjectName("so_search_push_button")
        self.verticalLayout.addWidget(self.so_search_push_button)
        self.verticalLayout_2.addWidget(self.groupBox)
        self.so_view_push_button = QtWidgets.QPushButton(self.centralwidget)
        self.so_view_push_button.setObjectName("so_view_push_button")
        self.verticalLayout_2.addWidget(self.so_view_push_button)
        self.sales_order_table_widget = QtWidgets.QTableWidget(self.centralwidget)
        self.sales_order_table_widget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.sales_order_table_widget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.sales_order_table_widget.setObjectName("sales_order_table_widget")
        self.sales_order_table_widget.setColumnCount(13)
        self.sales_order_table_widget.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.sales_order_table_widget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.sales_order_table_widget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.sales_order_table_widget.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.sales_order_table_widget.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.sales_order_table_widget.setHorizontalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        self.sales_order_table_widget.setHorizontalHeaderItem(5, item)
        item = QtWidgets.QTableWidgetItem()
        self.sales_order_table_widget.setHorizontalHeaderItem(6, item)
        item = QtWidgets.QTableWidgetItem()
        self.sales_order_table_widget.setHorizontalHeaderItem(7, item)
        item = QtWidgets.QTableWidgetItem()
        self.sales_order_table_widget.setHorizontalHeaderItem(8, item)
        item = QtWidgets.QTableWidgetItem()
        self.sales_order_table_widget.setHorizontalHeaderItem(9, item)
        item = QtWidgets.QTableWidgetItem()
        self.sales_order_table_widget.setHorizontalHeaderItem(10, item)
        item = QtWidgets.QTableWidgetItem()
        self.sales_order_table_widget.setHorizontalHeaderItem(11, item)
        item = QtWidgets.QTableWidgetItem()
        self.sales_order_table_widget.setHorizontalHeaderItem(12, item)
        self.sales_order_table_widget.horizontalHeader().setSortIndicatorShown(False)
        self.sales_order_table_widget.verticalHeader().setStretchLastSection(False)
        self.verticalLayout_2.addWidget(self.sales_order_table_widget)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1157, 21))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuFishbowl_2 = QtWidgets.QMenu(self.menubar)
        self.menuFishbowl_2.setObjectName("menuFishbowl_2")
        self.menuCut_Job = QtWidgets.QMenu(self.menubar)
        self.menuCut_Job.setObjectName("menuCut_Job")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionGet_Current_SO_Data_From_Fishbowl = QtWidgets.QAction(MainWindow)
        self.actionGet_Current_SO_Data_From_Fishbowl.setObjectName("actionGet_Current_SO_Data_From_Fishbowl")
        self.actionGet_Sales_Order_Data = QtWidgets.QAction(MainWindow)
        self.actionGet_Sales_Order_Data.setObjectName("actionGet_Sales_Order_Data")
        self.actionFind_Product_To_Add = QtWidgets.QAction(MainWindow)
        self.actionFind_Product_To_Add.setObjectName("actionFind_Product_To_Add")
        self.action_fishbowl_Get_Sales_Order_Data = QtWidgets.QAction(MainWindow)
        self.action_fishbowl_Get_Sales_Order_Data.setObjectName("action_fishbowl_Get_Sales_Order_Data")
        self.action_cut_job_Create_Blank = QtWidgets.QAction(MainWindow)
        self.action_cut_job_Create_Blank.setObjectName("action_cut_job_Create_Blank")
        self.action_cut_job_Show_All_Open = QtWidgets.QAction(MainWindow)
        self.action_cut_job_Show_All_Open.setObjectName("action_cut_job_Show_All_Open")
        self.actionSettings = QtWidgets.QAction(MainWindow)
        self.actionSettings.setObjectName("actionSettings")
        self.actionSystem_Properties = QtWidgets.QAction(MainWindow)
        self.actionSystem_Properties.setObjectName("actionSystem_Properties")
        self.menuFile.addAction(self.actionSettings)
        self.menuFile.addAction(self.actionSystem_Properties)
        self.menuFishbowl_2.addAction(self.action_fishbowl_Get_Sales_Order_Data)
        self.menuCut_Job.addAction(self.action_cut_job_Create_Blank)
        self.menuCut_Job.addAction(self.action_cut_job_Show_All_Open)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuFishbowl_2.menuAction())
        self.menubar.addAction(self.menuCut_Job.menuAction())

        self.retranslateUi(MainWindow)
        self.so_search_so_number_line_edit.returnPressed.connect(self.so_search_push_button.click)
        self.so_search_product_number_line_edit.returnPressed.connect(self.so_search_push_button.click)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.groupBox.setTitle(_translate("MainWindow", "Sales Order Search"))
        self.label_2.setText(_translate("MainWindow", "SO Number:"))
        self.label.setText(_translate("MainWindow", "Product Number:"))
        self.so_search_include_finished_check_box.setText(_translate("MainWindow", "Include Finished"))
        self.so_search_push_button.setText(_translate("MainWindow", "Search"))
        self.so_view_push_button.setText(_translate("MainWindow", "View"))
        item = self.sales_order_table_widget.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "Id"))
        item = self.sales_order_table_widget.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "Due Date"))
        item = self.sales_order_table_widget.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "Customer Name"))
        item = self.sales_order_table_widget.horizontalHeaderItem(3)
        item.setText(_translate("MainWindow", "SO Number"))
        item = self.sales_order_table_widget.horizontalHeaderItem(4)
        item.setText(_translate("MainWindow", "Line Number"))
        item = self.sales_order_table_widget.horizontalHeaderItem(5)
        item.setText(_translate("MainWindow", "Product Number"))
        item = self.sales_order_table_widget.horizontalHeaderItem(6)
        item.setText(_translate("MainWindow", "Description"))
        item = self.sales_order_table_widget.horizontalHeaderItem(7)
        item.setText(_translate("MainWindow", "Qty Left To Ship"))
        item = self.sales_order_table_widget.horizontalHeaderItem(8)
        item.setText(_translate("MainWindow", "Qty Left To Cut"))
        item = self.sales_order_table_widget.horizontalHeaderItem(9)
        item.setText(_translate("MainWindow", "Qty Scheduled To Cut"))
        item = self.sales_order_table_widget.horizontalHeaderItem(10)
        item.setText(_translate("MainWindow", "Fully Cut"))
        item = self.sales_order_table_widget.horizontalHeaderItem(11)
        item.setText(_translate("MainWindow", "Parent Number"))
        item = self.sales_order_table_widget.horizontalHeaderItem(12)
        item.setText(_translate("MainWindow", "Parent Description"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuFishbowl_2.setTitle(_translate("MainWindow", "Fishbowl"))
        self.menuCut_Job.setTitle(_translate("MainWindow", "Cut Job"))
        self.actionGet_Current_SO_Data_From_Fishbowl.setText(_translate("MainWindow", "Get Current SO Data From Fishbowl"))
        self.actionGet_Sales_Order_Data.setText(_translate("MainWindow", "Get Sales Order Data"))
        self.actionFind_Product_To_Add.setText(_translate("MainWindow", "Find Product To Add"))
        self.action_fishbowl_Get_Sales_Order_Data.setText(_translate("MainWindow", "Get Sales Order Data"))
        self.action_cut_job_Create_Blank.setText(_translate("MainWindow", "Create Blank Job"))
        self.action_cut_job_Show_All_Open.setText(_translate("MainWindow", "Show All Open"))
        self.actionSettings.setText(_translate("MainWindow", "Settings"))
        self.actionSystem_Properties.setText(_translate("MainWindow", "System Properties"))
