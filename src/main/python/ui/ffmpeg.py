# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ffmpeg.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ffmpegReportDialog(object):
    def setupUi(self, ffmpegReportDialog):
        ffmpegReportDialog.setObjectName("ffmpegReportDialog")
        ffmpegReportDialog.resize(800, 300)
        self.verticalLayout = QtWidgets.QVBoxLayout(ffmpegReportDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.message = QtWidgets.QLabel(ffmpegReportDialog)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.message.setFont(font)
        self.message.setText("")
        self.message.setObjectName("message")
        self.verticalLayout.addWidget(self.message)
        self.details = QtWidgets.QPlainTextEdit(ffmpegReportDialog)
        font = QtGui.QFont()
        font.setFamily("Consolas")
        self.details.setFont(font)
        self.details.setObjectName("details")
        self.verticalLayout.addWidget(self.details)
        self.buttonBox = QtWidgets.QDialogButtonBox(ffmpegReportDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Close)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(ffmpegReportDialog)
        self.buttonBox.accepted.connect(ffmpegReportDialog.accept) # type: ignore
        self.buttonBox.rejected.connect(ffmpegReportDialog.reject) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(ffmpegReportDialog)

    def retranslateUi(self, ffmpegReportDialog):
        _translate = QtCore.QCoreApplication.translate
        ffmpegReportDialog.setWindowTitle(_translate("ffmpegReportDialog", "ffmpeg"))
