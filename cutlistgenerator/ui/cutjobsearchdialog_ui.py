# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\cutlistgenerator\ui\cutjobsearchdialog_ui.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_cut_job_search_dialog(object):
    def setupUi(self, cut_job_search_dialog):
        cut_job_search_dialog.setObjectName("cut_job_search_dialog")
        cut_job_search_dialog.resize(1077, 444)
        self.verticalLayout = QtWidgets.QVBoxLayout(cut_job_search_dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.label = QtWidgets.QLabel(cut_job_search_dialog)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
        self.product_number_combo_box = QtWidgets.QComboBox(cut_job_search_dialog)
        self.product_number_combo_box.setEditable(True)
        self.product_number_combo_box.setInsertPolicy(QtWidgets.QComboBox.NoInsert)
        self.product_number_combo_box.setObjectName("product_number_combo_box")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.product_number_combo_box)
        self.label_2 = QtWidgets.QLabel(cut_job_search_dialog)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.wire_cutter_name_combo_box = QtWidgets.QComboBox(cut_job_search_dialog)
        self.wire_cutter_name_combo_box.setEditable(False)
        self.wire_cutter_name_combo_box.setObjectName("wire_cutter_name_combo_box")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.wire_cutter_name_combo_box)
        self.label_3 = QtWidgets.QLabel(cut_job_search_dialog)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.formLayout_2 = QtWidgets.QFormLayout()
        self.formLayout_2.setLabelAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.formLayout_2.setFormAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.formLayout_2.setObjectName("formLayout_2")
        self.label_11 = QtWidgets.QLabel(cut_job_search_dialog)
        self.label_11.setObjectName("label_11")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_11)
        self.linked_sales_order_number_value_label = QtWidgets.QLabel(cut_job_search_dialog)
        self.linked_sales_order_number_value_label.setText("")
        self.linked_sales_order_number_value_label.setObjectName("linked_sales_order_number_value_label")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.linked_sales_order_number_value_label)
        self.label_13 = QtWidgets.QLabel(cut_job_search_dialog)
        self.label_13.setObjectName("label_13")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_13)
        self.linked_sales_order_product_number_value_label = QtWidgets.QLabel(cut_job_search_dialog)
        self.linked_sales_order_product_number_value_label.setText("")
        self.linked_sales_order_product_number_value_label.setObjectName("linked_sales_order_product_number_value_label")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.linked_sales_order_product_number_value_label)
        self.label_15 = QtWidgets.QLabel(cut_job_search_dialog)
        self.label_15.setObjectName("label_15")
        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_15)
        self.linked_sales_order_line_number_value_label = QtWidgets.QLabel(cut_job_search_dialog)
        self.linked_sales_order_line_number_value_label.setText("")
        self.linked_sales_order_line_number_value_label.setObjectName("linked_sales_order_line_number_value_label")
        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.linked_sales_order_line_number_value_label)
        self.horizontalLayout.addLayout(self.formLayout_2)
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.find_so_item_push_button = QtWidgets.QPushButton(cut_job_search_dialog)
        self.find_so_item_push_button.setMaximumSize(QtCore.QSize(55, 16777215))
        self.find_so_item_push_button.setObjectName("find_so_item_push_button")
        self.verticalLayout_4.addWidget(self.find_so_item_push_button)
        self.remove_linked_so_item_push_button = QtWidgets.QPushButton(cut_job_search_dialog)
        self.remove_linked_so_item_push_button.setMaximumSize(QtCore.QSize(55, 16777215))
        self.remove_linked_so_item_push_button.setObjectName("remove_linked_so_item_push_button")
        self.verticalLayout_4.addWidget(self.remove_linked_so_item_push_button)
        self.horizontalLayout.addLayout(self.verticalLayout_4)
        self.formLayout.setLayout(2, QtWidgets.QFormLayout.FieldRole, self.horizontalLayout)
        self.verticalLayout.addLayout(self.formLayout)
        self.search_push_button = QtWidgets.QPushButton(cut_job_search_dialog)
        self.search_push_button.setObjectName("search_push_button")
        self.verticalLayout.addWidget(self.search_push_button)
        self.cut_job_table_widget = QtWidgets.QTableWidget(cut_job_search_dialog)
        self.cut_job_table_widget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.cut_job_table_widget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.cut_job_table_widget.setObjectName("cut_job_table_widget")
        self.cut_job_table_widget.setColumnCount(13)
        self.cut_job_table_widget.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.cut_job_table_widget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.cut_job_table_widget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.cut_job_table_widget.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.cut_job_table_widget.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.cut_job_table_widget.setHorizontalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        self.cut_job_table_widget.setHorizontalHeaderItem(5, item)
        item = QtWidgets.QTableWidgetItem()
        self.cut_job_table_widget.setHorizontalHeaderItem(6, item)
        item = QtWidgets.QTableWidgetItem()
        self.cut_job_table_widget.setHorizontalHeaderItem(7, item)
        item = QtWidgets.QTableWidgetItem()
        self.cut_job_table_widget.setHorizontalHeaderItem(8, item)
        item = QtWidgets.QTableWidgetItem()
        self.cut_job_table_widget.setHorizontalHeaderItem(9, item)
        item = QtWidgets.QTableWidgetItem()
        self.cut_job_table_widget.setHorizontalHeaderItem(10, item)
        item = QtWidgets.QTableWidgetItem()
        self.cut_job_table_widget.setHorizontalHeaderItem(11, item)
        item = QtWidgets.QTableWidgetItem()
        self.cut_job_table_widget.setHorizontalHeaderItem(12, item)
        self.verticalLayout.addWidget(self.cut_job_table_widget)
        self.select_push_button = QtWidgets.QPushButton(cut_job_search_dialog)
        self.select_push_button.setObjectName("select_push_button")
        self.verticalLayout.addWidget(self.select_push_button)
        self.label_2.setBuddy(self.wire_cutter_name_combo_box)
        self.label_3.setBuddy(self.find_so_item_push_button)

        self.retranslateUi(cut_job_search_dialog)
        QtCore.QMetaObject.connectSlotsByName(cut_job_search_dialog)

    def retranslateUi(self, cut_job_search_dialog):
        _translate = QtCore.QCoreApplication.translate
        cut_job_search_dialog.setWindowTitle(_translate("cut_job_search_dialog", "Cut Job Search"))
        self.label.setText(_translate("cut_job_search_dialog", "Product Number:"))
        self.label_2.setText(_translate("cut_job_search_dialog", "Wire Cutter:"))
        self.label_3.setText(_translate("cut_job_search_dialog", "Linked SO Item:"))
        self.label_11.setText(_translate("cut_job_search_dialog", "Sales Order Number:"))
        self.label_13.setText(_translate("cut_job_search_dialog", "Product Number:"))
        self.label_15.setText(_translate("cut_job_search_dialog", "Line Number:"))
        self.find_so_item_push_button.setText(_translate("cut_job_search_dialog", "Find"))
        self.remove_linked_so_item_push_button.setText(_translate("cut_job_search_dialog", "Remove"))
        self.search_push_button.setText(_translate("cut_job_search_dialog", "Search"))
        self.cut_job_table_widget.setSortingEnabled(False)
        item = self.cut_job_table_widget.horizontalHeaderItem(0)
        item.setText(_translate("cut_job_search_dialog", "Id"))
        item = self.cut_job_table_widget.horizontalHeaderItem(1)
        item.setText(_translate("cut_job_search_dialog", "Date Created"))
        item = self.cut_job_table_widget.horizontalHeaderItem(2)
        item.setText(_translate("cut_job_search_dialog", "Product Number"))
        item = self.cut_job_table_widget.horizontalHeaderItem(3)
        item.setText(_translate("cut_job_search_dialog", "SO Number"))
        item = self.cut_job_table_widget.horizontalHeaderItem(4)
        item.setText(_translate("cut_job_search_dialog", "Assigned Cutter"))
        item = self.cut_job_table_widget.horizontalHeaderItem(5)
        item.setText(_translate("cut_job_search_dialog", "Quantity Cut"))
        item = self.cut_job_table_widget.horizontalHeaderItem(6)
        item.setText(_translate("cut_job_search_dialog", "Cut Start Date"))
        item = self.cut_job_table_widget.horizontalHeaderItem(7)
        item.setText(_translate("cut_job_search_dialog", "Cut End Date"))
        item = self.cut_job_table_widget.horizontalHeaderItem(8)
        item.setText(_translate("cut_job_search_dialog", "Term Start Date"))
        item = self.cut_job_table_widget.horizontalHeaderItem(9)
        item.setText(_translate("cut_job_search_dialog", "Term End Date"))
        item = self.cut_job_table_widget.horizontalHeaderItem(10)
        item.setText(_translate("cut_job_search_dialog", "Splice Start Date"))
        item = self.cut_job_table_widget.horizontalHeaderItem(11)
        item.setText(_translate("cut_job_search_dialog", "Splice End Date"))
        item = self.cut_job_table_widget.horizontalHeaderItem(12)
        item.setText(_translate("cut_job_search_dialog", "Ready For Build"))
        self.select_push_button.setText(_translate("cut_job_search_dialog", "Select"))
