# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'opsdialog.ui'
#
# Created by: PyQt5 UI code generator 5.7
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_opsDialog(object):
    def setupUi(self, opsDialog):
        opsDialog.setObjectName("opsDialog")
        opsDialog.resize(522, 323)
        self.verticalLayout = QtWidgets.QVBoxLayout(opsDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox = QtWidgets.QGroupBox(opsDialog)
        self.groupBox.setObjectName("groupBox")
        self.formLayout = QtWidgets.QFormLayout(self.groupBox)
        self.formLayout.setObjectName("formLayout")
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.selectAmazon = QtWidgets.QRadioButton(self.groupBox)
        self.selectAmazon.setObjectName("selectAmazon")
        self.horizontalLayout_3.addWidget(self.selectAmazon)
        self.amazonBox = QtWidgets.QComboBox(self.groupBox)
        self.amazonBox.setObjectName("amazonBox")
        self.horizontalLayout_3.addWidget(self.amazonBox)
        self.selectVendor = QtWidgets.QRadioButton(self.groupBox)
        self.selectVendor.setObjectName("selectVendor")
        self.horizontalLayout_3.addWidget(self.selectVendor)
        self.vendorBox = QtWidgets.QComboBox(self.groupBox)
        self.vendorBox.setObjectName("vendorBox")
        self.horizontalLayout_3.addWidget(self.vendorBox)
        self.formLayout.setLayout(0, QtWidgets.QFormLayout.FieldRole, self.horizontalLayout_3)
        self.verticalLayout.addWidget(self.groupBox)
        self.groupBox_2 = QtWidgets.QGroupBox(opsDialog)
        self.groupBox_2.setObjectName("groupBox_2")
        self.gridLayout = QtWidgets.QGridLayout(self.groupBox_2)
        self.gridLayout.setObjectName("gridLayout")
        self.noLinksCheck = QtWidgets.QCheckBox(self.groupBox_2)
        self.noLinksCheck.setObjectName("noLinksCheck")
        self.gridLayout.addWidget(self.noLinksCheck, 0, 0, 1, 1)
        self.priceCheck = QtWidgets.QCheckBox(self.groupBox_2)
        self.priceCheck.setObjectName("priceCheck")
        self.gridLayout.addWidget(self.priceCheck, 1, 0, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.priceFromBox = QtWidgets.QDoubleSpinBox(self.groupBox_2)
        self.priceFromBox.setEnabled(False)
        self.priceFromBox.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.priceFromBox.setAccelerated(True)
        self.priceFromBox.setMaximum(99999.0)
        self.priceFromBox.setObjectName("priceFromBox")
        self.horizontalLayout.addWidget(self.priceFromBox)
        self.priceToLabel = QtWidgets.QLabel(self.groupBox_2)
        self.priceToLabel.setEnabled(False)
        self.priceToLabel.setObjectName("priceToLabel")
        self.horizontalLayout.addWidget(self.priceToLabel)
        self.priceToBox = QtWidgets.QDoubleSpinBox(self.groupBox_2)
        self.priceToBox.setEnabled(False)
        self.priceToBox.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.priceToBox.setAccelerated(True)
        self.priceToBox.setMaximum(99999.0)
        self.priceToBox.setObjectName("priceToBox")
        self.horizontalLayout.addWidget(self.priceToBox)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.gridLayout.addLayout(self.horizontalLayout, 1, 1, 1, 1)
        self.lastUpdateCheck = QtWidgets.QCheckBox(self.groupBox_2)
        self.lastUpdateCheck.setObjectName("lastUpdateCheck")
        self.gridLayout.addWidget(self.lastUpdateCheck, 2, 0, 1, 1)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.dateTimeEdit = QtWidgets.QDateTimeEdit(self.groupBox_2)
        self.dateTimeEdit.setEnabled(False)
        self.dateTimeEdit.setCalendarPopup(True)
        self.dateTimeEdit.setObjectName("dateTimeEdit")
        self.horizontalLayout_2.addWidget(self.dateTimeEdit)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.gridLayout.addLayout(self.horizontalLayout_2, 2, 1, 1, 1)
        self.verticalLayout.addWidget(self.groupBox_2)
        self.groupBox_3 = QtWidgets.QGroupBox(opsDialog)
        self.groupBox_3.setObjectName("groupBox_3")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.groupBox_3)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label_2 = QtWidgets.QLabel(self.groupBox_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setObjectName("label_2")
        self.gridLayout_2.addWidget(self.label_2, 0, 0, 1, 1)
        self.opsBox = QtWidgets.QComboBox(self.groupBox_3)
        self.opsBox.setObjectName("opsBox")
        self.gridLayout_2.addWidget(self.opsBox, 0, 1, 1, 1)
        self.verticalLayout.addWidget(self.groupBox_3)
        self.buttonBox = QtWidgets.QDialogButtonBox(opsDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)
        self.buttonBox.raise_()
        self.amazonBox.raise_()
        self.vendorBox.raise_()
        self.selectAmazon.raise_()
        self.selectVendor.raise_()
        self.priceFromBox.raise_()
        self.priceToLabel.raise_()
        self.priceToBox.raise_()
        self.groupBox.raise_()
        self.groupBox_2.raise_()
        self.priceFromBox.raise_()
        self.groupBox_3.raise_()

        self.retranslateUi(opsDialog)
        self.buttonBox.accepted.connect(opsDialog.accept)
        self.buttonBox.rejected.connect(opsDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(opsDialog)

    def retranslateUi(self, opsDialog):
        _translate = QtCore.QCoreApplication.translate
        opsDialog.setWindowTitle(_translate("opsDialog", "New Operation"))
        self.groupBox.setTitle(_translate("opsDialog", "Source:"))
        self.label.setText(_translate("opsDialog", "Select from:"))
        self.selectAmazon.setText(_translate("opsDialog", "Amazon:"))
        self.selectVendor.setText(_translate("opsDialog", "Vendor:"))
        self.groupBox_2.setTitle(_translate("opsDialog", "Filter by:"))
        self.noLinksCheck.setText(_translate("opsDialog", "No linked products"))
        self.priceCheck.setText(_translate("opsDialog", "Price:"))
        self.priceFromBox.setPrefix(_translate("opsDialog", "$"))
        self.priceToLabel.setText(_translate("opsDialog", "to"))
        self.priceToBox.setPrefix(_translate("opsDialog", "$"))
        self.lastUpdateCheck.setText(_translate("opsDialog", "Last update:"))
        self.groupBox_3.setTitle(_translate("opsDialog", "Operation:"))
        self.label_2.setText(_translate("opsDialog", "Operation:"))
