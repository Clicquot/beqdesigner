# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'merge_signals.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MergeSignalDialog(object):
    def setupUi(self, MergeSignalDialog):
        MergeSignalDialog.setObjectName("MergeSignalDialog")
        MergeSignalDialog.resize(400, 308)
        self.gridLayout = QtWidgets.QGridLayout(MergeSignalDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.signals = QtWidgets.QListWidget(MergeSignalDialog)
        self.signals.setDragEnabled(True)
        self.signals.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.signals.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.signals.setObjectName("signals")
        self.gridLayout.addWidget(self.signals, 0, 1, 1, 1)
        self.signalsLabel = QtWidgets.QLabel(MergeSignalDialog)
        self.signalsLabel.setObjectName("signalsLabel")
        self.gridLayout.addWidget(self.signalsLabel, 0, 0, 1, 1)
        self.durationLabel = QtWidgets.QLabel(MergeSignalDialog)
        self.durationLabel.setObjectName("durationLabel")
        self.gridLayout.addWidget(self.durationLabel, 1, 0, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(MergeSignalDialog)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Save)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 2, 1, 1, 1)
        self.duration = QtWidgets.QTimeEdit(MergeSignalDialog)
        self.duration.setReadOnly(True)
        self.duration.setObjectName("duration")
        self.gridLayout.addWidget(self.duration, 1, 1, 1, 1)

        self.retranslateUi(MergeSignalDialog)
        self.signals.itemSelectionChanged.connect(MergeSignalDialog.calc_duration) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(MergeSignalDialog)

    def retranslateUi(self, MergeSignalDialog):
        _translate = QtCore.QCoreApplication.translate
        MergeSignalDialog.setWindowTitle(_translate("MergeSignalDialog", "Merge Signals"))
        self.signalsLabel.setText(_translate("MergeSignalDialog", "Signals"))
        self.durationLabel.setText(_translate("MergeSignalDialog", "Duration"))
        self.duration.setDisplayFormat(_translate("MergeSignalDialog", "HH:mm:ss.zzz"))
