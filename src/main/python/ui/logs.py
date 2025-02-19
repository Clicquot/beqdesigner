# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'logs.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_logsForm(object):
    def setupUi(self, logsForm):
        logsForm.setObjectName("logsForm")
        logsForm.setEnabled(True)
        logsForm.resize(960, 768)
        self.centralwidget = QtWidgets.QWidget(logsForm)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.logViewer = QtWidgets.QPlainTextEdit(self.centralwidget)
        font = QtGui.QFont()
        font.setFamily("Consolas")
        font.setPointSize(9)
        self.logViewer.setFont(font)
        self.logViewer.setReadOnly(True)
        self.logViewer.setObjectName("logViewer")
        self.gridLayout.addWidget(self.logViewer, 3, 0, 1, 2)
        self.logLevel = QtWidgets.QComboBox(self.centralwidget)
        self.logLevel.setObjectName("logLevel")
        self.logLevel.addItem("")
        self.logLevel.addItem("")
        self.logLevel.addItem("")
        self.logLevel.addItem("")
        self.logLevel.addItem("")
        self.gridLayout.addWidget(self.logLevel, 1, 1, 1, 1)
        self.logSizeLabel = QtWidgets.QLabel(self.centralwidget)
        self.logSizeLabel.setObjectName("logSizeLabel")
        self.gridLayout.addWidget(self.logSizeLabel, 0, 0, 1, 1)
        self.maxRows = QtWidgets.QSpinBox(self.centralwidget)
        self.maxRows.setMinimum(10)
        self.maxRows.setMaximum(5000)
        self.maxRows.setSingleStep(10)
        self.maxRows.setProperty("value", 1000)
        self.maxRows.setObjectName("maxRows")
        self.gridLayout.addWidget(self.maxRows, 0, 1, 1, 1)
        self.logLevelLabel = QtWidgets.QLabel(self.centralwidget)
        self.logLevelLabel.setObjectName("logLevelLabel")
        self.gridLayout.addWidget(self.logLevelLabel, 1, 0, 1, 1)
        self.excludesLabel = QtWidgets.QLabel(self.centralwidget)
        self.excludesLabel.setObjectName("excludesLabel")
        self.gridLayout.addWidget(self.excludesLabel, 2, 0, 1, 1)
        self.excludes = QtWidgets.QLineEdit(self.centralwidget)
        self.excludes.setObjectName("excludes")
        self.gridLayout.addWidget(self.excludes, 2, 1, 1, 1)
        logsForm.setCentralWidget(self.centralwidget)

        self.retranslateUi(logsForm)
        self.maxRows.valueChanged['int'].connect(logsForm.set_log_size) # type: ignore
        self.logLevel.currentTextChanged['QString'].connect(logsForm.set_log_level) # type: ignore
        self.excludes.returnPressed.connect(logsForm.set_excludes) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(logsForm)
        logsForm.setTabOrder(self.maxRows, self.logLevel)
        logsForm.setTabOrder(self.logLevel, self.excludes)
        logsForm.setTabOrder(self.excludes, self.logViewer)

    def retranslateUi(self, logsForm):
        _translate = QtCore.QCoreApplication.translate
        logsForm.setWindowTitle(_translate("logsForm", "Logs"))
        self.logLevel.setCurrentText(_translate("logsForm", "DEBUG"))
        self.logLevel.setItemText(0, _translate("logsForm", "DEBUG"))
        self.logLevel.setItemText(1, _translate("logsForm", "INFO"))
        self.logLevel.setItemText(2, _translate("logsForm", "WARNING"))
        self.logLevel.setItemText(3, _translate("logsForm", "ERROR"))
        self.logLevel.setItemText(4, _translate("logsForm", "CRITICAL"))
        self.logSizeLabel.setText(_translate("logsForm", "Log Size"))
        self.logLevelLabel.setText(_translate("logsForm", "Log Level"))
        self.excludesLabel.setText(_translate("logsForm", "Excludes"))
