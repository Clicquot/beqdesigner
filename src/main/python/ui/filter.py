# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'filter.ui'
#
# Created by: PyQt5 UI code generator 5.12.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_editFilterDialog(object):
    def setupUi(self, editFilterDialog):
        editFilterDialog.setObjectName("editFilterDialog")
        editFilterDialog.resize(1390, 665)
        self.panes = QtWidgets.QGridLayout(editFilterDialog)
        self.panes.setObjectName("panes")
        self.viewPane = QtWidgets.QGridLayout()
        self.viewPane.setObjectName("viewPane")
        self.previewChart = MplWidget(editFilterDialog)
        self.previewChart.setObjectName("previewChart")
        self.viewPane.addWidget(self.previewChart, 0, 0, 1, 1)
        self.panes.addLayout(self.viewPane, 0, 1, 1, 1)
        self.paramsPane = QtWidgets.QGridLayout()
        self.paramsPane.setObjectName("paramsPane")
        self.passFilterType = QtWidgets.QComboBox(editFilterDialog)
        self.passFilterType.setEnabled(True)
        self.passFilterType.setObjectName("passFilterType")
        self.passFilterType.addItem("")
        self.passFilterType.addItem("")
        self.paramsPane.addWidget(self.passFilterType, 2, 1, 1, 1)
        self.filterType = QtWidgets.QComboBox(editFilterDialog)
        self.filterType.setObjectName("filterType")
        self.filterType.addItem("")
        self.filterType.addItem("")
        self.filterType.addItem("")
        self.filterType.addItem("")
        self.filterType.addItem("")
        self.filterType.addItem("")
        self.filterType.addItem("")
        self.filterType.addItem("")
        self.paramsPane.addWidget(self.filterType, 1, 1, 1, 1)
        self.typeLabel = QtWidgets.QLabel(editFilterDialog)
        self.typeLabel.setObjectName("typeLabel")
        self.paramsPane.addWidget(self.typeLabel, 1, 0, 1, 1)
        self.filterOrder = QtWidgets.QSpinBox(editFilterDialog)
        self.filterOrder.setEnabled(True)
        self.filterOrder.setMinimum(1)
        self.filterOrder.setMaximum(24)
        self.filterOrder.setProperty("value", 2)
        self.filterOrder.setObjectName("filterOrder")
        self.paramsPane.addWidget(self.filterOrder, 3, 1, 1, 1)
        self.gainLabel = QtWidgets.QLabel(editFilterDialog)
        self.gainLabel.setObjectName("gainLabel")
        self.paramsPane.addWidget(self.gainLabel, 7, 0, 1, 1)
        self.filterQLabel = QtWidgets.QLabel(editFilterDialog)
        self.filterQLabel.setObjectName("filterQLabel")
        self.paramsPane.addWidget(self.filterQLabel, 5, 0, 1, 1)
        self.sLabel = QtWidgets.QLabel(editFilterDialog)
        self.sLabel.setObjectName("sLabel")
        self.paramsPane.addWidget(self.sLabel, 6, 0, 1, 1)
        self.freqStepButton = QtWidgets.QToolButton(editFilterDialog)
        self.freqStepButton.setObjectName("freqStepButton")
        self.paramsPane.addWidget(self.freqStepButton, 4, 2, 1, 1)
        self.filterQ = QtWidgets.QDoubleSpinBox(editFilterDialog)
        self.filterQ.setDecimals(4)
        self.filterQ.setMinimum(0.001)
        self.filterQ.setMaximum(20.0)
        self.filterQ.setSingleStep(0.0001)
        self.filterQ.setProperty("value", 0.7071)
        self.filterQ.setObjectName("filterQ")
        self.paramsPane.addWidget(self.filterQ, 5, 1, 1, 1)
        self.orderLabel = QtWidgets.QLabel(editFilterDialog)
        self.orderLabel.setObjectName("orderLabel")
        self.paramsPane.addWidget(self.orderLabel, 3, 0, 1, 1)
        self.filterCount = QtWidgets.QSpinBox(editFilterDialog)
        self.filterCount.setMinimum(1)
        self.filterCount.setMaximum(20)
        self.filterCount.setObjectName("filterCount")
        self.paramsPane.addWidget(self.filterCount, 8, 1, 1, 1)
        self.filterGain = QtWidgets.QDoubleSpinBox(editFilterDialog)
        self.filterGain.setDecimals(1)
        self.filterGain.setMinimum(-30.0)
        self.filterGain.setMaximum(30.0)
        self.filterGain.setSingleStep(0.1)
        self.filterGain.setObjectName("filterGain")
        self.paramsPane.addWidget(self.filterGain, 7, 1, 1, 1)
        self.gainStepButton = QtWidgets.QToolButton(editFilterDialog)
        self.gainStepButton.setObjectName("gainStepButton")
        self.paramsPane.addWidget(self.gainStepButton, 7, 2, 1, 1)
        self.freqLabel = QtWidgets.QLabel(editFilterDialog)
        self.freqLabel.setObjectName("freqLabel")
        self.paramsPane.addWidget(self.freqLabel, 4, 0, 1, 1)
        self.freq = QtWidgets.QDoubleSpinBox(editFilterDialog)
        self.freq.setDecimals(1)
        self.freq.setMinimum(1.0)
        self.freq.setMaximum(500.0)
        self.freq.setSingleStep(0.1)
        self.freq.setProperty("value", 40.0)
        self.freq.setObjectName("freq")
        self.paramsPane.addWidget(self.freq, 4, 1, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.paramsPane.addItem(spacerItem, 13, 1, 1, 1)
        self.qStepButton = QtWidgets.QToolButton(editFilterDialog)
        self.qStepButton.setObjectName("qStepButton")
        self.paramsPane.addWidget(self.qStepButton, 5, 2, 1, 1)
        self.sStepButton = QtWidgets.QToolButton(editFilterDialog)
        self.sStepButton.setObjectName("sStepButton")
        self.paramsPane.addWidget(self.sStepButton, 6, 2, 1, 1)
        self.filterS = QtWidgets.QDoubleSpinBox(editFilterDialog)
        self.filterS.setEnabled(False)
        self.filterS.setDecimals(4)
        self.filterS.setMinimum(0.1)
        self.filterS.setMaximum(100.0)
        self.filterS.setSingleStep(0.0001)
        self.filterS.setProperty("value", 1.0)
        self.filterS.setObjectName("filterS")
        self.paramsPane.addWidget(self.filterS, 6, 1, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.addButton = QtWidgets.QToolButton(editFilterDialog)
        self.addButton.setObjectName("addButton")
        self.horizontalLayout.addWidget(self.addButton)
        self.saveButton = QtWidgets.QToolButton(editFilterDialog)
        self.saveButton.setText("")
        self.saveButton.setObjectName("saveButton")
        self.horizontalLayout.addWidget(self.saveButton)
        self.exitButton = QtWidgets.QToolButton(editFilterDialog)
        self.exitButton.setObjectName("exitButton")
        self.horizontalLayout.addWidget(self.exitButton)
        self.limitsButton = QtWidgets.QToolButton(editFilterDialog)
        self.limitsButton.setObjectName("limitsButton")
        self.horizontalLayout.addWidget(self.limitsButton)
        self.paramsPane.addLayout(self.horizontalLayout, 10, 0, 1, 3)
        self.filterSelector = QtWidgets.QComboBox(editFilterDialog)
        self.filterSelector.setObjectName("filterSelector")
        self.paramsPane.addWidget(self.filterSelector, 0, 0, 1, 3)
        self.filterCountLabel = QtWidgets.QLabel(editFilterDialog)
        self.filterCountLabel.setObjectName("filterCountLabel")
        self.paramsPane.addWidget(self.filterCountLabel, 8, 0, 1, 1)
        self.showIndividual = QtWidgets.QCheckBox(editFilterDialog)
        self.showIndividual.setChecked(True)
        self.showIndividual.setObjectName("showIndividual")
        self.paramsPane.addWidget(self.showIndividual, 9, 0, 1, 3)
        self.paramsPane.setColumnStretch(0, 1)
        self.panes.addLayout(self.paramsPane, 0, 0, 1, 1)
        self.panes.setColumnStretch(1, 1)

        self.retranslateUi(editFilterDialog)
        self.filterType.currentTextChanged['QString'].connect(editFilterDialog.enableFilterParams)
        self.passFilterType.currentTextChanged['QString'].connect(editFilterDialog.changeOrderStep)
        self.filterGain.valueChanged['double'].connect(editFilterDialog.enableOkIfGainIsValid)
        self.filterQ.valueChanged['double'].connect(editFilterDialog.recalcShelfFromQ)
        self.filterGain.valueChanged['double'].connect(editFilterDialog.recalcShelfFromGain)
        self.filterType.currentIndexChanged['int'].connect(editFilterDialog.previewFilter)
        self.passFilterType.currentIndexChanged['int'].connect(editFilterDialog.previewFilter)
        self.filterOrder.valueChanged['int'].connect(editFilterDialog.previewFilter)
        self.freq.valueChanged['double'].connect(editFilterDialog.previewFilter)
        self.filterQ.valueChanged['double'].connect(editFilterDialog.previewFilter)
        self.filterGain.valueChanged['double'].connect(editFilterDialog.previewFilter)
        self.filterCount.valueChanged['int'].connect(editFilterDialog.previewFilter)
        self.filterS.valueChanged['double'].connect(editFilterDialog.recalcShelfFromS)
        self.sStepButton.clicked.connect(editFilterDialog.handleSToolButton)
        self.qStepButton.clicked.connect(editFilterDialog.handleQToolButton)
        self.gainStepButton.clicked.connect(editFilterDialog.handleGainToolButton)
        self.freqStepButton.clicked.connect(editFilterDialog.handleFreqToolButton)
        self.saveButton.clicked.connect(editFilterDialog.accept)
        self.exitButton.clicked.connect(editFilterDialog.reject)
        self.filterSelector.currentIndexChanged['int'].connect(editFilterDialog.select_filter)
        self.showIndividual.clicked.connect(editFilterDialog.previewFilter)
        self.addButton.clicked.connect(editFilterDialog.add)
        self.limitsButton.clicked.connect(editFilterDialog.show_limits)
        QtCore.QMetaObject.connectSlotsByName(editFilterDialog)
        editFilterDialog.setTabOrder(self.filterType, self.passFilterType)
        editFilterDialog.setTabOrder(self.passFilterType, self.filterOrder)
        editFilterDialog.setTabOrder(self.filterOrder, self.freq)
        editFilterDialog.setTabOrder(self.freq, self.filterQ)
        editFilterDialog.setTabOrder(self.filterQ, self.filterS)
        editFilterDialog.setTabOrder(self.filterS, self.filterGain)
        editFilterDialog.setTabOrder(self.filterGain, self.filterCount)
        editFilterDialog.setTabOrder(self.filterCount, self.freqStepButton)
        editFilterDialog.setTabOrder(self.freqStepButton, self.qStepButton)
        editFilterDialog.setTabOrder(self.qStepButton, self.gainStepButton)
        editFilterDialog.setTabOrder(self.gainStepButton, self.sStepButton)
        editFilterDialog.setTabOrder(self.sStepButton, self.previewChart)

    def retranslateUi(self, editFilterDialog):
        _translate = QtCore.QCoreApplication.translate
        editFilterDialog.setWindowTitle(_translate("editFilterDialog", "Create Filter"))
        self.passFilterType.setItemText(0, _translate("editFilterDialog", "Butterworth"))
        self.passFilterType.setItemText(1, _translate("editFilterDialog", "Linkwitz-Riley"))
        self.filterType.setItemText(0, _translate("editFilterDialog", "Low Shelf"))
        self.filterType.setItemText(1, _translate("editFilterDialog", "High Shelf"))
        self.filterType.setItemText(2, _translate("editFilterDialog", "PEQ"))
        self.filterType.setItemText(3, _translate("editFilterDialog", "Gain"))
        self.filterType.setItemText(4, _translate("editFilterDialog", "Variable Q LPF"))
        self.filterType.setItemText(5, _translate("editFilterDialog", "Variable Q HPF"))
        self.filterType.setItemText(6, _translate("editFilterDialog", "Low Pass"))
        self.filterType.setItemText(7, _translate("editFilterDialog", "High Pass"))
        self.typeLabel.setText(_translate("editFilterDialog", "Type"))
        self.gainLabel.setText(_translate("editFilterDialog", "Gain"))
        self.filterQLabel.setText(_translate("editFilterDialog", "Q"))
        self.sLabel.setText(_translate("editFilterDialog", "S"))
        self.freqStepButton.setText(_translate("editFilterDialog", "..."))
        self.orderLabel.setText(_translate("editFilterDialog", "Order"))
        self.gainStepButton.setText(_translate("editFilterDialog", "..."))
        self.freqLabel.setText(_translate("editFilterDialog", "Freq"))
        self.qStepButton.setText(_translate("editFilterDialog", "..."))
        self.sStepButton.setText(_translate("editFilterDialog", "..."))
        self.addButton.setText(_translate("editFilterDialog", "..."))
        self.saveButton.setToolTip(_translate("editFilterDialog", "Save"))
        self.saveButton.setShortcut(_translate("editFilterDialog", "Return"))
        self.exitButton.setToolTip(_translate("editFilterDialog", "Exit"))
        self.exitButton.setText(_translate("editFilterDialog", "..."))
        self.limitsButton.setText(_translate("editFilterDialog", "..."))
        self.filterCountLabel.setText(_translate("editFilterDialog", "Count"))
        self.showIndividual.setText(_translate("editFilterDialog", "Show Individual Filters"))


from mpl import MplWidget
