# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './ui/listmatchingproducts_params.ui'
#
# Created by: PyQt5 UI code generator 5.7
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_listMatchingProductsParams(object):
    def setupUi(self, listMatchingProductsParams):
        listMatchingProductsParams.setObjectName("listMatchingProductsParams")
        listMatchingProductsParams.resize(400, 166)
        self.verticalLayout = QtWidgets.QVBoxLayout(listMatchingProductsParams)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.salesRankBox = QtWidgets.QSpinBox(listMatchingProductsParams)
        self.salesRankBox.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.salesRankBox.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.salesRankBox.setProperty("showGroupSeparator", True)
        self.salesRankBox.setMinimum(1)
        self.salesRankBox.setMaximum(9999999)
        self.salesRankBox.setProperty("value", 300000)
        self.salesRankBox.setObjectName("salesRankBox")
        self.gridLayout.addWidget(self.salesRankBox, 1, 2, 1, 1)
        self.label_2 = QtWidgets.QLabel(listMatchingProductsParams)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 0, 1, 1, 1)
        self.label = QtWidgets.QLabel(listMatchingProductsParams)
        self.label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.confidenceBox = QtWidgets.QSpinBox(listMatchingProductsParams)
        self.confidenceBox.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.confidenceBox.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.confidenceBox.setMaximum(100)
        self.confidenceBox.setProperty("value", 75)
        self.confidenceBox.setObjectName("confidenceBox")
        self.gridLayout.addWidget(self.confidenceBox, 0, 2, 1, 1)
        self.label_4 = QtWidgets.QLabel(listMatchingProductsParams)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 1, 1, 1, 1)
        self.label_3 = QtWidgets.QLabel(listMatchingProductsParams)
        self.label_3.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 1, 0, 1, 1)
        self.label_5 = QtWidgets.QLabel(listMatchingProductsParams)
        self.label_5.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 2, 0, 1, 1)
        self.label_6 = QtWidgets.QLabel(listMatchingProductsParams)
        self.label_6.setObjectName("label_6")
        self.gridLayout.addWidget(self.label_6, 2, 1, 1, 1)
        self.differenceBox = QtWidgets.QSpinBox(listMatchingProductsParams)
        self.differenceBox.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.differenceBox.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.differenceBox.setMaximum(999)
        self.differenceBox.setObjectName("differenceBox")
        self.gridLayout.addWidget(self.differenceBox, 2, 2, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        spacerItem = QtWidgets.QSpacerItem(20, 35, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)

        self.retranslateUi(listMatchingProductsParams)
        QtCore.QMetaObject.connectSlotsByName(listMatchingProductsParams)

    def retranslateUi(self, listMatchingProductsParams):
        _translate = QtCore.QCoreApplication.translate
        listMatchingProductsParams.setWindowTitle(_translate("listMatchingProductsParams", "Form"))
        self.label_2.setText(_translate("listMatchingProductsParams", "Match confidence at least "))
        self.label.setText(_translate("listMatchingProductsParams", "Create link if:"))
        self.confidenceBox.setSuffix(_translate("listMatchingProductsParams", "%"))
        self.label_4.setText(_translate("listMatchingProductsParams", "Sales rank less than "))
        self.label_3.setText(_translate("listMatchingProductsParams", "Get pricing if:"))
        self.label_5.setText(_translate("listMatchingProductsParams", "Get fees if:"))
        self.label_6.setText(_translate("listMatchingProductsParams", "Price ratio at least"))
        self.differenceBox.setSuffix(_translate("listMatchingProductsParams", "%"))

