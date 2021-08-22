# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\cutlistgenerator\ui\productdialog_ui.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_product_dialog(object):
    def setupUi(self, product_dialog):
        product_dialog.setObjectName("product_dialog")
        product_dialog.resize(437, 383)
        self.verticalLayout = QtWidgets.QVBoxLayout(product_dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.label = QtWidgets.QLabel(product_dialog)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
        self.lineEdit = QtWidgets.QLineEdit(product_dialog)
        self.lineEdit.setObjectName("lineEdit")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.lineEdit)
        self.label_2 = QtWidgets.QLabel(product_dialog)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.doubleSpinBox = QtWidgets.QDoubleSpinBox(product_dialog)
        self.doubleSpinBox.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.doubleSpinBox.setMaximum(10000.0)
        self.doubleSpinBox.setObjectName("doubleSpinBox")
        self.horizontalLayout.addWidget(self.doubleSpinBox)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.formLayout.setLayout(1, QtWidgets.QFormLayout.FieldRole, self.horizontalLayout)
        self.label_4 = QtWidgets.QLabel(product_dialog)
        self.label_4.setObjectName("label_4")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_4)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.comboBox = QtWidgets.QComboBox(product_dialog)
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("")
        self.horizontalLayout_2.addWidget(self.comboBox)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.formLayout.setLayout(2, QtWidgets.QFormLayout.FieldRole, self.horizontalLayout_2)
        self.label_3 = QtWidgets.QLabel(product_dialog)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.plainTextEdit = QtWidgets.QPlainTextEdit(product_dialog)
        self.plainTextEdit.setObjectName("plainTextEdit")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.plainTextEdit)
        self.verticalLayout.addLayout(self.formLayout)
        self.groupBox = QtWidgets.QGroupBox(product_dialog)
        self.groupBox.setCheckable(True)
        self.groupBox.setChecked(False)
        self.groupBox.setObjectName("groupBox")
        self.formLayout_2 = QtWidgets.QFormLayout(self.groupBox)
        self.formLayout_2.setObjectName("formLayout_2")
        self.label_5 = QtWidgets.QLabel(self.groupBox)
        self.label_5.setObjectName("label_5")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_5)
        self.comboBox_2 = QtWidgets.QComboBox(self.groupBox)
        self.comboBox_2.setObjectName("comboBox_2")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.comboBox_2)
        self.verticalLayout.addWidget(self.groupBox)
        self.pushButton = QtWidgets.QPushButton(product_dialog)
        self.pushButton.setObjectName("pushButton")
        self.verticalLayout.addWidget(self.pushButton)

        self.retranslateUi(product_dialog)
        QtCore.QMetaObject.connectSlotsByName(product_dialog)

    def retranslateUi(self, product_dialog):
        _translate = QtCore.QCoreApplication.translate
        product_dialog.setWindowTitle(_translate("product_dialog", "Product"))
        self.label.setText(_translate("product_dialog", "Number:"))
        self.lineEdit.setToolTip(_translate("product_dialog", "Number for this product. This must be unique for each product."))
        self.label_2.setText(_translate("product_dialog", "Unit Price:"))
        self.doubleSpinBox.setToolTip(_translate("product_dialog", "The sell price for one unit."))
        self.doubleSpinBox.setPrefix(_translate("product_dialog", "$ "))
        self.label_4.setText(_translate("product_dialog", "UOM:"))
        self.comboBox.setToolTip(_translate("product_dialog", "Unit of mesure for this product."))
        self.comboBox.setItemText(0, _translate("product_dialog", "Ea"))
        self.label_3.setText(_translate("product_dialog", "Description:"))
        self.plainTextEdit.setToolTip(_translate("product_dialog", "A description and or details for this product."))
        self.groupBox.setToolTip(_translate("product_dialog", "Check this to link a parent product to this product. The parent product is what would be on the customers SO."))
        self.groupBox.setTitle(_translate("product_dialog", "Parent Product"))
        self.label_5.setText(_translate("product_dialog", "Parent Product:"))
        self.comboBox_2.setToolTip(_translate("product_dialog", "Select a parent product number."))
        self.pushButton.setToolTip(_translate("product_dialog", "Save this product."))
        self.pushButton.setText(_translate("product_dialog", "Save"))
