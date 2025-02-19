# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'jriver_delay_filter.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_jriverDelayDialog(object):
    def setupUi(self, jriverDelayDialog):
        jriverDelayDialog.setObjectName("jriverDelayDialog")
        jriverDelayDialog.resize(360, 276)
        self.verticalLayout = QtWidgets.QVBoxLayout(jriverDelayDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.distance = QtWidgets.QDoubleSpinBox(jriverDelayDialog)
        self.distance.setEnabled(False)
        self.distance.setDecimals(3)
        self.distance.setMinimum(-686.0)
        self.distance.setMaximum(686.0)
        self.distance.setSingleStep(0.001)
        self.distance.setObjectName("distance")
        self.gridLayout.addWidget(self.distance, 0, 3, 1, 1)
        self.channelList = QtWidgets.QListWidget(jriverDelayDialog)
        self.channelList.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.channelList.setObjectName("channelList")
        self.gridLayout.addWidget(self.channelList, 2, 1, 1, 3)
        self.channelListLabel = QtWidgets.QLabel(jriverDelayDialog)
        self.channelListLabel.setObjectName("channelListLabel")
        self.gridLayout.addWidget(self.channelListLabel, 2, 0, 1, 1)
        self.label = QtWidgets.QLabel(jriverDelayDialog)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.millis = QtWidgets.QDoubleSpinBox(jriverDelayDialog)
        self.millis.setDecimals(3)
        self.millis.setMinimum(-2000.0)
        self.millis.setMaximum(2000.0)
        self.millis.setSingleStep(0.001)
        self.millis.setObjectName("millis")
        self.gridLayout.addWidget(self.millis, 0, 1, 1, 1)
        self.changeUnitButton = QtWidgets.QToolButton(jriverDelayDialog)
        self.changeUnitButton.setObjectName("changeUnitButton")
        self.gridLayout.addWidget(self.changeUnitButton, 0, 2, 1, 1)
        self.gridLayout.setColumnStretch(1, 1)
        self.gridLayout.setColumnStretch(2, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.buttonBox = QtWidgets.QDialogButtonBox(jriverDelayDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Save)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(jriverDelayDialog)
        self.buttonBox.accepted.connect(jriverDelayDialog.accept) # type: ignore
        self.buttonBox.rejected.connect(jriverDelayDialog.reject) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(jriverDelayDialog)
        jriverDelayDialog.setTabOrder(self.millis, self.channelList)
        jriverDelayDialog.setTabOrder(self.channelList, self.distance)

    def retranslateUi(self, jriverDelayDialog):
        _translate = QtCore.QCoreApplication.translate
        jriverDelayDialog.setWindowTitle(_translate("jriverDelayDialog", "Add/Edit Filter"))
        self.distance.setSuffix(_translate("jriverDelayDialog", " m"))
        self.channelListLabel.setText(_translate("jriverDelayDialog", "Channels"))
        self.label.setText(_translate("jriverDelayDialog", "Delay"))
        self.millis.setSuffix(_translate("jriverDelayDialog", " ms"))
        self.changeUnitButton.setText(_translate("jriverDelayDialog", "..."))
