# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'link.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_linkSignalDialog(object):
    def setupUi(self, linkSignalDialog):
        linkSignalDialog.setObjectName("linkSignalDialog")
        linkSignalDialog.resize(833, 325)
        self.gridLayout = QtWidgets.QGridLayout(linkSignalDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.addToMaster = QtWidgets.QToolButton(linkSignalDialog)
        self.addToMaster.setObjectName("addToMaster")
        self.gridLayout.addWidget(self.addToMaster, 0, 2, 1, 1)
        self.masterCandidates = QtWidgets.QComboBox(linkSignalDialog)
        self.masterCandidates.setObjectName("masterCandidates")
        self.gridLayout.addWidget(self.masterCandidates, 0, 1, 1, 1)
        self.masterCandidatesLabel = QtWidgets.QLabel(linkSignalDialog)
        self.masterCandidatesLabel.setObjectName("masterCandidatesLabel")
        self.gridLayout.addWidget(self.masterCandidatesLabel, 0, 0, 1, 1)
        self.linkSignals = QtWidgets.QTableView(linkSignalDialog)
        self.linkSignals.setObjectName("linkSignals")
        self.gridLayout.addWidget(self.linkSignals, 1, 0, 1, 3)
        self.buttonBox = QtWidgets.QDialogButtonBox(linkSignalDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Save)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 2, 0, 1, 3)
        self.gridLayout.setColumnStretch(1, 1)

        self.retranslateUi(linkSignalDialog)
        self.buttonBox.accepted.connect(linkSignalDialog.accept) # type: ignore
        self.buttonBox.rejected.connect(linkSignalDialog.reject) # type: ignore
        self.addToMaster.clicked.connect(linkSignalDialog.addMaster) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(linkSignalDialog)

    def retranslateUi(self, linkSignalDialog):
        _translate = QtCore.QCoreApplication.translate
        linkSignalDialog.setWindowTitle(_translate("linkSignalDialog", "Link Signals"))
        self.addToMaster.setText(_translate("linkSignalDialog", "..."))
        self.masterCandidatesLabel.setText(_translate("linkSignalDialog", "Make Master"))
