# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'imgviewer.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_imgViewerDialog(object):
    def setupUi(self, imgViewerDialog):
        imgViewerDialog.setObjectName("imgViewerDialog")
        imgViewerDialog.resize(1188, 892)
        imgViewerDialog.setSizeGripEnabled(True)
        self.verticalLayout = QtWidgets.QVBoxLayout(imgViewerDialog)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.scrollArea = QtWidgets.QScrollArea(imgViewerDialog)
        self.scrollArea.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.scrollArea.setFrameShadow(QtWidgets.QFrame.Plain)
        self.scrollArea.setLineWidth(0)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 1188, 892))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.label = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.label.setGeometry(QtCore.QRect(20, 30, 58, 18))
        self.label.setText("")
        self.label.setObjectName("label")
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout.addWidget(self.scrollArea)

        self.retranslateUi(imgViewerDialog)
        QtCore.QMetaObject.connectSlotsByName(imgViewerDialog)

    def retranslateUi(self, imgViewerDialog):
        _translate = QtCore.QCoreApplication.translate
        imgViewerDialog.setWindowTitle(_translate("imgViewerDialog", "Image Viewer"))
